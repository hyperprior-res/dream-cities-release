# Modification Notice and Licensing (Micropolis Engine)

## 1. Modification Notice (GNU GPL v3 Section 5(a) & Electronic Arts Section 7 Terms)

This directory (`engine/`) contains a **modified version** of the Micropolis C++ simulation engine (upstream `github.com/SimHacker/MicropolisCore` commit `bd6e12eed6e148fe25270e7a4e2278f71a89f26c` and `github.com/SimHacker/micropolis` commit `c98f6b08519887b450d9be198bfca5237aab6d0c`). **This is a modified version of the program and is NOT the original program.** We claim no affiliation or association with Electronic Arts Inc. or its employees, and nothing in this repository is distributed under the SimCity mark.

Modifications made on **8 November 2026** by **HyperPrior Research, London**:

1. **`engine/src/micropolis.cpp`:**
   - Initialised `mapBase(NULL)`, `mopBase(NULL)`, history pointers (`resHist`..`miscHist`), `callback(NULL)`, `cellSrc(NULL)`, `cellDst(NULL)`, `spriteList(NULL)`, and `freeSprites(NULL)` in `Micropolis::Micropolis()` so the first `initMapArrays()` and `setCallback()` invocations do not read or delete uninitialised heap pointers.
   - Removed debug `printf("init")` in `Micropolis::init()`.
   - Added cleanup of allocated `SimSprite` pools (`destroyAllSprites()` and `freeSprites`) and `cellSrc` in `Micropolis::destroy()`.
2. **`engine/src/allocate.cpp`:**
   - Removed debug `printf("destroyMapArrays: mapBase: %p\n", mapBase)` in `Micropolis::destroyMapArrays()`.
3. **`engine/src/sprite.cpp`:**
   - Replaced raw `newPtr(sizeof(SimSprite))` (`malloc`) allocation in `Micropolis::newSprite()` with C++ `new SimSprite()` so that the `std::string name` member is properly constructed in native builds.
3. **`engine/src/random.cpp`:**
   - Replaced wall-clock `gettimeofday` seeding in `Micropolis::randomlySeedRandom()` with deterministic `seedRandom(1)` so `initWillStuff()` does not introduce wall-clock state during headless replay.
4. **`engine/src/evaluate.cpp`:**
   - Sized and zero-initialised `problemTable` and `problemTaken` in `Micropolis::cityEvaluation()` and `Micropolis::doProblems()` to `PROBNUM + 1` so that the `problem == PROBNUM` iteration in `Micropolis::voteProblems()` does not read an uninitialised stack word past `problemTable` (which otherwise causes stack-dependent PRNG divergence across calls).
5. **`engine/stub/emscripten.h` & `engine/stub/emscripten/bind.h`:**
   - Added two minimal header stubs (`EM_ASM` and `EM_ASM_` no-ops) to compile the C++ sources natively without Emscripten.
6. **`engine/c_api.cpp` & `engine/verify_replay.cpp`:**
   - Added a native C shared-library shim (`libmicropolis.so`) and headless determinism/throughput verification driver under GNU GPL v3 (with Electronic Arts Section 7 Additional Terms).

## 2. Trademark Attribution (Micropolis Public Name License, Version 1, October 1st, 2024)

Micropolis is a registered trademark of Micropolis Corporation (Micropolis GmbH) and is licensed here as a courtesy of the owner under the Micropolis Public Name License (<https://www.micropolis.com>). See [`LICENSE`](LICENSE) and [`MicropolisPublicNameLicense.md`](MicropolisPublicNameLicense.md) for the full licence texts.
