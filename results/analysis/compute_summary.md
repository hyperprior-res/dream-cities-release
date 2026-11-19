# Compute in H200-equivalent hours

Generated 2026-11-15T11:24:32Z by `code/scripts/compute_summary.py`. Conversion: card-hours weighted by throughput multiples fixed before the study from published card specifications (relative to an H200); not measured on our workload; 12.1 card-hours on cards without a multiple left out.

| arm | H200-equivalent hours |
|---|---|
| local, training | 29.9 |
| local, fidelity | 2.5 |
| local, audits original | 2.6 |
| local, audits further | 13.6 |
| local, pool seeded | 13.0 |
| local, all logged | 61.6 |
| rented, all 130 pods | 101.4 |
| logged in total, local and rented | 163.0 |
| rented, reinforcement learning | 54.3 |
| rented, evaluation jobs (26 of 83 pods returned one) | 36.7 |
| rented, extended training | 9.7 |
| rented, no result (81 pods) | 7.8 |

Replanning, instance wall-hours: emulator side 11.7 (100 instances), perfect-emulator sides 6.0 (325 instances). Engine pool: 434 process-hours over 129 audits. Models trained: 17. Left out: 12.1 card-hours on cards without a multiple (23 rented pods).

Not counted: local evaluation jobs before the audit worker's log began, whose card no log records; jobs started and not finished; reinforcement learning run locally, whose card is not recorded; the engine time of threshold building and of reinforcement learning's engine-side phases; the second machine's processor time outside the engine pool; card-hours on cards without a throughput multiple.
