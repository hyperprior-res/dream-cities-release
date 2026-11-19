CXX ?= g++
CXXFLAGS := -O3 -DNDEBUG -std=c++17 -fPIC -pthread -I stub -I src
ENGINE_SRCS := $(filter-out src/emscripten.cpp, $(wildcard src/*.cpp))

.PHONY: all clean verify

all: libmicropolis.so verify_replay

libmicropolis.so: c_api.cpp $(ENGINE_SRCS)
	$(CXX) $(CXXFLAGS) -shared c_api.cpp $(ENGINE_SRCS) -o libmicropolis.so

verify_replay: verify_replay.cpp $(ENGINE_SRCS)
	$(CXX) $(CXXFLAGS) verify_replay.cpp $(ENGINE_SRCS) -o verify_replay

verify: verify_replay
	cd .. && ./engine/verify_replay data/cities/*.cty

clean:
	rm -f libmicropolis.so verify_replay
