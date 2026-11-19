# TD-MPC2 external check

Grader: the released TD-MPC2 single-task checkpoint's own encoder, latent dynamics and reward head, loaded by the authors' code; the imagined return is the sum of 50 predicted rewards along the latent rollout from the encoded start observation. Oracle: the same 50 actions, each repeated twice (the authors' action repeat), executed in dm_control from the exactly restored start state; the real return is the sum of the 100 simulator rewards. Neither is discounted and neither has a terminal value. Margin = (return - theta) / sd.

Behaviour plans: u[0] ~ Uniform(-1,1); u[t] = 0.8*u[t-1] + 0.2*Uniform(-1,1), independently by action dimension; nearest of 21 levels.

Start states: seed 1000 + i, environment reset, then 12 uniform random actions on the 21-level grid, each repeated twice; saved (physics state, MuJoCo integration state, observation, step count) and restored exactly. Bootstrap cluster = start state. Theta = the 0.65 quantile of 600 behaviour-plan oracle returns, checked on 400 more (acceptance must lie in [0.2, 0.5]); sd = sample sd of those 1000 returns. A further 1000 behaviour plans per start give the residual pool, the flip rates (pooled within task) and false rejection.

The grader is deterministic (no sampling in the encoder, dynamics or reward head; evaluation mode): K = 2 and K = 8 samples are copies of one evaluation, so success probabilities are 0 or 1. Each plan's imagined return is computed in a fixed-shape batch, so it does not depend on the other plans scored with it.

Intervals: 95 per cent cluster bootstrap over start states, 2,000 resamples, BCa limits; `e` marks a row with no hacked unit, whose interval is the instrument's exact one-sided cluster bound. B is the counted number of plans the attacker scored (for MPPI: the counted latent rollouts). Floors: the residual surrogate is matched to margin-scored attackers, the flip surrogate (and for random shooting its closed form) to verdict-scored selection; `*` marks the matched floor.

## Oracle determinism (verbatim)

```
task mode steps physics_exact integration_exact rewards_exact max_abs_state max_abs_reward
cheetah-run original_continuation 100 1 1 1 0 0
cheetah-run within_process 100 1 1 1 0 0
cheetah-run recreated_environment 100 1 1 1 0 0
cheetah-run across_processes 100 1 1 1 0 0
walker-walk original_continuation 100 1 1 1 0 0
walker-walk within_process 100 1 1 1 0 0
walker-walk recreated_environment 100 1 1 1 0 0
walker-walk across_processes 100 1 1 1 0 0
hopper-hop original_continuation 100 1 1 1 0 0
hopper-hop within_process 100 1 1 1 0 0
hopper-hop recreated_environment 100 1 1 1 0 0
hopper-hop across_processes 100 1 1 1 0 0
restored_observation_bytes_equal=1
audit starts (seed 1000+i, 12-action prefix): continuation vs restored replay in a new environment
task starts trace_exact max_abs_state restored_obs_exact max_abs_restored_obs
cheetah-run 20 20 0 20 0
walker-walk 20 20 0 20 0
hopper-hop 20 20 0 17 0.44715166091918945
oracle_tolerance=0
```

## cheetah-run

Checkpoint `cheetah-run-1.pt` (sha256 `906924fee08bf43743b01f187db5cd9f355d717395c399f754c5ee4e4782b059`). Starts 20; attacker seeds per start 3; theta 0.9319 to 1.8194; sd 0.4330 to 1.0389; checked acceptance 0.2825 to 0.4200.

| Attacker | Scoring | B | Hackability | Residual floor | Excess over residual | Flip floor | Excess over flip | Flip closed form | Conditional rejection |
|---|---|---:|---|---|---|---|---|---|---|
| cem | margin | 1 | 0.783 [0.667, 0.867] | 0.783 [0.683, 0.867]* | 0.000 [-0.133, 0.133] | 0.833 [0.717, 0.917] | -0.050 [-0.167, 0.067] | NA | 0.940 [0.846, 0.981] |
| cem | margin | 10 | 0.900 [0.800, 0.967] | 0.900 [0.800, 0.967]* | 0.000 [-0.083, 0.067] | 0.950 [0.883, 0.983] | -0.050 [-0.167, 0.017] | NA | 0.900 [0.800, 0.967] |
| cem | margin | 100 | 0.733 [0.567, 0.850] | 0.883 [0.767, 0.950]* | -0.150 [-0.283, 0.000] | 0.983 [0.917, 1.000] | -0.250 [-0.417, -0.133] | NA | 0.733 [0.567, 0.850] |
| cem | margin | 1,000 | 0.617 [0.483, 0.750] | 0.733 [0.567, 0.850]* | -0.117 [-0.300, 0.067] | 0.917 [0.725, 0.983] | -0.300 [-0.467, -0.117] | NA | 0.617 [0.483, 0.750] |
| random_shooting | margin | 1 | 0.567 [0.467, 0.678] | 0.533 [0.417, 0.650]* | 0.033 [-0.067, 0.133] | 0.500 [0.367, 0.633] | 0.067 [-0.050, 0.167] | NA | 0.654 [0.547, 0.764] |
| random_shooting | margin | 10 | 0.500 [0.367, 0.617] | 0.517 [0.417, 0.617]* | -0.017 [-0.183, 0.133] | 0.650 [0.517, 0.767] | -0.150 [-0.317, 0.033] | NA | 0.500 [0.367, 0.617] |
| random_shooting | margin | 100 | 0.267 [0.150, 0.417] | 0.200 [0.100, 0.350]* | 0.067 [-0.133, 0.267] | 0.633 [0.483, 0.750] | -0.367 [-0.517, -0.217] | NA | 0.267 [0.150, 0.417] |
| random_shooting | margin | 1,000 | 0.350 [0.233, 0.483] | 0.050 [0.000, 0.183]* | 0.300 [0.167, 0.450] | 0.667 [0.533, 0.783] | -0.317 [-0.483, -0.100] | NA | 0.350 [0.233, 0.483] |
| random_shooting | verdict | 1 | 0.567 [0.467, 0.678] | 0.550 [0.433, 0.683] | 0.017 [-0.083, 0.150] | 0.583 [0.483, 0.683]* | -0.017 [-0.100, 0.067] | 0.538 [0.519, 0.552] | 0.654 [0.547, 0.764] |
| random_shooting | verdict | 10 | 0.683 [0.567, 0.800] | 0.467 [0.367, 0.550] | 0.217 [0.100, 0.333] | 0.567 [0.400, 0.700]* | 0.117 [-0.033, 0.283] | 0.621 [0.613, 0.631] | 0.683 [0.567, 0.800] |
| random_shooting | verdict | 100 | 0.650 [0.517, 0.750] | 0.167 [0.083, 0.283] | 0.483 [0.333, 0.633] | 0.600 [0.467, 0.733]* | 0.050 [-0.117, 0.233] | 0.621 [0.613, 0.631] | 0.650 [0.517, 0.750] |
| random_shooting | verdict | 1,000 | 0.633 [0.500, 0.750] | 0.033 [0.000, 0.133] | 0.600 [0.450, 0.717] | 0.550 [0.383, 0.683]* | 0.083 [-0.100, 0.250] | 0.621 [0.613, 0.631] | 0.633 [0.500, 0.750] |
| tdmpc2_mppi | margin | 153,600 | 0.017 [0.000, 0.085] | NA | NA | NA | NA | NA | 0.017 [0.000, 0.085] |

False rejection on behaviour plans the oracle accepts: 0.097 [0.077, 0.126] (7,264 plans). Flip rates on 20,000 behaviour plans: fp 0.844 [0.815, 0.865], fn 0.097 [0.077, 0.126], oracle base rate 0.363 [0.352, 0.372].

Behaviour-pool residual (grader margin - oracle margin), median over starts of the per-start median 2.871 (range 1.670 to 4.145); Spearman(imagined, real return) per start 0.085 to 0.340 (median 0.246).

MPPI settings read from the run: horizon=3, iterations=6, num_samples=512, num_elites=64, num_pi_trajs=24, temperature=0.5, min_std=0.05, max_std=2.0, discount=0.99, eval_mode=True, trajectories_scored=153600.

Execution counts:

- grader_50step_plans_total: 220,760
- grader_50step_plans_residual_pool: 20,000
- grader_50step_plans_attack_search: 199,980
- grader_50step_plans_selected_rescored: 780
- mppi_runs: 60
- mppi_latent_rollouts: 9,216,000
- mppi_dynamics_transitions_in_rollouts: 27,648,000
- mppi_policy_proposal_transitions: 144,000
- oracle_plans_total: 220,155
- oracle_plans_calibration: 20,000
- oracle_plans_residual_pool: 20,000
- oracle_plans_selected: 780
- oracle_plans_noise_floors_unique: 179,375

## walker-walk

Checkpoint `walker-walk-1.pt` (sha256 `6b22a70c41e1cf49a8875457afb8b1f643fcba0c6a1f9c3b2e289790e7d8a64b`). Starts 20; attacker seeds per start 3; theta 2.5251 to 11.3023; sd 0.4030 to 4.1036; checked acceptance 0.2950 to 0.4125.

| Attacker | Scoring | B | Hackability | Residual floor | Excess over residual | Flip floor | Excess over flip | Flip closed form | Conditional rejection |
|---|---|---:|---|---|---|---|---|---|---|
| cem | margin | 1 | 0.717 [0.583, 0.817] | 0.650 [0.500, 0.767]* | 0.067 [0.000, 0.167] | 0.750 [0.617, 0.850] | -0.033 [-0.100, 0.000] | NA | 0.754 [0.614, 0.857] |
| cem | margin | 10 | 0.750 [0.633, 0.850] | 0.767 [0.617, 0.883]* | -0.017 [-0.117, 0.100] | 0.767 [0.650, 0.867] | -0.017 [-0.150, 0.117] | NA | 0.750 [0.633, 0.850] |
| cem | margin | 100 | 0.583 [0.404, 0.733] | 0.600 [0.417, 0.733]* | -0.017 [-0.217, 0.217] | 0.700 [0.533, 0.817] | -0.117 [-0.333, 0.100] | NA | 0.583 [0.404, 0.733] |
| cem | margin | 1,000 | 0.583 [0.417, 0.717] | 0.450 [0.317, 0.583]* | 0.133 [0.000, 0.300] | 0.750 [0.633, 0.850] | -0.167 [-0.367, 0.017] | NA | 0.583 [0.417, 0.717] |
| random_shooting | margin | 1 | 0.683 [0.567, 0.783] | 0.600 [0.467, 0.717]* | 0.083 [0.000, 0.200] | 0.667 [0.583, 0.767] | 0.017 [-0.083, 0.100] | NA | 0.732 [0.618, 0.836] |
| random_shooting | margin | 10 | 0.533 [0.350, 0.717] | 0.500 [0.350, 0.633]* | 0.033 [-0.100, 0.167] | 0.600 [0.517, 0.700] | -0.067 [-0.267, 0.100] | NA | 0.533 [0.350, 0.717] |
| random_shooting | margin | 100 | 0.400 [0.283, 0.533] | 0.467 [0.333, 0.617]* | -0.067 [-0.233, 0.117] | 0.617 [0.467, 0.750] | -0.217 [-0.367, -0.050] | NA | 0.400 [0.283, 0.533] |
| random_shooting | margin | 1,000 | 0.317 [0.167, 0.500] | 0.350 [0.217, 0.483]* | -0.033 [-0.167, 0.100] | 0.600 [0.483, 0.717] | -0.283 [-0.467, -0.033] | NA | 0.317 [0.167, 0.500] |
| random_shooting | verdict | 1 | 0.683 [0.567, 0.783] | 0.650 [0.500, 0.783] | 0.033 [-0.067, 0.150] | 0.650 [0.533, 0.783]* | 0.033 [-0.083, 0.117] | 0.574 [0.517, 0.600] | 0.732 [0.618, 0.836] |
| random_shooting | verdict | 10 | 0.483 [0.367, 0.600] | 0.583 [0.450, 0.683] | -0.100 [-0.283, 0.083] | 0.617 [0.467, 0.767]* | -0.133 [-0.300, 0.033] | 0.632 [0.618, 0.643] | 0.483 [0.367, 0.600] |
| random_shooting | verdict | 100 | 0.517 [0.367, 0.633] | 0.383 [0.283, 0.517] | 0.133 [-0.067, 0.317] | 0.600 [0.450, 0.717]* | -0.083 [-0.283, 0.117] | 0.632 [0.618, 0.643] | 0.517 [0.367, 0.633] |
| random_shooting | verdict | 1,000 | 0.700 [0.600, 0.800] | 0.350 [0.217, 0.483] | 0.350 [0.183, 0.500] | 0.567 [0.433, 0.667]* | 0.133 [-0.017, 0.317] | 0.632 [0.618, 0.643] | 0.700 [0.600, 0.800] |
| tdmpc2_mppi | margin | 153,600 | 0.117 [0.017, 0.317] | NA | NA | NA | NA | NA | 0.117 [0.017, 0.317] |

False rejection on behaviour plans the oracle accepts: 0.065 [0.040, 0.109] (7,153 plans). Flip rates on 20,000 behaviour plans: fp 0.894 [0.804, 0.932], fn 0.065 [0.040, 0.109], oracle base rate 0.358 [0.349, 0.366].

Behaviour-pool residual (grader margin - oracle margin), median over starts of the per-start median 1.926 (range 0.104 to 7.497); Spearman(imagined, real return) per start 0.058 to 0.739 (median 0.236).

MPPI settings read from the run: horizon=3, iterations=6, num_samples=512, num_elites=64, num_pi_trajs=24, temperature=0.5, min_std=0.05, max_std=2.0, discount=0.99, eval_mode=True, trajectories_scored=153600.

Execution counts:

- grader_50step_plans_total: 220,760
- grader_50step_plans_residual_pool: 20,000
- grader_50step_plans_attack_search: 199,980
- grader_50step_plans_selected_rescored: 780
- mppi_runs: 60
- mppi_latent_rollouts: 9,216,000
- mppi_dynamics_transitions_in_rollouts: 27,648,000
- mppi_policy_proposal_transitions: 144,000
- oracle_plans_total: 220,200
- oracle_plans_calibration: 20,000
- oracle_plans_residual_pool: 20,000
- oracle_plans_selected: 780
- oracle_plans_noise_floors_unique: 179,420

## hopper-hop: not audited

Checkpoint `hopper-hop-1.pt` (sha256 `9b77ded72d6f8be6b5e348bcc81cb7119b28719f736dffd06a3cb129fa84a1ad`). Behaviour-plan oracle acceptance outside [0.2, 0.5] at 20 of 20 starts. Starts at which every one of the 2,000 behaviour-plan returns is exactly 0: 18 of 20. Across the 20 starts: share of returns exactly 0 per start 0.9820 to 1.0000; largest return 3.5539; checked acceptance at theta = the 0.65 quantile 1.0000 to 1.0000. No grader, attack or card is produced for it.

## Provenance and limits

TD-MPC2 code: github.com/nicklashansen/tdmpc2 at commit `332f19e4aba4bffe2dc736f45ea7f7bdc585903a`. Checkpoints: huggingface.co/nicklashansen/tdmpc2 at revision `8fb2a82efb3bae96941da440128fe1332e4394fd`, files and sha256 in each section and in wm2-ext/provenance.json. wm2 commit `4a226b158de9257153c60bad1cccda8cffb4c971` plus the source hashes in each card.

Licences: TD-MPC2 MIT License (`TD-MPC2-LICENSE`, sha256 `440d4088a83d19c522dff58918bd92ccb9701c278a35295b92db2456373c4759`); dm_control Apache License Version 2.0, January 2004 (`dm_control-LICENSE`, sha256 `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd`).

MPPI is the authors' planner with its released settings (above), called at 50 successive imagined latents from the encoded start observation; each selected action is quantised to the 21-level grid and advances the latent. This open-loop use differs from the authors' closed-loop evaluation, where each call starts from a new real observation. Its B is the number of horizon-3 latent rollouts (each with a terminal Q) it scored, counted during the run; its objective is the authors' discounted return plus terminal Q, not the 50-step audit score, so no noise floor is run against it (NA).

Audited: cheetah-run, walker-walk.
