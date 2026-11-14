#!/usr/bin/env bash

export OPENAI_API_TYPE="open_ai"
export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="EMPTY"
export MODEL_NAME="Qwen3.6-35B-A3B"
# export MODEL_NAME="Qwen2.5-Coder-7B-Instruct"
# export MODEL_NAME="Ministral-3-14B-Reasoning-2512"
TEMPERATURE="0"
MAX_TOKENS="16384"
WORKERS="16"
DATA_ROOT="../SAGE-SQL/datasets/spider"
RUN_ID="run_1"
OUTPUT_DIR="outputs/macsql_spider_dev_${MODEL_NAME}_${RUN_ID}"

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p "$OUTPUT_DIR"
python run.py \
    --dataset_name spider \
    --dataset_mode dev \
    --input_file "$DATA_ROOT/dev.json" \
    --db_path "$DATA_ROOT/database" \
    --tables_json_path "$DATA_ROOT/tables.json" \
    --output_file "$OUTPUT_DIR/output.jsonl" \
    --log_file "$OUTPUT_DIR/run.log" \
    --temperature "$TEMPERATURE" \
    --max_tokens "$MAX_TOKENS" \
    --num_workers "$WORKERS" \
    "$@"
