#!/bin/bash
# the fourth GPU 1 queue: starts when the third queue (PID given as $1) has exited.
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
run tailcheck_50m $B tailcheck --size 50m --n 2000 --batch 128
run audit_50m_tail $B speed --path audit --size 50m --chunk 256 --variants fast,fast-tail
run rl_50m_200_tail $B speed --path rl --size 50m --envs 200 --variants fast,fast-tail
echo "[$(date -u +%H:%M:%S)] queue4 done" | tee -a $L/queue.log
