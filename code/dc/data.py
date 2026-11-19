"""Trajectory store, parallel generation driver, verification against the oracle, batch loaders.

A store is a directory of flat little-endian arrays (memory-mapped for reading) plus small tables:

=================  ======================  =====================================================
file               shape, dtype            content
=================  ======================  =====================================================
``tiles.u16``      (N, 120, 100) uint16    raw tile words, one row per observation
``half.u8``        (N, 5, 60, 50) uint8    density, traffic, pollution, land value, crime
``power.u1``       (N, 1500) uint8         power grid, 0/1 per tile, ``np.packbits`` of (120, 100)
``eighth.i16``     (N, 3, 15, 13) int16    rate of growth, fire coverage, police coverage
``scalars.i64``    (N, 20) int64           ``dc.engine.SCALAR_NAMES``
``ledger.i64``     (N, 27) int64           ``dc.engine.LEDGER_NAMES`` (carried simulator members)
``terrain.u8``     (N, 30, 25) uint8       terrain density map (carried)
``com_rate.i16``   (N, 15, 13) int16       commercial rate map (carried)
``plan.i16``       (T, 25) int16           one encoded grammar month per transition
``build_cost.i64`` (T,) int64              funds the engine charged for the month's tool calls
``refused.u16``    (T,) uint16             tool calls the engine refused that month
``traj.rec``       (J,) ``TRAJ_DTYPE``     one fixed-size record per trajectory (the commit log)
``starts.json``    -                       every start state the store may use (id, family, file, sha256)
``labels.json``    -                       behaviour labels, indexed by ``TRAJ_DTYPE.label_idx``
``gen_config.json`` -                      what generated the store (spec, seeds, file hashes)
``traj.npz``       -                       the per-trajectory table with strings, written at the end
``manifest.json``  -                       counts, shapes, sha256 of every file, the command; written
                                           only when the store is complete
=================  ======================  =====================================================

A trajectory of H months has H + 1 observation rows (row 0 is the observation right after the load)
and H transition rows. Trajectories are stored in generation order j = 0, 1, 2, ..., contiguously.

Crash safety. The record of trajectory j is appended to ``traj.rec`` only after its rows are written
and every data file has been fsynced; records are committed strictly in order of j. The committed
trajectories are therefore exactly the first ``len(traj.rec) // itemsize`` records, whatever else is
in the data files. Reopening a writer truncates a partial record, drops labels no committed record
uses, and truncates every data file to the committed row count, so a killed generation resumes at the
first uncommitted trajectory. Because trajectory j's content and its row offsets are functions of j
only, the store is byte-identical whatever the number of workers and however often it was resumed.

``verify`` is the store's proof that it is the engine's output: it replays stored trajectories from
(start file, stored action log, seed, disasters flag) with ``dc.oracle.replay`` and compares every
stored array and the final full-state hash.

Loader state format (shared with the emulator, ``REBUILD_SPEC.md`` section 4.3), batch size B:

``tile_index`` int64 (B, 120, 100) = tiles & 0x3FF; ``flags`` float32 (B, 5, 120, 100) in the order
zone, bulldozable, burnable, conductive, powered (animation bit dropped); ``power`` float32
(B, 120, 100); ``half`` float32 (B, 5, 60, 50) raw 0..255; ``eighth`` float32 (B, 3, 15, 13);
``scalars`` float32 (B, 20) raw (int64 -> float64 -> float32); ``ledger`` float32 (B, 27) raw
(int64 -> float64 -> float32); ``terrain`` float32 (B, 30, 25) raw; ``com_rate`` float32 (B, 15, 13) raw.

Store formats. ``dc-store-2`` adds ``ledger``, ``terrain`` and ``com_rate`` (the extended observation,
``results/oracle/observation_sufficiency.md``). Stores generated as ``dc-store-1`` get them from
``backfill_ledger``, which replays every trajectory and in the same pass verifies every existing array
and the final hash; the existing array files are never rewritten.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .engine import (
    ANIMBIT, BULLBIT, BURNBIT, COM_RATE_SHAPE, CONDBIT, LEDGER_NAMES, LG, LOMASK, NUM_LEDGER, NUM_SCALARS,
    PROTO_VERSION, PWRBIT, REPO_ROOT, TERRAIN_SHAPE, WORLD_H, WORLD_H_2, WORLD_H_8, WORLD_W, WORLD_W_2,
    WORLD_W_8, ZONEBIT, Engine, Obs,
)

STORE_FORMAT = "dc-store-2"
DATA_ROOT = Path(os.environ.get("WM2_DATA", "<cache>/data"))

PLAN_WIDTH = 25            # 4 budget columns, forced disaster kind, 4 macros x 5
PLAN_FORCED_COL = 4
N_TILES = WORLD_W * WORLD_H
POWER_BYTES = N_TILES // 8  # 1500
RASTER_CHANNELS = 15
ACTION_SCALARS = 11

# name -> (file, dtype, row shape)
OBS_FILES: Dict[str, Tuple[str, str, Tuple[int, ...]]] = {
    "tiles": ("tiles.u16", "<u2", (WORLD_W, WORLD_H)),
    "half": ("half.u8", "|u1", (5, WORLD_W_2, WORLD_H_2)),
    "power": ("power.u1", "|u1", (POWER_BYTES,)),
    "eighth": ("eighth.i16", "<i2", (3, WORLD_W_8, WORLD_H_8)),
    "scalars": ("scalars.i64", "<i8", (NUM_SCALARS,)),
    "ledger": ("ledger.i64", "<i8", (NUM_LEDGER,)),
    "terrain": ("terrain.u8", "|u1", TERRAIN_SHAPE),
    "com_rate": ("com_rate.i16", "<i2", COM_RATE_SHAPE),
}
LEDGER_FILES = ("ledger", "terrain", "com_rate")   # added in dc-store-2; backfilled into dc-store-1 stores
TRANS_FILES: Dict[str, Tuple[str, str, Tuple[int, ...]]] = {
    "plan": ("plan.i16", "<i2", (PLAN_WIDTH,)),
    "build_cost": ("build_cost.i64", "<i8", ()),
    "refused": ("refused.u16", "<u2", ()),
}
ALL_FILES = {**OBS_FILES, **TRANS_FILES}


def _row_bytes(name: str) -> int:
    _, dt, shape = ALL_FILES[name]
    return int(np.dtype(dt).itemsize * int(np.prod(shape, dtype=np.int64)))


ROW_BYTES = {k: _row_bytes(k) for k in ALL_FILES}
OBS_ROW_BYTES = sum(ROW_BYTES[k] for k in OBS_FILES)        # 43,186 (41,830 before the ledger)
LEDGER_ROW_BYTES = sum(ROW_BYTES[k] for k in LEDGER_FILES)  # 1,356
TRANS_ROW_BYTES = sum(ROW_BYTES[k] for k in TRANS_FILES)    # 60

SPLITS = ("train", "heldout")
TRAJ_DTYPE = np.dtype([
    ("traj_id", "<i8"),       # generation index j (equals the record's position)
    ("start_idx", "<i4"),     # into starts.json
    ("family_idx", "<i4"),    # into starts.json "families"
    ("split", "i1"),          # index into SPLITS
    ("disasters", "i1"),      # random disasters on (1) or off (0)
    ("label_idx", "<i2"),     # into labels.json
    ("n_forced", "<i2"),      # months with a forced disaster
    ("H", "<i4"),             # months
    ("seed", "<i8"),          # engine seed
    ("first_obs", "<i8"),     # first observation row
    ("first_trans", "<i8"),   # first transition row
    ("final_hash", "<u8"),    # engine full-state hash after month H
])

# Flag bits in loader channel order: zone, bulldozable, burnable, conductive, powered.
FLAG_BITS = (ZONEBIT, BULLBIT, BURNBIT, CONDBIT, PWRBIT)
FLAG_SHIFTS = tuple(int(b).bit_length() - 1 for b in FLAG_BITS)   # (10, 12, 13, 14, 15)
FLAG_MASK_ALL = 0xFFFF & ~LOMASK                                   # six flag bits incl. animation
FLAG_MASK_MODEL = FLAG_MASK_ALL & ~ANIMBIT                         # the five the model sees


# --------------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------------
def _die_with_parent() -> None:
    """Worker processes get SIGKILL when the parent dies (no orphans writing after a crash)."""
    try:
        import ctypes
        import signal

        ctypes.CDLL("libc.so.6", use_errno=True).prctl(1, int(signal.SIGKILL))  # PR_SET_PDEATHSIG
    except Exception:  # pragma: no cover
        pass


def sha256_file(path, bufsize: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _atomic_write_json(path: Path, obj: Any) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def _read_json(path: Path, default=None):
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def _rel_or_abs(p) -> str:
    p = Path(p).resolve()
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def resolve_path(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else REPO_ROOT / q


def pack_power(power: np.ndarray) -> np.ndarray:
    """(..., 120, 100) 0/1 -> (..., 1500) uint8. Raises if any value is not 0 or 1."""
    p = np.asarray(power)
    if p.size and int(p.max()) > 1:
        raise ValueError("power grid holds values other than 0 and 1; bit packing would lose them")
    lead = p.shape[:-2]
    return np.packbits(p.reshape(lead + (N_TILES,)).astype(np.uint8), axis=-1)


def unpack_power(packed: np.ndarray) -> np.ndarray:
    """(..., 1500) uint8 -> (..., 120, 100) uint8."""
    q = np.asarray(packed)
    lead = q.shape[:-1]
    return np.unpackbits(q, axis=-1, count=N_TILES).reshape(lead + (WORLD_W, WORLD_H))


def obs_arrays(states: Sequence[Obs]) -> Dict[str, np.ndarray]:
    """Stack observations into store rows (power bit-packed)."""
    return {
        "tiles": np.stack([o.tiles for o in states]).astype("<u2", copy=False),
        "half": np.stack([o.half for o in states]).astype("|u1", copy=False),
        "power": pack_power(np.stack([o.power for o in states])),
        "eighth": np.stack([o.eighth for o in states]).astype("<i2", copy=False),
        "scalars": np.stack([o.scalars for o in states]).astype("<i8", copy=False),
        "ledger": np.stack([o.ledger for o in states]).astype("<i8", copy=False),
        "terrain": np.stack([o.terrain for o in states]).astype("|u1", copy=False),
        "com_rate": np.stack([o.com_rate for o in states]).astype("<i2", copy=False),
    }


def refused_counts(tool_ok: Sequence[np.ndarray]) -> np.ndarray:
    return np.asarray([int(np.count_nonzero(np.asarray(r) != 1)) for r in tool_ok], dtype=np.int64)


# --------------------------------------------------------------------------------------------
# writer
# --------------------------------------------------------------------------------------------
class _DataFiles:
    """File descriptors for the eight data files; positional writes only (safe across processes)."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.fds = {k: os.open(str(self.path / f), os.O_RDWR | os.O_CREAT, 0o644) for k, (f, _, _) in ALL_FILES.items()}

    def close(self) -> None:
        for fd in self.fds.values():
            os.close(fd)
        self.fds = {}

    def pwrite(self, name: str, row0: int, arr: np.ndarray) -> None:
        _, dt, shape = ALL_FILES[name]
        a = np.ascontiguousarray(arr, dtype=np.dtype(dt))
        if a.shape[1:] != shape:
            raise ValueError(f"{name}: rows of shape {a.shape[1:]}, expected {shape}")
        b = memoryview(a).cast("B")
        off = int(row0) * ROW_BYTES[name]
        fd = self.fds[name]
        n = 0
        while n < len(b):
            n += os.pwrite(fd, b[n:], off + n)

    def write_trajectory(self, first_obs: int, first_trans: int, obs: Dict[str, np.ndarray],
                         trans: Dict[str, np.ndarray]) -> None:
        for k in OBS_FILES:
            self.pwrite(k, first_obs, obs[k])
        for k in TRANS_FILES:
            self.pwrite(k, first_trans, trans[k])

    def fsync(self) -> None:
        for fd in self.fds.values():
            os.fsync(fd)


class StoreWriter:
    """Append-only, crash-safe writer. Opening it repairs the store to its last commit.

    ``StoreWriter.create(path, starts, config)`` makes a new store; ``StoreWriter(path)`` reopens one
    (and is how a killed generation resumes). A lock file prevents two writers on one store.
    """

    def __init__(self, path):
        self.path = Path(path)
        if not (self.path / "gen_config.json").exists():
            raise FileNotFoundError(f"{self.path} is not a store (no gen_config.json); use StoreWriter.create")
        self._lock = open(self.path / ".writer.lock", "w")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(f"another writer holds {self.path}/.writer.lock")
        self.config = _read_json(self.path / "gen_config.json")
        st = _read_json(self.path / "starts.json")
        self.starts, self.families = st["starts"], st["families"]
        self.labels: List[str] = list(_read_json(self.path / "labels.json", []))
        self.files = _DataFiles(self.path)
        self._rec_fd = os.open(str(self.path / "traj.rec"), os.O_RDWR | os.O_CREAT, 0o644)
        self.repairs: List[str] = []
        self._repair()

    # -- creation ----------------------------------------------------------------------------
    @staticmethod
    def create(path, starts: Sequence[Dict[str, Any]], config: Dict[str, Any]) -> "StoreWriter":
        """``starts``: dicts with start_id, family_id, split ("train"/"heldout"), path (cty file)."""
        path = Path(path)
        if (path / "gen_config.json").exists():
            raise FileExistsError(f"{path} already holds a store")
        path.mkdir(parents=True, exist_ok=True)
        fams: List[str] = []
        table = []
        for s in starts:
            fam = str(s["family_id"])
            if fam not in fams:
                fams.append(fam)
            if s["split"] not in SPLITS:
                raise ValueError(f"split {s['split']!r} not in {SPLITS}")
            cty = resolve_path(_rel_or_abs(s["path"]))
            table.append({
                "start_id": str(s["start_id"]), "family_id": fam, "family_idx": fams.index(fam),
                "split": s["split"], "path": _rel_or_abs(s["path"]), "sha256": sha256_file(cty),
            })
        _atomic_write_json(path / "starts.json", {"starts": table, "families": fams})
        _atomic_write_json(path / "labels.json", [])
        cfg = dict(config)
        cfg.setdefault("store_format", STORE_FORMAT)
        cfg.setdefault("protocol_version", PROTO_VERSION)
        _atomic_write_json(path / "gen_config.json", cfg)
        return StoreWriter(path)

    # -- state -------------------------------------------------------------------------------
    def _read_records(self) -> np.ndarray:
        size = os.fstat(self._rec_fd).st_size
        n = size // TRAJ_DTYPE.itemsize
        if size != n * TRAJ_DTYPE.itemsize:
            os.ftruncate(self._rec_fd, n * TRAJ_DTYPE.itemsize)
            self.repairs.append(f"traj.rec: dropped a partial record ({size - n * TRAJ_DTYPE.itemsize} bytes)")
        if n == 0:
            return np.zeros((0,), dtype=TRAJ_DTYPE)
        buf = os.pread(self._rec_fd, n * TRAJ_DTYPE.itemsize, 0)
        return np.frombuffer(buf, dtype=TRAJ_DTYPE).copy()

    def _repair(self) -> None:
        rec = self._read_records()
        check_records(rec)
        self.n_traj = len(rec)
        self.n_obs = int(rec["first_obs"][-1] + rec["H"][-1] + 1) if len(rec) else 0
        self.n_trans = int(rec["first_trans"][-1] + rec["H"][-1]) if len(rec) else 0
        used = int(rec["label_idx"].max()) + 1 if len(rec) else 0
        if len(self.labels) > used:
            self.repairs.append(f"labels.json: dropped {len(self.labels) - used} labels no committed record uses")
            self.labels = self.labels[:used]
            _atomic_write_json(self.path / "labels.json", self.labels)
        elif len(self.labels) < used:
            raise RuntimeError("labels.json lacks labels that committed records use: store is corrupt")
        for k, (f, _, _) in ALL_FILES.items():
            rows = self.n_obs if k in OBS_FILES else self.n_trans
            need = rows * ROW_BYTES[k]
            have = os.fstat(self.files.fds[k]).st_size
            if have < need:
                raise RuntimeError(f"{f}: {have} bytes on disk, committed records need {need}: store is corrupt")
            if have > need:
                os.ftruncate(self.files.fds[k], need)
                self.repairs.append(f"{f}: truncated {have - need} uncommitted bytes")
        self.records = rec
        self._pending: List[Dict[str, Any]] = []

    # -- writing -----------------------------------------------------------------------------
    def label_index(self, label: str) -> int:
        label = str(label)
        if label not in self.labels:
            self.labels.append(label)
            self._labels_dirty = True
        return self.labels.index(label)

    def commit(self, metas: Sequence[Dict[str, Any]]) -> None:
        """Commit trajectories whose rows are already written, strictly in order of j."""
        if not metas:
            return
        recs = np.zeros((len(metas),), dtype=TRAJ_DTYPE)
        self._labels_dirty = False
        n_obs, n_trans = self.n_obs, self.n_trans
        for i, m in enumerate(metas):
            j = self.n_traj + i
            if int(m["traj_id"]) != j:
                raise RuntimeError(f"commit out of order: got trajectory {m['traj_id']}, expected {j}")
            if int(m["first_obs"]) != n_obs or int(m["first_trans"]) != n_trans:
                raise RuntimeError(f"trajectory {j}: rows at ({m['first_obs']}, {m['first_trans']}), expected ({n_obs}, {n_trans})")
            s = self.starts[int(m["start_idx"])]
            r = recs[i]
            r["traj_id"] = j
            r["start_idx"] = int(m["start_idx"])
            r["family_idx"] = int(s["family_idx"])
            r["split"] = SPLITS.index(s["split"])
            r["disasters"] = 1 if m["disasters"] else 0
            r["label_idx"] = self.label_index(m["label"])
            r["n_forced"] = int(m["n_forced"])
            r["H"] = int(m["H"])
            r["seed"] = int(m["seed"])
            r["first_obs"] = n_obs
            r["first_trans"] = n_trans
            r["final_hash"] = np.uint64(int(m["final_hash"]))
            n_obs += int(m["H"]) + 1
            n_trans += int(m["H"])
        # rows must be durable before the records that point at them
        self.files.fsync()
        if self._labels_dirty:
            _atomic_write_json(self.path / "labels.json", self.labels)
        b = recs.tobytes()
        off = self.n_traj * TRAJ_DTYPE.itemsize
        n = 0
        while n < len(b):
            n += os.pwrite(self._rec_fd, b[n:], off + n)
        os.fsync(self._rec_fd)
        self.records = np.concatenate([self.records, recs])
        self.n_traj += len(metas)
        self.n_obs, self.n_trans = n_obs, n_trans

    def append(self, meta: Dict[str, Any], obs: Dict[str, np.ndarray], trans: Dict[str, np.ndarray]) -> None:
        """Sequential use: write one trajectory at the end and commit it."""
        meta = dict(meta, traj_id=self.n_traj, first_obs=self.n_obs, first_trans=self.n_trans)
        self.files.write_trajectory(self.n_obs, self.n_trans, obs, trans)
        self.commit([meta])

    def finalise(self, command: Optional[str] = None, extra: Optional[Dict[str, Any]] = None,
                 hash_threads: int = 8) -> Dict[str, Any]:
        """Truncate to the committed rows, write traj.npz and manifest.json (with sha256 of every file)."""
        for k in ALL_FILES:
            rows = self.n_obs if k in OBS_FILES else self.n_trans
            os.ftruncate(self.files.fds[k], rows * ROW_BYTES[k])
        self.files.fsync()
        rec = self.records
        table = traj_table(rec, self.starts, self.families, self.labels)
        np.savez(self.path / "traj.npz", **table)
        names = [f for f, _, _ in ALL_FILES.values()] + ["traj.rec", "traj.npz", "starts.json", "labels.json", "gen_config.json"]
        with ThreadPoolExecutor(max(1, hash_threads)) as ex:
            shas = dict(zip(names, ex.map(lambda f: sha256_file(self.path / f), names)))
        arrays = {}
        for k, (f, dt, shape) in ALL_FILES.items():
            rows = self.n_obs if k in OBS_FILES else self.n_trans
            arrays[k] = {"file": f, "dtype": np.dtype(dt).str, "shape": [rows, *shape],
                         "bytes": rows * ROW_BYTES[k], "sha256": shas[f]}
        labels_count = {lab: int(np.count_nonzero(rec["label_idx"] == i)) for i, lab in enumerate(self.labels)}
        man = {
            "store_format": STORE_FORMAT,
            "protocol_version": PROTO_VERSION,
            "status": "complete",
            "name": self.config.get("name"),
            "counts": {"trajectories": int(self.n_traj), "observations": int(self.n_obs), "transitions": int(self.n_trans),
                       "city_months": int(rec["H"].sum()) if len(rec) else 0},
            "by_H": {str(int(h)): int(np.count_nonzero(rec["H"] == h)) for h in np.unique(rec["H"])},
            "by_label": labels_count,
            "disasters_on": int(rec["disasters"].sum()) if len(rec) else 0,
            "arrays": arrays,
            "traj_rec": {"file": "traj.rec", "dtype": [[n, TRAJ_DTYPE.fields[n][0].str] for n in TRAJ_DTYPE.names],
                         "itemsize": TRAJ_DTYPE.itemsize, "sha256": shas["traj.rec"]},
            "tables": {f: shas[f] for f in ("traj.npz", "starts.json", "labels.json", "gen_config.json")},
            "bytes_total": int(sum((self.path / f).stat().st_size for f in names)),
            "command": command,
            "finalised_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if extra:
            man.update(extra)
        _atomic_write_json(self.path / "manifest.json", man)
        return man

    def close(self) -> None:
        if getattr(self, "files", None) is not None:
            self.files.close()
            self.files = None
        if getattr(self, "_rec_fd", None) is not None:
            os.close(self._rec_fd)
            self._rec_fd = None
        if getattr(self, "_lock", None) is not None:
            fcntl.flock(self._lock, fcntl.LOCK_UN)
            self._lock.close()
            self._lock = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def check_records(rec: np.ndarray) -> None:
    """Records are numbered 0.. and contiguous."""
    if not len(rec):
        return
    if not np.array_equal(rec["traj_id"], np.arange(len(rec))):
        raise RuntimeError("traj.rec: trajectory ids are not 0..J-1 in order")
    H = rec["H"].astype(np.int64)
    fo = np.concatenate([[0], np.cumsum(H + 1)[:-1]])
    ft = np.concatenate([[0], np.cumsum(H)[:-1]])
    if not (np.array_equal(rec["first_obs"], fo) and np.array_equal(rec["first_trans"], ft)):
        raise RuntimeError("traj.rec: rows are not contiguous")


def traj_table(rec: np.ndarray, starts: List[Dict], families: List[str], labels: List[str]) -> Dict[str, np.ndarray]:
    sid = np.array([s["start_id"] for s in starts] or [""], dtype=str)
    fam = np.array(families or [""], dtype=str)
    lab = np.array(labels or [""], dtype=str)
    return {
        "traj_id": rec["traj_id"], "start_idx": rec["start_idx"], "start_id": sid[rec["start_idx"]],
        "family_idx": rec["family_idx"], "family_id": fam[rec["family_idx"]],
        "split": np.array(SPLITS)[rec["split"]], "label": lab[rec["label_idx"]], "label_idx": rec["label_idx"],
        "seed": rec["seed"], "disasters": rec["disasters"].astype(bool), "H": rec["H"], "n_forced": rec["n_forced"],
        "first_obs": rec["first_obs"], "first_trans": rec["first_trans"], "final_hash": rec["final_hash"],
    }


# --------------------------------------------------------------------------------------------
# reader
# --------------------------------------------------------------------------------------------
class TrajStore:
    """Random access to a store (complete, or the committed part of one being written)."""

    def __init__(self, path):
        self.path = Path(path)
        self.manifest = _read_json(self.path / "manifest.json")
        self.config = _read_json(self.path / "gen_config.json", {})
        # records before labels: labels.json is always written before the records that use it
        rec_path = self.path / "traj.rec"
        size = rec_path.stat().st_size if rec_path.exists() else 0
        rec = np.fromfile(rec_path, dtype=TRAJ_DTYPE, count=size // TRAJ_DTYPE.itemsize) if size else np.zeros((0,), TRAJ_DTYPE)
        if self.manifest is not None:
            rec = rec[: self.manifest["counts"]["trajectories"]]
        check_records(rec)
        self.traj = rec
        st = _read_json(self.path / "starts.json")
        self.starts, self.families = st["starts"], st["families"]
        self.labels = list(_read_json(self.path / "labels.json", []))
        self.n_traj = len(rec)
        self.n_obs = int(rec["first_obs"][-1] + rec["H"][-1] + 1) if len(rec) else 0
        self.n_trans = int(rec["first_trans"][-1] + rec["H"][-1]) if len(rec) else 0
        self.complete = self.manifest is not None and self.manifest.get("status") == "complete"
        self._first_trans = rec["first_trans"].astype(np.int64)
        self._first_obs = rec["first_obs"].astype(np.int64)
        self._H = rec["H"].astype(np.int64)
        self._mm: Optional[Dict[str, np.memmap]] = None

    # pickling (DataLoader workers under spawn): reopen from the path
    def __getstate__(self):
        return {"path": str(self.path)}

    def __setstate__(self, d):
        self.__init__(d["path"])

    @property
    def has_ledger(self) -> bool:
        """True when the store holds ledger, terrain and com_rate (dc-store-2, or backfilled)."""
        return all((self.path / ALL_FILES[k][0]).exists() for k in LEDGER_FILES)

    def _maps(self) -> Dict[str, np.ndarray]:
        if self._mm is None:
            mm = {}
            has_ledger = self.has_ledger
            for k, (f, dt, shape) in ALL_FILES.items():
                rows = self.n_obs if k in OBS_FILES else self.n_trans
                if k in LEDGER_FILES and not has_ledger:
                    continue
                if rows == 0:
                    mm[k] = np.zeros((0, *shape), dtype=dt)
                else:
                    mm[k] = np.memmap(self.path / f, dtype=dt, mode="r", shape=(rows, *shape))
            self._mm = mm
        return self._mm

    tiles = property(lambda self: self._maps()["tiles"])
    half = property(lambda self: self._maps()["half"])
    power_packed = property(lambda self: self._maps()["power"])
    eighth = property(lambda self: self._maps()["eighth"])
    scalars = property(lambda self: self._maps()["scalars"])
    plan = property(lambda self: self._maps()["plan"])
    build_cost = property(lambda self: self._maps()["build_cost"])
    refused = property(lambda self: self._maps()["refused"])
    ledger = property(lambda self: self._maps()["ledger"])
    terrain = property(lambda self: self._maps()["terrain"])
    com_rate = property(lambda self: self._maps()["com_rate"])

    def __len__(self) -> int:
        return self.n_trans

    # -- addressing --------------------------------------------------------------------------
    def traj_of(self, k) -> np.ndarray:
        k = np.asarray(k, dtype=np.int64)
        return np.searchsorted(self._first_trans, k, side="right") - 1

    def month_of(self, k) -> np.ndarray:
        """Position of transition k within its trajectory (0..H-1)."""
        k = np.asarray(k, dtype=np.int64)
        return k - self._first_trans[self.traj_of(k)]

    def obs_row_of(self, k) -> np.ndarray:
        """Observation row of the state before transition k (the state after is the next row)."""
        k = np.asarray(k, dtype=np.int64)
        if k.size and (k.min() < 0 or k.max() >= self.n_trans):
            raise IndexError("transition id out of range")
        return k + self.traj_of(k)

    # -- access ------------------------------------------------------------------------------
    def obs(self, row: int) -> Obs:
        m = self._maps()
        extra = [np.array(m[k][row]) for k in LEDGER_FILES] if "ledger" in m else []
        return Obs(np.array(m["tiles"][row]), np.array(m["half"][row]), unpack_power(m["power"][row]),
                   np.array(m["eighth"][row]), np.array(m["scalars"][row]), *extra)

    def transition(self, k: int) -> Tuple[Obs, np.ndarray, Obs]:
        """(observation before, encoded grammar month (25,) int16, observation after)."""
        r = int(self.obs_row_of(int(k)))
        return self.obs(r), np.array(self.plan[int(k)]), self.obs(r + 1)

    def record(self, j: int) -> Dict[str, Any]:
        r = self.traj[int(j)]
        s = self.starts[int(r["start_idx"])]
        return {
            "traj_id": int(r["traj_id"]), "start_idx": int(r["start_idx"]), "start_id": s["start_id"],
            "family_id": s["family_id"], "split": SPLITS[int(r["split"])], "label": self.labels[int(r["label_idx"])],
            "seed": int(r["seed"]), "disasters": bool(r["disasters"]), "H": int(r["H"]), "n_forced": int(r["n_forced"]),
            "first_obs": int(r["first_obs"]), "first_trans": int(r["first_trans"]), "final_hash": int(r["final_hash"]),
            "cty_path": str(resolve_path(s["path"])), "cty_sha256": s["sha256"],
        }

    def trajectory(self, j: int) -> Dict[str, Any]:
        """Record fields plus every stored array of trajectory j (power unpacked)."""
        d = self.record(j)
        o, t, H = d["first_obs"], d["first_trans"], d["H"]
        m = self._maps()
        d.update(
            tiles=np.array(m["tiles"][o:o + H + 1]), half=np.array(m["half"][o:o + H + 1]),
            power=unpack_power(m["power"][o:o + H + 1]), eighth=np.array(m["eighth"][o:o + H + 1]),
            scalars=np.array(m["scalars"][o:o + H + 1]), plan=np.array(m["plan"][t:t + H]),
            build_cost=np.array(m["build_cost"][t:t + H]), refused=np.array(m["refused"][t:t + H]),
        )
        if "ledger" in m:
            d.update({k: np.array(m[k][o:o + H + 1]) for k in LEDGER_FILES})
        return d

    # -- index helpers -----------------------------------------------------------------------
    def traj_ids(self, split: Optional[str] = None, families: Optional[Iterable[str]] = None,
                 labels: Optional[Iterable[str]] = None, H: Optional[Iterable[int]] = None,
                 starts: Optional[Iterable[str]] = None, disasters: Optional[bool] = None) -> np.ndarray:
        r = self.traj
        keep = np.ones(len(r), dtype=bool)
        if split is not None:
            keep &= r["split"] == SPLITS.index(split)
        if families is not None:
            fi = [i for i, f in enumerate(self.families) if f in {str(x) for x in families}]
            keep &= np.isin(r["family_idx"], fi)
        if labels is not None:
            li = [i for i, l in enumerate(self.labels) if l in set(labels)]
            keep &= np.isin(r["label_idx"], li)
        if H is not None:
            keep &= np.isin(r["H"], list(H))
        if starts is not None:
            si = [i for i, s in enumerate(self.starts) if s["start_id"] in {str(x) for x in starts}]
            keep &= np.isin(r["start_idx"], si)
        if disasters is not None:
            keep &= r["disasters"] == (1 if disasters else 0)
        return np.flatnonzero(keep).astype(np.int64)

    def transition_ids(self, traj_ids: Optional[Iterable[int]] = None, **filters) -> np.ndarray:
        """All transition ids of the given trajectories (in that order), or of those matching the
        ``traj_ids()`` filters; with both, the given trajectories that match the filters."""
        if traj_ids is None:
            js = self.traj_ids(**filters)
        else:
            js = np.asarray(np.fromiter(traj_ids, dtype=np.int64) if not isinstance(traj_ids, np.ndarray) else traj_ids, dtype=np.int64)
            if filters:
                js = js[np.isin(js, self.traj_ids(**filters))]
        if js.size == 0:
            return np.zeros((0,), dtype=np.int64)
        H = self._H[js]
        starts = self._first_trans[js]
        tot = int(H.sum())
        out = np.repeat(starts - np.concatenate([[0], np.cumsum(H)[:-1]]), H) + np.arange(tot, dtype=np.int64)
        return out

    def multistep_starts(self, index: np.ndarray, k: int) -> np.ndarray:
        """Transition ids in ``index`` that start k consecutive transitions of one trajectory, all in ``index``."""
        idx = np.unique(np.asarray(index, dtype=np.int64))
        if idx.size == 0:
            return idx
        j = self.traj_of(idx)
        pos = idx - self._first_trans[j]
        ok = pos + k <= self._H[j]
        n = idx.size
        for d in range(1, k):
            at = np.minimum(np.searchsorted(idx, idx + d), n - 1)
            ok &= idx[at] == idx + d
        return idx[ok]

    def cty_path(self, j: int) -> Path:
        return resolve_path(self.starts[int(self.traj[int(j)]["start_idx"])]["path"])


def check_manifest(store: TrajStore, hash_threads: int = 8) -> Dict[str, Any]:
    """Recompute the sha256 of every file the manifest lists; return mismatches."""
    if store.manifest is None:
        raise RuntimeError("store has no manifest (not finalised)")
    want = {v["file"]: v["sha256"] for v in store.manifest["arrays"].values()}
    want["traj.rec"] = store.manifest["traj_rec"]["sha256"]
    want.update(store.manifest["tables"])
    names = list(want)
    with ThreadPoolExecutor(max(1, hash_threads)) as ex:
        got = dict(zip(names, ex.map(lambda f: sha256_file(store.path / f), names)))
    return {"files": len(names), "mismatched": [f for f in names if got[f] != want[f]]}


# --------------------------------------------------------------------------------------------
# indices
# --------------------------------------------------------------------------------------------
def save_index(path, transition_ids: np.ndarray, traj_ids: Optional[np.ndarray] = None, meta: Optional[Dict] = None) -> None:
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez(tmp, transition_ids=np.asarray(transition_ids, np.int64),
             traj_ids=np.asarray(traj_ids if traj_ids is not None else [], np.int64),
             meta=np.array(json.dumps(meta or {})))
    os.replace(tmp, path)


def load_index(path) -> Tuple[np.ndarray, Dict[str, Any]]:
    with np.load(path) as z:
        return z["transition_ids"].copy(), json.loads(str(z["meta"]))


def stratified_traj_subset(store: TrajStore, frac: float, seed: int, by: Sequence[str] = ("H", "family", "label"),
                           traj_ids: Optional[np.ndarray] = None) -> np.ndarray:
    """A stratified sample of trajectories: within each value of the first key, exactly round(frac * n)
    trajectories, allocated over the remaining keys' strata by largest remainder, uniform within a stratum."""
    rec = store.traj if traj_ids is None else store.traj[traj_ids]
    ids = np.arange(store.n_traj) if traj_ids is None else np.asarray(traj_ids)
    cols = {"H": rec["H"], "family": rec["family_idx"], "label": rec["label_idx"], "start": rec["start_idx"],
            "disasters": rec["disasters"]}
    rng = np.random.default_rng(seed)
    out: List[np.ndarray] = []
    top, rest = by[0], list(by[1:])
    for v in np.unique(cols[top]):
        sel = cols[top] == v
        n_target = int(round(frac * int(sel.sum())))
        keys = np.stack([cols[c][sel] for c in rest], 1) if rest else np.zeros((int(sel.sum()), 1), np.int64)
        uniq, inv = np.unique(keys, axis=0, return_inverse=True)
        inv = inv.reshape(-1)
        cnt = np.bincount(inv, minlength=len(uniq))
        quota = frac * cnt
        base = np.floor(quota).astype(np.int64)
        short = n_target - int(base.sum())
        if short > 0:
            rema = quota - base
            order = np.lexsort((np.arange(len(uniq)), -rema))   # largest remainder, ties by stratum order
            base[order[:short]] += 1
        sid = ids[sel]
        for s in range(len(uniq)):
            members = sid[inv == s]
            if base[s] > 0:
                out.append(np.sort(rng.choice(members, size=int(base[s]), replace=False)))
    return np.sort(np.concatenate(out)) if out else np.zeros((0,), np.int64)


def open_split(name: str, root=None) -> Tuple[TrajStore, np.ndarray]:
    """(store, transition index) for train_full, train_small, train_eval or heldout_eval."""
    root = Path(root) if root is not None else DATA_ROOT
    if name == "train_small":
        idx, meta = load_index(root / "train_small.npz")
        return TrajStore(root / meta.get("store", "train_full")), idx
    st = TrajStore(root / name)
    return st, np.arange(st.n_trans, dtype=np.int64)


# --------------------------------------------------------------------------------------------
# parallel generation driver
# --------------------------------------------------------------------------------------------
class _GenCtx:
    job = None
    path = None
    files = None
    eng = None
    first_obs = None
    first_trans = None


def _layout(Hs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    H = np.asarray(Hs, dtype=np.int64)
    return np.concatenate([[0], np.cumsum(H + 1)[:-1]]), np.concatenate([[0], np.cumsum(H)[:-1]])


def _gen_init() -> None:
    _die_with_parent()
    _GenCtx.files = _DataFiles(_GenCtx.path)
    _GenCtx.eng = Engine()


def _gen_one(j: int) -> Dict[str, Any]:
    """Run trajectory j, write its rows at their fixed offsets, return its (small) record."""
    job = _GenCtx.job
    H = int(job.Hs[j])
    out = job.run(int(j), _GenCtx.eng)
    rep = out["replay"]
    plan = np.asarray(out["plan"])
    if plan.shape != (H, PLAN_WIDTH):
        raise RuntimeError(f"trajectory {j}: plan shape {plan.shape}, expected {(H, PLAN_WIDTH)}")
    if rep.states is None or len(rep.states) != H + 1:
        raise RuntimeError(f"trajectory {j}: replay must be recorded with record='full' and hold {H + 1} observations")
    obs = obs_arrays(rep.states)
    if not np.array_equal(obs["scalars"], rep.scalars):
        raise RuntimeError(f"trajectory {j}: replay scalars disagree with its observations")
    if getattr(rep, "ledger", None) is not None and not np.array_equal(obs["ledger"], rep.ledger):
        raise RuntimeError(f"trajectory {j}: replay ledger disagrees with its observations")
    if len(rep.build_cost) != H or len(rep.tool_ok) != H:
        raise RuntimeError(f"trajectory {j}: replay holds {len(rep.build_cost)} months, expected {H}")
    trans = {"plan": plan.astype("<i2"), "build_cost": np.asarray(rep.build_cost, dtype="<i8"),
             "refused": refused_counts(rep.tool_ok).astype("<u2")}
    fo, ft = int(_GenCtx.first_obs[j]), int(_GenCtx.first_trans[j])
    _GenCtx.files.write_trajectory(fo, ft, obs, trans)
    return {
        "traj_id": int(j), "start_idx": int(out["start_idx"]), "label": str(out["label"]), "seed": int(out["seed"]),
        "disasters": bool(out["disasters"]), "H": H, "n_forced": int(np.count_nonzero(plan[:, PLAN_FORCED_COL])),
        "first_obs": fo, "first_trans": ft, "final_hash": int(out["final_hash"]),
    }


def _content_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """The part of a generation config that determines the store's content (compared on resume)."""
    return {k: v for k, v in cfg.items() if k not in ("provenance",)}


def _full_config(job) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(job.config()))
    cfg.setdefault("store_format", STORE_FORMAT)
    cfg.setdefault("protocol_version", PROTO_VERSION)
    return cfg


def generate(path, job, workers: int = 1, *, commit_seconds: float = 10.0, crash_after: Optional[int] = None,
             command: Optional[str] = None, log: Callable[[str], None] = print, finalise: bool = True,
             progress_seconds: float = 60.0) -> Dict[str, Any]:
    """Generate (or resume) the store at ``path`` for ``job``.

    ``job`` provides ``n`` (trajectories), ``Hs`` (n,) months per trajectory, ``starts`` (start table
    for ``StoreWriter.create``), ``config()`` (dict; keys other than "provenance" must match on resume)
    and ``run(j, eng) -> dict(start_idx, label, seed, disasters, plan (H,25), replay (record='full'),
    final_hash)``. Trajectory j must depend on j only.

    ``crash_after`` (tests only): after trajectory j = crash_after is reported, write garbage past the
    committed end of every file and kill the process without committing.
    """
    import multiprocessing as mp

    path = Path(path)
    man_done = _read_json(path / "manifest.json")
    if man_done is not None and man_done.get("status") == "complete" and man_done["counts"]["trajectories"] == job.n:
        # finished: the spec must match, but not the code hashes, which later backfills change and record
        # in the manifest
        a = {k: v for k, v in _content_config(_read_json(path / "gen_config.json")).items() if k != "content_files"}
        b = {k: v for k, v in _content_config(_full_config(job)).items() if k != "content_files"}
        if a != b:
            diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            raise RuntimeError(f"{path}: generation config differs from the stored one in {diff}")
        return {"resumed_at": int(job.n), "n": int(job.n), "workers": int(workers), "already_complete": True,
                "n_traj": man_done["counts"]["trajectories"], "n_obs": man_done["counts"]["observations"],
                "n_trans": man_done["counts"]["transitions"]}
    cfg = _full_config(job)
    if not (path / "gen_config.json").exists():
        StoreWriter.create(path, job.starts, cfg).close()
    w = StoreWriter(path)
    try:
        a, b = _content_config(w.config), _content_config(cfg)
        if a != b:
            diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            raise RuntimeError(f"{path}: generation config differs from the stored one in {diff}; refusing to resume")
        for r in w.repairs:
            log(f"[{path.name}] repair: {r}")
        Hs = np.asarray(job.Hs, dtype=np.int64)
        fo, ft = _layout(Hs)
        j0 = w.n_traj
        if j0 and not (np.array_equal(w.records["H"], Hs[:j0]) and np.array_equal(w.records["first_obs"], fo[:j0])):
            raise RuntimeError("committed records do not match the job's layout")
        stats = {"resumed_at": j0, "n": int(job.n), "workers": int(workers)}
        if j0 < job.n:
            log(f"[{path.name}] generating trajectories {j0}..{job.n - 1} ({int(Hs[j0:].sum())} city-months) on {workers} worker(s)")
            _GenCtx.job, _GenCtx.path, _GenCtx.first_obs, _GenCtx.first_trans = job, path, fo, ft
            t0 = time.time()
            last_commit = last_log = t0
            pending: List[Dict[str, Any]] = []
            months_done = 0
            pool = None
            try:
                if workers <= 1:
                    _gen_init()
                    it = (_gen_one(j) for j in range(j0, job.n))
                else:
                    pool = mp.get_context("fork").Pool(workers, initializer=_gen_init)
                    it = pool.imap(_gen_one, range(j0, job.n), chunksize=1)
                for meta in it:
                    pending.append(meta)
                    months_done += meta["H"]
                    if crash_after is not None and meta["traj_id"] >= crash_after:
                        _simulate_crash(w)
                    now = time.time()
                    if now - last_commit >= commit_seconds:
                        batch, pending = pending, []
                        w.commit(batch)
                        last_commit = now
                    if now - last_log >= progress_seconds:
                        el = now - t0
                        rate = months_done / max(el, 1e-9)
                        left = int(Hs[meta["traj_id"] + 1:].sum())
                        log(f"[{path.name}] {meta['traj_id'] + 1}/{job.n} trajectories, {rate:,.0f} city-months/s, "
                            f"elapsed {el / 60:.1f} min, eta {left / max(rate, 1e-9) / 60:.1f} min")
                        last_log = now
                batch, pending = pending, []
                w.commit(batch)
            finally:
                if pending:
                    # complete trajectories reported in order are safe to commit even on an error
                    batch, pending = pending, []
                    w.commit(batch)
                if pool is not None:
                    pool.terminate()
                    pool.join()
                if _GenCtx.files is not None and workers <= 1:
                    _GenCtx.files.close()
                    _GenCtx.files = None
            el = time.time() - t0
            stats.update(seconds=el, city_months=months_done, city_months_per_s=months_done / max(el, 1e-9))
            log(f"[{path.name}] generated {months_done} city-months in {el:.1f} s = {months_done / max(el, 1e-9):,.0f} city-months/s")
        man_old = _read_json(path / "manifest.json")
        already = (man_old is not None and man_old.get("status") == "complete"
                   and man_old["counts"]["trajectories"] == w.n_traj)
        if w.n_traj == job.n and finalise and not already:
            man = w.finalise(command=command, extra={"generation": stats})
            stats["manifest"] = man
        stats.update(n_traj=w.n_traj, n_obs=w.n_obs, n_trans=w.n_trans)
        return stats
    finally:
        w.close()


def _simulate_crash(w: StoreWriter) -> None:
    for k, fd in w.files.fds.items():
        size = os.fstat(fd).st_size
        os.pwrite(fd, b"\xAB" * 777, size)
    os.pwrite(w._rec_fd, b"\xCD" * (TRAJ_DTYPE.itemsize // 2), os.fstat(w._rec_fd).st_size)
    os._exit(17)


# --------------------------------------------------------------------------------------------
# verification against the oracle
# --------------------------------------------------------------------------------------------
class _VerCtx:
    path = None
    compile_plan = None
    store = None
    eng = None


def _default_compile_plan():
    from .grammar import compile_plan  # B1
    return compile_plan


def _ver_init() -> None:
    _die_with_parent()
    _VerCtx.store = TrajStore(_VerCtx.path)
    _VerCtx.eng = Engine()
    if _VerCtx.compile_plan is None:
        _VerCtx.compile_plan = _default_compile_plan()


def _ver_one(j: int) -> Dict[str, Any]:
    from .oracle import replay

    st, eng = _VerCtx.store, _VerCtx.eng
    d = st.trajectory(j)
    bad: Dict[str, int] = {}
    cty = Path(d["cty_path"])
    if not cty.exists() or sha256_file(cty) != d["cty_sha256"]:
        return {"traj_id": j, "H": d["H"], "bad": {"start_file": 1}}
    actions, forced = _VerCtx.compile_plan(d["plan"])
    if len(actions) != d["H"]:
        return {"traj_id": j, "H": d["H"], "bad": {"plan_length": 1}}
    rep = replay(eng, cty, actions, d["seed"], disasters=d["disasters"], forced=forced, record="full", want_hash=True)
    got = obs_arrays(rep.states)
    for k in ("tiles", "half", "eighth", "scalars") + (LEDGER_FILES if "ledger" in d else ()):
        n = int(np.count_nonzero(np.any((got[k] != d[k]).reshape(d["H"] + 1, -1), axis=1)))
        if n:
            bad[k] = n
    if "ledger" in d and getattr(rep, "ledger", None) is not None and not np.array_equal(rep.ledger, d["ledger"]):
        bad["ledger_trajectory"] = 1
    n = int(np.count_nonzero(np.any((unpack_power(got["power"]) != d["power"]).reshape(d["H"] + 1, -1), axis=1)))
    if n:
        bad["power"] = n
    if not np.array_equal(np.asarray(rep.build_cost, np.int64), d["build_cost"].astype(np.int64)):
        bad["build_cost"] = int(np.count_nonzero(np.asarray(rep.build_cost) != d["build_cost"]))
    if not np.array_equal(refused_counts(rep.tool_ok), d["refused"].astype(np.int64)):
        bad["refused"] = int(np.count_nonzero(refused_counts(rep.tool_ok) != d["refused"]))
    if int(rep.hashes[-1]) != d["final_hash"]:
        bad["final_hash"] = 1
    return {"traj_id": j, "H": d["H"], "bad": bad}


def verify(store, n: Optional[int] = None, *, traj_ids: Optional[Sequence[int]] = None, seed: int = 0,
           workers: int = 1, compile_plan: Optional[Callable] = None) -> Dict[str, Any]:
    """Re-replay trajectories with ``dc.oracle.replay`` and compare every stored array and the final
    full-state hash. ``n`` random trajectories (without replacement, ``seed``), or ``traj_ids``, or all."""
    import multiprocessing as mp

    st = store if isinstance(store, TrajStore) else TrajStore(store)
    if traj_ids is not None:
        ids = np.asarray(traj_ids, dtype=np.int64)
    elif n is None or n >= st.n_traj:
        ids = np.arange(st.n_traj, dtype=np.int64)
    else:
        ids = np.sort(np.random.default_rng(seed).choice(st.n_traj, size=int(n), replace=False))
    _VerCtx.path, _VerCtx.compile_plan = st.path, compile_plan
    t0 = time.time()
    if workers <= 1:
        _ver_init()
        res = [_ver_one(int(j)) for j in ids]
    else:
        with mp.get_context("fork").Pool(workers, initializer=_ver_init) as pool:
            res = pool.map(_ver_one, [int(j) for j in ids], chunksize=1)
    el = time.time() - t0
    by_field: Dict[str, int] = {}
    for r in res:
        for k, v in r["bad"].items():
            by_field[k] = by_field.get(k, 0) + 1
    bad_ids = [r["traj_id"] for r in res if r["bad"]]
    months = int(sum(r["H"] for r in res))
    return {
        "store": str(st.path), "checked": len(res), "mismatched": len(bad_ids), "by_field": by_field,
        "mismatched_ids": bad_ids[:50], "observations_compared": int(sum(r["H"] + 1 for r in res)),
        "city_months": months, "seconds": round(el, 2), "city_months_per_s": round(months / max(el, 1e-9), 1),
    }


# --------------------------------------------------------------------------------------------
# summary
# --------------------------------------------------------------------------------------------
def behaviour_type(label: str) -> str:
    """Coarse behaviour type of a label: the part before '/' and '+' (builder, random, noop, budget_sweep)."""
    return str(label).split("+", 1)[0].split("/", 1)[0]


class _SumCtx:
    raster_fn = None   # None: no footprint split


def _sum_chunk(args) -> Dict[str, Any]:
    """Per-transition change counts for trajectories j0..j1-1, and the split of tile-index changes into
    inside / outside the month's action-raster footprint (union of the 15 channels)."""
    path, j0, j1 = args
    st = TrajStore(path)
    rec = st.traj[j0:j1]
    o0 = int(rec["first_obs"][0])
    o1 = int(rec["first_obs"][-1] + rec["H"][-1] + 1)
    t0 = int(rec["first_trans"][0])
    t1 = int(rec["first_trans"][-1] + rec["H"][-1])
    t = np.asarray(st.tiles[o0:o1])
    p = np.asarray(st.power_packed[o0:o1])
    # drop the cross-trajectory pairs (last row of one trajectory, first of the next)
    keep = np.ones(o1 - o0 - 1, dtype=bool)
    keep[(rec["first_obs"][1:] - 1 - o0).astype(np.int64)] = False
    idx = t & LOMASK
    chg = (idx[1:] != idx[:-1])[keep]
    d_idx = np.count_nonzero(chg, axis=(1, 2))
    d_f6 = np.count_nonzero(((t[1:] & FLAG_MASK_ALL) != (t[:-1] & FLAG_MASK_ALL))[keep], axis=(1, 2))
    d_f5 = np.count_nonzero(((t[1:] & FLAG_MASK_MODEL) != (t[:-1] & FLAG_MASK_MODEL))[keep], axis=(1, 2))
    anim = (((t[1:] | t[:-1]) & ANIMBIT) != 0)[keep]
    pw = np.unpackbits(p, axis=1)
    d_pw = np.count_nonzero((pw[1:] != pw[:-1])[keep], axis=1)
    T = t1 - t0
    assert chg.shape[0] == T
    out = {"t0": t0, "d_idx": d_idx, "d_f6": d_f6, "d_f5": d_f5, "d_pw": d_pw}
    if _SumCtx.raster_fn is not None:
        plan = np.asarray(st.plan[t0:t1])
        has = (plan[:, 5::5] != 0).any(axis=1)      # a month with no macro attempts no tool call
        fp_n = np.zeros(T, np.int64)
        c_in = np.zeros(T, np.int64)
        c_in_anim = np.zeros(T, np.int64)
        rows = np.flatnonzero(has)
        for a in range(0, rows.size, 256):
            r = rows[a:a + 256]
            fp = np.asarray(_SumCtx.raster_fn(plan[r])).any(axis=1)
            fp_n[r] = np.count_nonzero(fp, axis=(1, 2))
            c_in[r] = np.count_nonzero(chg[r] & fp, axis=(1, 2))
            c_in_anim[r] = np.count_nonzero(chg[r] & fp & anim[r], axis=(1, 2))
        empty = np.flatnonzero(~has)[:4]
        if empty.size and np.asarray(_SumCtx.raster_fn(plan[empty])).any():
            raise RuntimeError("a month with no macro has a non-empty raster; the footprint split assumes it is empty")
        out.update(fp_n=fp_n, c_in=c_in, c_out=d_idx - c_in,
                   c_out_anim=np.count_nonzero(chg & anim, axis=(1, 2)) - c_in_anim)
    return out


def _dist(x: np.ndarray, denom: float) -> Dict[str, Any]:
    s = np.asarray(x, dtype=np.float64) / denom
    q = np.quantile(s, [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) if s.size else [np.nan] * 6
    edges = [0, 1e-9, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0 + 1e-9]
    h, _ = np.histogram(s, bins=edges)
    return {"mean": float(s.mean()) if s.size else None, "q05": float(q[0]), "q25": float(q[1]), "median": float(q[2]),
            "q75": float(q[3]), "q95": float(q[4]), "q99": float(q[5]), "share_zero": float(np.mean(s == 0)) if s.size else None,
            "hist_edges": [float(e) for e in edges], "hist_counts": [int(c) for c in h]}


def _brief(x: np.ndarray, denom: float) -> Dict[str, Any]:
    s = np.asarray(x, dtype=np.float64) / denom
    if not s.size:
        return {}
    return {"mean": float(s.mean()), "median": float(np.median(s)), "q95": float(np.quantile(s, 0.95)),
            "share_zero": float(np.mean(s == 0))}


def _group_stats(sel: np.ndarray, rec_sel: np.ndarray, c: Dict[str, np.ndarray]) -> Dict[str, Any]:
    g: Dict[str, Any] = {"trajectories": int(rec_sel.sum()), "transitions": int(sel.sum())}
    if not sel.any():
        return g
    g["tiles_index_changed_share"] = _brief(c["d_idx"][sel], N_TILES)
    g["flags_model5_changed_share"] = _brief(c["d_f5"][sel], N_TILES)
    g["power_changed_share"] = _brief(c["d_pw"][sel], N_TILES)
    g["share_transitions_zero_index_change"] = float(np.mean(c["d_idx"][sel] == 0))
    g["changed_tiles_mean"] = float(c["d_idx"][sel].mean())
    if "fp_n" in c:
        fp, ci, co = c["fp_n"][sel], c["c_in"][sel], c["c_out"][sel]
        g["footprint"] = {
            "footprint_tiles_mean": float(fp.mean()),
            "share_months_with_footprint": float(np.mean(fp > 0)),
            "changed_inside_footprint_mean": float(ci.mean()),
            "changed_outside_footprint_mean": float(co.mean()),
            "changed_outside_footprint_animated_mean": float(c["c_out_anim"][sel].mean()),
            "share_of_changes_inside_footprint": float(ci.sum() / max(1, int(c["d_idx"][sel].sum()))),
        }
    return g


def summarise(store, workers: int = 8, chunk: int = 100, raster_fn: Any = None) -> Dict[str, Any]:
    """Counts and the one-month change distribution, computed over every transition of the store.

    ``raster_fn``: rows (B, 25) -> (B, 15, 120, 100) raster for the footprint split; None uses
    ``dc.grammar.raster_batch``; False skips the split."""
    import multiprocessing as mp
    from .engine import SCALAR_NAMES, SC_FUNDS, SC_POP

    st = store if isinstance(store, TrajStore) else TrajStore(store)
    rec = st.traj
    out: Dict[str, Any] = {"store": str(st.path), "name": st.config.get("name"), "complete": st.complete,
                           "counts": {"trajectories": st.n_traj, "transitions": st.n_trans, "observations": st.n_obs}}
    if st.n_traj == 0:
        return out
    split_names = np.array(SPLITS)[rec["split"]]
    out["counts"]["by_split"] = {s: {"trajectories": int((split_names == s).sum()), "transitions": int(rec["H"][split_names == s].sum())}
                                 for s in SPLITS if (split_names == s).any()}
    fam = {}
    for i, f in enumerate(st.families):
        sel = rec["family_idx"] == i
        if sel.any():
            fam[f] = {"trajectories": int(sel.sum()), "transitions": int(rec["H"][sel].sum())}
    out["counts"]["by_family"] = fam
    lab = {}
    for i, l in enumerate(st.labels):
        sel = rec["label_idx"] == i
        lab[l] = {"trajectories": int(sel.sum()), "transitions": int(rec["H"][sel].sum())}
    out["counts"]["by_label"] = lab
    out["counts"]["by_H"] = {str(int(h)): int((rec["H"] == h).sum()) for h in np.unique(rec["H"])}
    out["counts"]["by_start"] = {st.starts[int(s)]["start_id"]: int((rec["start_idx"] == s).sum()) for s in np.unique(rec["start_idx"])}
    out["counts"]["disasters_on_trajectories"] = int(rec["disasters"].sum())
    fk = np.asarray(st.plan[:, PLAN_FORCED_COL])
    out["counts"]["forced_disasters_by_kind"] = {str(int(k)): int((fk == k).sum()) for k in np.unique(fk) if k != 0}

    if raster_fn is None:
        raster_fn = _default_grammar()[0]
    _SumCtx.raster_fn = raster_fn if raster_fn is not False else None
    chunks = [(str(st.path), a, min(a + chunk, st.n_traj)) for a in range(0, st.n_traj, chunk)]
    if workers <= 1:
        parts = [_sum_chunk(c) for c in chunks]
    else:
        with mp.get_context("fork").Pool(workers) as pool:
            parts = pool.map(_sum_chunk, chunks, chunksize=1)
    parts.sort(key=lambda p: p["t0"])
    c = {k: np.concatenate([p[k] for p in parts]) for k in parts[0] if k != "t0"}
    d_idx, d_f6, d_f5, d_pw = c["d_idx"], c["d_f6"], c["d_f5"], c["d_pw"]
    assert d_idx.size == st.n_trans
    out["one_month_change"] = {
        "tiles_index_changed_share": _dist(d_idx, N_TILES),
        "tiles_flags_changed_share_all6": _dist(d_f6, N_TILES),
        "tiles_flags_changed_share_model5": _dist(d_f5, N_TILES),
        "power_changed_share": _dist(d_pw, N_TILES),
        "transitions": int(d_idx.size),
    }
    rows = st.obs_row_of(np.arange(st.n_trans))
    sc = np.asarray(st.scalars)
    d = np.abs(sc[rows + 1].astype(np.float64) - sc[rows].astype(np.float64))
    # by behaviour type (and by full label): change shares and the footprint split
    lab_t = np.repeat(rec["label_idx"].astype(np.int64), rec["H"].astype(np.int64))
    types = sorted({behaviour_type(l) for l in st.labels})
    tmap = np.array([types.index(behaviour_type(l)) for l in st.labels], dtype=np.int64)
    typ_t, typ_j = tmap[lab_t], tmap[rec["label_idx"].astype(np.int64)]
    out["one_month_change"]["by_behaviour_type"] = {ty: _group_stats(typ_t == i, typ_j == i, c) for i, ty in enumerate(types)}
    pert_t = np.array(["+perturb" in l for l in st.labels], dtype=bool)
    out["one_month_change"]["by_behaviour_type_perturbed"] = {
        f"{ty}{'+perturb' if pt else ''}": _group_stats((typ_t == i) & (pert_t[lab_t] == pt), (typ_j == i) & (pert_t[rec["label_idx"]] == pt), c)
        for i, ty in enumerate(types) for pt in (False, True) if ((typ_j == i) & (pert_t[rec["label_idx"]] == pt)).any()}
    out["one_month_change"]["all_transitions"] = _group_stats(np.ones(st.n_trans, bool), np.ones(st.n_traj, bool), c)
    out["one_month_change"]["scalar_mean_abs"] = {n: float(d[:, i].mean()) for i, n in enumerate(SCALAR_NAMES)}
    out["one_month_change"]["scalar_share_changed"] = {n: float(np.mean(d[:, i] != 0)) for i, n in enumerate(SCALAR_NAMES)}
    pop_edges = [0, 1, 1000, 2000, 5000, 10000, 30000, 80000, 150000, 300000, 600000, 10**9]
    funds_edges = [-10**12, 0, 1000, 5000, 10000, 20000, 40000, 100000, 300000, 10**6, 10**12]
    first = rec["first_obs"].astype(np.int64)
    for name, col, edges in (("population", SC_POP, pop_edges), ("funds", SC_FUNDS, funds_edges)):
        v = sc[:, col]
        h, _ = np.histogram(v, bins=edges)
        h0, _ = np.histogram(sc[first, col], bins=edges)
        out[f"{name}_histogram"] = {"edges": edges, "all_observations": [int(c) for c in h], "start_observations": [int(c) for c in h0],
                                    "quantiles_all": {q: float(np.quantile(v, float(q))) for q in ("0.05", "0.25", "0.5", "0.75", "0.95")}}
    if st.has_ledger:
        out["ledger_change"] = ledger_summary(st)
    bc = np.asarray(st.build_cost)
    rf = np.asarray(st.refused)
    out["build_cost_per_month"] = {"mean": float(bc.mean()), "q95": float(np.quantile(bc, 0.95)), "share_zero": float(np.mean(bc == 0))}
    out["refused_calls_per_month"] = {"mean": float(rf.mean()), "q95": float(np.quantile(rf, 0.95)), "share_zero": float(np.mean(rf == 0))}
    return out


def ledger_summary(store, block: int = 2000) -> Dict[str, Any]:
    """Over every transition: per ledger entry, the share of transitions in which it changes and its mean
    absolute one-month change; for the terrain and com_rate maps, the share of cells changing (mean over
    transitions), the share of transitions with any cell changing and the mean absolute cell change."""
    st = store if isinstance(store, TrajStore) else TrajStore(store)
    T = st.n_trans
    led_chg = np.zeros(NUM_LEDGER, np.int64)
    led_abs = np.zeros(NUM_LEDGER, np.float64)
    maps = {k: {"cells_changed": 0, "transitions_any": 0, "abs_sum": 0.0} for k in ("terrain", "com_rate")}
    for j0 in range(0, st.n_traj, block):
        rec = st.traj[j0:j0 + block]
        o0 = int(rec["first_obs"][0])
        o1 = int(rec["first_obs"][-1] + rec["H"][-1] + 1)
        keep = np.ones(o1 - o0 - 1, dtype=bool)
        keep[(rec["first_obs"][1:] - 1 - o0).astype(np.int64)] = False
        L = np.asarray(st.ledger[o0:o1])
        dl = (L[1:] - L[:-1])[keep]
        led_chg += np.count_nonzero(dl, axis=0)
        led_abs += np.abs(dl.astype(np.float64)).sum(axis=0)
        for k in ("terrain", "com_rate"):
            a = np.asarray(getattr(st, k)[o0:o1]).astype(np.int32)
            d = (a[1:] - a[:-1])[keep].reshape(int(keep.sum()), -1)
            nz = np.count_nonzero(d, axis=1)
            maps[k]["cells_changed"] += int(nz.sum())
            maps[k]["transitions_any"] += int(np.count_nonzero(nz))
            maps[k]["abs_sum"] += float(np.abs(d).sum())
    out: Dict[str, Any] = {"transitions": int(T), "ledger": {}}
    for i, n in enumerate(LEDGER_NAMES):
        out["ledger"][n] = {"share_transitions_changed": float(led_chg[i] / max(T, 1)),
                            "mean_abs_change": float(led_abs[i] / max(T, 1))}
    for k, shape in (("terrain", TERRAIN_SHAPE), ("com_rate", COM_RATE_SHAPE)):
        cells = int(np.prod(shape))
        m = maps[k]
        out[k] = {"cells": cells, "share_cells_changed_mean": m["cells_changed"] / max(T * cells, 1),
                  "share_transitions_any_cell_changed": m["transitions_any"] / max(T, 1),
                  "mean_abs_cell_change": m["abs_sum"] / max(T * cells, 1),
                  "cells_changed_per_transition_mean": m["cells_changed"] / max(T, 1)}
    return out


# --------------------------------------------------------------------------------------------
# backfill of the extended observation into dc-store-1 stores
# --------------------------------------------------------------------------------------------
BACKFILL_JOURNAL = "backfill_ledger.jsonl"


class _BfCtx:
    path = None
    compile_plan = None
    store = None
    eng = None
    fds = None


def _bf_init() -> None:
    _die_with_parent()
    _BfCtx.store = TrajStore(_BfCtx.path)
    _BfCtx.eng = Engine()
    _BfCtx.fds = {k: os.open(str(_BfCtx.path / (ALL_FILES[k][0] + ".part")), os.O_WRONLY) for k in LEDGER_FILES}
    if _BfCtx.compile_plan is None:
        _BfCtx.compile_plan = _default_compile_plan()


def _bf_chunk(args) -> Dict[str, Any]:
    """Replay trajectories j0..j1-1, compare every stored array and the final hash, write the new rows."""
    from .oracle import replay

    c, j0, j1 = args
    st, eng = _BfCtx.store, _BfCtx.eng
    bad: Dict[str, int] = {}
    bad_ids: List[int] = []
    months = 0
    for j in range(j0, j1):
        d = st.trajectory(j)
        H = d["H"]
        months += H
        b: Dict[str, int] = {}
        cty = Path(d["cty_path"])
        if not cty.exists() or sha256_file(cty) != d["cty_sha256"]:
            b["start_file"] = 1
        else:
            actions, forced = _BfCtx.compile_plan(d["plan"])
            if len(actions) != H:
                b["plan_length"] = 1
            else:
                rep = replay(eng, cty, actions, d["seed"], disasters=d["disasters"], forced=forced, record="full", want_hash=True)
                got = obs_arrays(rep.states)
                for k in ("tiles", "half", "eighth", "scalars"):
                    n = int(np.count_nonzero(np.any((got[k] != d[k]).reshape(H + 1, -1), axis=1)))
                    if n:
                        b[k] = n
                n = int(np.count_nonzero(np.any((unpack_power(got["power"]) != d["power"]).reshape(H + 1, -1), axis=1)))
                if n:
                    b["power"] = n
                if not np.array_equal(np.asarray(rep.build_cost, np.int64), d["build_cost"].astype(np.int64)):
                    b["build_cost"] = 1
                if not np.array_equal(refused_counts(rep.tool_ok), d["refused"].astype(np.int64)):
                    b["refused"] = 1
                if int(rep.hashes[-1]) != d["final_hash"]:
                    b["final_hash"] = 1
                if rep.ledger is None or not np.array_equal(rep.ledger, got["ledger"]):
                    b["ledger_vs_states"] = 1
                if int(got["ledger"][0, LG["disasters"]]) != int(d["disasters"]):
                    b["ledger_row0_disasters"] = 1
                o = d["first_obs"]
                for k in LEDGER_FILES:
                    a = np.ascontiguousarray(got[k], dtype=np.dtype(ALL_FILES[k][1]))
                    mv = memoryview(a).cast("B")
                    off = o * ROW_BYTES[k]
                    w = 0
                    while w < len(mv):
                        w += os.pwrite(_BfCtx.fds[k], mv[w:], off + w)
        if b:
            bad_ids.append(j)
            for k in b:
                bad[k] = bad.get(k, 0) + 1
    return {"chunk": c, "j0": j0, "j1": j1, "checked": j1 - j0, "city_months": months,
            "observations": months + (j1 - j0), "bad": bad, "bad_ids": bad_ids}


def _read_journal(path: Path) -> Dict[int, Dict[str, Any]]:
    done: Dict[int, Dict[str, Any]] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue          # a partial last line from a kill
            done[int(r["chunk"])] = r
    return done


def backfill_ledger(path, workers: int = 8, *, compile_plan: Optional[Callable] = None, chunk: int = 50,
                    command: Optional[str] = None, provenance: Optional[Dict[str, Any]] = None,
                    log: Callable[[str], None] = print, crash_after_chunks: Optional[int] = None,
                    progress_seconds: float = 60.0) -> Dict[str, Any]:
    """Add ledger / terrain / com_rate to a complete dc-store-1 store by replaying every trajectory, and
    verify in the same pass every existing array and the final full-state hash against the replay.

    New rows go to ``*.part`` files at fixed offsets; each finished chunk of trajectories is fsynced and
    then journalled in ``backfill_ledger.jsonl``, so a killed backfill resumes at the unfinished chunks.
    Only with every trajectory checked and no mismatch are the files renamed into place and the manifest
    updated (atomically) with their sha256; the existing array files are never written.
    ``crash_after_chunks`` (tests only) kills the process after that many journalled chunks."""
    import multiprocessing as mp

    path = Path(path)
    st = TrajStore(path)
    if not st.complete:
        raise RuntimeError(f"{path} is not a complete store")
    man = st.manifest
    if all(k in man["arrays"] for k in LEDGER_FILES):
        return {"store": str(path), "already_backfilled": True, "result": man.get("backfills", [])}
    final = {k: path / ALL_FILES[k][0] for k in LEDGER_FILES}
    part = {k: path / (ALL_FILES[k][0] + ".part") for k in LEDGER_FILES}
    journal = path / BACKFILL_JOURNAL
    chunks = [(c, a, min(a + chunk, st.n_traj)) for c, a in enumerate(range(0, st.n_traj, chunk))]
    t0 = time.time()
    new_months = 0
    if not all(f.exists() for f in final.values()):
        for k in LEDGER_FILES:
            fd = os.open(str(part[k]), os.O_RDWR | os.O_CREAT, 0o644)
            os.ftruncate(fd, st.n_obs * ROW_BYTES[k])
            os.close(fd)
        done = _read_journal(journal)
        for c, a, b in chunks:
            if c in done and (done[c]["j0"], done[c]["j1"]) != (a, b):
                raise RuntimeError(f"{journal}: chunk {c} covers {done[c]['j0']}..{done[c]['j1']}, expected {a}..{b}")
        prior_bad = [c for c, r in done.items() if r["bad"]]
        if prior_bad:
            raise RuntimeError(f"{journal} already records mismatches in chunks {prior_bad[:10]}; not continuing")
        pending = [x for x in chunks if x[0] not in done]
        log(f"[backfill {path.name}] {st.n_traj} trajectories in {len(chunks)} chunks; {len(pending)} to do on {workers} worker(s)")
        fds = {k: os.open(str(part[k]), os.O_RDWR) for k in LEDGER_FILES}
        jf = open(journal, "a")
        _BfCtx.path, _BfCtx.compile_plan = path, compile_plan
        pool = None
        stopped = False
        try:
            if workers <= 1:
                _bf_init()
                it = (_bf_chunk(x) for x in pending)
            else:
                pool = mp.get_context("fork").Pool(workers, initializer=_bf_init)
                it = pool.imap_unordered(_bf_chunk, pending, chunksize=1)
            n_done = 0
            last = time.time()
            for r in it:
                for fd in fds.values():
                    os.fsync(fd)
                jf.write(json.dumps(r) + "\n")
                jf.flush()
                os.fsync(jf.fileno())
                done[r["chunk"]] = r
                n_done += 1
                new_months += r["city_months"]
                if crash_after_chunks is not None and n_done >= crash_after_chunks:
                    os._exit(17)
                if r["bad"]:
                    log(f"[backfill {path.name}] MISMATCH in chunk {r['chunk']}: {r['bad']} trajectories {r['bad_ids'][:10]}; stopping")
                    stopped = True
                    break
                if time.time() - last >= progress_seconds:
                    el = time.time() - t0
                    log(f"[backfill {path.name}] {len(done)}/{len(chunks)} chunks, {new_months / el:,.0f} city-months/s, "
                        f"elapsed {el / 60:.1f} min")
                    last = time.time()
        finally:
            if pool is not None:
                pool.terminate()
                pool.join()
            for fd in fds.values():
                os.close(fd)
            jf.close()
            if workers <= 1 and _BfCtx.fds:
                for fd in _BfCtx.fds.values():
                    os.close(fd)
                _BfCtx.fds = None
        res = _aggregate_backfill(done, chunks)
        res.update(store=str(path), seconds_this_call=round(time.time() - t0, 1), city_months_this_call=new_months)
        if stopped or res["mismatched"] or res["checked"] != st.n_traj:
            res["published"] = False
            log(f"[backfill {path.name}] NOT published: {json.dumps(res)}")
            return res
        for k in LEDGER_FILES:
            os.replace(part[k], final[k])
        dfd = os.open(str(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    else:
        res = _aggregate_backfill(_read_journal(journal), chunks)
        res.update(store=str(path), seconds_this_call=round(time.time() - t0, 1), city_months_this_call=0)
        if res["mismatched"] or res["checked"] != st.n_traj:
            raise RuntimeError(f"{path}: new arrays are in place but the journal does not show a clean pass")
    # manifest: add the three arrays (sha256), keep everything else
    with ThreadPoolExecutor(3) as ex:
        shas = dict(zip(LEDGER_FILES, ex.map(lambda k: sha256_file(final[k]), LEDGER_FILES)))
    man = _read_json(path / "manifest.json")
    added = 0
    for k in LEDGER_FILES:
        f, dt, shape = ALL_FILES[k]
        size = final[k].stat().st_size
        if size != st.n_obs * ROW_BYTES[k]:
            raise RuntimeError(f"{f}: {size} bytes, expected {st.n_obs * ROW_BYTES[k]}")
        man["arrays"][k] = {"file": f, "dtype": np.dtype(dt).str, "shape": [st.n_obs, *shape], "bytes": size, "sha256": shas[k]}
        added += size
    man.setdefault("store_format_at_generation", man.get("store_format"))
    man["store_format"] = STORE_FORMAT
    man["bytes_total"] = int(man.get("bytes_total", 0)) + added
    rec = {"what": "ledger, terrain, com_rate (dc.engine.LEDGER_NAMES, TERRAIN_SHAPE, COM_RATE_SHAPE)",
           "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "command": command,
           "bytes_added": added, "journal": BACKFILL_JOURNAL, "journal_sha256": sha256_file(journal),
           "verification": {k: res[k] for k in ("checked", "mismatched", "by_field", "observations_compared", "city_months")}}
    if provenance:
        rec["provenance"] = provenance
    man.setdefault("backfills", []).append(rec)
    _atomic_write_json(path / "manifest.json", man)
    res.update(published=True, bytes_added=added, sha256=shas, manifest_sha256=sha256_file(path / "manifest.json"))
    log(f"[backfill {path.name}] published: {json.dumps({k: v for k, v in res.items() if k != 'sha256'})}")
    return res


def _aggregate_backfill(done: Dict[int, Dict[str, Any]], chunks) -> Dict[str, Any]:
    by: Dict[str, int] = {}
    ids: List[int] = []
    for r in done.values():
        for k, v in r["bad"].items():
            by[k] = by.get(k, 0) + v
        ids += r["bad_ids"]
    return {"chunks_done": len(done), "chunks": len(chunks), "checked": int(sum(r["checked"] for r in done.values())),
            "mismatched": len(ids), "by_field": by, "mismatched_ids": sorted(ids)[:50],
            "observations_compared": int(sum(r["observations"] for r in done.values())),
            "city_months": int(sum(r["city_months"] for r in done.values()))}


# --------------------------------------------------------------------------------------------
# batch loaders
# --------------------------------------------------------------------------------------------
def expand_state_np(tiles: np.ndarray, half: np.ndarray, power_packed: np.ndarray, eighth: np.ndarray,
                    scalars: np.ndarray, ledger: Optional[np.ndarray] = None, terrain: Optional[np.ndarray] = None,
                    com_rate: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
    """Reference (numpy) expansion of stored rows into the loader state format."""
    t = np.asarray(tiles).astype(np.int64)
    flags = np.stack([((t >> s) & 1) for s in FLAG_SHIFTS], axis=-3).astype(np.float32)
    out = {
        "tile_index": t & LOMASK,
        "flags": flags,
        "power": unpack_power(power_packed).astype(np.float32),
        "half": np.asarray(half).astype(np.float32),
        "eighth": np.asarray(eighth).astype(np.float32),
        "scalars": np.asarray(scalars).astype(np.float64).astype(np.float32),
    }
    if ledger is not None:
        out["ledger"] = np.asarray(ledger).astype(np.float64).astype(np.float32)
        out["terrain"] = np.asarray(terrain).astype(np.float32)
        out["com_rate"] = np.asarray(com_rate).astype(np.float32)
    return out


def _torch_unpack(packed, n_bits: int, shape: Tuple[int, ...]):
    import torch

    p = packed.to(torch.int32)
    shifts = torch.arange(7, -1, -1, device=p.device, dtype=torch.int32)
    bits = (p.unsqueeze(-1) >> shifts) & 1
    return bits.reshape(*p.shape[:-1], -1)[..., :n_bits].reshape(*p.shape[:-1], *shape)


def expand_state_torch(tiles_i16, half_u8, power_packed, eighth_i16, scalars_i64, ledger_i64=None,
                       terrain_u8=None, com_rate_i16=None) -> Dict[str, Any]:
    """Expand raw rows (on any device) into the loader state format. Leading dims are kept."""
    import torch

    w = tiles_i16.to(torch.int32) & 0xFFFF
    shifts = torch.tensor(FLAG_SHIFTS, device=w.device, dtype=torch.int32).view(5, 1, 1)
    out = {
        "tile_index": (w & LOMASK).to(torch.int64),
        "flags": ((w.unsqueeze(-3) >> shifts) & 1).to(torch.float32),
        "power": _torch_unpack(power_packed, N_TILES, (WORLD_W, WORLD_H)).to(torch.float32),
        "half": half_u8.to(torch.float32),
        "eighth": eighth_i16.to(torch.float32),
        "scalars": scalars_i64.to(torch.float64).to(torch.float32),
    }
    if ledger_i64 is not None:
        out["ledger"] = ledger_i64.to(torch.float64).to(torch.float32)
        out["terrain"] = terrain_u8.to(torch.float32)
        out["com_rate"] = com_rate_i16.to(torch.float32)
    return out


def _default_grammar() -> Tuple[Callable, Callable, Optional[Callable]]:
    from . import grammar  # B1
    return grammar.raster_batch, grammar.action_scalars, getattr(grammar, "action_scalars_batch", None)


class _BatchSource:
    """Map-style dataset whose items are whole batches: ``source[ids]`` gathers raw rows (numpy)."""

    def __init__(self, path, k: int, raster_fn: Optional[Callable], scalars_fn: Optional[Callable], ledger: bool = True):
        self.path, self.k, self.ledger = str(path), int(k), bool(ledger)
        self.raster_fn, self.scalars_fn = raster_fn, scalars_fn
        self.scalars_batch_fn: Optional[Callable] = None
        self._st: Optional[TrajStore] = None

    def __len__(self) -> int:
        return 1 << 62

    def __getstate__(self):
        d = dict(self.__dict__)
        d["_st"] = None
        return d

    def __getitem__(self, ids):
        if self._st is None:
            self._st = TrajStore(self.path)
        if self.raster_fn is None or self.scalars_fn is None:
            rf, sf, sbf = _default_grammar()
            if self.scalars_fn is None:
                self.scalars_fn, self.scalars_batch_fn = sf, sbf
            self.raster_fn = self.raster_fn or rf
        st, k = self._st, self.k
        ids = np.asarray(ids, dtype=np.int64)
        B = ids.shape[0]
        r = st.obs_row_of(ids)
        rows = (r[:, None] + np.arange(k + 1)[None, :]).reshape(-1)
        tr = (ids[:, None] + np.arange(k)[None, :]).reshape(-1)
        m = st._maps()
        plan = np.asarray(m["plan"][tr])
        rast = np.asarray(self.raster_fn(plan))
        if rast.shape != (B * k, RASTER_CHANNELS, WORLD_W, WORLD_H):
            raise RuntimeError(f"raster_batch returned {rast.shape}")
        flat = rast.reshape(B * k, -1)
        bits = flat != 0
        if not np.array_equal(flat, bits):
            raise RuntimeError("action raster is not 0/1; bit packing would lose values")
        if self.scalars_batch_fn is not None:
            asc = np.asarray(self.scalars_batch_fn(plan), dtype=np.float32)
        else:
            asc = np.stack([np.asarray(self.scalars_fn(p), dtype=np.float32) for p in plan])
        lead_o = (B, k + 1) if k > 1 else (B, 2)
        lead_t = (B, k) if k > 1 else (B,)
        extra = {}
        if self.ledger:
            extra = {"ledger": np.asarray(m["ledger"][rows]).reshape(*lead_o, NUM_LEDGER),
                     "terrain": np.asarray(m["terrain"][rows]).reshape(*lead_o, *TERRAIN_SHAPE),
                     "com_rate": np.asarray(m["com_rate"][rows]).reshape(*lead_o, *COM_RATE_SHAPE)}
        return {
            **extra,
            "ids": ids,
            "tiles": np.asarray(m["tiles"][rows]).view(np.int16).reshape(*lead_o, WORLD_W, WORLD_H),
            "half": np.asarray(m["half"][rows]).reshape(*lead_o, 5, WORLD_W_2, WORLD_H_2),
            "power": np.asarray(m["power"][rows]).reshape(*lead_o, POWER_BYTES),
            "eighth": np.asarray(m["eighth"][rows]).reshape(*lead_o, 3, WORLD_W_8, WORLD_H_8),
            "scalars": np.asarray(m["scalars"][rows]).reshape(*lead_o, NUM_SCALARS),
            "raster": np.packbits(bits, axis=1).reshape(*lead_t, -1),
            "act_scalars": asc.reshape(*lead_t, ACTION_SCALARS),
        }


class _BatchSampler:
    """Infinite stream of index batches drawn uniformly with replacement; depends only on the seed."""

    def __init__(self, index: np.ndarray, batch_size: int, seed: int):
        self.index, self.batch_size, self.seed = np.asarray(index, dtype=np.int64), int(batch_size), int(seed)

    def __iter__(self):
        rng = np.random.default_rng(self.seed)
        n = len(self.index)
        while True:
            yield self.index[rng.integers(0, n, size=self.batch_size)]


class _Batches:
    def __init__(self, store, index, batch_size: int, seed: int, device, k: int, num_workers: int,
                 prefetch: int, raster_fn, scalars_fn, pin_memory: Optional[bool], ledger: bool = True):
        import torch
        from torch.utils.data import DataLoader

        st = store if isinstance(store, TrajStore) else TrajStore(store)
        if ledger and not st.has_ledger:
            raise ValueError(f"{st.path} has no ledger / terrain / com_rate arrays (run `gen_data.py backfill`, "
                             "or pass ledger=False for the old state format)")
        self.store, self.k = st, int(k)
        self.index = np.asarray(index, dtype=np.int64)
        if self.k > 1:
            self.index = st.multistep_starts(self.index, self.k)
        if self.index.size == 0:
            raise ValueError("empty index")
        if self.index.min() < 0 or self.index.max() >= st.n_trans:
            raise IndexError("index holds transition ids outside the store")
        self.device = torch.device(device)
        pin = (self.device.type == "cuda") if pin_memory is None else bool(pin_memory)
        src = _BatchSource(st.path, self.k, raster_fn, scalars_fn, ledger)
        kw = dict(batch_size=None, sampler=_BatchSampler(self.index, batch_size, seed), num_workers=int(num_workers),
                  pin_memory=pin)
        if num_workers > 0:
            kw.update(prefetch_factor=int(prefetch), persistent_workers=True, multiprocessing_context="fork")
        self.loader = DataLoader(src, **kw)
        self._it = iter(self.loader)
        self.last_ids: Optional[np.ndarray] = None
        self.batches = 0
        self.samples = 0

    def __iter__(self):
        return self

    def _fetch(self):
        b = next(self._it)
        dev = self.device
        nb = dev.type == "cuda"
        self.last_ids = b.pop("ids").numpy()
        return {k: v.to(dev, non_blocking=nb) for k, v in b.items()}

    @staticmethod
    def _state(b):
        return expand_state_torch(b["tiles"], b["half"], b["power"], b["eighth"], b["scalars"],
                                  b.get("ledger"), b.get("terrain"), b.get("com_rate"))

    def _raster(self, packed):
        import torch

        return _torch_unpack(packed, RASTER_CHANNELS * N_TILES, (RASTER_CHANNELS, WORLD_W, WORLD_H)).to(torch.float32)

    def close(self) -> None:
        it = getattr(self, "_it", None)
        if it is not None and hasattr(it, "_shutdown_workers"):
            it._shutdown_workers()
        self._it = None

    def __del__(self):  # pragma: no cover
        try:
            self.close()
        except Exception:
            pass


class OneStepBatches(_Batches):
    """``(state_t, action raster (B,15,120,100), action scalars (B,11), state_t+1)`` on ``device``,
    transitions drawn uniformly with replacement from ``index`` (transition ids). States are dicts in
    the loader state format (with ``ledger``, ``terrain``, ``com_rate`` unless ``ledger=False``).
    ``last_ids`` holds the transition ids of the last batch."""

    def __init__(self, store, index, batch_size: int, seed: int, device, *, num_workers: int = 6, prefetch: int = 4,
                 raster_fn: Optional[Callable] = None, scalars_fn: Optional[Callable] = None,
                 pin_memory: Optional[bool] = None, ledger: bool = True):
        super().__init__(store, index, batch_size, seed, device, 1, num_workers, prefetch, raster_fn, scalars_fn, pin_memory,
                         ledger)

    def __next__(self):
        b = self._fetch()
        s = self._state(b)
        s0 = {k: v[:, 0] for k, v in s.items()}
        s1 = {k: v[:, 1] for k, v in s.items()}
        self.batches += 1
        self.samples += int(self.last_ids.shape[0])
        return s0, self._raster(b["raster"]), b["act_scalars"], s1


class MultiStepBatches(_Batches):
    """k consecutive transitions of one trajectory per sample.

    Default: a list of k tuples ``(state_t, action raster_t, action scalars_t, state_t+1)`` for
    t = 0..k-1, each in exactly ``OneStepBatches``' format (views into one stacked batch, no copies).
    With ``stacked=True``: ``(states, rasters, action scalars)`` with states a dict of (B, k+1, ...)
    tensors (index 0 is the start), rasters (B, k, 15, 120, 100), action scalars (B, k, 11).
    Starts are drawn uniformly with replacement from the transitions of ``index`` that begin k
    consecutive transitions of one trajectory, all in ``index``; ``last_ids`` holds them."""

    def __init__(self, store, index, batch_size: int, seed: int, device, k: int, *, num_workers: int = 6,
                 prefetch: int = 4, raster_fn: Optional[Callable] = None, scalars_fn: Optional[Callable] = None,
                 pin_memory: Optional[bool] = None, stacked: bool = False, ledger: bool = True):
        if k < 2:
            raise ValueError("MultiStepBatches needs k >= 2; use OneStepBatches for k = 1")
        self.stacked = bool(stacked)
        super().__init__(store, index, batch_size, seed, device, k, num_workers, prefetch, raster_fn, scalars_fn, pin_memory,
                         ledger)

    def __next__(self):
        b = self._fetch()
        s = self._state(b)
        r = self._raster(b["raster"])
        a = b["act_scalars"]
        self.batches += 1
        self.samples += int(self.last_ids.shape[0]) * self.k
        if self.stacked:
            return s, r, a
        return [({n: v[:, t] for n, v in s.items()}, r[:, t], a[:, t], {n: v[:, t + 1] for n, v in s.items()})
                for t in range(self.k)]


def bench_loader(store, index, batch_size: int, device, *, seconds: float = 30.0, num_workers: int = 6, k: int = 1,
                 warmup_batches: int = 5, raster_fn: Optional[Callable] = None, scalars_fn: Optional[Callable] = None,
                 seed: int = 0) -> Dict[str, Any]:
    """Sustained loader throughput: transitions a second delivered on ``device`` (synchronised per batch)."""
    import torch

    dev = torch.device(device)
    if k == 1:
        it = OneStepBatches(store, index, batch_size, seed, dev, num_workers=num_workers, raster_fn=raster_fn, scalars_fn=scalars_fn)
    else:
        it = MultiStepBatches(store, index, batch_size, seed, dev, k, num_workers=num_workers, raster_fn=raster_fn, scalars_fn=scalars_fn)
    sync = (lambda: torch.cuda.synchronize(dev)) if dev.type == "cuda" else (lambda: None)
    try:
        for _ in range(warmup_batches):
            next(it)
        sync()
        t0 = time.time()
        n = b = 0
        while time.time() - t0 < seconds:
            out = next(it)
            sync()
            n += batch_size * k
            b += 1
        el = time.time() - t0
    finally:
        it.close()
    return {"transitions_per_s": round(n / el, 1), "transitions": n, "batches": b, "seconds": round(el, 2),
            "batch_size": batch_size, "k": k, "loader_workers": num_workers, "device": str(dev),
            "index_size": int(len(index))}
