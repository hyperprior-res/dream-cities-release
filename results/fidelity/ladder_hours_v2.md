# Ladder v2: projected hours per run (censored likelihood, decoding a, three selections)

Hours = samples / samples per second / 3600 + evaluation hours per run (50M on GPU 0 measured with pilot 6: development selection 108 s per checkpoint (two checkpoints), test 119 s, train_eval 86 s, so 0.117 h per run; other sizes scaled by inference throughput (bench_infer.json, batch 256), GPU 1 by the 50M training-rate ratio 1.60; the three yardsticks are computed once (about 2 min each on CPU)).

| run | size | mode | samples | GPU 0 rate | GPU 0 hours | GPU 1 rate | GPU 1 hours |
|---|---|---|---|---|---|---|---|
| os_15m_small | 15m | onestep | 6,000,000 | 1542 p | 1.15 | 681 m | 2.56 |
| os_15m_full | 15m | onestep | 6,000,000 | 1542 p | 1.15 | 681 m | 2.56 |
| os_50m_small | 50m | onestep | 6,000,000 | 642 m | 2.71 | 401 p | 4.34 |
| os_50m_full | 50m | onestep | 6,000,000 | 642 m | 2.71 | 401 p | 4.34 |
| os_100m_small | 100m | onestep | 6,000,000 | 423 p | 4.11 | 257 p | 6.74 |
| os_100m_full | 100m | onestep | 6,000,000 | 423 p | 4.11 | 257 p | 6.74 |
| sf_15m_small | 15m | selfforce | 1,500,000 | 1065 p | 0.46 | 507 p | 0.94 |
| sf_15m_full | 15m | selfforce | 1,500,000 | 1065 p | 0.46 | 507 p | 0.94 |
| sf_50m_small | 50m | selfforce | 1,500,000 | 533 p | 0.90 | 324 p | 1.47 |
| sf_50m_full | 50m | selfforce | 1,500,000 | 533 p | 0.90 | 324 p | 1.47 |
| sf_100m_small | 100m | selfforce | 1,500,000 | 325 p | 1.45 | 198 p | 2.38 |
| sf_100m_full | 100m | selfforce | 1,500,000 | 325 p | 1.45 | 198 p | 2.38 |
| os_50m_full_s1 | 50m | onestep | 6,000,000 | 642 m | 2.71 | 401 p | 4.34 |
| os_50m_full_s2 | 50m | onestep | 6,000,000 | 642 m | 2.71 | 401 p | 4.34 |
| sf_50m_full_s1 | 50m | selfforce | 1,500,000 | 533 p | 0.90 | 324 p | 1.47 |
| sf_50m_full_s2 | 50m | selfforce | 1,500,000 | 533 p | 0.90 | 324 p | 1.47 |

Totals (all 16 on one card): GPU 0 28.8 h, GPU 1 48.5 h.

With ladder-v1's split (GPU 0: os_50m_full, sf_50m_full, os_100m_full, sf_100m_full, os_100m_small, sf_100m_small, os_50m_full_s1, sf_50m_full_s1; GPU 1: os_15m_full, sf_15m_full, os_15m_small, sf_15m_small, os_50m_small, sf_50m_small, os_50m_full_s2, sf_50m_full_s2): GPU 0 18.3 h, GPU 1 18.6 h, so about 18.6 h to the last run.

Rate marks: m = measured on this model (the ladder-v1 runs, same three-stage model and settings; the censored likelihood adds two element-wise limits per head), p = projected as in ladder_hours_bk.md.

* measured (m): median samples per second of the ladder-v1 runs before pilot 6 shared GPU 0 (02:47Z to 03:33Z, 10 Nov): os_50m_full alone on GPU 0, 642.2 over 592 log points; os_15m_full alone on GPU 1, 681.4 over 650 log points; same model, settings and loader as v2 (bk_updates 2, batch 128, no micro-batching on GPU 0)
* projected (p): as in ladder_hours_bk.md: GPU 1 benches and pilot 4's loader median; GPU 0 = GPU 1 x the GPU 0 / GPU 1 ratio measured on 9-10 Nov with the previous model. The two measured rates are 0.97 (GPU 0, 50M) and 0.93 (GPU 1, 15M) of their projections
* two runs at once on GPU 0: no gain (measured 9 Nov: 0.98 of one card in total); measured again 10 Nov: os_50m_full fell from 642 to 261 samples per second while pilot 6 shared the card
* third stage: 2 scalar-only updates of 4,096 rows per trunk step (ladder_queue_v2.json gives the reason)
