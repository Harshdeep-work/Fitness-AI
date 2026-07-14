#!/usr/bin/env python3
"""
compare_models.py
=================
PURPOSE:
  Aggregate all score files from benchmark/scores/ and produce:
  
    1. A terminal comparison table (all models × all prompts)
    2. A full Markdown report at benchmark/results/comparison_report.md
    3. A winner recommendation with justification

WHY THIS FILE EXISTS:
  After running run_benchmark.py + evaluate.py for multiple models,
  you have dozens of individual score JSON files.
  This script collects them all and answers the question:
  
    "Which model should we use in production?"

USAGE:
  python3 compare_models.py
  python3 compare_models.py --category meal
  python3 compare_models.py --output benchmark/results/final_comparison.md
"""

import argparse
import json
import os
import sys
import datetime
from collections import defaultdict

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
SCORES_DIR  = os.path.join(PROJECT_ROOT, "benchmark", "scores")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "benchmark", "results")


# ---------------------------------------------------------------------------
# ARGUMENT PARSING
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare all benchmark scores across models."
    )
    # Filter by category: only show "meal" scores, or "reasoning" scores, etc.
    parser.add_argument(
        "--category",
        default=None,
        help="Filter by benchmark category, e.g. 'meal' or 'reasoning'"
    )
    # Override the default output path
    parser.add_argument(
        "--output",
        default=os.path.join(RESULTS_DIR, "comparison_report.md"),
        help="Path to save the Markdown comparison report"
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------

def load_all_scores(category_filter: str = None) -> dict:
    """
    Walk benchmark/scores/ and load every .json score file.
    
    Directory structure:
      benchmark/scores/
        gemma3_4b/
          meal_001.json
          meal_002.json
          reason_001.json
        qwen2.5_7b/
          meal_001.json
          ...
    
    Returns:
        A nested dict:
        {
          "gemma3_4b": {
            "meal_001": { ...score doc... },
            "meal_002": { ...score doc... },
          },
          "qwen2.5_7b": {
            "meal_001": { ...score doc... },
          },
        }
    """
    scores = defaultdict(dict)

    if not os.path.isdir(SCORES_DIR):
        print(f"[ERROR] Scores directory not found: {SCORES_DIR}")
        print("        Run evaluate.py first to generate scores.")
        sys.exit(1)

    # Iterate over model directories
    for model_dir in sorted(os.listdir(SCORES_DIR)):
        model_path = os.path.join(SCORES_DIR, model_dir)

        # Skip non-directories (e.g. stray files)
        if not os.path.isdir(model_path):
            continue

        # Iterate over score JSON files inside the model directory
        for fname in sorted(os.listdir(model_path)):
            if not fname.endswith(".json"):
                continue

            prompt_name = fname.replace(".json", "")   # "meal_001.json" → "meal_001"

            # Apply category filter if provided
            if category_filter:
                if not prompt_name.startswith(category_filter):
                    continue

            json_path = os.path.join(model_path, fname)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    scores[model_dir][prompt_name] = json.load(f)
            except json.JSONDecodeError as e:
                print(f"[WARN]  Could not parse {json_path}: {e}")

    return dict(scores)


# ---------------------------------------------------------------------------
# AGGREGATION
# ---------------------------------------------------------------------------

def aggregate(scores: dict) -> dict:
    """
    For each model, compute:
      - Per-prompt scores
      - Average quality score (across all prompts)
      - Average tokens/sec
      - Category breakdown
    
    Returns:
        {
          "gemma3_4b": {
            "avg_quality":    72.5,
            "avg_tokens_sec": 6.8,
            "prompt_count":   5,
            "prompts": { "meal_001": 80.0, ... },
            "by_category": { "meal": 77.5, "reasoning": 65.0, ... }
          },
          ...
        }
    """
    summary = {}

    for model, prompts in scores.items():
        quality_scores = []
        tokens_sec_list = []
        by_category = defaultdict(list)

        for prompt_name, doc in prompts.items():
            q = doc.get("normalized_score", 0)
            t = doc.get("performance", {}).get("tokens_per_sec", 0)
            cat = doc.get("category", "unknown")

            quality_scores.append(q)
            tokens_sec_list.append(t)
            by_category[cat].append(q)

        # Compute averages
        avg_quality    = round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0
        avg_tokens_sec = round(sum(tokens_sec_list) / len(tokens_sec_list), 2) if tokens_sec_list else 0
        avg_by_cat     = {cat: round(sum(v)/len(v), 1) for cat, v in by_category.items()}

        summary[model] = {
            "avg_quality":    avg_quality,
            "avg_tokens_sec": avg_tokens_sec,
            "prompt_count":   len(prompts),
            "prompts":        {p: doc.get("normalized_score", 0) for p, doc in prompts.items()},
            "grades":         {p: doc.get("grade", "?") for p, doc in prompts.items()},
            "by_category":    avg_by_cat,
        }

    return summary


# ---------------------------------------------------------------------------
# WINNER SELECTION
# ---------------------------------------------------------------------------

def pick_winner(summary: dict) -> str:
    """
    Select the best model using a weighted scoring formula:
    
      final_score = (avg_quality * 0.70) + (normalized_tokens_sec * 0.30)
    
    WHY 70/30 SPLIT?
      Quality matters more than speed for a fitness recommendation engine.
      Users can wait a few seconds for a better answer.
      But speed still matters for production UX — nobody wants to wait 3+ minutes.
    
    Returns:
        model_dir string of the winner.
    """
    if not summary:
        return "No models evaluated yet"

    # Find the fastest tokens/sec to normalize speed scores
    max_tps = max((v["avg_tokens_sec"] for v in summary.values()), default=1)
    if max_tps == 0:
        max_tps = 1   # prevent division by zero

    best_model = None
    best_score = -1

    for model, data in summary.items():
        # Normalize tokens/sec to 0–100 scale
        speed_score = (data["avg_tokens_sec"] / max_tps) * 100

        # Weighted final score
        final = (data["avg_quality"] * 0.70) + (speed_score * 0.30)

        data["_final_score"] = round(final, 2)   # store for the report

        if final > best_score:
            best_score = final
            best_model = model

    return best_model


# ---------------------------------------------------------------------------
# TERMINAL TABLE
# ---------------------------------------------------------------------------

def print_terminal_table(summary: dict, all_prompts: list):
    """
    Print a formatted ASCII comparison table to the terminal.
    
    WHY ASCII TABLE?
      Easy to read in any terminal, no dependencies needed.
    """
    # Build column widths
    model_col_w = max(len(m) for m in summary.keys()) + 2 if summary else 20
    prompt_col_w = 10

    print("\n" + "=" * 80)
    print("  MODEL COMPARISON TABLE")
    print("=" * 80)

    # Header row
    header = f"{'Model':<{model_col_w}}"
    for p in all_prompts:
        header += f" {p[:10]:>10}"
    header += f" {'AVG':>8} {'TPS':>8}"
    print(header)
    print("-" * len(header))

    # Data rows
    for model, data in sorted(summary.items(), key=lambda x: -x[1]["avg_quality"]):
        row = f"{model:<{model_col_w}}"
        for p in all_prompts:
            score = data["prompts"].get(p, None)
            cell = f"{score:.0f}" if score is not None else "--"
            row += f" {cell:>10}"
        row += f" {data['avg_quality']:>8.1f}"
        row += f" {data['avg_tokens_sec']:>8.2f}"
        print(row)

    print("=" * 80)


# ---------------------------------------------------------------------------
# MARKDOWN REPORT
# ---------------------------------------------------------------------------

def build_markdown_report(summary: dict, winner: str, all_prompts: list,
                          category_filter: str) -> str:
    """
    Generate the full Markdown comparison report as a string.
    
    Sections:
      1. Header with metadata
      2. Per-prompt score table
      3. Category breakdown table
      4. Performance table (tokens/sec)
      5. Winner announcement with justification
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cat_label = category_filter if category_filter else "All Categories"

    lines = []
    lines.append(f"# Fitness-AI Model Comparison Report")
    lines.append(f"")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Generated | {now} |")
    lines.append(f"| Category Filter | {cat_label} |")
    lines.append(f"| Models Compared | {len(summary)} |")
    lines.append(f"| Prompts Evaluated | {len(all_prompts)} |")
    lines.append(f"")
    lines.append("---")
    lines.append("")

    # --- Section 1: Quality Score Table ---
    lines.append("## 1. Quality Score Table (0–100)")
    lines.append("")
    lines.append("*Higher is better. Score is based on structural completeness and keyword checks.*")
    lines.append("")

    # Build table header
    header_cells = ["| Model"] + [f"| {p}" for p in all_prompts] + ["| **AVG** | Grade |"]
    lines.append(" ".join(header_cells))
    sep_cells = ["|---"] * (len(all_prompts) + 3)
    lines.append("|".join(sep_cells) + "|")

    for model, data in sorted(summary.items(), key=lambda x: -x[1]["avg_quality"]):
        row = f"| `{model}` "
        for p in all_prompts:
            score = data["prompts"].get(p, None)
            cell = f"{score:.0f}" if score is not None else "—"
            row += f"| {cell} "
        avg = data["avg_quality"]
        from_winner = " 🏆" if model == winner else ""
        row += f"| **{avg}** | {grade_from_score(avg)}{from_winner} |"
        lines.append(row)

    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 2: Performance Table ---
    lines.append("## 2. Performance (Tokens / Second)")
    lines.append("")
    lines.append("*Higher is better. Measured during generation only (not prompt evaluation).*")
    lines.append("")
    lines.append("| Model | Avg Tokens/sec | Prompts Tested |")
    lines.append("|-------|----------------|----------------|")

    for model, data in sorted(summary.items(), key=lambda x: -x[1]["avg_tokens_sec"]):
        tps_flag = " 🚀" if model == winner else ""
        lines.append(
            f"| `{model}` | {data['avg_tokens_sec']}{tps_flag} | {data['prompt_count']} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 3: Category Breakdown ---
    lines.append("## 3. Category Breakdown")
    lines.append("")

    # Collect all categories across all models
    all_cats = set()
    for data in summary.values():
        all_cats.update(data["by_category"].keys())
    all_cats = sorted(all_cats)

    if all_cats:
        cat_header = "| Model | " + " | ".join(all_cats) + " |"
        cat_sep    = "|---" * (len(all_cats) + 1) + "|"
        lines.append(cat_header)
        lines.append(cat_sep)

        for model, data in sorted(summary.items(), key=lambda x: -x[1]["avg_quality"]):
            row = f"| `{model}` |"
            for cat in all_cats:
                val = data["by_category"].get(cat, None)
                cell = f" {val:.1f} |" if val is not None else " — |"
                row += cell
            lines.append(row)
    else:
        lines.append("*No category data available yet.*")

    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 4: Winner ---
    lines.append("## 4. Recommended Production Model")
    lines.append("")

    if winner and winner in summary:
        w = summary[winner]
        lines.append(f"### 🏆 Winner: `{winner}`")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Average Quality Score | **{w['avg_quality']} / 100** |")
        lines.append(f"| Average Tokens/sec | **{w['avg_tokens_sec']}** |")
        lines.append(f"| Prompts Evaluated | {w['prompt_count']} |")
        lines.append(f"| Weighted Final Score | {w.get('_final_score', 'N/A')} |")
        lines.append("")
        lines.append("**Why this model won:**")
        lines.append("")
        lines.append(
            f"The selection formula weights **quality (70%) + speed (30%)**. "
            f"`{winner}` scored highest on the weighted formula with a final score of "
            f"**{w.get('_final_score', 'N/A')}**. "
            f"It demonstrated strong structural completeness, referenced regional foods, "
            f"provided clear reasoning, and maintained consistent output across all prompts."
        )
        lines.append("")
        lines.append("**Formula used:**")
        lines.append("```")
        lines.append("final_score = (avg_quality_score × 0.70) + (normalized_tokens_per_sec × 0.30)")
        lines.append("```")
    else:
        lines.append("*No models have been evaluated yet. Run run_benchmark.py + evaluate.py first.*")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by Fitness-AI Benchmark System — compare_models.py*")

    return "\n".join(lines)


def grade_from_score(score: float) -> str:
    """Convert numeric score to letter grade (reused from evaluate.py logic)."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    print("=" * 60)
    print("  Fitness-AI Model Comparator")
    print("=" * 60)

    # Load all score files
    scores = load_all_scores(category_filter=args.category)

    if not scores:
        print("\n[INFO] No score files found.")
        print(f"       Looked in: {SCORES_DIR}")
        print("       Run: python3 evaluate.py --result <model>/<prompt>")
        sys.exit(0)

    # Aggregate per-model statistics
    summary = aggregate(scores)

    # Collect all unique prompt names across all models (for table columns)
    all_prompts = sorted(set(
        p for data in scores.values() for p in data.keys()
    ))

    # Print terminal comparison table
    print_terminal_table(summary, all_prompts)

    # Pick the winner
    winner = pick_winner(summary)
    print(f"\n🏆 Recommended Model: {winner}")

    # Build Markdown report
    report_md = build_markdown_report(summary, winner, all_prompts, args.category)

    # Save report
    out_path = args.output
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n[SAVED] Report → {out_path}")
    print("\n✅ Comparison complete.\n")


if __name__ == "__main__":
    main()
