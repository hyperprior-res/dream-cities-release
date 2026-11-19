#!/bin/bash
# the second GPU 1 queue: starts when the first queue (PID given as $1) has exited.
set -u
cd <repo>
while kill -0 "$1" 2>/dev/null; do sleep 5; done
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 PYTHONPATH=code:hpr-dream OMP_NUM_THREADS=6
PY=".venv/bin/python"
L=results/perf/logs
S=<tmp>
run() {
  local name=$1; shift
  echo "[$(date -u +%H:%M:%S)] $name: $*" | tee -a $L/queue.log
  taskset -c 0-5 $PY "$@" > $L/$name.log 2>&1
  echo "[$(date -u +%H:%M:%S)] $name exit $?" | tee -a $L/queue.log
}
B=code/scripts/bench_fast.py
cp $S/p4.py results/perf/profile_timers.py
run profile_tag_256_a results/perf/profile_timers.py x 256 default 1
run profile_fast_256_a results/perf/profile_timers.py x 256 default 1 fast
run profile_fast_200_a results/perf/profile_timers.py x 200 default 1 fast
run audit_50m_c512 $B speed --path audit --size 50m --chunk 512 --variants tag,fast
echo "[$(date -u +%H:%M:%S)] queue2 done" | tee -a $L/queue.log
