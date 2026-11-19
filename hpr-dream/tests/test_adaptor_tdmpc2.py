"""CPU tests with the real simulator, without model checkpoints."""
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from hpr_dream.adaptors import tdmpc2 as td

ROOT = Path(__file__).resolve().parents[2]
PYTHON = td.EXT_ROOT / "venv/bin/python"


def external(code):
    if not PYTHON.exists():
        pytest.skip("wm2-ext/venv is absent; no external packages are installed by tests")
    env = dict(os.environ, PYTHONPATH=str(ROOT / "hpr-dream"), MUJOCO_GL="disable",
               CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    return subprocess.run([str(PYTHON), "-c", code], env=env, check=True,
                          capture_output=True, text=True, timeout=60).stdout


def test_optional_import_is_lazy():
    code = "import sys; import hpr_dream; import hpr_dream.adaptors.tdmpc2; assert 'torch' not in sys.modules; assert 'dm_control' not in sys.modules"
    env = dict(os.environ, PYTHONPATH=str(ROOT / "hpr-dream"))
    subprocess.run([sys.executable, "-c", code], env=env, check=True, timeout=30)


def test_all_action_levels_round_trip():
    p = np.tile(np.arange(21, dtype=np.int16), (50, 1)).reshape(1, -1)
    a = td.decode_plans(p, 21)
    assert a.dtype == np.float32
    assert np.array_equal(td.encode_actions(a).reshape(p.shape), p)
    assert a.min() == -1 and a.max() == 1
    assert td.plan_space(21).contains(p).all()


def test_behaviour_reproducible_and_smoothed():
    p = td.behaviour_plans(np.random.default_rng(42), 1000, 3)
    q = td.behaviour_plans(np.random.default_rng(42), 1000, 3)
    assert np.array_equal(p, q)
    assert p.shape == (1000, 150)
    assert td.plan_space(3).contains(p).all()
    a = td.decode_plans(p, 3)
    # A consequence of the stated 0.8/0.2 recurrence and quantisation:
    # one step moves by no more than 0.5, including two rounding errors.
    assert np.max(np.abs(np.diff(a, axis=1))) <= 0.500001


@pytest.mark.parametrize("bad", [np.zeros((1, 150), float), np.full((1, 150), 21), np.zeros((1, 149), int)])
def test_invalid_plans_rejected(bad):
    with pytest.raises(ValueError):
        td.decode_plans(bad, 3)


@pytest.mark.parametrize("task", td.TASKS)
def test_original_continuation_and_exact_restoration(task, tmp_path):
    # The physics trace after restoration must equal the original continuation bit for bit. The
    # stored observation is the one the original continuation produced (what the grader encodes).
    # The observation recomputed after a restore is not asserted: hopper's touch sensors are
    # recomputed by forward() and differ at some starts (3 of the 20 audit starts) although the
    # physics trace is identical.
    output = external(f'''
from hpr_dream.adaptors import tdmpc2 as t
import numpy as np
s=t.capture_start({task!r}, 901)
s.save({str(tmp_path / 'state.npz')!r})
s2=t.StartState.load({str(tmp_path / 'state.npz')!r})
assert s.sha256==s2.sha256
env=t.make_env(s.task,s.seed)
dim=s.prefix.shape[1]
for a in t.decode_plans(s.prefix.reshape(1,-1),dim,len(s.prefix))[0]:
    for _ in range(t.ACTION_REPEAT): env.step(a.astype(np.float64))
assert t.observation(env).tobytes()==s.obs.tobytes()
p=t.behaviour_plans(np.random.default_rng(7),1,dim)[0]
original=t.replay(env,s,p,trace=True,restore_start=False)
reused=t.replay(env,s2,p,trace=True)
env2=t.make_env(s.task,12345)
fresh=t.replay(env2,s2,p,trace=True)
assert all(a.tobytes()==b.tobytes()==c.tobytes() for a,b,c in zip(original,reused,fresh))
assert len(original[0])==100
env.close(); env2.close()
print('exact')
''')
    assert output.strip() == "exact"


def test_oracle_equals_independent_simulator_loop():
    # A few-line dm_control loop with no adaptor code: reach the start from its seed and prefix,
    # step each action twice, sum the task's rewards. The adaptor's oracle restores the saved state
    # instead; both must agree bit for bit, and the control applied must be the decoded action.
    output = external('''
from hpr_dream.adaptors import tdmpc2 as t
import numpy as np
from dm_control import suite
s=t.capture_start('cheetah-run',1003)
dim=s.prefix.shape[1]
plans=np.stack([np.full(50*dim,10),np.full(50*dim,20),np.tile(np.repeat([0,20],dim),25),
                t.behaviour_plans(np.random.default_rng(3),1,dim)[0]])
dec=lambda x: np.asarray(x,np.float32).reshape(-1,dim)/np.float32(10)-np.float32(1)
mine=[]
for p in plans:
    env=suite.load('cheetah','run',task_kwargs={'random':s.seed},visualize_reward=False)
    env.reset()
    for a in dec(s.prefix):
        for _ in range(2): env.step(a.astype(np.float64))
    r=[]
    for a in dec(p):
        for _ in range(2):
            r.append(env.step(a.astype(np.float64)).reward)
            assert env.physics.data.ctrl.tobytes()==a.astype(np.float64).tobytes()
    mine.append(np.sum(np.asarray(r,np.float64)))
got=t.Oracle(s)(plans)
assert np.asarray(mine).tobytes()==got.tobytes(), (mine, got)
assert np.array_equal(t.decode_plans(plans,dim).reshape(len(plans),-1), dec(plans).reshape(len(plans),-1))
print('equal')
''')
    assert output.strip() == "equal"


def test_pad_rows_fixed_shape():
    x = np.arange(6).reshape(3, 2)
    y = td.pad_rows(x, 5)
    assert y.shape == (5, 2) and np.array_equal(y[:3], x) and (y[3:] == x[-1]).all()
    assert td.pad_rows(x, 3) is x
    with pytest.raises(ValueError):
        td.pad_rows(x, 2)


def test_oracle_counts_and_duplicate_replay():
    output = external('''
from hpr_dream.adaptors import tdmpc2 as t
import numpy as np
s=t.capture_start('cheetah-run',77)
o=t.Oracle(s)
p=t.behaviour_plans(np.random.default_rng(9),2,s.prefix.shape[1])
r=o(np.stack([p[0],p[1],p[0]]))
assert r[0].tobytes()==r[2].tobytes()
assert o.n_evals==3
assert len(o(p[:0]))==0 and o.n_evals==3
print('count=3')
''')
    assert output.strip() == "count=3"


def test_grader_refuses_unmasked_gpu_before_importing_torch(monkeypatch):
    monkeypatch.delenv("CUDA_VISIBLE_DEVICES", raising=False)
    with pytest.raises(RuntimeError, match="CUDA_VISIBLE_DEVICES=1"):
        td.Grader("cheetah-run", "unused.pt", 17, 6)
