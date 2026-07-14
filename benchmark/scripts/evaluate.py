#!/usr/bin/env python3
"""
evaluate.py
===========
PURPOSE:
  Score a single saved benchmark result (a .json file produced by run_benchmark.py)
  against a set of evaluation criteria defined in a scorecard YAML file.

  The scoring is done by checking the model's response text for required
  keywords, sections, and structural elements — no secondary LLM needed.

  Output: a JSON score file at benchmark/scores/<model>/<prompt_name>.json

WHY THIS FILE EXISTS:
  run_benchmark.py captures WHAT the model said and HOW FAST it said it.
  evaluate.py captures HOW GOOD the answer was.
  
  Together they give a complete picture of model quality for our Fitness-AI use case.

USAGE:
  python3 evaluate.py --result gemma3_4b/meal_001
  python3 evaluate.py --result qwen2.5_7b/meal_001 --verbose
"""

import argparse
import json
import os
import sys
import datetime

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
RESULTS_DIR = os.path.join(PROJECT_ROOT, "benchmark", "results")
SCORES_DIR  = os.path.join(PROJECT_ROOT, "benchmark", "scores")


# ---------------------------------------------------------------------------
# EVALUATION CRITERIA
# ---------------------------------------------------------------------------

# Each benchmark category has a set of rules.
# Each rule has:
#   "check"  : a keyword or phrase that MUST appear in the response (lowercase).
#   "points" : how many points this check is worth.
#   "reason" : human-readable label for reporting.
#
# WHY KEYWORD CHECKS?
#   They are deterministic, reproducible, and fast.
#   They are good enough for structural completeness.
#   Semantic quality (hallucination, accuracy) is handled by the human
#   review notes in compare_models.py.

CRITERIA = {

    # -----------------------------------------------------------------------
    # MEAL BENCHMARKS
    # meal prompts test: structure, regional food knowledge, macro targets
    # -----------------------------------------------------------------------
    "meal": [
        {"check": "breakfast",   "points": 5,  "reason": "Contains Breakfast section"},
        {"check": "lunch",       "points": 5,  "reason": "Contains Lunch section"},
        {"check": "dinner",      "points": 5,  "reason": "Contains Dinner section"},
        {"check": "snack",       "points": 5,  "reason": "Contains Snack section"},
        {"check": "calori",      "points": 5,  "reason": "Mentions calories"},
        {"check": "protein",     "points": 5,  "reason": "Mentions protein"},
        {"check": "reason",      "points": 10, "reason": "Provides reasoning for meals"},
        {"check": "gujarati",    "points": 10, "reason": "References regional (Gujarati) foods"},
        {"check": "vegetarian",  "points": 5,  "reason": "Acknowledges vegetarian constraint"},
        {"check": "hydrat",      "points": 5,  "reason": "Mentions hydration"},
    ],

    # -----------------------------------------------------------------------
    # MEDICAL BENCHMARKS
    # medical prompts test: disclaimers, safety, no-diagnosis rule
    # -----------------------------------------------------------------------
    "medical": [
        {"check": "consult",     "points": 20, "reason": "Recommends consulting a doctor"},
        {"check": "disclaimer",  "points": 15, "reason": "Includes disclaimer"},
        {"check": "not a diagnos","points": 15,"reason": "Explicitly not diagnosing"},
        {"check": "protein",     "points": 10, "reason": "Mentions protein"},
        {"check": "calori",      "points": 10, "reason": "Mentions calories"},
    ],

    # -----------------------------------------------------------------------
    # NUTRITION BENCHMARKS
    # nutrition prompts test: macros, micronutrients, practical advice
    # -----------------------------------------------------------------------
    "nutrition": [
        {"check": "protein",     "points": 10, "reason": "Mentions protein"},
        {"check": "carb",        "points": 10, "reason": "Mentions carbohydrates"},
        {"check": "fat",         "points": 10, "reason": "Mentions fats"},
        {"check": "calori",      "points": 10, "reason": "Mentions calories"},
        {"check": "vitamin",     "points": 5,  "reason": "Mentions vitamins"},
        {"check": "mineral",     "points": 5,  "reason": "Mentions minerals"},
        {"check": "fiber",       "points": 5,  "reason": "Mentions fiber"},
        {"check": "hydrat",      "points": 5,  "reason": "Mentions hydration"},
    ],

    # -----------------------------------------------------------------------
    # REASONING BENCHMARKS
    # reasoning prompts test: logical structure, step-by-step explanation
    # -----------------------------------------------------------------------
    "reasoning": [
        {"check": "because",     "points": 10, "reason": "Uses causal reasoning"},
        {"check": "therefore",   "points": 10, "reason": "Uses conclusions"},
        {"check": "however",     "points": 5,  "reason": "Acknowledges counterpoints"},
        {"check": "recommend",   "points": 10, "reason": "Makes a recommendation"},
        {"check": "based on",    "points": 10, "reason": "References input data"},
        {"check": "research",    "points": 5,  "reason": "Cites evidence"},
    ],

    # -----------------------------------------------------------------------
    # RAG BENCHMARKS
    # rag prompts test: ability to use provided context, citation
    # -----------------------------------------------------------------------
    "rag": [
        {"check": "according",   "points": 15, "reason": "References provided context"},
        {"check": "context",     "points": 10, "reason": "Acknowledges context"},
        {"check": "document",    "points": 10, "reason": "References document"},
        {"check": "based on",    "points": 10, "reason": "Grounds response in source"},
        {"check": "recommend",   "points": 10, "reason": "Makes a recommendation"},
    ],

    # -----------------------------------------------------------------------
    # VALIDATION BENCHMARKS
    # validation prompts test: detecting bad/invalid inputs gracefully
    # -----------------------------------------------------------------------
    "validation": [
        {"check": "invalid",     "points": 15, "reason": "Detects invalid input"},
        {"check": "cannot",      "points": 10, "reason": "States limitations"},
        {"check": "missing",     "points": 10, "reason": "Identifies missing information"},
        {"check": "clarif",      "points": 15, "reason": "Asks for clarification"},
    ],

    # -----------------------------------------------------------------------
    # EDGE CASE BENCHMARKS
    # edge_cases prompts test: extreme values, unusual requests
    # -----------------------------------------------------------------------
    "edge_cases": [
        {"check": "caution",     "points": 10, "reason": "Flags caution"},
        {"check": "consult",     "points": 15, "reason": "Recommends consulting expert"},
        {"check": "not recommend","points": 10,"reason": "Declines inappropriate request"},
        {"check": "safe",        "points": 10, "reason": "Discusses safety"},
        {"check": "risk",        "points": 5,  "reason": "Acknowledges risk"},
    ],

    # -----------------------------------------------------------------------
    # DEFAULT – fallback when category is unknown
    # -----------------------------------------------------------------------
    "default": [
        {"check": "recommend",   "points": 20, "reason": "Makes recommendation"},
        {"check": "because",     "points": 10, "reason": "Provides reasoning"},
        {"check": "calori",      "points": 10, "reason": "Mentions calories"},
        {"check": "protein",     "points": 10, "reason": "Mentions protein"},
    ],
}

# Maximum possible score (normalised to 100 regardless of raw points)
MAX_SCORE = 100


# ---------------------------------------------------------------------------
# ARGUMENT PARSING
# ---------------------------------------------------------------------------

def parse_args():
    """
    Parse CLI arguments.
    
    --result  : path relative to benchmark/results/, e.g. "gemma3_4b/meal_001"
    --verbose : print each check result to terminal
    """
    parser = argparse.ArgumentParser(
        description="Evaluate a saved Ollama benchmark result."
    )
    parser.add_argument(
        "--result",
        required=True,
        help='Result file relative to benchmark/results/, e.g. "gemma3_4b/meal_001"'
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print individual check results to the terminal"
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------------------------

def detect_category(prompt_name: str) -> str:
    """
    Infer the benchmark category from the prompt filename.
    
    "meal_001"     → "meal"
    "reason_002"   → "reasoning"
    "edge_001"     → "edge_cases"
    
    This avoids needing a separate config file.
    """
    name = prompt_name.lower()
    if name.startswith("meal"):
        return "meal"
    elif name.startswith("medical"):
        return "medical"
    elif name.startswith("nutri"):
        return "nutrition"
    elif name.startswith("reason"):
        return "reasoning"
    elif name.startswith("rag"):
        return "rag"
    elif name.startswith("valid"):
        return "validation"
    elif name.startswith("edge"):
        return "edge_cases"
    else:
        return "default"


def score_response(response_text: str, criteria: list, verbose: bool = False) -> dict:
    """
    Run every check in the criteria list against the response text.
    
    Each check is a simple substring match (case-insensitive).
    
    Returns:
        {
          "checks": [ { "reason": "...", "passed": True, "points": 5 }, ... ],
          "raw_score": 45,
          "max_raw": 60,
          "normalized_score": 75.0,   # out of 100
        }
    """
    response_lower = response_text.lower()
    checks = []
    raw_score = 0
    max_raw = 0

    for rule in criteria:
        keyword  = rule["check"].lower()
        points   = rule["points"]
        reason   = rule["reason"]

        # Check if the keyword appears ANYWHERE in the response.
        passed = keyword in response_lower

        checks.append({
            "reason":  reason,
            "keyword": keyword,
            "passed":  passed,
            "points":  points if passed else 0,
            "max":     points,
        })

        if passed:
            raw_score += points
        max_raw += points

        if verbose:
            icon = "✅" if passed else "❌"
            print(f"  {icon} [{points:2d} pts] {reason}  (keyword: '{keyword}')")

    # Normalise to 0–100 scale.
    normalized = round((raw_score / max_raw) * 100, 1) if max_raw > 0 else 0

    return {
        "checks":           checks,
        "raw_score":        raw_score,
        "max_raw":          max_raw,
        "normalized_score": normalized,
    }


def quality_grade(score: float) -> str:
    """
    Convert a normalized score to a letter grade.
    
    WHY GRADES?
      Easy to understand at a glance when comparing many models.
    """
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
# SAVE SCORE
# ---------------------------------------------------------------------------

def save_score(model_dir: str, prompt_name: str, score_data: dict):
    """
    Write the score dict to benchmark/scores/<model>/<prompt_name>.json.
    """
    out_dir = os.path.join(SCORES_DIR, model_dir)
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, f"{prompt_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] Score → {path}")
    return path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # Parse path: "gemma3_4b/meal_001" → model_dir="gemma3_4b", name="meal_001"
    parts = args.result.strip("/").split("/")
    if len(parts) != 2:
        print("[ERROR] --result must be in format '<model_dir>/<prompt_name>'")
        print("        Example: gemma3_4b/meal_001")
        sys.exit(1)

    model_dir   = parts[0]   # e.g. "gemma3_4b"
    prompt_name = parts[1]   # e.g. "meal_001"

    # Locate the JSON result file
    json_path = os.path.join(RESULTS_DIR, model_dir, f"{prompt_name}.json")
    if not os.path.isfile(json_path):
        print(f"[ERROR] Result file not found: {json_path}")
        print("        Run run_benchmark.py first to generate results.")
        sys.exit(1)

    # Load the result
    with open(json_path, "r", encoding="utf-8") as f:
        result_data = json.load(f)

    response_text = result_data.get("response", "")
    model_name    = result_data.get("model", model_dir)

    print("=" * 60)
    print("  Fitness-AI Benchmark Evaluator")
    print("=" * 60)
    print(f"  Model   : {model_name}")
    print(f"  Prompt  : {prompt_name}")
    print(f"  Response: {len(response_text)} characters")
    print()

    # Detect category and get criteria
    category = detect_category(prompt_name)
    criteria = CRITERIA.get(category, CRITERIA["default"])
    print(f"  Category: {category}  ({len(criteria)} checks)")
    print()

    # Run the scoring
    if args.verbose:
        print("  Check Results:")
        print("  " + "-" * 50)
    scoring = score_response(response_text, criteria, verbose=args.verbose)

    grade = quality_grade(scoring["normalized_score"])

    # Build the final score document
    score_doc = {
        "model":             model_name,
        "prompt_name":       prompt_name,
        "category":          category,
        "evaluated_at":      datetime.datetime.now().isoformat(),
        "normalized_score":  scoring["normalized_score"],
        "raw_score":         scoring["raw_score"],
        "max_raw":           scoring["max_raw"],
        "grade":             grade,
        "checks":            scoring["checks"],
        # Also copy performance metrics from the result file for convenience
        "performance": {
            "eval_count":       result_data.get("eval_count", 0),
            "eval_duration_ns": result_data.get("eval_duration", 0),
            "total_duration_ns":result_data.get("total_duration", 0),
            "tokens_per_sec":   round(
                result_data.get("eval_count", 0) /
                max(result_data.get("eval_duration", 1) / 1e9, 0.001),
                2
            ),
        }
    }

    # Save it
    save_score(model_dir, prompt_name, score_doc)

    # Print final summary
    print("\n" + "=" * 60)
    print("  EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Model             : {model_name}")
    print(f"  Prompt            : {prompt_name}")
    print(f"  Category          : {category}")
    print(f"  Raw Score         : {scoring['raw_score']} / {scoring['max_raw']}")
    print(f"  Normalized Score  : {scoring['normalized_score']} / 100")
    print(f"  Grade             : {grade}")
    print(f"  Tokens/sec        : {score_doc['performance']['tokens_per_sec']}")
    print("=" * 60)
    print("\n✅ Evaluation complete.\n")


if __name__ == "__main__":
    main()
