#!/bin/bash
# the ninth GPU 1 queue: starts when the eighth queue (PID given as $1) has exited.
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
for s in 0 1 2 3; do run fidelity_50m_tagc_seed$s $B fidelity --batch 32 --eval-seed $s --variants tag,tagc --out results/perf/fidelity_dev; done
echo "[$(date -u +%H:%M:%S)] queue9 done" | tee -a $L/queue.log
