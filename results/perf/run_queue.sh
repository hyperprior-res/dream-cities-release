#!/bin/bash
# the GPU 1 queue (sequential). Every command is logged with its output to results/perf/logs/.
set -u
cd <repo>
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 PYTHONPATH=code:hpr-dream OMP_NUM_THREADS=6
PY=".venv/bin/python"
L=results/perf/logs
mkdir -p $L
run() {
  local name=$1; shift
  echo "[$(date -u +%H:%M:%S)] $name: $*" | tee -a $L/queue.log
  taskset -c 0-5 $PY "$@" > $L/$name.log 2>&1
  echo "[$(date -u +%H:%M:%S)] $name exit $?" | tee -a $L/queue.log
}
B=code/scripts/bench_fast.py
run equiv_50m $B equiv --size 50m --n 2000 --out results/perf/equiv_50m.json
run audit_50m $B speed --path audit --size 50m --chunk 256 --variants tag,raster,fused,fast
run rl_50m_200 $B speed --path rl --size 50m --envs 200 --variants tag-eager,tag,fast
run rl_50m_400 $B speed --path rl --size 50m --envs 400 --variants tag,fast
run fidelity_50m $B fidelity --batch 32 --out results/perf/fidelity_dev
run audit_15m $B speed --path audit --size 15m --chunk 256 --variants tag,fast
run audit_100m $B speed --path audit --size 100m --chunk 256 --variants tag,fast
run rl_15m_200 $B speed --path rl --size 15m --envs 200 --variants tag-eager,tag,fast
run rl_100m_200 $B speed --path rl --size 100m --envs 200 --variants tag-eager,tag,fast
run equiv_15m $B equiv --size 15m --n 2000 --out results/perf/equiv_15m.json
run equiv_100m $B equiv --size 100m --n 2000 --out results/perf/equiv_100m.json
echo "[$(date -u +%H:%M:%S)] queue done" | tee -a $L/queue.log
