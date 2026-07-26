#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_TYPE="open_ai"
export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="EMPTY"
export MODEL_NAME="Qwen3.6-35B-A3B"

MAX_TOKENS=16384
TEMPERATURE=0

DATASET_ROOT="/root/autodl-tmp/workspace/kouan/datasets/bird/dev"
OUTPUT_DIR="./outputs/bird_dev_Qwen3.6-35B-A3B"

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
    --max_tokens ${MAX_TOKENS}

echo "Generate SQL on env test data done!"