#!/bin/bash
#SBATCH --job-name=slp-sweep
#SBATCH --account=CHANGE_ME
#SBATCH --partition=ckpt
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=4:00:00
#SBATCH --output=runs/logs/%x-%A_%a.out
#SBATCH --array=0-119%40

# Randomized-restart sweep. Each array task uses a distinct seed block, so
# results across tasks are independent and can be pooled safely.
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"
mkdir -p runs/logs
module load gcc 2>/dev/null || true

python3 scripts/run_baselines.py \
  --suite "${SUITE:-random}" \
  --methods rnbp paar2 \
  --restarts "${RESTARTS:-500}" \
  --seed "$SLURM_ARRAY_TASK_ID" \
  --name "sweep_${SLURM_ARRAY_TASK_ID}" \
  --notes "seed block ${SLURM_ARRAY_TASK_ID} of job ${SLURM_ARRAY_JOB_ID}"
