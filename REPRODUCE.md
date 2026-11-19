# Reproducing "Dream Cities: Measuring World-Model Exploitation Against an Exact Simulator"

How a reader with the release reproduces every number and figure in the paper, stage by stage. Correspondence via
hyperprior.net. Commands run from the repository root with `PYTHONPATH=hpr-dream:code` in a Python environment providing
`numpy`, `scipy`, `torch`, and `pytest` (building the paper also requires `matplotlib` and Tectonic 0.17.0). Compute is
reported in H200-equivalent GPU hours in `results/analysis/compute_summary.{json,md}` alongside per-audit `costs.json`
records. Large regenerable intermediate stores (trajectory shards, neural checkpoints, and rollout caches) are written to
an external `<cache>` directory rather than stored inside the repository.

## What is not released, and why
Neural world-model weights are not distributed because whether weights trained on trajectories of a GPL simulator
constitute derived works remains legally untested; instead, table (a) below records the exact SHA-256 digest of every
checkpoint audited in the paper (stored alongside run configs in `paper/data/ckpt_meta/`). No trained policies (whether
trained inside world models or on the C++ engine) are distributed. Engine-linked code (`engine/`, `code/`) is released
under GPL-3.0 with Electronic Arts' additional terms (`engine/MODIFICATION_NOTICE.md`), `hpr-dream/` is Apache-2.0, and
result tables, task definitions, figure scripts, and paper sources are CC BY 4.0.

## Stages

| # | Stage | Command | Needs | Writes | Compute / Runtime | Paper Reference |
|---|---|---|---|---|---|---|
| 1 | Engine build | `make -C engine` | C++17 compiler; `engine/src` (patched MicropolisCore) | `engine/libmicropolis.so`, `engine/verify_replay` | seconds (CPU) | all stages |
| 2 | Exact replay & Markov sufficiency | `python -m pytest code/tests/test_oracle_exact.py`; `make -C engine verify`; `python code/scripts/check_sufficiency.py` | stage 1 | `results/oracle/bundled_hashes.npy`, `results/oracle/sufficiency/summary.json` | CPU | Section 2.1, Appendix A.1 |
| 3 | Held-out & training start states | `python code/scripts/build_families.py --workers 16`; `python code/scripts/build_families_x.py build --workers 16` | stage 1 | `data/families/`, `data/families.json`, `data/families_x.json` | CPU | Sections 2.1, 3.3; Appendices A.2, A.5 |
| 4 | Trajectory stores | `python code/scripts/gen_data.py all --workers 28` (then `gen_data.py verify --split train_full --n 500`) | stages 1, 3 | trajectory shards in `<cache>` (~135 GB); `results/data/summary.json` | CPU | Section 2.1, Appendix A.2 |
| 5 | Calibrated tasks & thresholds | `python code/scripts/calibrate_tasks.py`; `code/scripts/task_frontier.py`, `threshold_reread.py` | stages 1, 3 | `data/tasks_v2_H24.json`, `data/tasks_v2x_H24.json`, `results/tasks_v2*/` | CPU | Section 2.3, Appendix A.4, Table 4 |
| 6 | World-model ladder, coverage & seed runs | `python code/scripts/ladder.py --queue code/scripts/ladder_queue_v2.json --gpu 0` (single runs: `code/scripts/train_run.py`) | stage 4 | checkpoints in `<cache>`; `results/fidelity/ladder/<run>/` | see `compute_summary.md` (17 runs) | Section 2.1, Appendix A.3, Tables 2--3 |
| 7 | Short- & task-horizon fidelity | run by `ladder.py` (`code/scripts/eval_fidelity.py`); then `python code/scripts/fidelity_horizon.py`, `raw_tile_f1.py`, `logged_plan_verdicts.py` | stage 6 | `results/fidelity/ladder/<run>/{dev,test,test_half,train_eval}/` | see `compute_summary.md` | Section 2.2, Appendices A.9, B.1, Tables 16--17 |
| 8 | Ground-truth oracle & exact-simulator references | inside each audit (`dc.oracle` on 32 reserved seeds; exact-simulator reference on disjoint seeds) | stages 1, 5 | each audit's `reference.json`; `results/audit/engine_reference/` | CPU engine pool (totals in `compute_summary.md`) | Sections 2.3, 3 |
| 9 | Search audits: 40-city core, 80-city expansion, adaptive CEM, $10^4$ scaling | `python code/scripts/run_audit.py --ckpt <ckpt> --out results/audit/ladder/<run>/samples_<N>/tasks_v2_H24` (`--tasks data/tasks_v2x_H24.json` for expansion split); scaling axis: `python code/scripts/pressure_axis.py` | stages 5, 6 | `results/audit/ladder/<run>/samples_<N>/tasks_v2*_H24*/` (records, `costs.json`) | see `compute_summary.md` and `costs.json` | Sections 3, 4.1, 5; Tables 8--9, 13--15 |
| 10 | Counterfactual subsystem patching & controls | `python code/scripts/run_patching.py --run-dir <audit dir>`; `python code/scripts/patching_controls.py` | stage 9 | `patching.jsonl.gz` beside audit; `results/analysis/patching_controls.*` | GPU + CPU | Section 4.2, Appendix A.6, Table 5 |
| 11 | Inference-time defences | `python code/scripts/run_defences.py --settings all` (then `--report`); `defence_baselines.py` | stages 6, 9 | `results/defences/` | GPU + CPU | Section 7, Appendix A.8, Appendix B.6 |
| 12 | In-imagination & engine-trained PPO | `python code/scripts/rl_queue.py --queue <queue> --gpu 0` (single runs: `run_rl.py train --env emulator ...` or `--env engine ...`); then `python code/scripts/rl_axis.py replay` | stage 6 | `results/rl/<run>/` (evaluation records and logs; policies not distributed) | see `compute_summary.md` (375 model runs + engine reference) | Sections 3.4, 4.1, 5, 6; Appendix A.7, Tables 7, 10, 19 |
| 13 | Cross-model audit analysis | `CUDA_VISIBLE_DEVICES= python code/scripts/analyse_ladder.py` | stages 9, 12 | `results/analysis/main_claim.{json,md}`, `pairs.csv`, `replication.json` | ~3 minutes (CPU) | Section 5, Figure 7, Appendix B.7 |
| 14 | Coverage retraining & extended training controls | `CUDA_VISIBLE_DEVICES= python code/scripts/coverage_seeds.py`; `python code/scripts/showcase_36m.py`; `CUDA_VISIBLE_DEVICES= python code/scripts/extended_training.py` | stages 6, 9, 12 | `results/analysis/coverage_seeds.*`, `coverage.json`, `showcase_36m.json`, `extended_training.*` | GPU + CPU | Sections 2.2, 3.2, 3.4, 5, 6; Appendices B.2, B.5, Tables 7, 11 |
| 15 | Monthly closed-loop replanning | `python code/scripts/run_replan.py --model engine ...` (and `--seed-stream fresh1` for fresh-seed reference) and `--model emulator --checkpoint <main checkpoint> ...`; then `python code/scripts/replan_control.py --engine results/replan/engine` and `python code/scripts/replan_axis.py --emulator results/replan/emulator --engine results/replan/engine` (and `--engine results/replan/engine_fresh --out results/analysis/replan_fresh`) | stages 5, 6 | `results/replan/*/records.jsonl.gz`; `results/analysis/replan*.json` | see `compute_summary.md` | Section 3.5, Appendix B.5, Table 12 |
| 16 | Compute summary | `python code/scripts/compute_summary.py` | run logs | `results/analysis/compute_summary.{json,md}` (H200-equivalent GPU hours) | seconds (CPU) | Compute section, Appendix A.1, Table 1 |
| 17 | External continuous-control check (TD-MPC2) | `code/scripts/external_tdmpc2.py determinism`, `audit`, `report` (with `dm_control`) | public TD-MPC2 checkpoints | `results/external/`, `cards/external/` | GPU + CPU | Appendix C |
| 18 | Paper, figures, & verification gates | `make -C paper && make -C paper check` | `results/`, `data/`, Tectonic 0.17.0 | `paper/figures/*.pdf`, `paper/numbers.tex`, `paper/main.pdf` | ~1 minute (CPU) | entire paper |

Every empirical quantity in the paper is generated into `paper/numbers.tex` by `paper/scripts/make_numbers.py` from
released result files; `paper/numbers_ledger.md` traces each macro to its exact source file and JSON field, and
`make -C paper check` verifies zero hardcoded prose numbers, zero unresolved references, zero overfull boxes, and full
font embedding.

## (a) Checkpoints audited in the paper (weights not distributed)

SHA-256 digests of every checkpoint (`paper/data/ckpt_meta/<run>/samples_<N>.pt.sha256`). Runs prefixed `os_` denote
one-step variational models; `sf_` denotes pushforward rollout fine-tuning from the corresponding one-step parent; sizes
`15m`, `50m`, `100m` denote capacity scales; `full` and `small` denote training-data budgets.

| run | samples | point | role | SHA-256 |
|---|---|---|---|---|
| `os_100m_full` | 3,000,064 | half | ladder (Section 5) | `2f778adea97a5930324db2b07de26103699b3e4636998bcbd0c097f387846e6a` |
| `os_100m_full` | 6,000,000 | final | ladder (Section 5) | `b36210a87f489f92497ec8ddcaad892117fd29cd64faf8d7183651329eb39b89` |
| `os_100m_small` | 3,000,064 | half | ladder (Section 5) | `d8ff787cea087b1ff75ff0807e278856c5c7353357d51de2ceaf42dcb8736061` |
| `os_100m_small` | 6,000,000 | final | ladder (Section 5) | `efe193ac70672254e6725195c09bfaeed7797efc257525cd742f404d04f2add8` |
| `os_15m_full` | 3,000,064 | half | ladder (Section 5) | `1186f3d5a89740f117b2dd6aa189342976ff13903c7280005b36e1895e332289` |
| `os_15m_full` | 6,000,000 | final | ladder (Section 5) | `daa4e5e65c05d2cda1792ab2ffa713b311d04a287f05e17367461ae1a2be48f6` |
| `os_15m_small` | 3,000,064 | half | ladder (Section 5) | `aa62c6793484adf0b297ee5bf86e4620f6ecc87447ac9c1cd3185e3fb6997b04` |
| `os_15m_small` | 6,000,000 | final | ladder (Section 5) | `7b7a3027427dbcc7c0e9c0410de1bbcb7b1d959dafd5f5a902c8994b7ea73eb4` |
| `os_50m_cov` | 3,000,064 | half | coverage-retrained model (Section 6) | `21b00a3d84fdb743db4906df2c5b384587de5386655c088594b2aee68beb7e0e` |
| `os_50m_cov` | 6,000,000 | final | coverage-retrained model (Section 6) | `a4c38f8729f2a7f1fcc4dcf5b4fb38abb5c7ce61ac35206dfd5de3d305a5ef29` |
| `os_50m_full` | 3,000,064 | half | ladder (Section 5) | `e2c8d843fd7c7e2503e5d2e7fd94c78421c13635e3b94e97dd97da0edf299fef` |
| `os_50m_full` | 6,000,000 | final | ladder; primary checkpoint | `7b08be25577b36669ef6b35cdc6cc6a62f927de00d0e69f96496afc1b6934283` |
| `os_50m_full_36m` | 6,000,000 | 2 ep | sixfold extended-training control (Appendix B.2) | `56e4f6965b1e23308b7bb86fd7d229801a93f2daa4340e1b5b0ad4739f955dd1` |
| `os_50m_full_36m` | 12,000,000 | 4 ep | sixfold extended-training control (Appendix B.2) | `512dc047e852aac76d25eed79c7616e1dfdbfe4bec8a1a56df07d96797ad9cb8` |
| `os_50m_full_36m` | 18,000,000 | 6 ep | sixfold extended-training control (Appendix B.2) | `19ecbf9de8f858c05495ce9c50eaa2692243ca52673e0950180af23e56334c3e` |
| `os_50m_full_36m` | 24,000,000 | 8 ep | sixfold extended-training control (Appendix B.2) | `89600bf2baa2372d961ef30f2682fdf1294eeb8f83baa4a0d17c93773fc46082` |
| `os_50m_full_36m` | 30,000,000 | 10 ep | sixfold extended-training control (Appendix B.2) | `cbdb3f307c036453ed4b03163e25afa35bd36635b5d246d2b7ec6190963c9ada` |
| `os_50m_full_36m` | 36,000,000 | 12 ep (final) | sixfold extended-training control (Sections 2--3, 5; Appendix B.2) | `bf86bcc432630af3c5d313dd6b81cfa82d4f6bac9ed20f649901ddc5084522ca` |
| `os_50m_full_s1` | 3,000,064 | half | additional seed of primary configuration (Sections 6--7) | `486470b628beb2ffaf0f34b4235b343802bb4979e1a1c0b38dbefdaaa6c07ecb` |
| `os_50m_full_s1` | 6,000,000 | final | additional seed of primary configuration (Sections 6--7) | `1d4fb0602fbbb7156e586ead2e6b6a1235a070d3489868a97f1a57d84d6b9cf4` |
| `os_50m_full_s2` | 3,000,064 | half | additional seed of primary configuration (Sections 6--7) | `18e600cf9680ad44b5d31325154d5e3c6c955d2db13040f0d6ecdb07400b0589` |
| `os_50m_full_s2` | 6,000,000 | final | additional seed of primary configuration (Sections 6--7) | `9d9debc5dad3eb2c5c6d1177fe22fe1741d433a111c10d51202c88295b59091f` |
| `os_50m_small` | 3,000,064 | half | ladder (Section 5) | `266252e86d6e3f08573eaf000bfa82a28922461942bd50c631cb93988d76197d` |
| `os_50m_small` | 6,000,000 | final | ladder (Section 5) | `01bdbd075806b21ef5e2def8ebe3e482437ba5c4031967b18beb30df7c3c16d7` |
| `sf_100m_full` | 750,080 | half | ladder (Section 5) | `7154d2d1abcbd8e02066a883f4275bbbafe3955160a5e9c31216cfb16bab0642` |
| `sf_100m_full` | 1,500,032 | final | ladder (Section 5) | `5d764d18e17f4f40420975b34eba6e10547b66ffdee9a574a65281831d3616b7` |
| `sf_100m_small` | 750,080 | half | ladder (Section 5) | `a35568554bd04391b48f66eac61abb40bdedcf68a310e1bf6603c476b40cef21` |
| `sf_100m_small` | 1,500,032 | final | ladder (Section 5) | `177911d3c1132ba0304f1bacfd9934afb7bd297cbc19f92298e2ecc4e8081e91` |
| `sf_15m_full` | 750,080 | half | ladder (Section 5) | `d96533bdbf4fde2b4a2b7cc58dee1ef7559ab65184bbdfb5f09ad2e228c5da53` |
| `sf_15m_full` | 1,500,032 | final | ladder (Section 5) | `6bb31a6dc7a2fdfcd0e8902faa8eac797f06de0ef6172d85a7f4ca02bd1439f6` |
| `sf_15m_small` | 750,080 | half | ladder (Section 5) | `ff79c2bf42d42941dc1d40b10fce16ac56521d136d05f687b29290cb7049f4eb` |
| `sf_15m_small` | 1,500,032 | final | ladder (Section 5) | `3fde3a11af5ed787b9007f524b266e943fbc5dcb1009fbff482ec15f3e665b45` |
| `sf_50m_full` | 750,080 | half | ladder (Section 5) | `136f29a695f0de6650c8400d2206ed5ccd8d1f6d469831d1afd94eeef3934477` |
| `sf_50m_full` | 1,500,032 | final | ladder (Section 5) | `33836137e6971f5469f5b00aabfe1ed973beeeba78079baaebb9f7b6ce4e9ec1` |
| `sf_50m_full_s1` | 750,080 | half | additional seed of primary configuration (Sections 6--7) | `271deab4d283d37c027a155571d68df689d7211ae461b7138071244ee39324db` |
| `sf_50m_full_s1` | 1,500,032 | final | additional seed of primary configuration (Sections 6--7) | `56eb987cae86a0a9c1d2ce1b990124e2c5b6dc7905223a7a7d094e03dcd80e84` |
| `sf_50m_full_s2` | 750,080 | half | additional seed of primary configuration (Sections 6--7) | `98e462e8cf3846802bc2e33f6be2eadccb3b680e5a3344408032df21db677c48` |
| `sf_50m_full_s2` | 1,500,032 | final | additional seed of primary configuration (Sections 6--7) | `6555bb9734271725aa1111fe3fde61154b4b09491896453b2404cffcdb930ab6` |
| `sf_50m_small` | 750,080 | half | ladder (Section 5) | `31a26b40488bf9ae407df47c484689893937b92df274e9f8a1aa11458c4c443c` |
| `sf_50m_small` | 1,500,032 | final | ladder (Section 5) | `6d459475a4031347595b333e3614e00107abf0decf8ce78a2d005aa261d13de3` |

## (b) What can be verified directly without model weights

| Verification | Inputs | Command |
|---|---|---|
| Every number, table, and figure in the paper | `results/`, `data/`, `figures/data/` | `make -C paper && make -C paper check` (stage 18) |
| Cross-model Spearman correlations, permutation null, single-plan calibration | `results/audit/**/records.jsonl.gz`, `results/rl/**` | stage 13 (`analyse_ladder.py`) |
| Search budget scaling, split consistency, coverage seed comparisons, patching controls, monthly replanning | stored evaluation records in `results/` | stages 9 (`pressure_axis.py`), 13, 14, 10 (`patching_controls.py`), 15 (`replan_axis.py`, `replan_control.py`) |
| Bit-exact C++ replay, ground-truth oracle verdicts, exact-simulator references, calibrated task thresholds | `engine/` (stage 1) and `data/` | stages 2, 5, 8 on CPU |
| World-model rollouts, patching rollouts, inference-time defences, and in-imagination PPO | retrained checkpoints | stages 4 and 6, followed by stages 7, 9--12, 15 (retrained weights will produce new SHA-256 digests) |
