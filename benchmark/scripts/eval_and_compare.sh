#!/usr/bin/env bash
# eval_and_compare.sh
# ====================
# PURPOSE:
#   After run_benchmark.py finishes for a model, run this script to:
#   1. Evaluate every result file for that model
#   2. Generate the cross-model comparison report
#
# USAGE:
#   bash benchmark/scripts/eval_and_compare.sh gemma3_4b
#   bash benchmark/scripts/eval_and_compare.sh qwen3_4b
#   bash benchmark/scripts/eval_and_compare.sh all          ← evaluate everything

set -e   # exit on any error

MODEL_DIR="${1:-all}"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPTS_DIR/../.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/benchmark/results"

echo "=============================="
echo " Fitness-AI: Evaluate & Compare"
echo " Model Dir : $MODEL_DIR"
echo "=============================="

if [ "$MODEL_DIR" = "all" ]; then
    # Evaluate every model directory inside benchmark/results/
    for dir in "$RESULTS_DIR"/*/; do
        model=$(basename "$dir")
        # Skip non-model directories like 'comparison_report.md'
        [ -d "$dir" ] || continue
        echo ""
        echo "--- Evaluating model: $model ---"
        for json_file in "$dir"*.json; do
            [ -f "$json_file" ] || continue
            prompt_name=$(basename "$json_file" .json)
            echo "  -> $prompt_name"
            python3 "$SCRIPTS_DIR/evaluate.py" --result "$model/$prompt_name"
        done
    done
else
    # Evaluate only the specified model directory
    dir="$RESULTS_DIR/$MODEL_DIR"
    if [ ! -d "$dir" ]; then
        echo "[ERROR] Directory not found: $dir"
        exit 1
    fi
    for json_file in "$dir"*.json; do
        [ -f "$json_file" ] || continue
        prompt_name=$(basename "$json_file" .json)
        echo "  -> $prompt_name"
        python3 "$SCRIPTS_DIR/evaluate.py" --result "$MODEL_DIR/$prompt_name"
    done
fi

echo ""
echo "=============================="
echo " Running Cross-Model Comparator"
echo "=============================="
python3 "$SCRIPTS_DIR/compare_models.py"

echo ""
echo "✅ eval_and_compare.sh complete."
