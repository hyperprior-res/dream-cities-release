#!/bin/bash
# the sixth GPU 1 queue: starts when the fifth queue (PID given as $1) has exited.
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
run audit_50m_small16 $B speed --path audit --size 50m --chunk 16 --K 8 --buckets 16 --plans 16 --reps 3 --variants tag,fast
run rl_50m_40 $B speed --path rl --size 50m --envs 40 --variants tag,fast
echo "[$(date -u +%H:%M:%S)] queue6 done" | tee -a $L/queue.log
