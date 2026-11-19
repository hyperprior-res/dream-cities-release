# Ladder: projected hours per run (measured training rates of the current model)

Hours = samples / measured samples per second / 3600, plus 0.10 h per run for evaluating its two checkpoints.

| run | size | mode | samples | GPU 0 rate | GPU 0 hours | GPU 1 rate | GPU 1 hours |
|---|---|---|---|---|---|---|---|
| os_15m_small | 15m | onestep | 6,000,000 | 1542 | 1.18 | 734 | 2.37 |
| os_15m_full | 15m | onestep | 6,000,000 | 1542 | 1.18 | 734 | 2.37 |
| os_50m_small | 50m | onestep | 6,000,000 | 659 | 2.63 | 401 | 4.26 |
| os_50m_full | 50m | onestep | 6,000,000 | 659 | 2.63 | 401 | 4.26 |
| os_100m_small | 100m | onestep | 6,000,000 | 423 | 4.04 | 257 | 6.58 |
| os_100m_full | 100m | onestep | 6,000,000 | 423 | 4.04 | 257 | 6.58 |
| sf_15m_small | 15m | selfforce | 1,500,000 | 1065 | 0.49 | 507 | 0.92 |
| sf_15m_full | 15m | selfforce | 1,500,000 | 1065 | 0.49 | 507 | 0.92 |
| sf_50m_small | 50m | selfforce | 1,500,000 | 533 | 0.88 | 324 | 1.38 |
| sf_50m_full | 50m | selfforce | 1,500,000 | 533 | 0.88 | 324 | 1.38 |
| sf_100m_small | 100m | selfforce | 1,500,000 | 325 | 1.38 | 198 | 2.21 |
| sf_100m_full | 100m | selfforce | 1,500,000 | 325 | 1.38 | 198 | 2.21 |
| os_50m_full_s1 | 50m | onestep | 6,000,000 | 659 | 2.63 | 401 | 4.26 |
| os_50m_full_s2 | 50m | onestep | 6,000,000 | 659 | 2.63 | 401 | 4.26 |
| sf_50m_full_s1 | 50m | selfforce | 1,500,000 | 533 | 0.88 | 324 | 1.38 |
| sf_50m_full_s2 | 50m | selfforce | 1,500,000 | 533 | 0.88 | 324 | 1.38 |

Totals (all 16 on one card): GPU 0 28.2 h, GPU 1 46.7 h.

* GPU 1 (gpu-b, 24 GB): measured with the current model (SIZES: two-stage, level histograms, ledger): one-step 15M bench (data on the GPU), 50M pilot 4's median with the real loader, 100M bench; self-forcing benches; batch 128 as micro-batches of 64 (50M) and 32 (100M)
* GPU 0 (gpu-a, 98 GB): projected, not measured (busy until 02:20Z with noledger_50m_full_1step): GPU 1 rate x the GPU 0 / GPU 1 ratio measured on 9-10 Nov with the previous model at the same sizes (15M 1258.8 / 599.5 = 2.10, both batch 128; 50M 789.7 / 480.7 = 1.64, batch 128 vs 64; 100M uses the 50M ratio)
* two runs at once on GPU 0: no gain: measured 9 Nov (previous model), 15M and 50M together kept 609.5 / 1258.8 = 48% and 389.7 / 789.7 = 49% of their solo speed, 0.98 of one card in total
* evaluation: 0.1 h per run assumed for the two checkpoints (measured 140 to 200 s per checkpoint for 50M)
* third stage: 2 scalar-only updates of 4,096 rows per trunk step; cost per update measured on GPU 1 at width 384 from pilot 5 against pilot 4 (4.0 ms), scaled by width squared for 15M (256) and 100M (512)
