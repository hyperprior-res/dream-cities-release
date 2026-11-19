# Held-out likelihood at half and final 

Generated 2026-11-12T13:00:42Z by `PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/fidelity_horizon.py`. Held-out likelihood: the total bound (ELBO) in nats per transition (`onestep.loglik_nats_per_transition.elbo`; higher is better) on the development selection (2,000 held-out transitions, every stored checkpoint) and the test selection (finals only). Final below half: the final's ELBO is lower than the half's on the development selection, the only selection holding both.

| run | half (samples) | final (samples) | dev ELBO, half | dev ELBO, final | final minus half | per cent of half | final below half | best stored (dev) | test ELBO, final |
|---|---|---|---|---|---|---|---|---|---|
| os_15m_small | 3,000,064 | 6,000,000 | -2947.8 | -3061.4 | -113.7 | -3.9 | yes | 3,000,064 (of 2 stored) | -3013.3 |
| sf_15m_small | 750,080 | 1,500,032 | -2999.6 | -3063.2 | -63.6 | -2.1 | yes | 750,080 (of 2 stored) | -3009.6 |
| os_15m_full | 3,000,064 | 6,000,000 | -2928.0 | -2779.1 | +148.9 | +5.1 | no | 6,000,000 (of 2 stored) | -2723.7 |
| sf_15m_full | 750,080 | 1,500,032 | -2843.0 | -2821.7 | +21.3 | +0.7 | no | 1,500,032 (of 2 stored) | -2762.4 |
| os_50m_small | 3,000,064 | 6,000,000 | -2951.8 | -3414.2 | -462.4 | -15.7 | yes | 3,000,064 (of 2 stored) | -3376.9 |
| sf_50m_small | 750,080 | 1,500,032 | -3159.4 | -3316.4 | -157.0 | -5.0 | yes | 750,080 (of 2 stored) | -3272.1 |
| os_50m_full | 3,000,064 | 6,000,000 | -2771.2 | -2664.2 | +107.0 | +3.9 | no | 6,000,000 (of 6 stored) | -2610.4 |
| sf_50m_full | 750,080 | 1,500,032 | -2719.3 | -2701.0 | +18.3 | +0.7 | no | 1,500,032 (of 2 stored) | -2648.5 |
| os_100m_small | 3,000,064 | 6,000,000 | -2905.3 | -3664.8 | -759.6 | -26.1 | yes | 3,000,064 (of 2 stored) | -3613.7 |
| sf_100m_small | 750,080 | 1,500,032 | -3280.2 | -3513.6 | -233.4 | -7.1 | yes | 750,080 (of 2 stored) | -3457.9 |
| os_100m_full | 3,000,064 | 6,000,000 | -2705.0 | -2574.4 | +130.6 | +4.8 | no | 6,000,000 (of 2 stored) | -2525.4 |
| sf_100m_full | 750,080 | 1,500,032 | -2626.5 | -2604.2 | +22.3 | +0.8 | no | 1,500,032 (of 2 stored) | -2552.0 |
| os_50m_full_s1 | 3,000,064 | 6,000,000 | -2780.0 | -2661.9 | +118.1 | +4.2 | no | 6,000,000 (of 2 stored) | -2607.2 |
| sf_50m_full_s1 | 750,080 | 1,500,032 | -2717.9 | -2700.1 | +17.8 | +0.7 | no | 1,500,032 (of 2 stored) | -2643.8 |
| os_50m_full_s2 | 3,000,064 | 6,000,000 | -2771.8 | -2665.9 | +105.9 | +3.8 | no | 6,000,000 (of 2 stored) | -2619.3 |
| sf_50m_full_s2 | 750,080 | 1,500,032 | -2725.4 | -2704.4 | +21.0 | +0.8 | no | 1,500,032 (of 2 stored) | -2657.4 |
| os_50m_cov (beside) | 3,000,064 | 6,000,000 | -2786.4 | -2663.9 | +122.4 | +4.4 | no | 6,000,000 (of 6 stored) | -2617.0 |

Of the 16 training runs with both (the 12 seed-0 runs and 4 seed replicas), 6 have a final below their half on the development selection.

- `os_50m_full`, development selection, every stored checkpoint: 1,200,000: -3032.5; 2,400,000: -2825.6; 3,000,064: -2771.2; 3,600,000: -2737.1; 4,800,000: -2688.4; 6,000,000: -2664.2.
- `os_50m_cov`, development selection, every stored checkpoint: 1,200,000: -3075.5; 2,400,000: -2853.9; 3,000,064: -2786.4; 3,600,000: -2738.2; 4,800,000: -2685.9; 6,000,000: -2663.9.
