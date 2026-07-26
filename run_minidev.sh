#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASET_ROOT="${BIRD_MINIDEV_ROOT:-/home/linhx/workspace/kouan/datasets/bird/minidev/MINIDEV}"
OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/outputs/bird_minidev}"

export OPENAI_API_TYPE="${OPENAI_API_TYPE:-open_ai}"
export OPENAI_API_BASE="${OPENAI_API_BASE:-http://127.0.0.1:8000/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-EMPTY}"

if [[ -z "${MODEL_NAME:-}" ]]; then
    echo "MODEL_NAME is required and must match an id returned by ${OPENAI_API_BASE}/models." >&2
    echo "Example: MODEL_NAME=your-model-id ./run_minidev.sh" >&2
    exit 2
fi

for required_path in \
    "${DATASET_ROOT}/mini_dev_sqlite.json" \
    "${DATASET_ROOT}/dev_tables.json" \
    "${DATASET_ROOT}/dev_databases"; do
    if [[ ! -e "${required_path}" ]]; then
        echo "Required dataset path not found: ${required_path}" >&2
        exit 2
    fi
done

mkdir -p "${OUTPUT_DIR}"

run_args=(
    python "${PROJECT_ROOT}/run.py"
    --dataset_name bird
    --dataset_mode dev
    --input_file "${DATASET_ROOT}/mini_dev_sqlite.json"
    --db_path "${DATASET_ROOT}/dev_databases"
    --tables_json_path "${DATASET_ROOT}/dev_tables.json"
    --output_file "${OUTPUT_DIR}/output_bird.json"
    --log_file "${OUTPUT_DIR}/log.txt"
)

# For a one-sample smoke test, use START_POS=1533.
if [[ -n "${START_POS:-}" ]]; then
    run_args+=(--start_pos "${START_POS}")
fi

# Set WITHOUT_SELECTOR=1 to skip schema pruning calls.
if [[ "${WITHOUT_SELECTOR:-0}" == "1" ]]; then
    run_args+=(--without_selector)
fi

cd "${PROJECT_ROOT}"
echo "Model: ${MODEL_NAME}"
echo "API: ${OPENAI_API_BASE}"
echo "Dataset: ${DATASET_ROOT}"
echo "Output: ${OUTPUT_DIR}"
exec "${run_args[@]}"
