#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_TYPE="open_ai"
export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="EMPTY"
export MODEL_NAME="Qwen3.6-35B-A3B"
# export MODEL_NAME="Qwen2.5-Coder-7B-Instruct"
# export MODEL_NAME="Ministral-3-14B-Reasoning-2512"

MAX_TOKENS=16384
TEMPERATURE=0
NUM_THREADS="8"

DATASET_ROOT="../SAGE-SQL/datasets/bird/dev"
DATASET="bird_dev"
OUTPUT_DIR="./outputs/macsql_${DATASET}_${MODEL_NAME}_run_3"

mkdir -p "${OUTPUT_DIR}"

python run.py \
    --dataset_name bird \
    --dataset_mode dev \
    --input_file "${DATASET_ROOT}/dev.json" \
    --db_path "${DATASET_ROOT}/dev_databases" \
    --tables_json_path "${DATASET_ROOT}/dev_tables.json" \
    --output_file "${OUTPUT_DIR}/output_bird.json" \
    --log_file "${OUTPUT_DIR}/log.txt" \
    --temperature ${TEMPERATURE} \
    --max_tokens ${MAX_TOKENS} \
    --num_workers "${NUM_THREADS}"

echo "Generate SQL on env test data done!"