/* verify_replay.cpp
 *
 * MODIFIED / DERIVED WORK NOTICE (per GNU GPL v3 Section 5(a) and Electronic
 * Arts Additional Terms under GPL Section 7):
 * Created on 2026-11-08 by HyperPrior Research to verify bit-exact headless
 * replay across all 32 bundled cities over 240 months with disasters enabled
 * (within process and across processes) and measure per-core and multi-core
 * city-month throughput.
 * Released under the GNU General Public License v3 with Electronic Arts
 * Section 7 Additional Terms (see engine/LICENSE).
 */

#include "micropolis.h"
#include "callback.h"
#include "tool.h"
#include <chrono>
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <new>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <sys/wait.h>
#include <unistd.h>

static uint64_t hashMap(Micropolis &m) {
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

struct CityRunResult {
    std::vector<uint64_t> monthHashes;
    long startPop;
    long endPop;
    long startFunds;
    long endFunds;
    double elapsedSec;
};

static CityRunResult runCity(const char* path, int seed, int months, bool disasters) {
    CityRunResult res;
    res.monthHashes.reserve(months);
    void *mem = calloc(1, sizeof(Micropolis));
    Micropolis *m = new (mem) Micropolis();
    m->setCallback(new ConsoleCallback(), emscripten::val::null());
    m->init();
    m->seedRandom(seed);
    if (!m->loadCity(path)) {
        fprintf(stderr, "Failed to load city: %s\n", path);
        exit(2);
    }
    m->seedRandom(seed);
    m->setSpeed(3);
    m->setPasses(1);
    m->setEnableDisasters(disasters);
    res.startFunds = m->totalFunds;

    // Run 1 evaluation tick to populate startPop if needed
    long startT = m->cityTime;
    auto t0 = std::chrono::high_resolution_clock::now();
    for (int mo = 0; mo < months; mo++) {
        long targetT = startT + (long)(mo + 1) * 4;
        while (m->cityTime < targetT || m->phaseCycle != 0) {
            m->simTick();
        }
        if (mo == 0) res.startPop = m->cityPop;
        res.monthHashes.push_back(hashMap(*m));
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    res.endPop = m->cityPop;
    res.endFunds = m->totalFunds;
    res.elapsedSec = std::chrono::duration<double>(t1 - t0).count();
    m->~Micropolis();
    free(mem);
    return res;
}

int main(int argc, char** argv) {
    if (argc >= 2 && strcmp(argv[1], "--child") == 0) {
        // Child mode: run one city and write 240 uint64 hashes to stdout
        const char* cityPath = argv[2];
        int seed = atoi(argv[3]);
        int months = atoi(argv[4]);
        CityRunResult r = runCity(cityPath, seed, months, true);
        fwrite(r.monthHashes.data(), sizeof(uint64_t), r.monthHashes.size(), stdout);
        fflush(stdout);
        return 0;
    }

    int months = 240;
    int seed = 7;
    int altSeed = 8;
    std::vector<std::string> cities;
    for (int i = 1; i < argc; i++) {
        cities.push_back(argv[i]);
    }
    if (cities.empty()) {
        fprintf(stderr, "Usage: %s data/cities/*.cty\n", argv[0]);
        return 1;
    }

    printf("Verifying bit-exact replay on %zu bundled cities over %d months (disasters=true)...\n",
           cities.size(), months);

    int withinProcMatches = 0;
    int crossProcMatches = 0;
    int altSeedDiffers = 0;
    int totalMonthChecks = 0;
    int totalMismatches = 0;
    double totalSec = 0.0;

    FILE *jf = fopen("results/oracle/determinism_32cities.json", "w");
    fprintf(jf, "{\n  \"months\": %d,\n  \"seed\": %d,\n  \"alt_seed\": %d,\n  \"disasters_enabled\": true,\n  \"cities\": [\n",
            months, seed, altSeed);

    for (size_t idx = 0; idx < cities.size(); idx++) {
        const char* cpath = cities[idx].c_str();
        const char* base = strrchr(cpath, '/');
        base = base ? base + 1 : cpath;

        CityRunResult r1 = runCity(cpath, seed, months, true);
        CityRunResult r2 = runCity(cpath, seed, months, true);
        CityRunResult r3 = runCity(cpath, altSeed, months, true);
        totalSec += r1.elapsedSec;

        // Spawn child process to verify cross-process determinism
        int pipefd[2];
        if (pipe(pipefd) != 0) { perror("pipe"); exit(1); }
        pid_t pid = fork();
        if (pid == 0) {
            close(pipefd[0]);
            dup2(pipefd[1], STDOUT_FILENO);
            close(pipefd[1]);
            char seedStr[32], moStr[32];
            snprintf(seedStr, sizeof(seedStr), "%d", seed);
            snprintf(moStr, sizeof(moStr), "%d", months);
            execl(argv[0], argv[0], "--child", cpath, seedStr, moStr, (char*)NULL);
            perror("execl");
            _exit(1);
        }
        close(pipefd[1]);
        std::vector<uint64_t> childHashes(months, 0);
        size_t bytesNeeded = months * sizeof(uint64_t);
        uint8_t *buf = (uint8_t*)childHashes.data();
        size_t got = 0;
        while (got < bytesNeeded) {
            ssize_t n = read(pipefd[0], buf + got, bytesNeeded - got);
            if (n <= 0) break;
            got += n;
        }
        close(pipefd[0]);
        int status = 0;
        waitpid(pid, &status, 0);

        bool wpOk = true;
        bool cpOk = (got == bytesNeeded);
        for (int mo = 0; mo < months; mo++) {
            totalMonthChecks++;
            if (r1.monthHashes[mo] != r2.monthHashes[mo]) { wpOk = false; totalMismatches++; }
            if (!cpOk || r1.monthHashes[mo] != childHashes[mo]) { cpOk = false; totalMismatches++; }
        }
        bool altDiff = (r1.monthHashes.back() != r3.monthHashes.back());
        if (wpOk) withinProcMatches++;
        if (cpOk) crossProcMatches++;
        if (altDiff) altSeedDiffers++;

        double msPerMonth = 1000.0 * r1.elapsedSec / months;
        printf("  [%2zu/%2zu] %-28s %.3f ms/mo | pop %6ld -> %6ld | funds %6ld -> %6ld | within=%s cross=%s alt_diff=%s | final=%016llx\n",
               idx + 1, cities.size(), base, msPerMonth,
               r1.startPop, r1.endPop, r1.startFunds, r1.endFunds,
               wpOk ? "OK" : "FAIL", cpOk ? "OK" : "FAIL", altDiff ? "YES" : "NO",
               (unsigned long long)r1.monthHashes.back());

        fprintf(jf, "    {\"city\": \"%s\", \"ms_per_month\": %.4f, \"start_pop\": %ld, \"end_pop\": %ld, \"start_funds\": %ld, \"end_funds\": %ld, \"within_process_exact\": %s, \"cross_process_exact\": %s, \"alt_seed_differs\": %s, \"final_hash\": \"%016llx\"}%s\n",
                base, msPerMonth, r1.startPop, r1.endPop, r1.startFunds, r1.endFunds,
                wpOk ? "true" : "false", cpOk ? "true" : "false", altDiff ? "true" : "false",
                (unsigned long long)r1.monthHashes.back(),
                (idx + 1 < cities.size()) ? "," : "");
    }

    double meanMsPerMonth = 1000.0 * totalSec / (cities.size() * months);
    double singleCoreMonthsPerSec = (cities.size() * months) / totalSec;

    // Measure 20-core parallel throughput on 20 threads (each running 32 cities x 60 months = 1920 months, total 38,400 months)
    int numThreads = 20;
    int parMonths = 60;
    auto tp0 = std::chrono::high_resolution_clock::now();
    std::vector<std::thread> workers;
    for (int t = 0; t < numThreads; t++) {
        workers.emplace_back([&, t]() {
            for (size_t idx = 0; idx < cities.size(); idx++) {
                runCity(cities[idx].c_str(), seed + t * 100 + (int)idx, parMonths, true);
            }
        });
    }
    for (auto &th : workers) th.join();
    auto tp1 = std::chrono::high_resolution_clock::now();
    double parSec = std::chrono::duration<double>(tp1 - tp0).count();
    long totalParMonths = (long)numThreads * (long)cities.size() * (long)parMonths;
    double multiCoreMonthsPerSec = totalParMonths / parSec;

    fprintf(jf, "  ],\n  \"summary\": {\n    \"num_cities\": %zu,\n    \"months_per_city\": %d,\n    \"total_month_checks\": %d,\n    \"within_process_matches\": %d,\n    \"cross_process_matches\": %d,\n    \"alt_seed_differs\": %d,\n    \"total_mismatches\": %d,\n    \"mean_ms_per_month_single_core\": %.4f,\n    \"single_core_city_months_per_sec\": %.1f,\n    \"parallel_threads\": %d,\n    \"parallel_city_months_per_sec\": %.1f\n  }\n}\n",
            cities.size(), months, totalMonthChecks, withinProcMatches, crossProcMatches,
            altSeedDiffers, totalMismatches, meanMsPerMonth, singleCoreMonthsPerSec,
            numThreads, multiCoreMonthsPerSec);
    fclose(jf);

    printf("\n=== SUMMARY ===\n");
    printf("Cities verified: %d/%zu within-process, %d/%zu cross-process (%d total month checks, %d mismatches)\n",
           withinProcMatches, cities.size(), crossProcMatches, cities.size(), totalMonthChecks, totalMismatches);
    printf("Single-core throughput: %.3f ms/city-month (%.1f city-months/sec)\n",
           meanMsPerMonth, singleCoreMonthsPerSec);
    printf("20-core parallel throughput: %.1f city-months/sec (1M transitions in %.1f sec)\n",
           multiCoreMonthsPerSec, 1e6 / multiCoreMonthsPerSec);

    return (totalMismatches == 0) ? 0 : 1;
}
