"""hpr_dream: audit a learned simulator used as a grader against an exact oracle.

Modules: :mod:`hpr_dream.attack` (attackers with exact budget accounting),
:mod:`hpr_dream.stats` (statistics with cluster-bootstrap intervals), :mod:`hpr_dream.noise`
(noise-only surrogate graders), :mod:`hpr_dream.card` (the grader card). numpy and scipy only.
"""

__version__ = "0.1.0"

from .attack import (  # noqa: E402
    CEM_SCHEDULE,
    BudgetError,
    Marginals,
    Selected,
    Space,
    best_of_n,
    cem,
    cem_schedule,
    cem_seeded,
    fit_marginals,
    random_shooting,
)
from .card import build_card, write_card  # noqa: E402
from .noise import (  # noqa: E402
    CalibratedResidualSurrogate,
    FlipSurrogate,
    OracleCache,
    PoolTooSmall,
    ResidualFamily,
    ResidualSurrogate,
    SurrogateGrader,
    SurrogateResult,
    VolatilityResidualSurrogate,
    attack_surrogate,
    calibrated_neighbours,
    flip_surrogate,
    pool_family_residuals,
    residual_surrogate,
    volatility_neighbours,
)
from .stats import (  # noqa: E402
    BrierDecomposition,
    Estimate,
    FlipFloor,
    auc,
    brier_decomposition,
    clustered_kendall,
    clustered_spearman,
    conditional_mean,
    conditional_reject,
    dream_overfit_probability,
    excess,
    false_rejection,
    flip_floor,
    hackability,
    log_score,
    noise_floor_flip,
    unlucky_share,
    zero_count_upper_bound,
)

__all__ = [
    "__version__",
    "BrierDecomposition", "BudgetError", "CEM_SCHEDULE", "CalibratedResidualSurrogate", "Estimate", "FlipFloor",
    "FlipSurrogate",
    "Marginals", "OracleCache", "PoolTooSmall", "ResidualFamily", "ResidualSurrogate", "Selected", "Space",
    "SurrogateGrader", "SurrogateResult", "VolatilityResidualSurrogate", "pool_family_residuals",
    "volatility_neighbours", "zero_count_upper_bound",
    "attack_surrogate", "auc", "best_of_n", "brier_decomposition", "build_card", "calibrated_neighbours", "cem",
    "cem_schedule", "cem_seeded",
    "clustered_kendall", "clustered_spearman", "conditional_mean", "conditional_reject", "dream_overfit_probability",
    "excess", "false_rejection", "fit_marginals", "flip_floor", "flip_surrogate", "hackability",
    "log_score", "noise_floor_flip", "random_shooting", "residual_surrogate", "unlucky_share",
    "write_card",
]
