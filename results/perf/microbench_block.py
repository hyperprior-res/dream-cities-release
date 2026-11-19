"""Microbench: ConvNeXt block, tag form vs fc1+GELU in the cuBLASLt epilogue (torch._addmm_activation)."""
import time, torch, torch.nn as nn, torch.nn.functional as F
torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True; torch.backends.cudnn.benchmark = True
dev = "cuda"


class Block(nn.Module):
    def __init__(self, dim, C, r=4):
        super().__init__()
        self.dw = nn.Conv2d(dim, dim, 7, padding=3, groups=dim)
        self.norm = nn.LayerNorm(dim, elementwise_affine=False)
        self.film = nn.Linear(C, 2 * dim); self.fc1 = nn.Linear(dim, r * dim); self.fc2 = nn.Linear(r * dim, dim)
        self.gamma = nn.Parameter(torch.full((dim,), 0.1))

    def forward(self, x, cond):
        h = self.dw(x).permute(0, 2, 3, 1)
        h = self.norm(h)
        g, b = self.film(cond)[:, None, None, :].chunk(2, dim=-1)
        h = h * (1.0 + g) + b
        h = self.fc2(F.gelu(self.fc1(h), approximate="tanh")) * self.gamma
        return x + h.permute(0, 3, 1, 2)


def fused(blk, x, cond):
    h = blk.dw(x).permute(0, 2, 3, 1)
    h = blk.norm(h)
    g, b = blk.film(cond)[:, None, None, :].chunk(2, dim=-1)
    h = (h * (1.0 + g) + b).to(torch.bfloat16)
    B, X, Y, D = h.shape
    w1 = blk.fc1.weight.to(torch.bfloat16); b1 = blk.fc1.bias.to(torch.bfloat16)
    a = torch._addmm_activation(b1, h.reshape(-1, D), w1.t(), use_gelu=True)
    h = F.linear(a, blk.fc2.weight.to(torch.bfloat16), blk.fc2.bias.to(torch.bfloat16)).view(B, X, Y, D) * blk.gamma
    return x + h.permute(0, 3, 1, 2)


for (dim, X, Y, r) in ((192, 60, 50, 4), (96, 120, 100, 4), (384, 30, 25, 4), (768, 15, 13, 4)):
    blk = Block(dim, 512, r).to(dev).to(memory_format=torch.channels_last).eval()
    with torch.no_grad():
        blk.film.weight.normal_(0, 0.02)
    x = torch.randn(256, dim, X, Y, device=dev).contiguous(memory_format=torch.channels_last)
    c = torch.randn(256, 512, device=dev)
    fo = torch.compile(blk, dynamic=False)
    ff = torch.compile(lambda x, c: fused(blk, x, c), dynamic=False)
    res = {}
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        ref = blk(x, c)
        for name, f in (("eager", blk), ("compiled", fo), ("fused-compiled", ff), ("fused-eager", lambda x, c: fused(blk, x, c))):
            for _ in range(3):
                y = f(x, c)
            torch.cuda.synchronize(); t = time.perf_counter()
            for _ in range(20):
                y = f(x, c)
            torch.cuda.synchronize(); res[name] = (time.perf_counter() - t) / 20 * 1000
            d = (y.float() - ref.float()).abs()
            res[name + "_maxdiff"] = d.max().item()
    print(dim, X, Y, {k: round(v, 3) for k, v in res.items()})
