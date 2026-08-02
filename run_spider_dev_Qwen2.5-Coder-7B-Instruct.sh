#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_TYPE="open_ai"
export OPENAI_API_BASE="http://127.0.0.1:8001/v1"
export OPENAI_API_KEY="EMPTY"
export MODEL_NAME="Qwen2.5-Coder-7B-Instruct"


MAX_TOKENS=16384
TEMPERATURE=0

DATASET_ROOT="../datasets/spider"
OUTPUT_DIR="./outputs/spider_dev_${MODEL_NAME}"

mkdir -p "${OUTPUT_DIR}"

python run.py \
    --dataset_name spider \
    --dataset_mode dev \
    --input_file "${DATASET_ROOT}/dev.json" \
    --db_path "${DATASET_ROOT}/database" \
    --tables_json_path "${DATASET_ROOT}/tables.json" \
    --output_file "${OUTPUT_DIR}/output_spider.json" \
    --log_file "${OUTPUT_DIR}/log.txt" \
    --temperature ${TEMPERATURE} \
    --max_tokens ${MAX_TOKENS}

echo "Generate SQL on Spider dev data done!"
