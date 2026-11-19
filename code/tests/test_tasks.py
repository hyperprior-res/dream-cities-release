import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dc.engine import (SC_COAL, SC_FUNDS, SC_NUCLEAR, SC_POP, SC_POWERED, SC_TAX, SC_TAX_FUND,  # noqa: E402
                       SC_UNPOWERED)
from dc.tasks import (ORACLE_N, TASKS, calibrate_theta, feasible, margin, oracle_seeds, oracle_share,  # noqa: E402
                      oracle_value, oracle_verdict, statistic, verdict)


def traj(pop, funds, powered=10, unpowered=0, plants0=1, plantsH=1):
    H = len(pop) - 1
    s = np.zeros((H + 1, 20))
    s[:, SC_POP] = pop
    s[:, SC_FUNDS] = funds
    s[:, SC_POWERED] = powered
    s[:, SC_UNPOWERED] = unpowered
    s[0, SC_COAL] = plants0
    s[-1, SC_COAL] = plantsH
    return s


def test_hand_cases():
    up = traj([1000, 1500, 3000], [5000, 4000, 4500])
    assert verdict("grow", up, 3000) and not verdict("grow", up, 3001)
    neg = traj([1000, 1500, 3000], [5000, -1, 4500])
    assert not verdict("grow", neg, 0)                      # funds went negative in the dream
    assert verdict("solvent", up, 2000)                     # never below half of 5000
    low = traj([1000, 1500, 3000], [5000, 2499, 4500])
    assert not verdict("solvent", low, 0)
    rev = traj([1000, 1500, 3000], [5000, 4000, 4500])
    rev[:, SC_TAX], rev[-1, SC_TAX_FUND] = 7, 900
    assert verdict("treasury", rev, 900) and not verdict("treasury", rev, 901)       # revenue form
    hike = rev.copy(); hike[1, SC_TAX] = 8
    assert not verdict("treasury", hike, 0)                 # the tax rate rose above the start rate
    cut = rev.copy(); cut[1:, SC_TAX] = 3
    assert verdict("treasury", cut, 900)                    # lowering it is allowed
    broke = rev.copy(); broke[1, SC_FUNDS] = -1
    assert not verdict("treasury", broke, 0)
    assert abs(statistic("recover", up) - 3.0) < 1e-12 and verdict("recover", up, 3.0)
    assert verdict("power", traj([1, 1], [1, 1], powered=19, unpowered=1), 20)       # 95 per cent exactly
    assert not verdict("power", traj([1, 1], [1, 1], powered=18, unpowered=2), 0)
    assert not verdict("power", traj([1, 1], [1, 1], plants0=1, plantsH=3), 0)       # too many plants
    assert not verdict("power", traj([1, 1], [1, 1], powered=0, unpowered=0), 0)     # no zones is not success


def test_batched_shapes_and_calibration():
    rng = np.random.default_rng(0)
    s = np.zeros((500, 25, 20))
    s[:, :, SC_POP] = rng.integers(0, 10000, size=(500, 1)) + rng.integers(0, 50, size=(500, 25))
    s[:, :, SC_FUNDS] = rng.integers(-200, 20000, size=(500, 25))
    s[:, :, SC_POWERED] = rng.integers(0, 60, size=(500, 1))
    s[:, :, SC_UNPOWERED] = rng.integers(0, 4, size=(500, 1))
    s[:, :, SC_TAX] = 7
    s[:, -1, SC_TAX_FUND] = rng.integers(0, 3000, size=500)
    for t in TASKS:
        assert feasible(t, s).shape == (500,) and statistic(t, s).shape == (500,)
        theta, rate, feas = calibrate_theta(t, s)
        assert np.isclose(rate, np.mean(verdict(t, s, theta)))
        if feas >= 0.35:
            assert 0.2 <= rate <= 0.5, (t, rate, feas)


def test_margin_sign_is_the_verdict():
    rng = np.random.default_rng(1)
    s = np.zeros((2000, 25, 20))
    s[:, :, SC_POP] = rng.integers(0, 10000, size=(2000, 1)) + rng.integers(0, 50, size=(2000, 25))
    s[:, :, SC_FUNDS] = rng.integers(-500, 20000, size=(2000, 25))
    s[:, :, SC_POWERED] = rng.integers(0, 60, size=(2000, 1))
    s[:, :, SC_UNPOWERED] = rng.integers(0, 4, size=(2000, 1))
    s[:, 0, SC_COAL] = rng.integers(0, 3, size=2000)
    s[:, -1, SC_COAL] = rng.integers(0, 5, size=2000)
    for t in TASKS:
        theta, _, _ = calibrate_theta(t, s)
        m = margin(t, s, theta, stat_sd=float(np.std(statistic(t, s))) or 1.0)
        assert np.array_equal(m >= 0, verdict(t, s, theta)), t


def test_oracle_majority_over_seeds():
    """16 of 32 seeds passing is a pass; oracle_value is the largest theta that still passes."""
    rng = np.random.default_rng(3)
    for task in TASKS:
        s = np.zeros((50, 32, 25, 20))
        s[..., SC_POP] = rng.integers(1000, 10000, size=(50, 32, 1)) + rng.integers(0, 50, size=(50, 32, 25))
        s[..., SC_FUNDS] = rng.integers(-300, 20000, size=(50, 32, 25))
        s[..., SC_POWERED] = rng.integers(0, 60, size=(50, 32, 1))
        s[..., SC_UNPOWERED] = rng.integers(0, 3, size=(50, 32, 1))
        val = oracle_value(task, s)
        assert val.shape == (50,)
        for theta in np.quantile(statistic(task, s), [0.1, 0.5, 0.9]):
            share = oracle_share(task, s, theta)
            v = oracle_verdict(task, s, theta)
            assert np.array_equal(v, share >= 0.5)
            assert np.array_equal(v, val >= theta)
    up = traj([1000, 1500, 3000], [5000, 4000, 4500])
    down = traj([1000, 1500, 2000], [5000, 4000, 4500])
    half = np.stack([up] * 16 + [down] * 16)
    assert oracle_verdict("grow", half, 3000) and oracle_share("grow", half, 3000) == 0.5
    assert not oracle_verdict("grow", np.stack([up] * 15 + [down] * 17), 3000)
    a, b = oracle_seeds("x", "grow", 24), oracle_seeds("x", "solvent", 24)
    assert len(a) == ORACLE_N == len(set(a)) and not set(a) & set(b) and a == oracle_seeds("x", "grow", 24)


def test_start_row_alone_is_a_valid_prefix():
    """Potential-based rewards evaluate the margin on prefixes; the one-row prefix must not raise."""
    one = traj([1000], [5000])
    one[:, SC_TAX], one[-1, SC_TAX_FUND] = 7, 100
    for task in TASKS:
        assert np.isfinite(margin(task, one, 50.0, 10.0)) or task == "power"
        assert feasible(task, one).shape == ()
    assert feasible("treasury", one) and margin("treasury", one, 50.0, 10.0) == 1.0     # funds slack binds (5000 / 5000)
    assert margin("treasury", one, 95.0, 10.0) == 0.5                                   # the statistic's slack binds
