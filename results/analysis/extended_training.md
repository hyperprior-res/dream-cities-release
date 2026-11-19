# Sixfold Extended One-Step Training Control (`os_50m_full_36m`, 36M examples / 12 epochs)

Status: **complete** (generated `2026-11-15T21:36:19Z` on CPU).

## 1. Held-out test fidelity and likelihood across milestones

| Checkpoint | Examples | Test ELBO | 1m struct F1 | 12m pop err | 12m funds err | 24m overlay ratio (ge 1) | 24m powered-zone MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `os_50m_full` (2 ep) | 6,000,000 | -2610.4 | 0.179 | 0.060 | 0.035 | 1.058 (6/8) | 6.13 |
| `os_50m_full_36m` (2 ep) | 6,000,000 | -2643.8 | 0.180 | 0.052 | 0.059 | 0.947 (3/8) | 5.18 |
| `os_50m_full_36m` (4 ep) | 12,000,000 | -2602.1 | 0.181 | 0.051 | 0.054 | 0.974 (3/8) | 9.63 |
| `os_50m_full_36m` (6 ep) | 18,000,000 | -2527.6 | 0.181 | 0.056 | 0.046 | 0.999 (3/8) | 8.64 |
| `os_50m_full_36m` (8 ep) | 24,000,000 | -2435.9 | 0.180 | 0.058 | 0.040 | 1.045 (6/8) | 8.70 |
| `os_50m_full_36m` (10 ep) | 30,000,000 | -2389.6 | 0.182 | 0.059 | 0.035 | 1.088 (6/8) | 11.41 |
| `os_50m_full_36m` (12 ep) | 36,000,000 | -2375.4 | 0.183 | 0.065 | 0.028 | 1.139 (6/8) | 11.50 |

## 2. Adaptive CEM at B = 10,000 (193 core instances)

- `os_50m_full` (6M): false acceptance `0.207`, excess `+0.135`, false rejection `0.346`, oracle pass `0.269`, shortfall `-0.311`.
- `os_50m_full_36m` (36M): false acceptance `0.036`, excess `-0.036`, false rejection `0.639`, oracle pass `0.316`, shortfall `-0.264`.
- Exact simulator: false acceptance `0.073`, false rejection `0.080`, oracle pass `0.580`.

## 3. In-imagination PPO at 1,000,000 steps (15 runs)

- All 5 families: dream `0.075` (6M `0.271`), oracle `0.119` (6M `0.138`), closed `0.159` (6M `0.202`), initial-plan excess `-0.021` (6M `+0.122`).
- Treasury (3 seeds): dream `0.340` -> oracle `0.423` (6M `0.599` -> `0.340`, diff `+0.083`).
- Four spatial/grid families (12 seeds): dream `0.009` -> closed `0.096` (6M `0.189` -> `0.166`).

## 4. All 120 held-out cities (574 instances)

- Single-plan (`B = 1`): false acceptance `0.014` (6M `0.092`, ref `0.016`, excess `-0.002`).
- Random shooting (`B = 1,000`): false acceptance `0.031`, excess `-0.038`, false rejection `0.662`, oracle pass `0.361` (6M `0.336`, ref `0.516`).
- Adaptive CEM (`B = 1,000`): false acceptance `0.026`, excess `-0.056`, false rejection `0.648`, oracle pass `0.307` (6M `0.287`, ref `0.495`).

## 5. Out-of-sample cross-model calibration (25 checkpoints, 125 pairs)

- Single-plan (`B = 1`) vs PPO margin inflation: within-family Spearman `0.702` [0.549, 0.823], pooled `0.876` [0.830, 0.912].
