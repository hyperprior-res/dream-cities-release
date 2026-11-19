"""Faster emulator inference that is the same model: a drop-in for the audit judge and the RL environment.

What changes (and nothing else does):

1. **Trunk, fc1 + GELU in one GEMM.** Every ConvNeXt block's first MLP layer and its tanh-GELU run as one
   cuBLASLt GEMM with a bias-GELU epilogue (``torch._addmm_activation(..., use_gelu=True)``, which is the
   tanh approximation the model uses). Same weights, same operand precision as the tag under autocast
   (bf16 inputs and weights, float32 accumulation); the bias and GELU are applied to the float32
   accumulator before the one rounding to bf16, where the tag's path rounds the GEMM output to bf16 first.
   That removes one read and one write of the 4x-wide hidden activation per block (the largest non-GEMM
   cost of a step). Everything else in the trunk is the tag's own code path, op for op. On CPU (no autocast)
   the fused call is plain float32 ``addmm`` followed by the same GELU.
2. **CUDA graphs for the trunk** at each batch shape it meets (captured lazily, at most ``max_graphs``):
   the same kernels replayed without per-kernel launch cost and without the GPU waiting for the host after
   the sampling's host synchronisations. The trunk draws no random numbers.
3. **The action raster built on the card** (``raster_rows``), from the same rectangles as
   ``dc.grammar.raster_batch`` (exactly equal; tested), instead of on the host and copied over.

What does not change: the sampling (every random draw, in the same order, with the same shapes, from the
same generator), the three stages, the heads' numerics, the decoding, the batch layout. The model's own
``sample_next`` and ``rollout`` run unchanged; only the instance's trunk function is replaced. So for a
given seed and batch layout the fast path consumes the identical random stream, and its samples differ
from the tag's only where a floating-point difference in a distribution parameter moves a draw across a
threshold (as the tag's own eager and compiled trunks differ from each other). Within a rollout one moved
draw changes every later month of that sample, so long rollouts agree in distribution, not element for
element (measured: ``results/perf/report.md``).

Measured and refused: compiling the sampling tail (``experimental_compiled_tail``, not reachable from
``accelerate``): it reassigns random draws among quantities (identical trunk output in, 5.6 per cent of
half-overlay cells differ), so it is not the same sampler. Graphs are not captured above 256 rows (no gain
there, and two large graphs exhaust a 24 GB card).

Use (one line each for the owners of ``dc.audit`` and ``dc.rl_adaptor``)::

    from dc import fast
    fast.accelerate(model)                 # instead of model.compile_trunk(dynamic=False)
    traj = fast.emulator_rollout(model, state0, plans, K, device, max_batch)   # instead of audit.emulator_rollout

The equivalence tests are ``code/tests/test_fast.py`` (CPU, tiny size: fused trunk equals the tag's trunk to
float32 rounding; samples equal element for element under the same seed; raster exactly equal) and
``code/scripts/bench_fast.py equiv`` (GPU, trained checkpoint, held-out states: every head's distribution
parameters against the tag's eager and compiled trunks).
"""

from __future__ import annotations

import hashlib
import inspect
import sys
from typing import Callable, Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F


def _source_sha(model) -> str:
    """sha256 of the source text of the model package's ``Trunk.forward`` + ``Block.forward``."""
    mod = sys.modules[type(model).__module__]
    src = inspect.getsource(mod.Trunk.forward) + inspect.getsource(mod.Block.forward)
    return hashlib.sha256(src.encode()).hexdigest()


# The sources the fused restatement below was written against: tag ladder-v2, dc/model.py, verbatim. The
# fused trunk restates Trunk.forward; if a model package's code differs from this text, ``accelerate`` refuses.
_REF_TRUNK_FORWARD = '''    def forward(self, tile_index: torch.Tensor, flags: torch.Tensor, power: torch.Tensor, half: torch.Tensor,
                eighth: torch.Tensor, raster: torch.Tensor, cond: torch.Tensor,
                terrain: Optional[torch.Tensor] = None, com_rate: Optional[torch.Tensor] = None):
        B = tile_index.shape[0]
        # full resolution, NHWC
        other = torch.cat([flags, power.unsqueeze(1), raster.to(flags.dtype)], dim=1)       # (B,21,X,Y)
        f0 = self.tile_emb(tile_index) + self.full_in(other.permute(0, 2, 3, 1))
        f0 = self.full_norm(f0)                                                              # (B,X,Y,d0)
        x0 = nhwc_to_nchw(f0)
        # 60 x 50
        e8 = torch.stack([eighth[:, i] / s for i, s in enumerate(EIGHTH_IN_SCALE)], dim=1)   # (B,3,15,13)
        e8_up = e8.repeat_interleave(4, dim=2).repeat_interleave(4, dim=3)[:, :, :, :WORLD_H_2]
        ov = torch.cat([half / HALF_IN_SCALE, e8_up], dim=1).permute(0, 2, 3, 1)
        h1 = self.patch(x0) + nhwc_to_nchw(self.half_in(ov))
        for b in self.enc1:
            h1 = b(h1, cond)
        # 30 x 25
        h2 = self.down1(h1)
        if terrain is not None:
            h2 = h2 + nhwc_to_nchw(self.terrain_in((terrain.float() / 255.0).unsqueeze(-1)))
        for b in self.enc2:
            h2 = b(h2, cond)
        # 15 x 13 (right-pad 25 -> 26 so cells align with the engine's 8 x 8 blocks)
        h3 = self.down2(F.pad(self.down2_norm(h2), (0, 1)))
        h3 = h3 + nhwc_to_nchw(self.eighth_in(e8.permute(0, 2, 3, 1)))
        if com_rate is not None:
            h3 = h3 + nhwc_to_nchw(self.com_rate_in((com_rate.float() / 64.0).unsqueeze(-1)))
        for b in self.bot:
            h3 = b(h3, cond)
        # back up
        u2 = self.up2(h3)[:, :, :, :WORLD_H_2 // 2] + h2
        for b in self.dec2:
            u2 = b(u2, cond)
        u1 = self.up1(u2) + h1
        for b in self.dec1:
            u1 = b(u1, cond)
        u0 = self.up0(u1) + x0
        for b in self.full:
            u0 = b(u0, cond)
        feat = self.full_out_norm(u0.permute(0, 2, 3, 1))                                    # (B,X,Y,d0)
        dense = self.head_full(feat)                                                         # (B,X,Y,7)
        cur = torch.cat([flags, power.unsqueeze(1)], dim=1).permute(0, 2, 3, 1)              # (B,X,Y,6)
        dense = torch.cat([dense[..., :1], dense[..., 1:] + self.copy_gain * (2.0 * cur - 1.0)], dim=-1)
        half_par = self.head_half(self.half_norm(u1.permute(0, 2, 3, 1)))                    # (B,60,50,5*(1+3k))
        eighth_par = self.head_eighth(self.eighth_norm(h3.permute(0, 2, 3, 1)))              # (B,15,13,3*(1+3k))
        pooled = torch.cat([h3.mean(dim=(2, 3)), u1.mean(dim=(2, 3)), cond], dim=1)
        terrain_par = com_par = None
        if terrain is not None:
            terrain_par = self.head_terrain(self.terrain_norm(u2.permute(0, 2, 3, 1)))      # (B,30,25,1+3k)
            com_par = self.head_com_rate(self.eighth_norm(h3.permute(0, 2, 3, 1)))         # (B,15,13,1+3k)
        return feat, dense, half_par, eighth_par, pooled, terrain_par, com_par
'''
_REF_BLOCK_FORWARD = '''    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        h = self.dw(x).permute(0, 2, 3, 1)
        h = self.norm(h)
        g, b = self.film(cond)[:, None, None, :].chunk(2, dim=-1)
        h = h * (1.0 + g) + b
        h = self.fc2(F.gelu(self.fc1(h), approximate="tanh")) * self.gamma
        return x + h.permute(0, 3, 1, 2)
'''
LADDER_V2_SOURCE_SHA = hashlib.sha256((_REF_TRUNK_FORWARD + _REF_BLOCK_FORWARD).encode()).hexdigest()


# ----------------------------------------------------------------------------------------------
# The trunk with fc1 + GELU fused
# ----------------------------------------------------------------------------------------------
def _fc1_gelu(lin: torch.nn.Linear, h: torch.Tensor) -> torch.Tensor:
    """tanh-GELU(lin(h)) as one GEMM with a bias-GELU epilogue. Under CUDA autocast the operands are cast
    to the autocast dtype exactly as autocast casts them for ``F.linear`` (round to nearest even)."""
    shp = h.shape
    x = h.reshape(-1, shp[-1])
    w, b = lin.weight, lin.bias
    if h.is_cuda and torch.is_autocast_enabled("cuda"):
        dt = torch.get_autocast_dtype("cuda")
        x, w, b = x.to(dt), w.to(dt), b.to(dt)
        out = torch._addmm_activation(b, x, w.t(), use_gelu=True)
    else:
        out = F.gelu(torch.addmm(b, x, w.t()), approximate="tanh")
    return out.view(*shp[:-1], w.shape[0])


def _block(blk, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
    """``Block.forward`` of the tag with fc1 and its GELU fused (see the module docstring)."""
    h = blk.dw(x).permute(0, 2, 3, 1)
    h = blk.norm(h)
    g, b = blk.film(cond)[:, None, None, :].chunk(2, dim=-1)
    h = h * (1.0 + g) + b
    h = blk.fc2(_fc1_gelu(blk.fc1, h)) * blk.gamma
    return x + h.permute(0, 3, 1, 2)


def make_fused_trunk(model) -> Callable:
    """A function with the signature of ``model.trunk`` that restates the tag's ``Trunk.forward`` with
    ``_block`` in place of each ``Block.forward``. Refuses a model whose code differs from the reference."""
    sha = _source_sha(model)
    if sha != LADDER_V2_SOURCE_SHA:
        raise RuntimeError(f"dc.fast: Trunk.forward / Block.forward of {type(model).__module__} differ from the "
                           f"ladder-v2 reference (sha {sha[:12]} != {LADDER_V2_SOURCE_SHA[:12]}); not accelerating")
    mod = sys.modules[type(model).__module__]
    t = model.trunk
    EIGHTH_IN_SCALE, HALF_IN_SCALE, WORLD_H_2 = mod.EIGHTH_IN_SCALE, mod.HALF_IN_SCALE, mod.WORLD_H_2
    nhwc_to_nchw = mod.nhwc_to_nchw

    def forward(tile_index, flags, power, half, eighth, raster, cond, terrain=None, com_rate=None):
        other = torch.cat([flags, power.unsqueeze(1), raster.to(flags.dtype)], dim=1)
        f0 = t.tile_emb(tile_index) + t.full_in(other.permute(0, 2, 3, 1))
        f0 = t.full_norm(f0)
        x0 = nhwc_to_nchw(f0)
        e8 = torch.stack([eighth[:, i] / s for i, s in enumerate(EIGHTH_IN_SCALE)], dim=1)
        e8_up = e8.repeat_interleave(4, dim=2).repeat_interleave(4, dim=3)[:, :, :, :WORLD_H_2]
        ov = torch.cat([half / HALF_IN_SCALE, e8_up], dim=1).permute(0, 2, 3, 1)
        h1 = t.patch(x0) + nhwc_to_nchw(t.half_in(ov))
        for b in t.enc1:
            h1 = _block(b, h1, cond)
        h2 = t.down1(h1)
        if terrain is not None:
            h2 = h2 + nhwc_to_nchw(t.terrain_in((terrain.float() / 255.0).unsqueeze(-1)))
        for b in t.enc2:
            h2 = _block(b, h2, cond)
        h3 = t.down2(F.pad(t.down2_norm(h2), (0, 1)))
        h3 = h3 + nhwc_to_nchw(t.eighth_in(e8.permute(0, 2, 3, 1)))
        if com_rate is not None:
            h3 = h3 + nhwc_to_nchw(t.com_rate_in((com_rate.float() / 64.0).unsqueeze(-1)))
        for b in t.bot:
            h3 = _block(b, h3, cond)
        u2 = t.up2(h3)[:, :, :, :WORLD_H_2 // 2] + h2
        for b in t.dec2:
            u2 = _block(b, u2, cond)
        u1 = t.up1(u2) + h1
        for b in t.dec1:
            u1 = _block(b, u1, cond)
        u0 = t.up0(u1) + x0
        for b in t.full:
            u0 = _block(b, u0, cond)
        feat = t.full_out_norm(u0.permute(0, 2, 3, 1))
        dense = t.head_full(feat)
        cur = torch.cat([flags, power.unsqueeze(1)], dim=1).permute(0, 2, 3, 1)
        dense = torch.cat([dense[..., :1], dense[..., 1:] + t.copy_gain * (2.0 * cur - 1.0)], dim=-1)
        half_par = t.head_half(t.half_norm(u1.permute(0, 2, 3, 1)))
        eighth_par = t.head_eighth(t.eighth_norm(h3.permute(0, 2, 3, 1)))
        pooled = torch.cat([h3.mean(dim=(2, 3)), u1.mean(dim=(2, 3)), cond], dim=1)
        terrain_par = com_par = None
        if terrain is not None:
            terrain_par = t.head_terrain(t.terrain_norm(u2.permute(0, 2, 3, 1)))
            com_par = t.head_com_rate(t.eighth_norm(h3.permute(0, 2, 3, 1)))
        return feat, dense, half_par, eighth_par, pooled, terrain_par, com_par

    return forward


# ----------------------------------------------------------------------------------------------
# CUDA graphs
# ----------------------------------------------------------------------------------------------
class GraphedTrunk:
    """Replays a captured CUDA graph of ``fn`` per input signature (shapes, dtypes, autocast state).

    Inputs are copied into static buffers, the graph replays, and the static outputs are returned: they are
    valid until the next call (``sample_next`` consumes them before it calls the trunk again; nothing it
    returns aliases them). One memory pool is shared by every graph of the instance. Beyond ``max_graphs``
    signatures, and for batches above ``max_rows`` rows, the function runs without a graph."""

    def __init__(self, fn: Callable, max_graphs: int = 8, warmup: int = 3, max_rows: int = 256) -> None:
        self.fn, self.max_graphs, self.warmup, self.max_rows = fn, int(max_graphs), int(warmup), int(max_rows)
        self.graphs: Dict[tuple, tuple] = {}
        self.pool = None
        self.n_replays = 0
        self.n_fallback = 0

    @staticmethod
    def _key(args) -> tuple:
        sig = tuple(None if a is None else (tuple(a.shape), a.dtype, a.stride()) for a in args)
        return sig + (torch.is_autocast_enabled("cuda"), torch.get_autocast_dtype("cuda"))

    def _capture(self, args):
        static_in = [None if a is None else a.clone() for a in args]
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            for _ in range(self.warmup):                      # compiles, autotunes cuDNN, warms the allocator
                self.fn(*static_in)
        torch.cuda.current_stream().wait_stream(s)
        if self.pool is None:
            self.pool = torch.cuda.graph_pool_handle()
        g = torch.cuda.CUDAGraph()
        with torch.cuda.graph(g, pool=self.pool):
            static_out = self.fn(*static_in)
        return static_in, static_out, g

    def __call__(self, *args):
        key = self._key(args)
        ent = self.graphs.get(key)
        if ent is None:
            # Each graph keeps its activations' memory for its lifetime (one pool shared by all graphs, but the
            # warm-up before a capture runs outside it). Above max_rows rows launch costs are a small share of a
            # step, so large shapes run without a graph (measured: 2 per cent at 256 rows; a 416-row capture
            # beside a 512-row graph ran out of the gpu-b's 24 GB).
            if len(self.graphs) >= self.max_graphs or args[0].shape[0] > self.max_rows:
                self.n_fallback += 1
                return self.fn(*args)
            ent = self.graphs[key] = self._capture(args)
        static_in, static_out, g = ent
        for buf, a in zip(static_in, args):
            if buf is not None:
                buf.copy_(a)
        g.replay()
        self.n_replays += 1
        return static_out


# ----------------------------------------------------------------------------------------------
# REFUSED lever, kept only to reproduce its measurement (``bench_fast.py tailcheck``): the sampling tail compiled.
# Measured on the 50M checkpoint, 2,000 held-out states, identical trunk output in: the random generator ends
# in the same state, but 5.6 per cent of half-overlay cells, 2.1 per cent of eighth-overlay cells and 9 per cent
# of scalars differ from the tag's tail (the compiled code assigns the same draws to other quantities), and
# recompilation made it slower. Not reachable from ``accelerate``.
# ----------------------------------------------------------------------------------------------
def _fallback_random(fn: Callable) -> Callable:
    """Run ``fn`` (a torch.compile'd function) with inductor's ``fallback_random`` on: compiled code then draws
    its random numbers with the ATen calls eager code makes (same generator, shapes and order), not with
    inductor's own Philox stream."""
    import torch._inductor.config as ic

    def w(*a, **k):
        with ic.patch(fallback_random=True):
            return fn(*a, **k)
    return w


def _scalar_stage_forward(ss, dense_part: Callable) -> Callable:
    """The tag's ``ScalarStage.forward`` with its static-shaped part (overlay networks, level table, the MLP)
    as one compiled function; the changed-tile part (data-dependent shapes) stays eager, op for op."""
    def forward(pooled, s0, s1, raster, spend_cost, cond_in=None, state_x=None, direct=None):
        mod = sys.modules[type(ss).__module__]
        k0, k1 = mod.scalar_keys(s0), mod.scalar_keys(s1)
        B = k0.shape[0]
        dev = k0.device
        skip = torch.zeros(B, ss.nL, device=dev)
        tfeat = torch.zeros(B, ss.ss_table_dim, device=dev)
        cfeat = torch.zeros(B, ss.ss_change_dim, device=dev)
        bi, xi, yi = (k0 != k1).nonzero(as_tuple=True)
        if bi.numel() > 0:
            a, b = k0[bi, xi, yi], k1[bi, xi, yi]
            skip = skip.index_add(0, bi, ss.delta_skip(b) - ss.delta_skip(a))
            tfeat = tfeat.index_add(0, bi, ss.delta_feat(b) - ss.delta_feat(a))
            r = raster[bi, :, xi, yi].float()
            price = (r * spend_cost).sum(-1, keepdim=True) / 100.0
            sh = torch.arange(4, device=dev)
            x = torch.cat([ss.code_emb(a >> 4), ss.code_emb(b >> 4), r, price,
                           ((a & 15).unsqueeze(1) >> sh & 1).float(), ((b & 15).unsqueeze(1) >> sh & 1).float()], dim=1)
            o = ss.change_mlp(x)
            skip = skip.index_add(0, bi, o[:, :ss.nL])
            cfeat = cfeat.index_add(0, bi, o[:, ss.nL:])
        return dense_part(tfeat, cfeat, skip, pooled, s0["half"], s1["half"], s0["eighth"], s1["eighth"], k1,
                          cond_in, state_x, direct)
    return forward


def _scalar_stage_dense(ss) -> Callable:
    mod = sys.modules[type(ss).__module__]
    HALF_IN_SCALE, EIGHTH_IN_SCALE = mod.HALF_IN_SCALE, mod.EIGHTH_IN_SCALE
    WORLD_W_2, WORLD_H_2, WORLD_W_8, WORLD_H_8 = mod.WORLD_W_2, mod.WORLD_H_2, mod.WORLD_W_8, mod.WORLD_H_8

    def dense_part(tfeat, cfeat, skip, pooled, h0, h1, e0, e1, k1, cond_in, state_x, direct):
        B = k1.shape[0]
        dev = k1.device
        hv = torch.cat([h1, h0], dim=1).float().permute(0, 2, 3, 1) / HALF_IN_SCALE
        hp = ss.half_mlp(hv).sum(dim=(1, 2)) / (WORLD_W_2 * WORLD_H_2)
        sc = torch.tensor(EIGHTH_IN_SCALE * 2, device=dev)
        ev = torch.cat([e1, e0], dim=1).float().permute(0, 2, 3, 1) / sc
        ep = ss.eighth_mlp(ev).sum(dim=(1, 2)) / (WORLD_W_8 * WORLD_H_8)
        parts = [tfeat, cfeat / 10.0, hp, ep, pooled.float()]
        if ss.ss_level_dim > 0:
            lv = ss.level(k1.reshape(B, -1)) / 1000.0
            parts.append(ss.level_norm(lv) + lv)
        if ss.ss_direct_cond:
            parts.append(cond_in.float())
        if ss.ledger:
            parts.append(direct.float())
            skip = skip + ss.state_skip(state_x.float())
        h = ss.norm(torch.cat(parts, dim=1))
        return ss.mlp(h), skip
    return dense_part


_REF_SCALAR_STAGE_FORWARD = '''    def forward(self, pooled: torch.Tensor, s0: State, s1: State, raster: torch.Tensor, spend_cost: torch.Tensor,
                cond_in: Optional[torch.Tensor] = None, state_x: Optional[torch.Tensor] = None,
                direct: Optional[torch.Tensor] = None):
        k0, k1 = scalar_keys(s0), scalar_keys(s1)
        B = k0.shape[0]
        dev = k0.device
        skip = torch.zeros(B, self.nL, device=dev)
        tfeat = torch.zeros(B, self.ss_table_dim, device=dev)
        cfeat = torch.zeros(B, self.ss_change_dim, device=dev)
        bi, xi, yi = (k0 != k1).nonzero(as_tuple=True)
        if bi.numel() > 0:
            a, b = k0[bi, xi, yi], k1[bi, xi, yi]
            skip = skip.index_add(0, bi, self.delta_skip(b) - self.delta_skip(a))
            tfeat = tfeat.index_add(0, bi, self.delta_feat(b) - self.delta_feat(a))
            r = raster[bi, :, xi, yi].float()
            price = (r * spend_cost).sum(-1, keepdim=True) / 100.0
            sh = torch.arange(4, device=dev)
            x = torch.cat([self.code_emb(a >> 4), self.code_emb(b >> 4), r, price,
                           ((a & 15).unsqueeze(1) >> sh & 1).float(), ((b & 15).unsqueeze(1) >> sh & 1).float()], dim=1)
            o = self.change_mlp(x)
            skip = skip.index_add(0, bi, o[:, :self.nL])
            cfeat = cfeat.index_add(0, bi, o[:, self.nL:])
        hv = torch.cat([s1["half"], s0["half"]], dim=1).float().permute(0, 2, 3, 1) / HALF_IN_SCALE
        hp = self.half_mlp(hv).sum(dim=(1, 2)) / (WORLD_W_2 * WORLD_H_2)
        sc = torch.tensor(EIGHTH_IN_SCALE * 2, device=dev)
        ev = torch.cat([s1["eighth"], s0["eighth"]], dim=1).float().permute(0, 2, 3, 1) / sc
        ep = self.eighth_mlp(ev).sum(dim=(1, 2)) / (WORLD_W_8 * WORLD_H_8)
        parts = [tfeat, cfeat / 10.0, hp, ep, pooled.float()]
        if self.ss_level_dim > 0:
            lv = self.level(k1.reshape(B, -1)) / 1000.0
            parts.append(self.level_norm(lv) + lv)
        if self.ss_direct_cond:
            parts.append(cond_in.float())
        if self.ledger:
            parts.append(direct.float())
            skip = skip + self.state_skip(state_x.float())
        h = self.norm(torch.cat(parts, dim=1))
        return self.mlp(h), skip
'''
SCALAR_STAGE_SOURCE_SHA = hashlib.sha256(_REF_SCALAR_STAGE_FORWARD.encode()).hexdigest()


def experimental_compiled_tail(model) -> None:
    """REFUSED (see the comment above this section). Compile the sampling tail of the instance: ``_sample_overlay`` and ``_sample_bk`` (the tag's methods,
    unchanged, compiled at fixed shapes with every random draw through ATen) and the static-shaped part of the
    second stage (restated above; refused if the tag's ``ScalarStage.forward`` differs). Data-dependent parts
    (the changed tiles and their categorical) stay eager."""
    import torch._dynamo.config as dyn
    mod = sys.modules[type(model).__module__]
    sha = hashlib.sha256(inspect.getsource(mod.ScalarStage.forward).encode()).hexdigest()
    if sha != SCALAR_STAGE_SOURCE_SHA:
        raise RuntimeError("dc.fast: ScalarStage.forward differs from the ladder-v2 reference; tail not accelerated")
    dyn.cache_size_limit = max(dyn.cache_size_limit, 64)      # one entry per (overlay, batch) shape
    for name in ("_sample_overlay", "_sample_bk"):
        object.__setattr__(model, name, _fallback_random(torch.compile(getattr(model, name), dynamic=False)))
    ss = model.scalar_stage
    dense = _fallback_random(torch.compile(_scalar_stage_dense(ss), dynamic=False))
    object.__setattr__(ss, "forward", _scalar_stage_forward(ss, dense))


# ----------------------------------------------------------------------------------------------
# The drop-in
# ----------------------------------------------------------------------------------------------
LEVERS = ("fused", "compile", "graphs")


def accelerate(model, fused: bool = True, compile: bool = True, graphs: bool = True, max_graphs: int = 8,
               graph_max_rows: int = 256):
    """Replace the instance's trunk function (``model._trunk_fn``, the hook ``compile_trunk`` uses) by the
    fused trunk, compiled with inductor at fixed shapes and replayed as CUDA graphs. Returns the model.
    ``sample_next`` / ``rollout`` / ``log_prob`` of the model then run the tag's code with this trunk.
    On CPU only the fused restatement is used (no compile, no graphs)."""
    cuda = next(model.parameters()).is_cuda
    fn = make_fused_trunk(model) if fused else model.trunk
    if cuda and compile:
        import torch._dynamo.config as dyn
        # dynamo keeps at most cache_size_limit compiled entries per code object (default 8), counted over batch
        # shapes and model instances in one process; beyond it the trunk silently runs uncompiled
        dyn.cache_size_limit = max(dyn.cache_size_limit, 64)
        fn = torch.compile(fn, dynamic=False)
    if cuda and graphs:
        fn = GraphedTrunk(fn, max_graphs=max_graphs, max_rows=graph_max_rows)
    object.__setattr__(model, "_trunk_fn", fn)
    object.__setattr__(model, "_fast_levers", {"fused": bool(fused), "compile": bool(cuda and compile),
                                               "graphs": bool(cuda and graphs),
                                               "source_sha": _source_sha(model)})
    return model


def describe(model) -> dict:
    """What ``accelerate`` did to this instance (for the judge's description)."""
    return dict(getattr(model, "_fast_levers", {}) or {"fast": False})


# ----------------------------------------------------------------------------------------------
# Raster on the card (exact) and the audit's rollout adaptor
# ----------------------------------------------------------------------------------------------
_AXES: Dict[str, Tuple[torch.Tensor, torch.Tensor]] = {}


def raster_rows(rows: np.ndarray, device, grammar=None) -> torch.Tensor:
    """Canonical plan rows (B, 25) -> float32 (B, 15, 120, 100) on ``device``, equal to
    ``grammar.raster_batch(rows)`` (the same macro rectangles; overlapping marks are 1, as there).
    ``grammar``: the ``dc.grammar`` module to take the geometry from (default: this checkout's)."""
    if grammar is None:
        from . import grammar
    from .engine import WORLD_H, WORLD_W
    r = grammar._rows2d(rows)
    ch, x0, x1, y0, y1, n, _ = grammar._macro_geometry(r)
    dev = torch.device(device)
    key = str(dev)
    if key not in _AXES:
        _AXES[key] = (torch.arange(WORLD_W, device=dev), torch.arange(WORLD_H, device=dev))
    xs, ys = _AXES[key]
    geo = torch.from_numpy(np.stack([np.asarray(a, dtype=np.int64) for a in (ch, x0, x1, y0, y1, n)])).to(dev)
    ch, x0, x1, y0, y1, n = geo.unbind(0)
    valid = (n > 0) & (ch >= 0)
    mx = ((xs >= x0[..., None]) & (xs < x1[..., None])).to(torch.float32)          # (B, M, 120)
    my = ((ys >= y0[..., None]) & (ys < y1[..., None])).to(torch.float32)          # (B, M, 100)
    oh = F.one_hot(ch.clamp(min=0), grammar.N_CHANNELS).to(torch.float32) * valid[..., None]   # (B, M, 15)
    # number of macros of channel c covering (x, y): sum_m oh[b,m,c] mx[b,m,x] my[b,m,y]; marked where > 0
    cnt = torch.einsum("bmc,bmx,bmy->bcxy", oh, mx, my)
    # contiguous like the host array: the same values in another memory layout can take other kernel paths
    return (cnt > 0.5).to(torch.float32).contiguous()


def emulator_rollout(model, state0: dict, plans: np.ndarray, K: int, device, max_batch: int,
                     **decoding) -> np.ndarray:
    """``dc.audit.emulator_rollout`` with the raster built on the card: the same rollout call (the model's own
    default decoding unless ``temperature`` / ``overlay`` are passed), the same inputs (the raster is exactly
    equal), the same random stream. -> (B, K, H+1, 20) float64."""
    from .grammar import N_COLS, action_scalars_batch
    B, H = plans.shape[0], plans.shape[1]
    act = torch.from_numpy(action_scalars_batch(plans.reshape(-1, N_COLS)).reshape(B, H, -1)).to(device)
    P = np.ascontiguousarray(plans)

    def raster(h):
        return raster_rows(P[:, h], device)

    s0 = {k: v.expand(B, *v.shape[1:]) for k, v in state0.items()}
    traj, _ = model.rollout(s0, raster, act, K=K, max_batch=max_batch, **decoding)
    return traj.double().cpu().numpy()
