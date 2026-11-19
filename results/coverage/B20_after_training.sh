#!/bin/bash
# B20 (round 2), NOT RUN BY B20. What follows the training of os_50m_cov (paper section 6), in order.
# Training itself was launched by B20 (section A, for the record). B and C mirror what every other checkpoint gets:
# wm2-cache/audit/queue3_gpu0_20261111.sh (audit) and results/rl/queue_rented_batch1.json in wm2-fleet (RL).
# Model code. The checkpoint's training commit is tag ladder-v2-cov (0b822c4: ladder-v2 + the union loader; dc/model.py
# byte-identical to ladder-v2). run_audit.py loads a ladder checkpoint with --model-src auto = that commit, and dc.fast
# accepts it: results/coverage/fast_check_cov.json (tiny checkpoint written by the cov checkout's Trainer, loaded as
# run_audit does, Trunk/Block/ScalarStage sources equal the ladder-v2 reference, fused trunk = tag trunk exactly on CPU).
# The RL runs name the same commit explicitly (--model-src ladder-v2-cov).
set -u
CK=<cache>/ckpt/ladder_v2
PYV=<repo>/.venv/bin/python

# ---- A. training  --
#   cd <home>/development/wm2-ladder-v2-cov && nohup $PYV code/scripts/ladder.py \
#       --queue <cache>/ckpt/queue_cov_gpu0.json --gpu 0 --ckpt-root $CK \
#       >> <cache>/ckpt/cov_gpu0.out 2>&1 &
#   index train_full_cov12 = wm2-cache/data/train_full_cov12 (union.json: train_full, train_cov, train_cov2);
#   bookkeeping caches wm2-cache/ckpt/bookkeeping_cache/{train_full,train_cov,train_cov2}.npz
#   checkpoints $CK/os_50m_cov/samples_*.pt; logs $CK/os_50m_cov.out, $CK/ladder_gpu0.log; after training the runner
#   evaluates fidelity as the ladder did (dev, test, train_eval) into the cov checkout's results/fidelity/ladder/os_50m_cov

# ---- B. audit of the final checkpoint (same plan as every other checkpoint, then cem_seeded, then the reference) --
cd <repo> || exit 1
T=<repo>/data/tasks_v2_H24.json
LOG=<cache>/audit/logs
W=<cache>/audit/work/ladder
REF=results/audit/engine_reference/tasks_v2_H24
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=hpr-dream:code
PY=.venv/bin/python
ENG="--workers 10 --remote host-b --remote-workers 22"
step() { name=$1; shift; echo "$(date -u +%FT%TZ) START $name"; "$@" > $LOG/$name.log 2>&1 && echo "$(date -u +%FT%TZ) DONE $name" || echo "$(date -u +%FT%TZ) FAILED $name (see $LOG/$name.log)"; }
RC=os_50m_cov/samples_006000000; N=$(echo $RC | tr '/' '_')
[ -s $CK/$RC.pt.sha256 ] || { echo "no final checkpoint $CK/$RC.pt yet"; exit 1; }
mkdir -p $W/${RC}_lean
step ${N}_lean $PY -u code/scripts/run_audit.py --plan amendment2 --checkpoint $CK/$RC.pt --tasks $T --methods random,best_of_n,random_verdict --subset-n 0 --work $W/${RC}_lean --out results/audit/ladder/$RC/tasks_v2_H24 --device cuda:0 $ENG
step ${N}_reference $PY code/scripts/run_audit.py --compare-reference results/audit/ladder/$RC/tasks_v2_H24 --reference $REF/B_economy
mkdir -p $W/${RC}_cem_seeded && [ -e $W/${RC}_cem_seeded/samples ] || ln -s $W/${RC}_lean/samples $W/${RC}_cem_seeded/samples
step ${N}_cem_seeded $PY -u code/scripts/run_audit.py --plan amendment2 --checkpoint $CK/$RC.pt --tasks $T --methods cem_seeded --subset-n 0 --work $W/${RC}_cem_seeded --out results/audit/ladder/$RC/tasks_v2_H24_cem_seeded --device cuda:0 $ENG
step ${N}_cem_seeded_reference $PY code/scripts/run_audit.py --compare-reference results/audit/ladder/$RC/tasks_v2_H24_cem_seeded --reference $REF/cem_seeded_B_economy

# ---- C. RL: 15 runs (five families x three seeds), committed learner (dc.rl.FROZEN, the --make default), from the
# fleet checkout (tag rl-v1); queue and checkpoint list kept outside that checkout
cd <home>/development/wm2-fleet || exit 1
echo "$CK/os_50m_cov/samples_006000000.pt" > <cache>/rl/ckpts_cov.txt
PYTHONPATH=code $PYV code/scripts/rl_queue.py --make --ckpts <cache>/rl/ckpts_cov.txt \
    --tasks grow,solvent,treasury,recover,power --seeds 0,1,2 --tasks-file data/tasks_v2_H24.json \
    --model-src ladder-v2-cov --out <cache>/rl/queue_cov_gpu0.json
PYTHONPATH=code $PYV code/scripts/rl_queue.py --queue <cache>/rl/queue_cov_gpu0.json --gpu 0
