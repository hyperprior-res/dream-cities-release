# Sufficient observation: the ledger, and the proof 

2026-11-10. Branch `hpr/wm2-rebuild`. Raw outputs: `results/oracle/sufficiency/`
(`tables.md`, `derivability.md`, `summary.json`, `raw.npz`, `specs.json`, `run.log`).

## 1. Result

- **Ledger: 27 int64 entries** (`LEDGER_NAMES`, section 2.1) **plus 2 carried maps**: `terrain`
  (`terrainDensityMap`, 30 x 25 uint8) and `com_rate` (`comRateMap`, 15 x 13 int16). Five more
  carried members are exact functions of the observation and are derived, not stored (section 2.3).
- **Long run**: 240 behaviour-mix trajectories of 36 months from 48 start states (16 train/bundled,
  16 train/generated, 16 held-out/generated), 120 with disasters off and 120 with disasters on (48 of them in a
  stress set with two forced disasters each), transitions at t = 0..24 = **6,000 transitions**, each
  with a 12-month continuation. Wall time 340 s on 8 workers.
- **Variant a** (everything restored including sprites, fresh `Engine()` per transition): every field
  of the extended observation, the generator state, the sprite list and the dynamic hash identical in
  **6000/6000 at month 1 and 6000/6000 at every month of the 12-month continuation**. Round trip
  (restore, read back) 6000/6000.
- **Variant a_full** (a, plus the members nothing in the update reads: graph histories etc.):
  `mc_hash_full` identical **6000/6000** at month 1 and at every month.
- **Variant b** (sprites not restored): 4196/6000 transitions differ outside the sprite list (all
  from month 1); 0 of the 1734 transitions without sprites at t differ; 4196 of the 4266 with
  sprites do. Split by rail / seaport / airport in section 4.2.
- **Variant c** (re-seeded after the restore): the fields that never differ across 3 re-seedings of
  the true run (global one-month set: tax, city time, `sim_cycle`, `sprite_cycle`, `disasters`,
  `initial_eval`, the three `*_hist1`, the three caps, `fire_fund`, `auto_budget`) match in
  **5999/6000**; the one miss (`fire_fund`, one transition) is reproduced by the true run re-seeded
  with the same seed. Control: restored-and-re-seeded run identical to the true run re-seeded with
  the same seed in **6000/6000** (month 1 and all 12 months).
- **Every ledger entry and both maps earn their place**: left at its reset value, each one changes
  other fields of the next 12 months in the long run (from 5 transitions for `fire_pop` to 6000 for
  `res_hist0`; table in section 4.4), and targeted tests show `fire_pop` and `auto_budget` on built
  cases.
- **Nothing else moved**: `results/oracle/bundled_hashes.npy` sha256 `cf5997cf...3683bbe6`,
  unchanged and reproduced by the new library; all 87 tests under `code/tests/` pass (75 existing,
  12 new).
- **Not closed**: none for exactness. The sprite list is outside the extended observation; variant b
  measures what that costs. `city_center_x/y` are kept although they equal the zone centre of the
  observed tiles at 8880/8880 behaviour-mix boundaries (section 4.6).

## 1.1 What was built

| file | change |
|---|---|
| `engine/c_api.cpp` | additions: `enum LedgerIndex`; `mc_get_ledger` (ledger + 2 maps), `mc_get_rng` (64-bit generator state), `mc_get_sprites` (sprite list in list order, 25 int32 per sprite incl. which sprite the engine keeps per type), `mc_hash_dynamic`, `mc_ledger_len`, `mc_sprite_fields`, `mc_aux_len`; test only: `mc_test_get_aux`, `mc_test_restore`. Existing functions unchanged. |
| `code/dc/engine.py` | additions: `LEDGER_NAMES`, `NUM_LEDGER`, `LG`, `LEDGER_ALL`, `TERRAIN_SHAPE`, `COM_RATE_SHAPE`, `SPRITE_FIELDS`, sprite type constants; `Obs.ledger`, `Obs.terrain`, `Obs.com_rate` (default None, after the five existing fields); `Engine.observe()` fills them; `Engine.ledger()`, `rng_state()`, `sprites()`, `hash_dynamic()`; test only: `Engine._test_aux()`, `Engine._test_restore(obs, rng_state, sprites=None, *, aux, ledger_mask, map_mask)`. The 20 scalars, their order and every existing array are unchanged. |
| `code/dc/oracle.py` | additions: `Replay.ledger` (H+1, 27) int64 beside `scalars`, filled by `replay` for `record="scalars"` and `"full"`. Row 0 is read after `set_disasters` (see 6.2). Replay order untouched. |
| `code/tests/test_observation_sufficient.py` | 12 tests, 0.7 s. |
| `code/scripts/check_sufficiency.py` | the long run (variants a, a_full, b, c, ablations, stress set) and `--derivability`. |
| `engine/libmicropolis.so` | rebuilt with the Makefile's compiler command into a temporary file and moved into place, because running processes (`run_audit.py` and its workers) had the library mapped; `make -C engine` now reports nothing to do. |

The restore is reached only through `Engine._test_restore`; the comment at its definition (both
files) says it is never called by `dc.oracle`, the data generator or any experiment, and
`test_test_restore_used_only_by_the_sufficiency_test` greps the code tree (`.py .cpp .h .c .sh .js`,
Makefiles; outside `legacy/`, `data/`, `results/`, the venv and caches): the four names appear only
in `engine/c_api.cpp`, `code/dc/engine.py` and the two B7 files.

## 2. The carried state, from the source

Protocol (`dc.engine`, `dc.oracle`): speed 1, one pass, level easy, auto-budget and auto-bulldoze on,
disasters on or off; per month `Engine.apply` (tax, funding, tool calls), an optional forced disaster,
then `mc_step_month`, which ticks until four city-time units have passed and `phaseCycle` is back to 0
(`engine/c_api.cpp:164`). A month is therefore 4 cycles of 16 phases (`simulate.cpp:159-277`), and at
speed 1 the simulator runs on one tick in five (`simulate.cpp:115-121`), about 320 ticks a month; the
sprites move on every tick (`micropolis.cpp:1013-1037`, `sprite.cpp:562`). Line numbers are in
`engine/src/` unless a file is named.

Two facts about the clock that the table relies on. `simCycle` is 0 at the load (`simulate.cpp:291`)
and grows by 4 a month, wrapping at 1024, so it is 0 mod 4 at every boundary: cycles 1 and 3 of a month
are odd and cycles 2 and 4 even; `setValves` and the power and pollution scans run in cycles 2 and 4
only (`simulate.cpp:175, 235, 245`). The monthly census (`take10Census`, `simulate.cpp:198`) runs in the
one cycle of the month in which `cityTime % 4 == 0`; which cycle that is depends on the city time at
the load (fixed for a trajectory, not observable from one month).

### 2.1 The ledger (27 entries, `LEDGER_NAMES` in `code/dc/engine.py`, `enum LedgerIndex` in `engine/c_api.cpp`)

| # | entry | member, type, range | written | read in a later month, before being rewritten | why the observation does not determine it |
|---|---|---|---|---|---|
| 0 | `sim_cycle` | `simCycle`, short, 0..1023 (0 mod 4 at boundaries) | `simulate.cpp:163` (phase 0), `:291` (load) | `setValves` gate `:175`; `decRateOfGrowthMap` every 5th cycle `:215`; power, pollution, crime, density, fire scans `:235-269` | counts cycles since the load: city time minus the city time at the load, which is not observed |
| 1 | `sprite_cycle` | `spriteCycle`, short (wraps) | `sprite.cpp:570` (every tick) | train, helicopter, airplane, explosion cadence `sprite.cpp:652, 790, 817, 1319`; `speedCycle` is derived from it | counts ticks since the reset in `init()` |
| 2 | `disasters` | `enableDisasters`, 0/1 | `utilities.cpp:319` via `Engine.set_disasters` | meltdown `simulate.cpp:1477`; `doDisasters` `disasters.cpp:110`; aircraft and bus collisions `sprite.cpp:839, 1607` | a trajectory setting, not in the observation |
| 3 | `initial_eval` | `doInitialEval`, 0/1 | set by the load `simulate.cpp:315`, cleared `:168` | `simulate.cpp:167`: a city evaluation at the first cycle after a load (draws from the generator, moves the score) | 1 only at the boundary right after a load |
| 4 | `total_pop` | `totalPop`, short | `setValves` `simulate.cpp:613` (cycles 2 and 4), load `:314` (= 1) | train generation `sprite.cpp:1847` (mapScan in cycle 1); tax `simulate.cpp:887-889` and evaluation `evaluate.cpp:125` when the yearly collection falls in cycle 1 | computed in cycle 4 from the cycle-3 census; the observation holds the cycle-4 census |
| 5-10 | `res_hist0/1`, `com_hist0/1`, `ind_hist0/1` | `resHist[0..1]` (resPop/8), `comHist[0..1]`, `indHist[0..1]`, short | `take10Census` `simulate.cpp:742-763` (once a month) | `setValves` `simulate.cpp:616, 626-628` reads index 1; index 0 becomes index 1 at the next census | index 1 is the census before last; index 0 equals the observed census only when the census runs in cycle 4 |
| 11-13 | `res_cap`, `com_cap`, `ind_cap` | `resCap`, `comCap`, `indCap`, 0/1 | `sendMessages` `message.cpp:146-166`, when `cityTime & 63` is 26, 28, 30 (every 16 months) | `setValves` `simulate.cpp:675-685`; score `evaluate.cpp:403-411` | set from the census of a cycle up to 16 months back |
| 14-15 | `need_hospital`, `need_church` | `needHospital`, `needChurch`, short, -1..1 | `take10Census` `simulate.cpp:778-801`; `makeHospital` `zone.cpp:294, 312` | `doHospitalChurch` `zone.cpp:159, 184`; `makeHospital` `zone.cpp:292, 298` | from hospital and church counts at the census cycle |
| 16-18 | `road_fund`, `police_fund`, `fire_fund` | `roadFund`, `policeFund`, `fireFund`, Quad | `collectTax` `simulate.cpp:884-886` (yearly) | `updateFundEffects` `simulate.cpp:916-932` on every `Engine.apply` (effect = max x spend / fund); `doBudgetNow` `budget.cpp:118-120` | requested at the last collection; equal to the spend scalars only when the auto-budget paid in full |
| 19 | `auto_budget` | `autoBudget`, 0/1 | `doBudgetNow` `budget.cpp:315` (switched off when the treasury cannot pay) | `budget.cpp:267` | an engine flag that stays off |
| 20 | `fire_pop` | `firePop`, short | `mapScan` `simulate.cpp:975`, cleared `:696` | `getFireSeverity` `evaluate.cpp:375` in the evaluation of the first cycle after a load (`simulate.cpp:169`, before `clearCensus`) | fire tiles counted while the scan ran; fires spread and go out during the scan |
| 21-22 | `city_center_x`, `city_center_y` | `cityCenterX/Y`, short | `populationDensityScan` `scan.cpp:177-183` (phase 14) | `computeComRateMap` `scan.cpp:591` in cycle 1 (it runs before the centre is updated, `scan.cpp:173`), land value `scan.cpp:275` | centre of the zone tiles at phase 14 of the last cycle |
| 23-24 | `pollution_max_x`, `pollution_max_y` | `pollutionMaxX/Y`, short | pollution scan `scan.cpp:314-318`, ties broken by the generator | monster target `sprite.cpp:228-229, 1935-1936` | tie-break draws from the generator |
| 25 | `flood_count` | `floodCount`, short, 0..30 | `makeFlood` `disasters.cpp:369`; minus 1 per cycle `:102-103` | `doFlood` `disasters.cpp:390` (spread or recede) | not visible in the tiles |
| 26 | `abs_dist` | `absDist`, int | `getDir` `sprite.cpp:510` | helicopter `sprite.cpp:747, 758`; airplane `:833` (read without a fresh `getDir` on 4 ticks in 5); monster `:1054, 1120` | scratch value left by the last sprite that called `getDir` |

### 2.2 Carried maps that are not observed (`Obs.terrain`, `Obs.com_rate`)

| map | type | written | read in a later month | why not a function of the observation |
|---|---|---|---|---|
| `terrainDensityMap` | (30, 25) uint8 | `smoothTerrain` `scan.cpp:464-507`, at the end of each pollution scan (`scan.cpp:328`) | land-value equation `scan.cpp:277` in the next pollution scan (cycle 2 of the next month) | computed from the tiles at the last scan; tiles change before it is read (growth, fire, the next month's tool calls) |
| `comRateMap` | (15, 13) int16 | `computeComRateMap` `scan.cpp:585-597`, called at `scan.cpp:173` before the centre is updated | commercial growth `zone.cpp:905` (cycle 1 of the next month) | a function of the city centre one population scan earlier |

### 2.3 Carried members that are functions of the observation (derived by the restore; no entry)

| member | written | read | derived as |
|---|---|---|---|
| `cityPop` | `mc_step_month` (`engine/c_api.cpp:167`); `evalInit` at the load (`evaluate.cpp:151`) | `doPopNum` `evaluate.cpp:196-205` (migration term of the score `:442-452`) | the population scalar; 0 while `initial_eval` = 1 |
| `crimeAverage` | `crimeScan` `scan.cpp:450` | `doProblems` `evaluate.cpp:262` | mean crime over blocks with land value > 0 |
| `landValueAverage` | pollution scan `scan.cpp:293` | tax `simulate.cpp:887`; `evaluate.cpp:264` | mean land value over blocks with land value > 0 |
| `pollutionAverage` | pollution scan `scan.cpp:323` | monster chance `disasters.cpp:148`; `evaluate.cpp:263` | mean pollution over blocks with pollution > 0 |
| `speedCycle` | `simFrame` `simulate.cpp:115` | which ticks run the simulator `simulate.cpp:119` | `spriteCycle` mod 1024 (both count ticks, both zeroed by `init()`) |

The overlays are the engine's maps (the averages are taken over the same scan's output, and nothing
writes those maps between the scan and the boundary), so these are exact; the test checks them by
restoring with them computed this way.

### 2.4 Excluded, and why

Read by nothing in the monthly update (graphs, display, messages):

| members | written | read only by |
|---|---|---|
| `resHist[2..239]`, `comHist[2..239]`, `indHist[2..239]`, `moneyHist`, `crimeHist`, `pollutionHist` | `take10Census` / `take120Census` `simulate.cpp:742-772, 819-843` | the graphs (`graph.cpp`), the shift itself; `setValves` reads index 1 only |
| `crimeRamp`, `pollutionRamp` | `simulate.cpp:765-769` | `crimeHist[0]`, `pollutionHist[0]`, `miscHist[10..11]` |
| `cashFlow` | `collectTax` `simulate.cpp:869, 891` | `moneyHist[0]` `simulate.cpp:771` |
| `miscHist` | `setValves` `simulate.cpp:595-609` | the loader (`simLoadInit` `simulate.cpp:468-504`) and `saveFile`; never within a trajectory |
| `cityTaxAverage` | `simulate.cpp:173, 882` | `simulate.cpp:880` into a local `z` that is never used |
| `totalPopLast` | `simulate.cpp:612` | nothing |
| `cityYes`, `problemVotes`, `problemOrder`, `cityAssessedValue`, `cityScoreDelta` | `evaluate.cpp` | the evaluation window |
| `cityClass` | `doPopNum` `evaluate.cpp:205` | `miscHist[16]`; `doScenarioScore` (scenarios only) |
| `trafficAverage` | `evaluate.cpp:343` | messages `message.cpp:232`; `doScenarioScore` |
| `cityPopLast`, `categoryLast`, `totalZonePop` | `message.cpp` | messages |
| `externalMarket` | `simulate.cpp:426, 468` | `miscHist[1]` |
| `crimeMaxX/Y` | `scan.cpp:439` | nothing |
| `mop` | the loader | nothing |
| UI state: `valveFlag`, `censusChanged`, `evalChanged`, `mustDrawBudget`, `mustUpdateFunds`, `mustUpdateOptions`, `newMap`, `newMapFlags`, `mapSerial`, `cityTimeLast` and the other `*Last` fields, `blinkFlag` (wall clock), `cityMonth`, `cityYear`, `startingYear`, `resHist10Max` and the other graph maxima, `simLoops`, `simPass`, `cityName`, `cityFileName`, sound and message state | `update.cpp`, `graph.cpp`, `micropolis.cpp` | the user interface; the native callbacks are no-ops (`callback.cpp`) |

Constant under the protocol: `phaseCycle` = 0 and `initSimLoad` = 0 at every boundary; `newPower` =
true (set at the load and by every power scan, never cleared); `taxFlag` = false; `autoBulldoze` =
true; `gameLevel` = 0; `simSpeed` = 1; `simPasses` = 1; `donDither` = 0 (the dithering branches of the
smoothers never run, `scan.cpp:466, 570, 577`); `faith` = 0; `heatSteps` = 0; `doAnimation` = true;
`scenario`, `disasterEvent`, `scoreType` = none and `disasterWait`, `scoreWait` = 0 (the loader sets no
scenario, `fileio.cpp:387`, `simulate.cpp:540-545`).

Rewritten before the next month reads them: the census counters cleared at phase 0 of every cycle
(`clearCensus` `simulate.cpp:692-721`) and read in the same cycle (`railTotal`, the zone counts,
`hospitalPop`, `churchPop`, `stadiumPop`, `policeStationPop`, `fireStationPop`, `seaportPop`,
`airportPop`); `fireStationMap` and `policeStationMap` (cleared at phase 0); the power and traffic
stacks and `tempMap1/2/3` (reset or fully rewritten before use); `roadEffect`, `policeEffect`,
`fireEffect` (recomputed from spend and fund by every `Engine.apply`, `simulate.cpp:912-933`);
`roadPercent`, `policePercent`, `firePercent` (the action); `roadValue`, `policeValue`, `fireValue`
(inside `doBudgetNow`); `cityPopDelta` (inside one evaluation); `trafMaxX/Y` (inside one call,
`traffic.cpp:187-195`). Mutable static locals: only `simHeat`'s accumulator (`micropolis.cpp:810`),
which runs only when `heatSteps` > 0; the other non-const statics are tables that are never written.

Observed already (the 20 scalars, the tile map, the overlays) and read by the next month:
`resPop`, `comPop`, `indPop` (by `setValves` before the census is cleared), `poweredZoneCount` and
`unpoweredZoneCount` (by the evaluation after a load), the funds, tax, valves, city time, score, the
three spend values, and every observed map.

The generator (`nextRandom`, 64-bit, `random.cpp:107-111`) and the sprite list are passed beside the
extended observation (`Engine.rng_state()`, `Engine.sprites()`), not in it.

## 3. The test

Per trajectory (`check_sufficiency.process`): the behaviour policy is played with
`dc.behaviour.rollout_behaviour` (its plan is the action log); the plan is replayed with the oracle's
protocol in an instrumented loop that snapshots every boundary (extended observation, generator
state, sprite list, `mc_hash_dynamic`, `mc_hash_full`, the aux members); the loop's `mc_hash_full`
trajectory must equal the rollout's at every boundary (checked, 240/240). For each t = 0..24, with A
the true snapshots at t+1..t+12:

- **a**: a new `Engine()`; `_test_restore(obs_t, rng_t, sprites_t)`; read back and compare with the
  snapshot at t (round trip); then 12 months of the same actions (tool calls, forced disaster) and
  compare each month with A.
- **a_full**: as a in a reused instance, also restoring the aux members, and compare `mc_hash_full`.
- **b**: restore without the sprite list.
- **c**: the true run is replayed from its start state to t and re-seeded with three seeds; a field
  is in the one-month (12-month) invariant set of the transition if all three re-seeded runs equal A
  on it at month 1 (at every month); the global set is the intersection over all 6000 transitions.
  The restored instance is re-seeded with a fourth seed and compared with A on those sets. Control:
  the true run re-seeded with that fourth seed, compared with the restored-and-re-seeded run.
- **ablation**: as a, with one ledger entry (or one map, or the derived members) left at the value the
  reset leaves (what `init()` produces: e.g. `sim_cycle` 0, `initial_eval` 1, `total_pop` 1, the
  histories 0, the funds 0, `auto_budget` 1, the centre (60, 50), `disasters` 0). An item earns its
  place if some other field differs from the true run.

Fields compared (63): tiles; the five half-resolution overlays; power grid; the three eighth-resolution
overlays; each of the 20 scalars; each of the 27 ledger entries; the two carried maps; generator
state; sprite list; `mc_hash_dynamic`; `mc_hash_full`. `mc_hash_dynamic` hashes everything
`mc_hash_full` does except the members of section 2.4 that nothing reads, plus `cityPop`,
`doInitialEval`, `speedCycle`, `spriteCycle`, `absDist`, the centre, the pollution maximum, every
sprite field and the per-type sprite pointer. It covers members that the restore does not set but
the month recomputes (census counters, effects, station maps), so it can only match after a step.

The stress set: 48 trajectories (one per start state) whose policy is wrapped to force a disaster at
months 2 and 13 (kinds cycle through fire, flood, earthquake, tornado, monster, meltdown); the
behaviour mix's own perturbations add forced disasters elsewhere (121 transitions have a forced
disaster in month t).

## 4. Results

The tables below are `results/oracle/sufficiency/tables.md` (run 2; run 1 had identical variant a, b,
c and month-1 ablation counts and a bug in the 12-month ablation column, fixed before run 2) and
`results/oracle/sufficiency/derivability.md`, pasted unchanged except for headings.

### 4.0 Run

trajectories: 240 (48 in the forced-disaster stress set); start states: 48 (train/bundled 16, train/generated 16, heldout/generated 16); months per trajectory: 36; transitions: 6000 (disasters off 3000, on 3000; t = 0..24); continuation: 12 months
transitions with sprites at t: 4266; with rail 3432, seaport 3735, airport 2604; with a forced disaster in month t: 121

Round trip (restore, then read back): extended observation identical in 6000/6000

### 4.1 Variants a, a_full and b, field by field (transitions identical, of 6000)

| field | a: month 1 | a: all 12 months | a_full: month 1 | a_full: all 12 | b: month 1 | b: all 12 |
|---|---|---|---|---|---|---|
| tiles | 6000 | 6000 | 6000 | 6000 | 1823 | 1812 |
| half:pop_density | 6000 | 6000 | 6000 | 6000 | 1850 | 1817 |
| half:traffic | 6000 | 6000 | 6000 | 6000 | 1842 | 1810 |
| half:pollution | 6000 | 6000 | 6000 | 6000 | 1842 | 1813 |
| half:land_value | 6000 | 6000 | 6000 | 6000 | 1914 | 1812 |
| half:crime | 6000 | 6000 | 6000 | 6000 | 1834 | 1812 |
| power | 6000 | 6000 | 6000 | 6000 | 5429 | 4445 |
| eighth:growth | 6000 | 6000 | 6000 | 6000 | 1840 | 1817 |
| eighth:fire_cov | 6000 | 6000 | 6000 | 6000 | 5980 | 5553 |
| eighth:police_cov | 6000 | 6000 | 6000 | 6000 | 5980 | 5488 |
| scalar:funds | 6000 | 6000 | 6000 | 6000 | 5737 | 2527 |
| scalar:tax | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| scalar:res_valve | 6000 | 6000 | 6000 | 6000 | 5383 | 4579 |
| scalar:com_valve | 6000 | 6000 | 6000 | 6000 | 3448 | 2232 |
| scalar:ind_valve | 6000 | 6000 | 6000 | 6000 | 5981 | 2622 |
| scalar:pop | 6000 | 6000 | 6000 | 6000 | 2051 | 1817 |
| scalar:res_pop | 6000 | 6000 | 6000 | 6000 | 2190 | 1817 |
| scalar:com_pop | 6000 | 6000 | 6000 | 6000 | 3436 | 1895 |
| scalar:ind_pop | 6000 | 6000 | 6000 | 6000 | 3499 | 2000 |
| scalar:city_time | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| scalar:score | 6000 | 6000 | 6000 | 6000 | 5717 | 2152 |
| scalar:tax_fund | 6000 | 6000 | 6000 | 6000 | 5892 | 2503 |
| scalar:road_spend | 6000 | 6000 | 6000 | 6000 | 5711 | 2141 |
| scalar:fire_spend | 6000 | 6000 | 6000 | 6000 | 5989 | 5755 |
| scalar:police_spend | 6000 | 6000 | 6000 | 6000 | 5987 | 5738 |
| scalar:powered_zones | 6000 | 6000 | 6000 | 6000 | 5827 | 4887 |
| scalar:unpowered_zones | 6000 | 6000 | 6000 | 6000 | 5856 | 5077 |
| scalar:coal_plants | 6000 | 6000 | 6000 | 6000 | 5997 | 5973 |
| scalar:nuclear_plants | 6000 | 6000 | 6000 | 6000 | 5996 | 5957 |
| scalar:road_total | 6000 | 6000 | 6000 | 6000 | 2159 | 1818 |
| ledger:sim_cycle | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| ledger:sprite_cycle | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| ledger:disasters | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| ledger:initial_eval | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| ledger:total_pop | 6000 | 6000 | 6000 | 6000 | 2909 | 1817 |
| ledger:res_hist0 | 6000 | 6000 | 6000 | 6000 | 3589 | 1817 |
| ledger:res_hist1 | 6000 | 6000 | 6000 | 6000 | 6000 | 1817 |
| ledger:com_hist0 | 6000 | 6000 | 6000 | 6000 | 3702 | 1897 |
| ledger:com_hist1 | 6000 | 6000 | 6000 | 6000 | 6000 | 1905 |
| ledger:ind_hist0 | 6000 | 6000 | 6000 | 6000 | 3728 | 2000 |
| ledger:ind_hist1 | 6000 | 6000 | 6000 | 6000 | 6000 | 2013 |
| ledger:res_cap | 6000 | 6000 | 6000 | 6000 | 6000 | 5979 |
| ledger:com_cap | 6000 | 6000 | 6000 | 6000 | 6000 | 5987 |
| ledger:ind_cap | 6000 | 6000 | 6000 | 6000 | 6000 | 5996 |
| ledger:need_hospital | 6000 | 6000 | 6000 | 6000 | 5799 | 4250 |
| ledger:need_church | 6000 | 6000 | 6000 | 6000 | 5863 | 4518 |
| ledger:road_fund | 6000 | 6000 | 6000 | 6000 | 5701 | 2058 |
| ledger:police_fund | 6000 | 6000 | 6000 | 6000 | 5999 | 5940 |
| ledger:fire_fund | 6000 | 6000 | 6000 | 6000 | 6000 | 5958 |
| ledger:auto_budget | 6000 | 6000 | 6000 | 6000 | 6000 | 5997 |
| ledger:fire_pop | 6000 | 6000 | 6000 | 6000 | 5311 | 4508 |
| ledger:city_center_x | 6000 | 6000 | 6000 | 6000 | 5981 | 5679 |
| ledger:city_center_y | 6000 | 6000 | 6000 | 6000 | 5974 | 5701 |
| ledger:pollution_max_x | 6000 | 6000 | 6000 | 6000 | 3707 | 2113 |
| ledger:pollution_max_y | 6000 | 6000 | 6000 | 6000 | 3757 | 2018 |
| ledger:flood_count | 6000 | 6000 | 6000 | 6000 | 5993 | 5912 |
| ledger:abs_dist | 6000 | 6000 | 6000 | 6000 | 3687 | 3510 |
| map:terrain | 6000 | 6000 | 6000 | 6000 | 5185 | 4111 |
| map:com_rate | 6000 | 6000 | 6000 | 6000 | 5958 | 5515 |
| rng | 6000 | 6000 | 6000 | 6000 | 1901 | 1818 |
| sprites | 6000 | 6000 | 6000 | 6000 | 1771 | 1756 |
| hash_dynamic | 6000 | 6000 | 6000 | 6000 | 1744 | 1744 |
| hash_full | 0 | 0 | 6000 | 6000 | 0 | 0 |
| (of) | 6000 | 6000 | 6000 | 6000 | 6000 | 6000 |

variant a: every field of the extended observation and the dynamic hash identical at month 1 in 6000/6000; at every month of the continuation in 6000/6000
variant a_full: mc_hash_full identical at month 1 in 6000/6000; at every month in 6000/6000

### 4.2 Variant b by city kind

Variant b (sprites not restored): transitions with any difference in the extended observation without the sprite list (month 1 / within 12 months)

| city at t | transitions | with sprites at t | differ at month 1 | differ within 12 months |
|---|---|---|---|---|
| no rail, seaport or airport | 1650 | 16 | 16 | 16 |
| rail (any) | 3432 | 3427 | 3366 | 3366 |
| seaport (any) | 3735 | 3640 | 3619 | 3619 |
| airport (any) | 2604 | 2558 | 2539 | 2539 |
| rail, no seaport/airport | 594 | 589 | 540 | 540 |
| seaport or airport | 3756 | 3661 | 3640 | 3640 |
| all | 6000 | 4266 | 4196 | 4196 |

variant b, first month with a difference (transitions that differ within 12 months): m1: 4256, m2: 0, m3: 0, m4: 0, m5: 0, m6: 0, m7: 0, m8: 0, m9: 0, m10: 0, m11: 0, m12: 0

### 4.3 Variant c

Variant c (generator re-seeded after the restore).
fields that never differ across seeds in the true run at one month (all 6000 transitions, 3 re-seeds each): scalar:tax, scalar:city_time, ledger:sim_cycle, ledger:sprite_cycle, ledger:disasters, ledger:initial_eval, ledger:res_hist1, ledger:com_hist1, ledger:ind_hist1, ledger:res_cap, ledger:com_cap, ledger:ind_cap, ledger:fire_fund, ledger:auto_budget
over the 12-month continuation: scalar:tax, scalar:city_time, ledger:sim_cycle, ledger:sprite_cycle, ledger:disasters, ledger:initial_eval
restored and re-seeded run matches the true run on every field of the global one-month set in 5999/6000; on the global 12-month set in 6000/6000
control: restored-and-re-seeded run identical to the true run re-seeded with the same seed, every field and the dynamic hash, at month 1 in 6000/6000; at every month in 6000/6000
per-transition sets (fields equal across the 3 re-seeded true runs of that transition): match at month 1 in 4514/6000; over 12 months in 5105/6000; mean set size 40.4 fields at month 1, 27.8 over 12 months
the true run re-seeded with that same seed leaves its per-transition set in the same transitions: month 1 6000/6000 agree, 12 months 6000/6000 agree

| field | invariant across seeds at month 1 (transitions) | c identical at month 1 | invariant over 12 months | c identical over 12 months |
|---|---|---|---|---|
| tiles | 1 | 4 | 0 | 0 |
| half:pop_density | 1 | 18 | 0 | 0 |
| half:traffic | 132 | 164 | 123 | 121 |
| half:pollution | 58 | 83 | 0 | 1 |
| half:land_value | 105 | 182 | 0 | 0 |
| half:crime | 1 | 7 | 0 | 0 |
| power | 5098 | 5303 | 3835 | 4175 |
| eighth:growth | 1 | 10 | 0 | 0 |
| eighth:fire_cov | 5960 | 5974 | 5282 | 5457 |
| eighth:police_cov | 5928 | 5957 | 5175 | 5362 |
| scalar:funds | 5579 | 5617 | 774 | 972 |
| scalar:tax | 6000 | 6000 | 6000 | 6000 |
| scalar:res_valve | 4649 | 4861 | 3312 | 3553 |
| scalar:com_valve | 1934 | 2318 | 505 | 565 |
| scalar:ind_valve | 5871 | 5941 | 916 | 1015 |
| scalar:pop | 8 | 268 | 0 | 0 |
| scalar:res_pop | 42 | 533 | 0 | 0 |
| scalar:com_pop | 911 | 2324 | 49 | 77 |
| scalar:ind_pop | 942 | 2325 | 220 | 265 |
| scalar:city_time | 6000 | 6000 | 6000 | 6000 |
| scalar:score | 5515 | 5547 | 110 | 337 |
| scalar:tax_fund | 5707 | 5823 | 353 | 1069 |
| scalar:road_spend | 5556 | 5595 | 378 | 787 |
| scalar:fire_spend | 5983 | 5983 | 5655 | 5707 |
| scalar:police_spend | 5984 | 5985 | 5590 | 5663 |
| scalar:powered_zones | 5638 | 5761 | 4298 | 4700 |
| scalar:unpowered_zones | 5700 | 5813 | 4546 | 4903 |
| scalar:coal_plants | 5993 | 5997 | 5918 | 5968 |
| scalar:nuclear_plants | 5992 | 5999 | 5888 | 5962 |
| scalar:road_total | 358 | 705 | 161 | 186 |
| ledger:sim_cycle | 6000 | 6000 | 6000 | 6000 |
| ledger:sprite_cycle | 6000 | 6000 | 6000 | 6000 |
| ledger:disasters | 6000 | 6000 | 6000 | 6000 |
| ledger:initial_eval | 6000 | 6000 | 6000 | 6000 |
| ledger:total_pop | 251 | 1457 | 0 | 0 |
| ledger:res_hist0 | 1023 | 2551 | 0 | 12 |
| ledger:res_hist1 | 6000 | 6000 | 3 | 15 |
| ledger:com_hist0 | 1205 | 2659 | 49 | 76 |
| ledger:com_hist1 | 6000 | 6000 | 60 | 87 |
| ledger:ind_hist0 | 1129 | 2552 | 221 | 265 |
| ledger:ind_hist1 | 6000 | 6000 | 234 | 278 |
| ledger:res_cap | 6000 | 6000 | 5962 | 5981 |
| ledger:com_cap | 6000 | 6000 | 5975 | 5982 |
| ledger:ind_cap | 6000 | 6000 | 5983 | 5992 |
| ledger:need_hospital | 5496 | 5717 | 3137 | 3638 |
| ledger:need_church | 5631 | 5812 | 3528 | 4029 |
| ledger:road_fund | 5544 | 5584 | 303 | 694 |
| ledger:police_fund | 5998 | 5999 | 5839 | 5917 |
| ledger:fire_fund | 6000 | 5999 | 5928 | 5948 |
| ledger:auto_budget | 6000 | 6000 | 5975 | 5986 |
| ledger:fire_pop | 4881 | 5126 | 3921 | 4183 |
| ledger:city_center_x | 5914 | 5962 | 5299 | 5544 |
| ledger:city_center_y | 5910 | 5965 | 5407 | 5604 |
| ledger:pollution_max_x | 1773 | 2999 | 325 | 565 |
| ledger:pollution_max_y | 1716 | 3041 | 234 | 446 |
| ledger:flood_count | 5981 | 5994 | 5785 | 5885 |
| ledger:abs_dist | 3608 | 3740 | 3301 | 3370 |
| map:terrain | 4764 | 5033 | 3300 | 3613 |
| map:com_rate | 5877 | 5938 | 5093 | 5364 |
| rng | 0 | 0 | 0 | 0 |
| sprites | 1969 | 2082 | 1630 | 1683 |
| hash_dynamic | 0 | 0 | 0 | 0 |
| hash_full | 0 | 0 | 0 | 0 |

### 4.4 Ablation: every item earns its place

Ablation (variant a with one item left at its reset value): transitions where the extended observation differs from the true run

| item left out | other fields differ at month 1 | other fields differ within 12 months | the item itself differs at month 1 | most affected other fields at month 1 (transitions) |
|---|---|---|---|---|
| ledger:sim_cycle | 4800 | 4800 | 5760 | eighth:growth 4800 |
| ledger:sprite_cycle | 3215 | 4243 | 5760 | sprites 3128, rng 3044, tiles 3032, half:traffic 3002 |
| ledger:disasters | 3000 | 3000 | 3000 | rng 2951, tiles 2930, half:pop_density 2873, eighth:growth 2871 |
| ledger:initial_eval | 5760 | 5760 | 0 | rng 5760, tiles 5755, eighth:growth 5746, half:crime 5743 |
| ledger:total_pop | 33 | 33 | 12 | half:crime 23, tiles 22, half:traffic 22, half:pop_density 22 |
| ledger:res_hist0 | 6000 | 6000 | 0 | ledger:res_hist1 6000, scalar:ind_valve 1570, scalar:com_valve 1493, tiles 895 |
| ledger:res_hist1 | 5322 | 5322 | 0 | scalar:ind_valve 4968, scalar:com_valve 4945, tiles 3606, eighth:growth 3475 |
| ledger:com_hist0 | 5997 | 5997 | 0 | ledger:com_hist1 5997, scalar:res_valve 1604, scalar:com_valve 1489, tiles 1282 |
| ledger:com_hist1 | 5718 | 5718 | 0 | tiles 4950, scalar:res_valve 4879, eighth:growth 4823, half:pop_density 4806 |
| ledger:ind_hist0 | 6000 | 6000 | 0 | ledger:ind_hist1 6000, scalar:res_valve 1679, scalar:com_valve 1508, tiles 1393 |
| ledger:ind_hist1 | 5748 | 5748 | 0 | scalar:res_valve 5440, tiles 5355, eighth:growth 5266, half:pop_density 5247 |
| ledger:res_cap | 164 | 164 | 161 | scalar:res_valve 163, tiles 98, half:pop_density 92, eighth:growth 91 |
| ledger:com_cap | 11 | 21 | 21 | scalar:com_valve 11, tiles 8, half:traffic 7, half:pop_density 7 |
| ledger:ind_cap | 30 | 34 | 33 | scalar:ind_valve 30, rng 5, half:pollution 4, tiles 4 |
| ledger:need_hospital | 230 | 230 | 98 | tiles 227, half:pop_density 227, half:crime 212, eighth:growth 190 |
| ledger:need_church | 169 | 169 | 59 | tiles 169, half:traffic 153, half:pop_density 152, eighth:growth 151 |
| ledger:road_fund | 77 | 77 | 4112 | tiles 77, half:pop_density 77, eighth:growth 77, half:crime 77 |
| ledger:police_fund | 299 | 299 | 4110 | half:crime 299, eighth:police_cov 299, tiles 277, rng 277 |
| ledger:fire_fund | 245 | 245 | 3918 | eighth:fire_cov 245, tiles 50, half:pollution 48, eighth:growth 42 |
| ledger:auto_budget | 0 | 14 | 284 |  |
| ledger:fire_pop | 5 | 5 | 0 | scalar:score 5 |
| ledger:city_center_x | 115 | 115 | 0 | tiles 111, half:crime 106, half:traffic 105, eighth:growth 104 |
| ledger:city_center_y | 109 | 109 | 0 | tiles 107, half:pop_density 102, half:traffic 102, half:crime 102 |
| ledger:pollution_max_x | 15 | 15 | 4 | ledger:abs_dist 15, sprites 6, rng 5, tiles 4 |
| ledger:pollution_max_y | 14 | 14 | 2 | ledger:abs_dist 13, tiles 8, half:traffic 8, half:pop_density 8 |
| ledger:flood_count | 143 | 143 | 125 | tiles 143, half:pollution 143, rng 143, half:pop_density 142 |
| ledger:abs_dist | 980 | 1033 | 1335 | sprites 967, tiles 957, half:traffic 951, eighth:growth 945 |
| map:terrain | 5854 | 5854 | 663 | half:crime 5736, tiles 5586, eighth:growth 5411, half:pop_density 5390 |
| map:com_rate | 220 | 220 | 0 | tiles 217, eighth:growth 215, half:crime 214, half:pop_density 213 |
| derived | 2256 | 5931 | - | ledger:sprite_cycle 1680, sprites 1193, rng 1035, tiles 1030 |

### 4.5 Forced-disaster stress set

Forced-disaster stress set: 1200 transitions; variant a identical at month 1 in 1200, over 12 months in 1200; by forced kind in month t: kind 1: 17 (17 identical over 12), kind 2: 19 (19 identical over 12), kind 3: 17 (17 identical over 12), kind 4: 16 (16 identical over 12), kind 5: 16 (16 identical over 12), kind 6: 18 (18 identical over 12)

### 4.6 Is a ledger entry a function of the observation after all?

For the entries with an obvious candidate, the candidate computed from the observation alone, compared with the engine's value at every boundary of the 240 trajectories (`check_sufficiency.py --derivability`):

Boundaries examined: 8880 (all boundaries of 240 trajectories); with city time = 0 mod 4 (census in the last cycle): 6290

| ledger entry | candidate from the observation | equal to the engine's value | equal, city time = 0 mod 4 | equal, other |
|---|---|---|---|---|
| total_pop | res_pop / 8 + com_pop + ind_pop | 3723/8880 | 2838/6290 | 885/2590 |
| res_hist0 | res_pop // 8 | 7505/8880 | 6190/6290 | 1315/2590 |
| com_hist0 | com_pop | 7517/8880 | 6240/6290 | 1277/2590 |
| ind_hist0 | ind_pop | 7732/8880 | 6240/6290 | 1492/2590 |
| road_fund | road_spend | 8525/8880 | 6106/6290 | 2419/2590 |
| fire_fund | fire_spend | 8295/8880 | 5951/6290 | 2344/2590 |
| police_fund | police_spend | 8112/8880 | 5830/6290 | 2282/2590 |
| fire_pop | fire tiles in the tile map | 8109/8880 | 5829/6290 | 2280/2590 |
| city_center_x | mean x of zone centres | 8880/8880 | 6290/6290 | 2590/2590 |
| city_center_y | mean y of zone centres | 8880/8880 | 6290/6290 | 2590/2590 |
| pollution_max_x | first maximum of the pollution overlay | 4700/8880 | 3549/6290 | 1151/2590 |
| pollution_max_y | first maximum of the pollution overlay | 4969/8880 | 3771/6290 | 1198/2590 |

boundaries where the pollution maximum is tied (the engine breaks ties with the generator): 5910/8880

The city centre equals the centre of the zone tiles at every one of these boundaries. By the source it is the centre at phase 14 of the last cycle, and a zone centre destroyed in the ticks after it (a monster or tornado step, a flood at phase 15) separates the two. A scratch search with a forced flood, tornado or monster in every month (96 trajectories of 48 months from the same 48 start states, 4608 boundaries) found 2 boundaries where they differ by one tile (tr-b-haight-v3 month 20, ho-g-28-v0 month 27); in both, restoring the tile centre instead of the ledger value gave the same next 12 months. The entries are kept so that the restore is exact by construction.

### 4.7 Targeted cases (in `test_observation_sufficient.py`)

- `fire_pop` is read only by the evaluation that runs at the first cycle after a load. A start state
  saved one month after six forced fires (so it loads burning), restored at t = 0 with `fire_pop`
  left out: the score at month 1 differs (scratch run on three cities: 666 vs 708, 513 vs 555,
  546 vs 624); with it, the restore is exact. The long run has 5 such transitions (t = 0 with fire
  at the load).
- `auto_budget`: a start state with an empty treasury (`Engine.set_funds(0)` before saving, as the
  family builder does), tax 0 until the first collection switches the auto-budget off (boundary 9),
  then tax 20 and 25 % funding: with `auto_budget` left out, the road, fire and police spend differ at
  the next collection (month 12 after the boundary); with it, exact over 12 months. The long run has
  14 transitions where it changes other fields within 12 months, none at month 1.
- `flood_count`, `pollution_max_*`, sprites: forced monster, flood, tornado and fire, restore exact
  over 10 months at five boundaries; `flood_count` left out after the flood changes the city.

### 4.8 What this says about the original symptom

The valves are not seed-independent at one month in general: setValves runs in cycles 2 and 4 of the
month and reads the census of cycles 1 and 3, which the generator influences. Across 3 re-seedings
of the true run (variant c table), `res_valve` was identical in 4649/6000 transitions, `com_valve`
in 1934/6000, `ind_valve` in 5871/6000 and the score in 5515/6000. What the ledger fixes is the
part that is deterministic but hidden: with `res_hist1`, `com_hist1`, `ind_hist1` the valve update
has its inputs (leaving `com_hist1` out changes `res_valve` at month 1 in 4879/6000 transitions).

## 5. Checks run

```
$ CUDA_VISIBLE_DEVICES="" PYTHONPATH=code pytest code/tests/test_observation_sufficient.py -q
............                                                             [100%]
12 passed in 0.70s

$ CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 PYTHONPATH=code pytest code/tests -q
87 passed in 50.23s

bundled hashes recomputed with the installed library (test_oracle_exact.hashes_for, 32 cities x 240
months) into a scratch file: sha256=cf5997cfa6562c6a5040417e20dca0b92a57c90d236949bdf7617d3a0683bbe6
match=True; results/oracle/bundled_hashes.npy itself not rewritten, sha256 unchanged.

$ make -n -C engine
make: Nothing to be done for 'all'.
```

## 6. For the builder who extends the data generator and the store

### 6.1 What to store per boundary

| item | dtype, shape | range seen / by type |
|---|---|---|
| `ledger` | int64 (27,) | fits int32; `sim_cycle` 0..1023, `sprite_cycle` int16, flags 0/1, `need_*` -1..1, `*_hist*` and `total_pop`, `fire_pop` int16, funds int32, centre 0..119 / 0..99, pollution maximum 0..118 / 0..98, `flood_count` 0..30, `abs_dist` int32 |
| `terrain` | uint8 (30, 25) | 750 bytes |
| `com_rate` | int16 (15, 13) | -64..64, 390 bytes |

`Replay.ledger` gives the (H+1, 27) trajectory from `dc.oracle.replay`. `rollout_behaviour`
 records `Obs` objects, which now carry `ledger`, `terrain`, `com_rate`.

### 6.2 Row 0 and the disaster switch

The oracle reads `obs0` right after the load, before `set_disasters` and `seed` (so that `obs0` does
not depend on the seed). `obs0.ledger[disasters]` is therefore 0 on every trajectory. `Replay.ledger`
row 0 is read after `set_disasters` and holds the trajectory's switch; every other entry is the same
in both. `rollout_behaviour`'s `states[0]` has the same property as `obs0`: take the ledger's row 0
from `Replay.ledger` (oracle) or overwrite the `disasters` entry with the trajectory's flag.

### 6.3 Not in the extended observation

The generator state (`Engine.rng_state()`) and the sprite list (`Engine.sprites()`) are needed for
exactness (variant a) and are deliberately outside the observation. Variant b is the cost of leaving
the sprites out: in cities with rail, a seaport or an airport the engine keeps trains, ships, planes
and helicopters alive almost all the time (4266 of 6000 transitions had sprites at t), and their
generator draws and map effects (bridges opening for ships, crashes) make 4196/6000 transitions
differ from month 1.

## 7. Deviations from the brief, weaknesses, next steps

Deviations:
- `disasters` is a ledger entry (the brief lists it as protocol): the switch is simulator state that
  the month reads and the observation lacks, and with it `_test_restore(obs, rng_state, sprites)`
  needs no further argument. It earns its place (3000/3000 disaster-on transitions differ without it).
- `Replay.ledger` row 0 is read after `set_disasters` (6.2), not taken from `obs0`.
- Additions beyond the brief, all read-only or test-only: `mc_hash_dynamic` / `Engine.hash_dynamic`
  (`mc_hash_full` includes members nothing reads, so it cannot match without restoring them);
  `mc_test_get_aux` and the `aux` argument of the restore (variant a_full, which shows those members are
  the whole difference in `mc_hash_full`); `ledger_mask` / `map_mask` (ablations).
- The library was built with the Makefile's compiler command to a temporary file and moved into
  place instead of `make` writing over it, because other processes had it mapped.

Weaknesses:
- Exactness is shown on 6000 behaviour-mix transitions and the targeted cases; a member read only on a
  path none of them reached could still be missing. The source review in section 2 covers every data
  member of `Micropolis` and every mutable static; the paths with fewest transitions in the run are
  `fire_pop` (t = 0 with fire at the load, 5), `com_cap` (21), `ind_cap` (34), `pollution_max_*`
  (monster targets, 15 and 14) and `auto_budget` (14).
- `city_center_x/y` are not exact functions of the observed tiles (2 counterexamples in 4608
  disaster-heavy boundaries) but no transition was found where that difference changes the next 12
  months; dropping them (deriving the centre from the zone tiles) would make the ledger 25 entries
  at the cost of exactness by construction.
- Variant c with three seeds: per-transition invariant sets are estimates (4514/6000 transitions keep
  every field of their own set at month 1); every miss is reproduced by the true run with the same
  seed (6000/6000 agree), so they are seed effects, not restore errors.
- `sprite_cycle` and `speedCycle` (derived from it) count ticks since the reset in `init()`; the
  derivation holds because every start goes through `mc_load_start`.

Next: extend the store with `ledger`, `terrain`, `com_rate` (6.1, 6.2); decide whether the emulator
should see `sprite_cycle` and `abs_dist`, which matter only through sprites, which it does not see.
