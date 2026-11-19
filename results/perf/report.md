# Emulator inference speed pass 

Saved by the coordinator from the builder's hand-back (the builder could not write this file). GPU 1 (gpu-b) alone; model code at tag `ladder-v2`; rates are month-steps per second at decoding a, before -> after.

B10 hand-back. GPU 1 alone throughout; none of my processes is still running. Model code is tag ladder-v2 loaded through load_emulator. All rates are month-steps/s at decoding a, before → after. The raw records, each with the command that produced it, are in results/perf/bench/*.jsonl; results/perf/run_queue*.sh is the exact command sequence.
1. Audit judge (chunk 256, K=2): 15M 2,249→3,243 (×1.44), 50M 1,522→2,048 (×1.35), 100M 985→1,249 (×1.27). There is no trained 15M or 100M checkpoint, so those two use freshly initialised weights: the trunk cost does not depend on the weights, the sampling tail does.
2. RL step (200 envs, state on the card), against the default eager trunk / against the tag's compiled trunk: 15M 1,527 / 2,621 → 2,982; 50M 977 / 1,663 → 1,947 and 2,030 in two runs; 100M 634 / 1,051 → 1,207. That is ×1.90–2.08 against eager and ×1.14–1.22 against compiled. At 50M, 400 envs went 1,772→2,085 and 40 envs 1,278→1,534.
3. Profile (50M, 256 rows): the trunk is 88% of a step. Its GEMMs already run at 145 TFLOPS, 88% of the gpu-b's bf16 peak. The headroom was the memory passes around them (the bias+GELU pass alone was 25 of 148 ms), the host raster (+13% when moved to the card) and launch gaps. The sampling tail is 11% of the step, 13% after the changes.
4. The three levers (audit 50M, added one after another):
   - raster built on the card: +13.3% (1,522→1,725);
   - fc1 and its tanh-GELU as one cuBLASLt GEMM with a bias-GELU epilogue (same weights, bf16 operands, fp32 accumulation): +16.2% (→2,004; trunk 129.6→106.5 ms per step);
   - CUDA graphs for the trunk: +2.2% at 256 rows, +11% at 16 rows, +20% at RL's 40 slots.
5. Test (a), 2,000 held-out dev transitions, same inputs and z. The tolerance is the tag's own eager-vs-compiled disagreement; the criterion, fixed before the run, was fast-vs-eager ≤ 2× that at the max and at p99.9. 50M: 39/39 heads pass. Untrained 15M and 100M: 38/39 each. The two misses are summed per-transition log-likelihoods: 15M eighth overlays (p99.9 ratio 2.10) and 100M build cost (max ratio 2.16). Every per-cell head parameter passes. CPU tests: 7 pass in about 30 s, including 24-month tiny-model rollouts identical element for element and the raster exactly equal to grammar.raster_batch.
6. Test (b), dev fidelity, 4 noise seeds per variant on GPU 1, plus one fast run at another batch layout: fast vs the eager tag is within 2 SE on 18/19 rows. The tag's own compiled trunk vs its eager trunk scores 17/19, and fast vs the compiled tag 18/19. The one row fast misses (ind_valve one month, −0.0012) is also missed by the tag's compiled trunk (−0.0010).
7. The literal criterion  fails for fast on 12/19 rows. The tag fails it too: re-run on GPU 1 it is within on only 8/19 against the seed 0, and its compiled trunk on 6–7/19 against its eager trunk. One difference is too small a noise estimate.
8. audit.py owner: line 844 `self.model.compile_trunk(dynamic=False)` becomes `fast.accelerate(self.model)`. Line 813 becomes `return fast.raster_rows(plans[:, h], device)`. Your decision: also add `fast.describe(self.model)` to describe(); this changes the judge description, so instances already computed are recomputed rather than mixed.
9. rl_adaptor.py owner: in EmulatorBackend.__init__, `fast.accelerate(self.model)` on CUDA, with compile_trunk=False, exactly as the comment at line 203 says. The judge shares the model, so its verdicts get it too. Two caveats: graphed trunk outputs are overwritten by the next trunk call (sample_next and log_prob never keep them), and accelerate raises dynamo's cache_size_limit to 64 globally.
10. Tried and not adopted:
   - Compiled sampling tail: +2.4% audit, +2.7% RL, but refused. With identical trunk output in, it draws the same number of random numbers but assigns them differently (5.6% of half-overlay cells differ). `accelerate` cannot reach it.
   - Chunk 512: +0.6% for the tag, +3.5% for fast.
   - Graphs above 256 rows: no gain (2,120 with, 2,126 without), and two large graphs ran out of the 24 GB card, so they are switched off above 256 rows.
11. Largest lever still open, and it needs your yes because it changes which draws go to which rows: a 144-row bucket for CEM's 400-row generations (now padded to 512). It raises throughput on CEM calls by 26% (tag 1,202→1,514, fast 1,610→2,028); CEM is 34% of a checkpoint, so about 7% overall. The tail is now 13% of a fast step and only a rewrite that keeps the draw order can take it.
12. Flags: (i) the harness refused my writing results/perf/report.md, so the detail is below. (ii) audit.py switched from overlay "mean" to the model's default decoding at 05:04Z, during my run. All the benches above use the new decoding; the early overlay-mean numbers are in bench/speed_overlay_mean_prelim.jsonl. (iii) The scratch 15M and 100M checkpoints take 472 MB in <cache>/perf and can be deleted.

--- Detail for results/perf/report.md (I could not write it) ---
Files (all new, nothing committed): <repo>/code/dc/fast.py, <repo>/code/scripts/bench_fast.py, <repo>/code/tests/test_fast.py, <repo>/results/perf/. Nothing had to change inside model.py, so results/perf/patches is empty. accelerate() replaces only the instance's `_trunk_fn`, the hook compile_trunk uses. It refuses to run if the loaded package's Trunk.forward / Block.forward source differs from the ladder-v2 text it restates (sha256 check; ladder-v1 matches too).

Generated outputs in results/perf:
- bench/speed_table.md: every speed configuration, built from the log by `bench_fast.py table`.
- equiv_{15m,50m,100m}.json: every head, three comparisons (compiled vs eager, fast vs eager, fast vs compiled), plus the share of sampled elements that differ under the same seed. Example at 50M: tile_index differs in 1.60e-3 (compiled vs eager) and 1.62e-3 (fast vs eager) of elements.
- fidelity_seeds_gpu1.md, fidelity_seeds_control_tagc_vs_tag.md, fidelity_seeds_fast_vs_tagc.md, fidelity_seeds_gpu1_and_b3.md .
- fidelity_dev*/: the evaluation JSONs. The single-seed fidelity_check_seed{1,2,3}.md files hold tagc-vs-tag, because the tagc runs overwrote the fast-vs-tag versions.
- profile_timers_*.txt, results/perf/logs/profile_*_a.log, profile_kernels_50m_b256_mean_compiled.txt, trunk_flops.txt (15M/50M/100M trunk: 11.15 / 32.14 / 66.62 GFLOP per sample; 32.14 at 50M is 28.82 in GEMMs), microbench_block.txt.

Profile of the tag, 50M, 256 rows (timers, decoding a): sample_next 146.7 ms, trunk 129.6, tail 16.0 (second stage 5.1, third stage 3.0, overlays 2.5, Bernoullis 1.4, categorical 0.9), cond_input 0.7. The host raster for 256 rows took 41.8 ms; the audit builds it per plan, about half that. Smaller batches: at 16 rows the trunk is 56% of the step and the tail 40% (it is launch-bound). After fast, 256 rows: step 123.7 ms, trunk 106.5, tail 16.0.

Standard command shape (prefix `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 PYTHONPATH=code:hpr-dream .venv/bin/python`):
- code/scripts/bench_fast.py speed --path audit --size 50m --chunk 256 --variants tag,raster,fused,fast
- bench_fast.py speed --path rl --size 50m --envs 200 --variants tag-eager,tag,fast
- bench_fast.py equiv --size 50m --n 2000
- bench_fast.py fidelity --batch 32 --eval-seed s [--variants tag,tagc]
- bench_fast.py fidelity-seeds [--fast-name, --tag-name, --with-b3]
- bench_fast.py tailcheck --size 50m

Known weaknesses:
- Speed ratios are for the gpu-b; GPU 0 needs its own measurement.
- RL replicate runs vary by about 4% between processes.
- 15M and 100M use untrained weights.
- The fidelity check has n=4 per variant.
- Each CUDA graph keeps its memory for its lifetime: peak was 5.9 GB at chunk 256 against 7.7 GB for the tag.
