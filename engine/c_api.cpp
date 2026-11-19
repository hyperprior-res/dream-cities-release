/* c_api.cpp
 *
 * MODIFIED / DERIVED WORK NOTICE (per GNU GPL v3 Section 5(a) and Electronic
 * Arts Additional Terms under GPL Section 7):
 * Created on 2026-11-08 by HyperPrior Research as a native C interface to the
 * modified Micropolis C++ engine for headless deterministic replay.
 * Released under the GNU General Public License v3 with Electronic Arts
 * Section 7 Additional Terms (see engine/LICENSE).
 *
 * MODIFIED 2026-11-09 by HyperPrior Research (exact-replay protocol):
 *   - removed mc_set_state. Restoring a partial state into a live simulator
 *     left the rest of the simulator from the previous city, so a replay was
 *     not a function of (start, action log, seed). Every replay now starts
 *     from a full reset plus the engine's own city-file load (mc_load_start).
 *   - added mc_load_start, mc_save_city, mc_set_funds, mc_set_game_level,
 *     mc_get_build_cost, mc_hash_full.
 *   - mc_get_state derives cityPop from the census instead of reading the
 *     cached field, so the observation is valid immediately after a load.
 *
 * MODIFIED 2026-11-10 by HyperPrior Research (sufficient observation):
 *   - added the ledger: mc_get_ledger returns the simulator members that are
 *     carried from one month to a later one and are not functions of the
 *     observation (named layout below, mirrored by LEDGER_NAMES in
 *     code/dc/engine.py), plus the two carried maps that are not observed.
 *   - added read-only accessors mc_get_rng, mc_get_sprites, mc_hash_dynamic.
 *   - added mc_test_restore and mc_test_get_aux, used only by the sufficiency
 *     test (see the comment at their definition). The replay path
 *     (mc_load_start, mc_seed, tool calls, mc_step_month) is unchanged.
 */

// The full-state hash below reads private simulator fields. Access only; the
// class layout is unchanged.
#define private public
#define protected public
#include "micropolis.h"
#undef private
#undef protected
#include "callback.h"
#include "tool.h"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <new>
#include <string>

extern "C" {

struct EngineHandle {
    Micropolis sim;
    ConsoleCallback *cb;
    int64_t monthBuildCost;
    int64_t prevFunds;
};

static uint64_t fnv1a_map_funds_pop(Micropolis &m) {
    uint64_t h = 1469598103934665603ULL;
    for (int x = 0; x < WORLD_W; x++) {
        for (int y = 0; y < WORLD_H; y++) {
            h ^= (uint64_t)m.getTile(x, y);
            h *= 1099511628211ULL;
        }
    }
    h ^= (uint64_t)m.totalFunds;
    h *= 1099511628211ULL;
    h ^= (uint64_t)m.cityPop;
    return h;
}

void* mc_create() {
    void *mem = calloc(1, sizeof(EngineHandle));
    EngineHandle *h = new (mem) EngineHandle();
    h->cb = new ConsoleCallback();
    h->sim.setCallback(h->cb, emscripten::val::null());
    h->sim.init();
    h->monthBuildCost = 0;
    h->prevFunds = h->sim.totalFunds;
    return (void*)h;
}

void mc_destroy(void* ptr) {
    if (!ptr) return;
    EngineHandle *h = (EngineHandle*)ptr;
    h->~EngineHandle();
    free(ptr);
}

void mc_init_generated(void* ptr, int seed, int funds, int speed, int passes, int disasters, int level) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.init();
    h->sim.seedRandom(seed);
    h->sim.generateSomeCity(seed);
    h->sim.seedRandom(seed);
    h->sim.setGameLevel((GameLevel)clamp(level, 0, 2));
    h->sim.setSpeed((short)speed);
    h->sim.setPasses(passes);
    h->sim.setFunds(funds);
    h->sim.setEnableDisasters(disasters != 0);
    h->sim.setAutoBudget(true);
    h->sim.setAutoBulldoze(true);
    h->sim.cityEvaluation();
    h->monthBuildCost = 0;
    h->prevFunds = h->sim.totalFunds;
}

int mc_init_city(void* ptr, const char* filename, int seed, int speed, int passes, int disasters) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.init();
    h->sim.seedRandom(seed);
    bool ok = h->sim.loadCity(std::string(filename));
    if (!ok) return 0;
    h->sim.seedRandom(seed);
    h->sim.setSpeed((short)speed);
    h->sim.setPasses(passes);
    h->sim.setEnableDisasters(disasters != 0);
    h->sim.setAutoBudget(true);
    h->sim.setAutoBulldoze(true);
    h->monthBuildCost = 0;
    h->prevFunds = h->sim.totalFunds;
    return 1;
}

void mc_seed(void* ptr, int seed) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.seedRandom(seed);
}

void mc_set_disasters(void* ptr, int disasters) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.setEnableDisasters(disasters != 0);
}

void mc_set_tax(void* ptr, int tax) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.setCityTax((short)clamp(tax, 0, 20));
}

void mc_set_funding(void* ptr, float road_pct, float fire_pct, float police_pct) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.roadPercent = clamp(road_pct, 0.0f, 1.0f);
    h->sim.firePercent = clamp(fire_pct, 0.0f, 1.0f);
    h->sim.policePercent = clamp(police_pct, 0.0f, 1.0f);
    h->sim.updateFundEffects();
}

int mc_do_tool(void* ptr, int tool, int x, int y) {
    EngineHandle *h = (EngineHandle*)ptr;
    if (tool < (int)TOOL_FIRST || tool > (int)TOOL_LAST) return 0;
    Quad before = h->sim.totalFunds;
    ToolResult res = h->sim.doTool((EditingTool)tool, (short)x, (short)y);
    Quad after = h->sim.totalFunds;
    if (before > after) {
        h->monthBuildCost += (before - after);
    }
    return (int)res;
}

void mc_force_disaster(void* ptr, int kind) {
    EngineHandle *h = (EngineHandle*)ptr;
    switch (kind) {
        case 1: h->sim.makeFire(); break;
        case 2: h->sim.makeFlood(); break;
        case 3: h->sim.makeEarthquake(); break;
        case 4: h->sim.makeTornado(); break;
        case 5: h->sim.makeMonster(); break;
        case 6: h->sim.makeMeltdown(); break;
        default: h->sim.setFire(); break;
    }
}

void mc_step_month(void* ptr) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->prevFunds = h->sim.totalFunds;
    Quad startT = h->sim.cityTime;
    while (h->sim.cityTime - startT < 4 || h->sim.phaseCycle != 0) {
        h->sim.simTick();
    }
    h->sim.cityPop = (h->sim.resPop + (h->sim.comPop + h->sim.indPop) * 8L) * 20L;
    h->monthBuildCost = 0;
}

uint64_t mc_hash_state(void* ptr) {
    EngineHandle *h = (EngineHandle*)ptr;
    return fnv1a_map_funds_pop(h->sim);
}

/*
 * Extract complete state:
 * - tiles: 120 * 100 uint16_t (raw 16-bit tile word: lower 10 bits index, upper 6 bits flags)
 * - overlays_half: 5 * 60 * 50 uint8_t (popDensity, trafficDensity, pollutionDensity, landValue, crimeRate)
 * - power_grid: 120 * 100 uint8_t
 * - overlays_eighth: 3 * 15 * 13 int16_t (rateOfGrowth, fireCoverage, policeCoverage)
 * - scalars: 20 int64_t:
 *     0: totalFunds
 *     1: cityTax
 *     2: resValve
 *     3: comValve
 *     4: indValve
 *     5: cityPop
 *     6: resPop
 *     7: comPop
 *     8: indPop
 *     9: cityTime
 *    10: cityScore
 *    11: taxFund
 *    12: roadSpend
 *    13: fireSpend
 *    14: policeSpend
 *    15: poweredZoneCount
 *    16: unpoweredZoneCount
 *    17: coalPowerPop
 *    18: nuclearPowerPop
 *    19: roadTotal
 */
void mc_get_state(
    void* ptr,
    uint16_t* tiles_out,
    uint8_t* overlays_half_out,
    uint8_t* power_grid_out,
    int16_t* overlays_eighth_out,
    int64_t* scalars_out
) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;

    if (tiles_out) {
        for (int x = 0; x < WORLD_W; x++) {
            memcpy(tiles_out + x * WORLD_H, m.map[x], WORLD_H * sizeof(uint16_t));
        }
    }

    if (overlays_half_out) {
        const size_t n2 = WORLD_W_2 * WORLD_H_2;
        memcpy(overlays_half_out + 0 * n2, m.populationDensityMap.getBase(), n2);
        memcpy(overlays_half_out + 1 * n2, m.trafficDensityMap.getBase(), n2);
        memcpy(overlays_half_out + 2 * n2, m.pollutionDensityMap.getBase(), n2);
        memcpy(overlays_half_out + 3 * n2, m.landValueMap.getBase(), n2);
        memcpy(overlays_half_out + 4 * n2, m.crimeRateMap.getBase(), n2);
    }

    if (power_grid_out) {
        memcpy(power_grid_out, m.powerGridMap.getBase(), WORLD_W * WORLD_H);
    }

    if (overlays_eighth_out) {
        const size_t n8 = WORLD_W_8 * WORLD_H_8;
        memcpy(overlays_eighth_out + 0 * n8, m.rateOfGrowthMap.getBase(), n8 * sizeof(int16_t));
        memcpy(overlays_eighth_out + 1 * n8, m.fireStationEffectMap.getBase(), n8 * sizeof(int16_t));
        memcpy(overlays_eighth_out + 2 * n8, m.policeStationEffectMap.getBase(), n8 * sizeof(int16_t));
    }

    if (scalars_out) {
        scalars_out[0] = (int64_t)m.totalFunds;
        scalars_out[1] = (int64_t)m.cityTax;
        scalars_out[2] = (int64_t)m.resValve;
        scalars_out[3] = (int64_t)m.comValve;
        scalars_out[4] = (int64_t)m.indValve;
        scalars_out[5] = (int64_t)((m.resPop + (m.comPop + m.indPop) * 8L) * 20L);
        scalars_out[6] = (int64_t)m.resPop;
        scalars_out[7] = (int64_t)m.comPop;
        scalars_out[8] = (int64_t)m.indPop;
        scalars_out[9] = (int64_t)m.cityTime;
        scalars_out[10] = (int64_t)m.cityScore;
        scalars_out[11] = (int64_t)m.taxFund;
        scalars_out[12] = (int64_t)m.roadSpend;
        scalars_out[13] = (int64_t)m.fireSpend;
        scalars_out[14] = (int64_t)m.policeSpend;
        scalars_out[15] = (int64_t)m.poweredZoneCount;
        scalars_out[16] = (int64_t)m.unpoweredZoneCount;
        scalars_out[17] = (int64_t)m.coalPowerPop;
        scalars_out[18] = (int64_t)m.nuclearPowerPop;
        scalars_out[19] = (int64_t)m.roadTotal;
    }
}

/* ---------------------------------------------------------------------------
 * Exact-replay protocol (HyperPrior, 2026-11-09)
 * ------------------------------------------------------------------------- */

/* Full reset, then load a saved city with the engine's own loader. After this
 * call the simulator state is a function of the file bytes and the arguments
 * only: nothing survives from whatever this instance simulated before. */
int mc_load_start(void* ptr, const char* filename, int game_level, int speed, int passes) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.destroyAllSprites();
    h->sim.init();
    h->sim.seedRandom(1);
    bool ok = h->sim.loadCity(std::string(filename));
    if (!ok) return 0;
    h->sim.setGameLevel((GameLevel)clamp(game_level, 0, 2));
    h->sim.setSpeed((short)speed);
    h->sim.setPasses(passes);
    h->sim.setEnableDisasters(false);
    h->sim.setAutoBudget(true);
    h->sim.setAutoBulldoze(true);
    h->sim.seedRandom(1);
    h->monthBuildCost = 0;
    h->prevFunds = h->sim.totalFunds;
    return 1;
}

int mc_save_city(void* ptr, const char* filename) {
    EngineHandle *h = (EngineHandle*)ptr;
    return h->sim.saveFile(std::string(filename)) ? 1 : 0;
}

void mc_set_funds(void* ptr, int funds) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.setFunds(funds);
    h->prevFunds = h->sim.totalFunds;
}

void mc_set_game_level(void* ptr, int level) {
    EngineHandle *h = (EngineHandle*)ptr;
    h->sim.setGameLevel((GameLevel)clamp(level, 0, 2));
}

/* Funds spent by tool calls since the last mc_step_month. */
int64_t mc_get_build_cost(void* ptr) {
    EngineHandle *h = (EngineHandle*)ptr;
    return h->monthBuildCost;
}

static inline void fnv_bytes(uint64_t &hsh, const void *data, size_t n) {
    const unsigned char *p = (const unsigned char *)data;
    for (size_t i = 0; i < n; i++) { hsh ^= (uint64_t)p[i]; hsh *= 1099511628211ULL; }
}
#define fnv_val(hsh, v) do { auto fnv_tmp_ = (v); fnv_bytes((hsh), &fnv_tmp_, sizeof(fnv_tmp_)); } while (0)

/* Hash of every simulator field that can influence a later state: maps,
 * overlays, census, budget, averages, cycle counters, histories, the random
 * generator, and the sprite list. Used by the determinism tests. */
uint64_t mc_hash_full(void* ptr) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;
    uint64_t x = 1469598103934665603ULL;
    for (int i = 0; i < WORLD_W; i++) fnv_bytes(x, m.map[i], WORLD_H * sizeof(unsigned short));
    fnv_bytes(x, m.powerGridMap.getBase(), WORLD_W * WORLD_H);
    const size_t n2 = WORLD_W_2 * WORLD_H_2, n4 = WORLD_W_4 * WORLD_H_4, n8 = WORLD_W_8 * WORLD_H_8;
    fnv_bytes(x, m.populationDensityMap.getBase(), n2);
    fnv_bytes(x, m.trafficDensityMap.getBase(), n2);
    fnv_bytes(x, m.pollutionDensityMap.getBase(), n2);
    fnv_bytes(x, m.landValueMap.getBase(), n2);
    fnv_bytes(x, m.crimeRateMap.getBase(), n2);
    fnv_bytes(x, m.terrainDensityMap.getBase(), n4);
    fnv_bytes(x, m.rateOfGrowthMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.fireStationMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.fireStationEffectMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.policeStationMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.policeStationEffectMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.comRateMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.resHist, HISTORY_LENGTH);
    fnv_bytes(x, m.comHist, HISTORY_LENGTH);
    fnv_bytes(x, m.indHist, HISTORY_LENGTH);
    fnv_bytes(x, m.moneyHist, HISTORY_LENGTH);
    fnv_bytes(x, m.pollutionHist, HISTORY_LENGTH);
    fnv_bytes(x, m.crimeHist, HISTORY_LENGTH);
    fnv_val(x, m.totalFunds); fnv_val(x, m.cityTax); fnv_val(x, m.cityTime);
    fnv_val(x, m.resValve); fnv_val(x, m.comValve); fnv_val(x, m.indValve);
    fnv_val(x, m.resPop); fnv_val(x, m.comPop); fnv_val(x, m.indPop);
    fnv_val(x, m.totalPop); fnv_val(x, m.totalPopLast);
    fnv_val(x, m.resZonePop); fnv_val(x, m.comZonePop); fnv_val(x, m.indZonePop);
    fnv_val(x, m.hospitalPop); fnv_val(x, m.churchPop); fnv_val(x, m.stadiumPop);
    fnv_val(x, m.policeStationPop); fnv_val(x, m.fireStationPop);
    fnv_val(x, m.coalPowerPop); fnv_val(x, m.nuclearPowerPop);
    fnv_val(x, m.seaportPop); fnv_val(x, m.airportPop);
    fnv_val(x, m.roadTotal); fnv_val(x, m.railTotal); fnv_val(x, m.firePop);
    fnv_val(x, m.poweredZoneCount); fnv_val(x, m.unpoweredZoneCount);
    fnv_val(x, m.crimeAverage); fnv_val(x, m.pollutionAverage); fnv_val(x, m.landValueAverage);
    fnv_val(x, m.cityTaxAverage); fnv_val(x, m.cityScore); fnv_val(x, m.cityYes);
    fnv_val(x, (int)m.cityClass); fnv_val(x, (int)m.gameLevel);
    fnv_val(x, m.taxFund); fnv_val(x, m.roadFund); fnv_val(x, m.policeFund); fnv_val(x, m.fireFund);
    fnv_val(x, m.roadSpend); fnv_val(x, m.policeSpend); fnv_val(x, m.fireSpend);
    fnv_val(x, m.roadEffect); fnv_val(x, m.policeEffect); fnv_val(x, m.fireEffect);
    fnv_val(x, m.roadPercent); fnv_val(x, m.policePercent); fnv_val(x, m.firePercent);
    fnv_val(x, m.needHospital); fnv_val(x, m.needChurch);
    fnv_val(x, m.resCap); fnv_val(x, m.comCap); fnv_val(x, m.indCap);
    fnv_val(x, m.valveFlag); fnv_val(x, m.newPower);
    fnv_val(x, m.disasterWait); fnv_val(x, m.floodCount); fnv_val(x, m.scoreWait);
    fnv_val(x, m.simCycle); fnv_val(x, m.phaseCycle);
    fnv_val(x, m.simSpeed); fnv_val(x, m.enableDisasters); fnv_val(x, m.autoBudget); fnv_val(x, m.autoBulldoze);
    fnv_val(x, m.nextRandom);
    int nsprites = 0;
    for (SimSprite *sp = m.spriteList; sp != NULL; sp = sp->next) {
        nsprites++;
        fnv_val(x, sp->type); fnv_val(x, sp->frame); fnv_val(x, sp->x); fnv_val(x, sp->y);
        fnv_val(x, sp->destX); fnv_val(x, sp->destY); fnv_val(x, sp->count);
    }
    fnv_val(x, nsprites);
    return x;
}

/* ---------------------------------------------------------------------------
 * Sufficient observation: the ledger (HyperPrior, 2026-11-10)
 *
 * The observation (mc_get_state) does not contain every simulator member that
 * the monthly update reads. The ledger is the list of members that are written
 * in one month and read in a later month before being rewritten, under the
 * replay protocol (speed 1, one pass, level easy, auto-budget and
 * auto-bulldoze on), and that are not exact functions of the observation.
 * The derivation from the engine source, with file and line references, is in
 * results/oracle/observation_sufficiency.md. Order and names are mirrored by
 * LEDGER_NAMES in code/dc/engine.py; append only.
 *
 * Carried maps that are not observed: terrainDensityMap (30 x 25 bytes, read
 * by the land-value equation before it is recomputed) and comRateMap (15 x 13
 * shorts, read by commercial growth before it is recomputed).
 *
 * Carried members derived from the observation by the test restore, so not in
 * the ledger: cityPop (the population scalar, or 0 while the initial
 * evaluation is pending), crimeAverage, pollutionAverage, landValueAverage
 * (averages of the observed overlays), speedCycle (= spriteCycle mod 1024:
 * both count simulator ticks since the reset in init()).
 * ------------------------------------------------------------------------- */

enum LedgerIndex {
    LG_SIM_CYCLE = 0,      // simCycle: cycle counter 0..1023 (setValves, scan cadence, decRateOfGrowthMap)
    LG_SPRITE_CYCLE,       // spriteCycle: tick counter (short), sprite cadence; speedCycle derived from it
    LG_DISASTERS,          // enableDisasters: the trajectory's disaster switch (set once, read every month)
    LG_INITIAL_EVAL,       // doInitialEval: city evaluation pending at the first cycle after a load
    LG_TOTAL_POP,          // totalPop: from setValves on even cycles; train generation, tax, evaluation
    LG_RES_HIST0,          // resHist[0]: last census (resPop / 8)
    LG_RES_HIST1,          // resHist[1]: census before last (read by setValves)
    LG_COM_HIST0,          // comHist[0]
    LG_COM_HIST1,          // comHist[1]
    LG_IND_HIST0,          // indHist[0]
    LG_IND_HIST1,          // indHist[1]
    LG_RES_CAP,            // resCap: residential demand capped (no stadium), set every 64 city-time units
    LG_COM_CAP,            // comCap: commercial demand capped (no airport)
    LG_IND_CAP,            // indCap: industrial demand capped (no seaport)
    LG_NEED_HOSPITAL,      // needHospital: -1, 0, 1 from take10Census
    LG_NEED_CHURCH,        // needChurch: -1, 0, 1 from take10Census
    LG_ROAD_FUND,          // roadFund: road funding requested at the last tax collection
    LG_POLICE_FUND,        // policeFund
    LG_FIRE_FUND,          // fireFund
    LG_AUTO_BUDGET,        // autoBudget: switched off by the engine when the treasury cannot pay
    LG_FIRE_POP,           // firePop: fire tiles counted by the last cycle (read by the initial evaluation)
    LG_CITY_CENTER_X,      // cityCenterX: centre of mass of zones at the last population scan
    LG_CITY_CENTER_Y,      // cityCenterY
    LG_POLLUTION_MAX_X,    // pollutionMaxX: most polluted block (ties broken by the generator); monster target
    LG_POLLUTION_MAX_Y,    // pollutionMaxY
    LG_FLOOD_COUNT,        // floodCount: flood spreads while > 0
    LG_ABS_DIST,           // absDist: last sprite distance computed by getDir, read stale by sprites
    LG_COUNT
};

static const int MC_TERRAIN_N = WORLD_W_4 * WORLD_H_4;   // 30 x 25
static const int MC_COMRATE_N = WORLD_W_8 * WORLD_H_8;   // 15 x 13
static const int MC_SPRITE_FIELDS = 25;
static const int MC_AUX_LEN = 6 * 240 + 7;

int mc_ledger_len() { return LG_COUNT; }
int mc_sprite_fields() { return MC_SPRITE_FIELDS; }
int mc_aux_len() { return MC_AUX_LEN; }

void mc_get_ledger(void* ptr, int64_t* ledger_out, uint8_t* terrain_out, int16_t* comrate_out) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;
    if (ledger_out) {
        int64_t *L = ledger_out;
        L[LG_SIM_CYCLE] = m.simCycle;
        L[LG_SPRITE_CYCLE] = m.spriteCycle;
        L[LG_DISASTERS] = m.enableDisasters ? 1 : 0;
        L[LG_INITIAL_EVAL] = m.doInitialEval ? 1 : 0;
        L[LG_TOTAL_POP] = m.totalPop;
        L[LG_RES_HIST0] = m.resHist[0];
        L[LG_RES_HIST1] = m.resHist[1];
        L[LG_COM_HIST0] = m.comHist[0];
        L[LG_COM_HIST1] = m.comHist[1];
        L[LG_IND_HIST0] = m.indHist[0];
        L[LG_IND_HIST1] = m.indHist[1];
        L[LG_RES_CAP] = m.resCap ? 1 : 0;
        L[LG_COM_CAP] = m.comCap ? 1 : 0;
        L[LG_IND_CAP] = m.indCap ? 1 : 0;
        L[LG_NEED_HOSPITAL] = m.needHospital;
        L[LG_NEED_CHURCH] = m.needChurch;
        L[LG_ROAD_FUND] = m.roadFund;
        L[LG_POLICE_FUND] = m.policeFund;
        L[LG_FIRE_FUND] = m.fireFund;
        L[LG_AUTO_BUDGET] = m.autoBudget ? 1 : 0;
        L[LG_FIRE_POP] = m.firePop;
        L[LG_CITY_CENTER_X] = m.cityCenterX;
        L[LG_CITY_CENTER_Y] = m.cityCenterY;
        L[LG_POLLUTION_MAX_X] = m.pollutionMaxX;
        L[LG_POLLUTION_MAX_Y] = m.pollutionMaxY;
        L[LG_FLOOD_COUNT] = m.floodCount;
        L[LG_ABS_DIST] = m.absDist;
    }
    if (terrain_out) memcpy(terrain_out, m.terrainDensityMap.getBase(), MC_TERRAIN_N);
    if (comrate_out) memcpy(comrate_out, m.comRateMap.getBase(), MC_COMRATE_N * sizeof(int16_t));
}

/* The random generator's full state (the engine draws from bits 8..23). */
uint64_t mc_get_rng(void* ptr) {
    EngineHandle *h = (EngineHandle*)ptr;
    return (uint64_t)h->sim.nextRandom;
}

static void sprite_to_row(Micropolis &m, SimSprite *sp, int32_t *r) {
    r[0] = sp->type; r[1] = sp->frame; r[2] = sp->x; r[3] = sp->y;
    r[4] = sp->width; r[5] = sp->height; r[6] = sp->xOffset; r[7] = sp->yOffset;
    r[8] = sp->xHot; r[9] = sp->yHot; r[10] = sp->origX; r[11] = sp->origY;
    r[12] = sp->destX; r[13] = sp->destY; r[14] = sp->count; r[15] = sp->soundCount;
    r[16] = sp->dir; r[17] = sp->newDir; r[18] = sp->step; r[19] = sp->flag;
    r[20] = sp->control; r[21] = sp->turn; r[22] = sp->accel; r[23] = sp->speed;
    int t = sp->type;
    r[24] = (t >= 0 && t < SPRITE_COUNT && m.globalSprites[t] == sp) ? 1 : 0;
}

/* The active sprite list in list order (inactive frame-0 entries included:
 * they stay in the list until the next tick and can be re-used). One row of
 * MC_SPRITE_FIELDS int32 per sprite; the last column is 1 if the sprite is the
 * one the engine keeps for its type. Returns the number of sprites (rows
 * written: at most max_rows), or -1 if a sprite has a non-empty name (never
 * produced by the engine; such a sprite would not be removed when inactive). */
int mc_get_sprites(void* ptr, int32_t* out, int max_rows) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;
    int n = 0;
    for (SimSprite *sp = m.spriteList; sp != NULL; sp = sp->next) {
        if (!sp->name.empty()) return -1;
        if (out && n < max_rows) sprite_to_row(m, sp, out + (size_t)n * MC_SPRITE_FIELDS);
        n++;
    }
    return n;
}

/* Hash of every simulator field that can influence a later state, by the
 * analysis in results/oracle/observation_sufficiency.md: mc_hash_full without
 * the members that nothing in the monthly update reads (graph histories past
 * index 1, totalPopLast, cityTaxAverage, cityYes, cityClass), plus the carried
 * members mc_hash_full leaves out (cityPop, doInitialEval, speedCycle,
 * spriteCycle, absDist, city centre, pollution maximum, every sprite field and
 * which sprite the engine keeps per type). */
uint64_t mc_hash_dynamic(void* ptr) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;
    uint64_t x = 1469598103934665603ULL;
    for (int i = 0; i < WORLD_W; i++) fnv_bytes(x, m.map[i], WORLD_H * sizeof(unsigned short));
    fnv_bytes(x, m.powerGridMap.getBase(), WORLD_W * WORLD_H);
    const size_t n2 = WORLD_W_2 * WORLD_H_2, n4 = WORLD_W_4 * WORLD_H_4, n8 = WORLD_W_8 * WORLD_H_8;
    fnv_bytes(x, m.populationDensityMap.getBase(), n2);
    fnv_bytes(x, m.trafficDensityMap.getBase(), n2);
    fnv_bytes(x, m.pollutionDensityMap.getBase(), n2);
    fnv_bytes(x, m.landValueMap.getBase(), n2);
    fnv_bytes(x, m.crimeRateMap.getBase(), n2);
    fnv_bytes(x, m.terrainDensityMap.getBase(), n4);
    fnv_bytes(x, m.rateOfGrowthMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.fireStationMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.fireStationEffectMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.policeStationMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.policeStationEffectMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.comRateMap.getBase(), n8 * sizeof(short));
    fnv_bytes(x, m.resHist, 2 * sizeof(short));
    fnv_bytes(x, m.comHist, 2 * sizeof(short));
    fnv_bytes(x, m.indHist, 2 * sizeof(short));
    fnv_val(x, m.totalFunds); fnv_val(x, m.cityTax); fnv_val(x, m.cityTime);
    fnv_val(x, m.resValve); fnv_val(x, m.comValve); fnv_val(x, m.indValve);
    fnv_val(x, m.resPop); fnv_val(x, m.comPop); fnv_val(x, m.indPop);
    fnv_val(x, m.totalPop); fnv_val(x, m.cityPop);
    fnv_val(x, m.resZonePop); fnv_val(x, m.comZonePop); fnv_val(x, m.indZonePop);
    fnv_val(x, m.hospitalPop); fnv_val(x, m.churchPop); fnv_val(x, m.stadiumPop);
    fnv_val(x, m.policeStationPop); fnv_val(x, m.fireStationPop);
    fnv_val(x, m.coalPowerPop); fnv_val(x, m.nuclearPowerPop);
    fnv_val(x, m.seaportPop); fnv_val(x, m.airportPop);
    fnv_val(x, m.roadTotal); fnv_val(x, m.railTotal); fnv_val(x, m.firePop);
    fnv_val(x, m.poweredZoneCount); fnv_val(x, m.unpoweredZoneCount);
    fnv_val(x, m.crimeAverage); fnv_val(x, m.pollutionAverage); fnv_val(x, m.landValueAverage);
    fnv_val(x, m.cityScore); fnv_val(x, (int)m.gameLevel);
    fnv_val(x, m.taxFund); fnv_val(x, m.roadFund); fnv_val(x, m.policeFund); fnv_val(x, m.fireFund);
    fnv_val(x, m.roadSpend); fnv_val(x, m.policeSpend); fnv_val(x, m.fireSpend);
    fnv_val(x, m.roadEffect); fnv_val(x, m.policeEffect); fnv_val(x, m.fireEffect);
    fnv_val(x, m.roadPercent); fnv_val(x, m.policePercent); fnv_val(x, m.firePercent);
    fnv_val(x, m.needHospital); fnv_val(x, m.needChurch);
    fnv_val(x, m.resCap); fnv_val(x, m.comCap); fnv_val(x, m.indCap);
    fnv_val(x, m.newPower);
    fnv_val(x, m.disasterWait); fnv_val(x, m.floodCount); fnv_val(x, m.scoreWait);
    fnv_val(x, m.simCycle); fnv_val(x, m.phaseCycle); fnv_val(x, m.speedCycle); fnv_val(x, m.spriteCycle);
    fnv_val(x, m.doInitialEval); fnv_val(x, m.absDist);
    fnv_val(x, m.cityCenterX); fnv_val(x, m.cityCenterY); fnv_val(x, m.pollutionMaxX); fnv_val(x, m.pollutionMaxY);
    fnv_val(x, m.simSpeed); fnv_val(x, m.enableDisasters); fnv_val(x, m.autoBudget); fnv_val(x, m.autoBulldoze);
    fnv_val(x, m.nextRandom);
    int nsprites = 0;
    int32_t row[MC_SPRITE_FIELDS];
    for (SimSprite *sp = m.spriteList; sp != NULL; sp = sp->next) {
        nsprites++;
        sprite_to_row(m, sp, row);
        fnv_bytes(x, row, sizeof(row));
    }
    fnv_val(x, nsprites);
    return x;
}

/* ---------------------------------------------------------------------------
 * TEST ONLY. mc_test_get_aux and mc_test_restore exist only to prove that the
 * extended observation (observation + ledger + the two carried maps) plus the
 * generator state, and optionally the sprite list, determine the next month
 * (code/tests/test_observation_sufficient.py, code/scripts/check_sufficiency.py).
 * They are never called by dc.oracle, the data generator or any experiment;
 * test_observation_sufficient.py greps the tree to keep it that way. A replay
 * starts only from mc_load_start (ground rule 3 of REBUILD_SPEC.md).
 * ------------------------------------------------------------------------- */

/* Members that nothing in the monthly update reads but that mc_hash_full
 * hashes, or that feed what it hashes: the six graph histories (all 240
 * entries), totalPopLast, cityTaxAverage, cityYes, cityClass, and crimeRamp,
 * pollutionRamp, cashFlow (written into crimeHist[0], pollutionHist[0],
 * moneyHist[0] by the monthly census). Restored only by variant "a_full" of
 * the test, to show that they are the whole difference in mc_hash_full. */
void mc_test_get_aux(void* ptr, int64_t* out) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;
    short *hist[6] = { m.resHist, m.comHist, m.indHist, m.moneyHist, m.pollutionHist, m.crimeHist };
    int k = 0;
    for (int a = 0; a < 6; a++) for (int i = 0; i < 240; i++) out[k++] = hist[a][i];
    out[k++] = m.totalPopLast;
    out[k++] = m.cityTaxAverage;
    out[k++] = m.cityYes;
    out[k++] = (int64_t)m.cityClass;
    out[k++] = m.crimeRamp;
    out[k++] = m.pollutionRamp;
    out[k++] = m.cashFlow;
}

static void free_sprite_lists(Micropolis &m) {
    SimSprite *sp = m.spriteList;
    while (sp != NULL) { SimSprite *nx = sp->next; delete sp; sp = nx; }
    sp = m.freeSprites;
    while (sp != NULL) { SimSprite *nx = sp->next; delete sp; sp = nx; }
    m.spriteList = NULL;
    m.freeSprites = NULL;
    memset(m.globalSprites, 0, sizeof(m.globalSprites));
}

/* TEST ONLY (see above). Full reset of this instance, then set the simulator
 * from an extended observation:
 *   tiles, half, power, eighth, scalars: as returned by mc_get_state;
 *   ledger (LG_COUNT int64), terrain (30 x 25 bytes), comrate (15 x 13 shorts):
 *     as returned by mc_get_ledger;
 *   rng: as returned by mc_get_rng;
 *   sprites/nsprites: rows as returned by mc_get_sprites, or NULL for none;
 *   aux: as returned by mc_test_get_aux, or NULL to leave those members at
 *     their reset values (they are not read by the monthly update);
 *   ledger_mask: bit i set = restore ledger entry i (cleared bits leave the
 *     reset value; used to show that every entry is needed);
 *   map_mask: bit 0 terrain map, bit 1 comRate map, bit 2 derived members.
 * Members derived here from the observation: cityPop, crimeAverage,
 * pollutionAverage, landValueAverage, speedCycle. Protocol settings come from
 * the arguments (level, speed, passes) as in mc_load_start; auto-bulldoze on.
 * Returns 1. */
int mc_test_restore(void* ptr,
                    const uint16_t* tiles, const uint8_t* half, const uint8_t* power,
                    const int16_t* eighth, const int64_t* scalars,
                    const int64_t* ledger, const uint8_t* terrain, const int16_t* comrate,
                    uint64_t rng, const int32_t* sprites, int nsprites, const int64_t* aux,
                    uint64_t ledger_mask, int map_mask, int game_level, int speed, int passes) {
    EngineHandle *h = (EngineHandle*)ptr;
    Micropolis &m = h->sim;

    // Full reset, as mc_load_start does before the loader.
    free_sprite_lists(m);
    m.init();
    m.setGameLevel((GameLevel)clamp(game_level, 0, 2));
    m.setSpeed((short)speed);
    m.setPasses(passes);
    m.setEnableDisasters(false);
    m.setAutoBudget(true);
    m.setAutoBulldoze(true);

    // Observation: maps.
    for (int x = 0; x < WORLD_W; x++) memcpy(m.map[x], tiles + x * WORLD_H, WORLD_H * sizeof(uint16_t));
    const size_t n2 = WORLD_W_2 * WORLD_H_2, n8 = WORLD_W_8 * WORLD_H_8;
    memcpy(m.populationDensityMap.getBase(), half + 0 * n2, n2);
    memcpy(m.trafficDensityMap.getBase(), half + 1 * n2, n2);
    memcpy(m.pollutionDensityMap.getBase(), half + 2 * n2, n2);
    memcpy(m.landValueMap.getBase(), half + 3 * n2, n2);
    memcpy(m.crimeRateMap.getBase(), half + 4 * n2, n2);
    memcpy(m.powerGridMap.getBase(), power, WORLD_W * WORLD_H);
    memcpy(m.rateOfGrowthMap.getBase(), eighth + 0 * n8, n8 * sizeof(int16_t));
    memcpy(m.fireStationEffectMap.getBase(), eighth + 1 * n8, n8 * sizeof(int16_t));
    memcpy(m.policeStationEffectMap.getBase(), eighth + 2 * n8, n8 * sizeof(int16_t));

    // Observation: scalars (index 5, the population, is derived from 6..8).
    m.setFunds((int)scalars[0]);
    m.setCityTax((short)scalars[1]);
    m.resValve = (short)scalars[2];
    m.comValve = (short)scalars[3];
    m.indValve = (short)scalars[4];
    m.resPop = (short)scalars[6];
    m.comPop = (short)scalars[7];
    m.indPop = (short)scalars[8];
    m.cityTime = (Quad)scalars[9];
    m.cityScore = (short)scalars[10];
    m.taxFund = (Quad)scalars[11];
    m.roadSpend = (Quad)scalars[12];
    m.fireSpend = (Quad)scalars[13];
    m.policeSpend = (Quad)scalars[14];
    m.poweredZoneCount = (short)scalars[15];
    m.unpoweredZoneCount = (short)scalars[16];
    m.coalPowerPop = (short)scalars[17];
    m.nuclearPowerPop = (short)scalars[18];
    m.roadTotal = (short)scalars[19];

    // Members that nothing in the monthly update reads (variant a_full only).
    if (aux) {
        short *hist[6] = { m.resHist, m.comHist, m.indHist, m.moneyHist, m.pollutionHist, m.crimeHist };
        int k = 0;
        for (int a = 0; a < 6; a++) for (int i = 0; i < 240; i++) hist[a][i] = (short)aux[k++];
        m.totalPopLast = (short)aux[k++];
        m.cityTaxAverage = (short)aux[k++];
        m.cityYes = (short)aux[k++];
        m.cityClass = (CityClass)aux[k++];
        m.crimeRamp = (short)aux[k++];
        m.pollutionRamp = (short)aux[k++];
        m.cashFlow = (short)aux[k++];
    }

    // Ledger.
#define LG_ON(i) ((ledger_mask >> (i)) & 1ULL)
    const int64_t *L = ledger;
    if (LG_ON(LG_SIM_CYCLE)) m.simCycle = (short)L[LG_SIM_CYCLE];
    if (LG_ON(LG_SPRITE_CYCLE)) m.spriteCycle = (short)L[LG_SPRITE_CYCLE];
    if (LG_ON(LG_DISASTERS)) m.setEnableDisasters(L[LG_DISASTERS] != 0);
    if (LG_ON(LG_INITIAL_EVAL)) m.doInitialEval = L[LG_INITIAL_EVAL] != 0;
    if (LG_ON(LG_TOTAL_POP)) m.totalPop = (short)L[LG_TOTAL_POP];
    if (LG_ON(LG_RES_HIST0)) m.resHist[0] = (short)L[LG_RES_HIST0];
    if (LG_ON(LG_RES_HIST1)) m.resHist[1] = (short)L[LG_RES_HIST1];
    if (LG_ON(LG_COM_HIST0)) m.comHist[0] = (short)L[LG_COM_HIST0];
    if (LG_ON(LG_COM_HIST1)) m.comHist[1] = (short)L[LG_COM_HIST1];
    if (LG_ON(LG_IND_HIST0)) m.indHist[0] = (short)L[LG_IND_HIST0];
    if (LG_ON(LG_IND_HIST1)) m.indHist[1] = (short)L[LG_IND_HIST1];
    if (LG_ON(LG_RES_CAP)) m.resCap = L[LG_RES_CAP] != 0;
    if (LG_ON(LG_COM_CAP)) m.comCap = L[LG_COM_CAP] != 0;
    if (LG_ON(LG_IND_CAP)) m.indCap = L[LG_IND_CAP] != 0;
    if (LG_ON(LG_NEED_HOSPITAL)) m.needHospital = (short)L[LG_NEED_HOSPITAL];
    if (LG_ON(LG_NEED_CHURCH)) m.needChurch = (short)L[LG_NEED_CHURCH];
    if (LG_ON(LG_ROAD_FUND)) m.roadFund = (Quad)L[LG_ROAD_FUND];
    if (LG_ON(LG_POLICE_FUND)) m.policeFund = (Quad)L[LG_POLICE_FUND];
    if (LG_ON(LG_FIRE_FUND)) m.fireFund = (Quad)L[LG_FIRE_FUND];
    if (LG_ON(LG_AUTO_BUDGET)) m.setAutoBudget(L[LG_AUTO_BUDGET] != 0);
    if (LG_ON(LG_FIRE_POP)) m.firePop = (short)L[LG_FIRE_POP];
    if (LG_ON(LG_CITY_CENTER_X)) m.cityCenterX = (short)L[LG_CITY_CENTER_X];
    if (LG_ON(LG_CITY_CENTER_Y)) m.cityCenterY = (short)L[LG_CITY_CENTER_Y];
    if (LG_ON(LG_POLLUTION_MAX_X)) m.pollutionMaxX = (short)L[LG_POLLUTION_MAX_X];
    if (LG_ON(LG_POLLUTION_MAX_Y)) m.pollutionMaxY = (short)L[LG_POLLUTION_MAX_Y];
    if (LG_ON(LG_FLOOD_COUNT)) m.floodCount = (short)L[LG_FLOOD_COUNT];
    if (LG_ON(LG_ABS_DIST)) m.absDist = (int)L[LG_ABS_DIST];
#undef LG_ON

    // Carried maps that are not observed.
    if ((map_mask & 1) && terrain) memcpy(m.terrainDensityMap.getBase(), terrain, MC_TERRAIN_N);
    if ((map_mask & 2) && comrate) memcpy(m.comRateMap.getBase(), comrate, MC_COMRATE_N * sizeof(int16_t));

    // Members derived from the observation (and the ledger).
    if (map_mask & 4) {
        // cityPop: mc_step_month sets it to the census population; after a load it is 0
        // until the initial evaluation runs (evalInit in simLoadInit).
        m.cityPop = m.doInitialEval ? 0 : (Quad)((m.resPop + (m.comPop + m.indPop) * 8L) * 20L);
        // crimeAverage (crimeScan): mean crime over blocks with land value > 0.
        // landValueAverage (pollutionTerrainLandValueScan): mean over blocks with land value > 0.
        // pollutionAverage (same scan): mean over blocks with pollution > 0.
        Quad ctot = 0, lvtot = 0, ptot = 0;
        int cnum = 0, pnum = 0;
        const Byte *lv = m.landValueMap.getBase(), *cr = m.crimeRateMap.getBase(), *pl = m.pollutionDensityMap.getBase();
        for (size_t i = 0; i < n2; i++) {
            if (lv[i] > 0) { cnum++; ctot += cr[i]; lvtot += lv[i]; }
            if (pl[i] > 0) { pnum++; ptot += pl[i]; }
        }
        m.crimeAverage = cnum > 0 ? (short)(ctot / cnum) : 0;
        m.landValueAverage = cnum > 0 ? (short)(lvtot / cnum) : 0;
        m.pollutionAverage = pnum > 0 ? (short)(ptot / pnum) : 0;
        // speedCycle counts ticks mod 1024 and spriteCycle counts ticks mod 65536 (as a short);
        // both are zeroed by init(), so speedCycle = spriteCycle mod 1024.
        m.speedCycle = (short)(((unsigned short)m.spriteCycle) % 1024);
    }

    m.phaseCycle = 0;
    m.initSimLoad = 0;

    // Sprites, in list order, with the per-type pointer the engine keeps.
    if (sprites && nsprites > 0) {
        SimSprite *tail = NULL;
        for (int i = 0; i < nsprites; i++) {
            const int32_t *r = sprites + (size_t)i * MC_SPRITE_FIELDS;
            SimSprite *sp = new SimSprite();
            sp->name = "";
            sp->type = r[0]; sp->frame = r[1]; sp->x = r[2]; sp->y = r[3];
            sp->width = r[4]; sp->height = r[5]; sp->xOffset = r[6]; sp->yOffset = r[7];
            sp->xHot = r[8]; sp->yHot = r[9]; sp->origX = r[10]; sp->origY = r[11];
            sp->destX = r[12]; sp->destY = r[13]; sp->count = r[14]; sp->soundCount = r[15];
            sp->dir = r[16]; sp->newDir = r[17]; sp->step = r[18]; sp->flag = r[19];
            sp->control = r[20]; sp->turn = r[21]; sp->accel = r[22]; sp->speed = r[23];
            sp->next = NULL;
            if (tail) tail->next = sp; else m.spriteList = sp;
            tail = sp;
            if (r[24] && sp->type >= 0 && sp->type < SPRITE_COUNT) m.globalSprites[sp->type] = sp;
        }
    }

    m.nextRandom = (UQuad)rng;
    h->monthBuildCost = 0;
    h->prevFunds = m.totalFunds;
    return 1;
}

} // extern "C"
