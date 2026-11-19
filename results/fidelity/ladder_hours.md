# Ladder: projected hours per run (measured training rates of the current model)

Hours = samples / measured samples per second / 3600, plus 0.10 h per run for evaluating its two checkpoints.

| run | size | mode | samples | GPU 0 rate | GPU 0 hours | GPU 1 rate | GPU 1 hours |
|---|---|---|---|---|---|---|---|
| os_15m_small | 15m | onestep | 6,000,000 | 1574 | 1.16 | 750 | 2.32 |
| os_15m_full | 15m | onestep | 6,000,000 | 1574 | 1.16 | 750 | 2.32 |
| os_50m_small | 50m | onestep | 6,000,000 | 676 | 2.57 | 412 | 4.15 |
| os_50m_full | 50m | onestep | 6,000,000 | 676 | 2.57 | 412 | 4.15 |
| os_100m_small | 100m | onestep | 6,000,000 | 435 | 3.93 | 265 | 6.39 |
| os_100m_full | 100m | onestep | 6,000,000 | 435 | 3.93 | 265 | 6.39 |
| sf_15m_small | 15m | selfforce | 1,500,000 | 1080 | 0.49 | 514 | 0.91 |
| sf_15m_full | 15m | selfforce | 1,500,000 | 1080 | 0.49 | 514 | 0.91 |
| sf_50m_small | 50m | selfforce | 1,500,000 | 544 | 0.87 | 331 | 1.36 |
| sf_50m_full | 50m | selfforce | 1,500,000 | 544 | 0.87 | 331 | 1.36 |
| sf_100m_small | 100m | selfforce | 1,500,000 | 332 | 1.35 | 202 | 2.16 |
| sf_100m_full | 100m | selfforce | 1,500,000 | 332 | 1.35 | 202 | 2.16 |
| os_50m_full_s1 | 50m | onestep | 6,000,000 | 676 | 2.57 | 412 | 4.15 |
| os_50m_full_s2 | 50m | onestep | 6,000,000 | 676 | 2.57 | 412 | 4.15 |
| sf_50m_full_s1 | 50m | selfforce | 1,500,000 | 544 | 0.87 | 331 | 1.36 |
| sf_50m_full_s2 | 50m | selfforce | 1,500,000 | 544 | 0.87 | 331 | 1.36 |

Totals (all 16 on one card): GPU 0 27.6 h, GPU 1 45.6 h.

* GPU 1 (gpu-b, 24 GB): measured with the current model (SIZES: two-stage, level histograms, ledger): one-step 15M bench (data on the GPU), 50M pilot 4's median with the real loader, 100M bench; self-forcing benches; batch 128 as micro-batches of 64 (50M) and 32 (100M)
* GPU 0 (gpu-a, 98 GB): projected, not measured (busy until 02:20Z with noledger_50m_full_1step): GPU 1 rate x the GPU 0 / GPU 1 ratio measured on 9-10 Nov with the previous model at the same sizes (15M 1258.8 / 599.5 = 2.10, both batch 128; 50M 789.7 / 480.7 = 1.64, batch 128 vs 64; 100M uses the 50M ratio)
* two runs at once on GPU 0: no gain: measured 9 Nov (previous model), 15M and 50M together kept 609.5 / 1258.8 = 48% and 389.7 / 789.7 = 49% of their solo speed, 0.98 of one card in total
* evaluation: 0.1 h per run assumed for the two checkpoints (measured 140 to 200 s per checkpoint for 50M)
