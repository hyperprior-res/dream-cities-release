# Dream Cities: Measuring World-Model Exploitation Against an Exact Simulator

This repository contains the C++ simulator patches, Python evaluation harness, calibrated task definitions, empirical
result records, figure scripts, and LaTeX paper sources for "Dream Cities: Measuring World-Model Exploitation Against an
Exact Simulator" (HyperPrior Research, London). Correspondence via hyperprior.net. Start with `REPRODUCE.md`: it gives,
stage by stage, each command, its inputs, its outputs, and the sections and tables of the paper that read them. Compute
is reported in `results/analysis/compute_summary.md` (H200-equivalent GPU hours).

## Licences
- `hpr-dream/` (domain-general world-model audit library; contains no simulator code): Apache-2.0, `hpr-dream/LICENSE`
  and `hpr-dream/NOTICE`; a copy is at `LICENSE-Apache-2.0`.
- `engine/` (patched Micropolis C++ engine sources, C shim, and replay verifier) and `code/` (Micropolis adaptor,
  bit-exact replay oracle, data generator, task harness, search/RL runners, and test suite): GPL-3.0 with Electronic
  Arts' additional terms under section 7, `engine/LICENSE`; a copy is at `LICENSE-GPL-3.0-with-EA-terms`. Modifications
  are documented in `engine/MODIFICATION_NOTICE.md`. "Micropolis" is a registered trademark of Micropolis Corporation
  (Micropolis GmbH), used under the Micropolis Public Name License (`engine/MicropolisPublicNameLicense.md`). Nothing
  here is distributed under the SimCity mark, and nothing claims affiliation with Electronic Arts.
- `results/`, `data/`, `figures/`, `paper/`, and `REPRODUCE.md`: Creative Commons Attribution 4.0 International
  (CC BY 4.0), `LICENSE-CC-BY-4.0`.
- `template/` holds the HyperPrior document class and wordmark, which are not licensed for reuse, and the XCharter
  fonts under their own licence (`template/fonts/LICENCE.txt`).

## Rewritten for release
Paths, host names, user names, and local hardware identifiers in this tree were sanitised for release by deterministic
rules: the repository path as `<repo>`, its external cache as `<cache>`, home directories as
`<home>`, temporary directories as `<tmp>`, local hosts as `host-a` and `host-b`, cloud nodes as `rented-node`, and
local/cloud GPU identifiers as `gpu-a`, `gpu-b`, and `rented-gpu`. Every numeric field of every rewritten JSON record
was verified identical before and after rewriting. Stored file digests inside historical result records and
`paper/numbers_manifest.json` refer to pre-sanitisation source files; the files whose text changed during sanitisation
are:
- `code/dc/tasks.py`: tasks_code_sha256 (audit, replanning and analysis configs)
- `code/dc/audit.py`: git.file_sha256 (audit configs)
- `code/scripts/run_audit.py`: git.file_sha256 (audit configs)
- `code/scripts/gen_builder_pool.py`: git.file_sha256 (audit configs)
- `code/dc/replan.py`: replan_code_sha256 and git.file_sha256 (replanning configs)
- `code/scripts/run_replan.py`: git.file_sha256 (replanning configs)
- `code/dc/behaviour.py`: git.file_sha256 (replanning configs)
- `code/dc/fast.py`: fast.source_sha (emulator judges)
- `data/tasks_v2_H24.json`: tasks_sha256
- `data/tasks_v2x_H24.json`: tasks_sha256
- `data/replan_order_v1.json`: order_sha256 (replanning configs)

## Not distributed
Neural world-model weights: because whether neural weights trained on trajectories of a GPL simulator constitute derived
works remains legally untested, `REPRODUCE.md` and `paper/data/ckpt_meta/` provide exact SHA-256 digests instead.
Trained policies (whether trained inside world models or on the engine) are likewise not distributed.
