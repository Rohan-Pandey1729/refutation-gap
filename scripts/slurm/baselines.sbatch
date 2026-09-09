#!/bin/bash
#SBATCH --job-name=slp-baselines
#SBATCH --account=CHANGE_ME
#SBATCH --partition=ckpt              # preemptable/free on klone; use compute for guaranteed
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=8:00:00
#SBATCH --output=runs/logs/%x-%A_%a.out
#SBATCH --error=runs/logs/%x-%A_%a.err
#SBATCH --array=0-4

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"
mkdir -p runs/logs

module load gcc 2>/dev/null || true
INSTANCES=(aes_mixcolumns aes_inv_mixcolumns anubis clefia_m0 clefia_m1)
INST=${INSTANCES[$SLURM_ARRAY_TASK_ID]}

python3 scripts/run_baselines.py \
  --instances "$INST" \
  --methods paar1 paar2 bp rnbp \
  --restarts "${RESTARTS:-1000}" \
  --node-cap "${NODE_CAP:-0}" \
  --seed "${SLURM_ARRAY_TASK_ID}" \
  --name "slurm_baselines_${INST}" \
  --notes "hyak array job ${SLURM_ARRAY_JOB_ID}"
