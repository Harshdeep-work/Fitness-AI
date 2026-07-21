#!/usr/bin/env python3
"""
run_benchmark.py
================
PURPOSE:
  Single-entry-point benchmark runner for the Fitness-AI project.
  
  It does ONE job per invocation:
    1. Read a prompt file from benchmark/prompts/<category>/<name>.txt
    2. POST that prompt to the local Ollama REST API
    3. Save the raw JSON response to benchmark/results/<model>/<name>.json
    4. Generate a human-readable Markdown report at benchmark/results/<model>/<name>.md

USAGE:
  python3 run_benchmark.py --model gemma3:4b --prompt meal/meal_001
  python3 run_benchmark.py --model qwen2.5:7b --prompt meal/meal_002
  python3 run_benchmark.py --model llama3.2:3b --prompt reasoning/reason_001

WHY THIS FILE EXISTS:
  Manual curl commands are error-prone, hard to repeat, and produce inconsistent
  output formats. This script enforces a standard structure so every model and
  prompt combination is saved in the same way, making compare_models.py reliable.
"""

import argparse       # Parse command-line flags (--model, --prompt, etc.)
import json           # Serialize/deserialize JSON payloads
import os             # Build file paths, create directories
import sys            # Exit with non-zero code on errors
import time           # Measure wall-clock latency
import datetime       # Timestamp for the report header
import requests       # Make HTTP calls to the Ollama REST API

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

# The local Ollama server endpoint.
# Ollama always listens on port 11434 by default.
# /api/generate is the non-streaming generation endpoint.
OLLAMA_URL = "http://localhost:11434/api/generate"

# Base directory of the whole project.
# __file__ resolves to .../benchmark/scripts/run_benchmark.py
# Going up two levels lands at .../benchmark/
# Going up three levels lands at the project root (Fitness-AI/).
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# The folder where all prompt .txt files live.
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "benchmark", "prompts")

# The folder where raw JSON results and Markdown reports are stored.
RESULTS_DIR = os.path.join(PROJECT_ROOT, "benchmark", "results")

# ---------------------------------------------------------------------------
# ARGUMENT PARSING
# ---------------------------------------------------------------------------

def parse_args():
    """
    Define and parse the CLI arguments.
    
    Returns:
        argparse.Namespace with attributes:
            .model  – the Ollama model tag, e.g. "gemma3:4b"
            .prompt – relative path under prompts/, e.g. "meal/meal_001"
            .host   – optional override for the Ollama server URL
    """
    parser = argparse.ArgumentParser(
        description="Run a single benchmark prompt against an Ollama model."
    )

    # --model: which Ollama model to call.
    # Must match a model already pulled with `ollama pull <model>`.
    parser.add_argument(
        "--model",
        required=True,
        help='Ollama model tag, e.g. "gemma3:4b" or "qwen2.5:7b"'
    )

    # --prompt: relative path inside benchmark/prompts/ WITHOUT the .txt extension.
    # Example: "meal/meal_001" → reads benchmark/prompts/meal/meal_001.txt
    parser.add_argument(
        "--prompt",
        required=True,
        help='Prompt path relative to benchmark/prompts/, e.g. "meal/meal_001"'
    )

    # --host: optional override so we can point at a remote Ollama server.
    parser.add_argument(
        "--host",
        default=OLLAMA_URL,
        help=f"Ollama API URL (default: {OLLAMA_URL})"
    )

    # --no_think: for Qwen3 models, append /no_think to the prompt to disable
    # the built-in chain-of-thought reasoning block.
    # WHY? Qwen3 thinking mode can generate 5000+ tokens before the answer,
    # making benchmarks very slow and hard to compare with other models.
    # In production, we may want thinking ON for complex reasoning tasks
    # but OFF for simple meal recommendations.
    parser.add_argument(
        "--no_think",
        action="store_true",
        help="Append /no_think to prompt (for Qwen3 models)"
    )

    # --timeout: seconds to wait for the Ollama response (default 1200 = 20 min)
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="Request timeout in seconds (default: 1200)"
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# FILE HELPERS
# ---------------------------------------------------------------------------

def load_prompt(prompt_path: str) -> str:
    """
    Read the prompt text file and return its contents as a string.
    
    Args:
        prompt_path: relative path like "meal/meal_001"
                     (no .txt extension needed)
    
    Returns:
        The raw prompt text.
    
    Raises:
        SystemExit if the file does not exist.
    """
    # Build the full file path by joining the base prompts directory
    # with the user-supplied sub-path, then appending ".txt".
    full_path = os.path.join(PROMPTS_DIR, prompt_path + ".txt")

    if not os.path.isfile(full_path):
        print(f"[ERROR] Prompt file not found: {full_path}")
        print(f"        Available categories: {os.listdir(PROMPTS_DIR)}")
        sys.exit(1)

    # Read the entire file as UTF-8 text.
    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    print(f"[INFO]  Loaded prompt from: {full_path}")
    print(f"[INFO]  Prompt length: {len(text)} characters")
    return text


def ensure_output_dir(model: str) -> str:
    """
    Create (if needed) benchmark/results/<model_safe>/ and return that path.
    
    Model names like "gemma3:4b" contain a colon which is illegal in directory
    names on some OS. We replace ":" with "_" for safety.
    
    Args:
        model: raw model tag, e.g. "gemma3:4b"
    
    Returns:
        Absolute path to the output directory.
    """
    # Replace colon with underscore so "gemma3:4b" → "gemma3_4b".
    # But if the user already tested with "gemma" folder, keep that folder.
    # We create the sanitized version; existing results won't be overwritten.
    model_safe = model.replace(":", "_").replace("/", "_")

    out_dir = os.path.join(RESULTS_DIR, model_safe)
    os.makedirs(out_dir, exist_ok=True)   # no-op if already exists
    return out_dir


# ---------------------------------------------------------------------------
# OLLAMA API CALL
# ---------------------------------------------------------------------------

def call_ollama(host: str, model: str, prompt: str,
                timeout: int = 1200, no_think: bool = False) -> dict:
    """
    POST the prompt to the Ollama /api/generate endpoint and return the
    full parsed JSON response.
    
    Args:
        host:   Ollama server URL, e.g. "http://localhost:11434/api/generate"
        model:  model tag string, e.g. "gemma3:4b"
        prompt: the full prompt text
    
    Returns:
        Parsed JSON dict from Ollama.
    
    Raises:
        SystemExit on connection or HTTP errors.
    """
    # Build the request body.
    # "stream": False is critical — it tells Ollama to wait until the full
    # response is generated before returning, instead of streaming tokens.
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": 4096},
    }

    # Only add the 'think' key for Qwen3 models via --no_think flag.
    # Sending think=True to Llama/Gemma/Mistral causes a 400 Bad Request error
    # because those models do not support the thinking API parameter.
    if no_think:
        payload["think"] = False

    print(f"\n[INFO]  Sending request to Ollama...")
    print(f"[INFO]  Model  : {model}")
    print(f"[INFO]  Host   : {host}")

    # Record wall-clock start time so we can report how long it really took
    # from the user's perspective (includes network overhead, queue time, etc.).
    wall_start = time.time()

    try:
        # timeout: Large models on CPU can take many minutes to generate.
        # Qwen3 thinking mode especially generates long chains before answering.
        # Without a timeout, the script would hang forever on errors.
        response = requests.post(host, json=payload, timeout=timeout)

        # Raise an HTTPError for 4xx and 5xx status codes.
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to Ollama. Is it running?")
        print("        Start it with: ollama serve")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 600 seconds.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}")
        print(f"        Response body: {response.text[:500]}")
        sys.exit(1)

    wall_elapsed = time.time() - wall_start

    # Parse the response body as JSON.
    data = response.json()

    # Inject the wall-clock time into the dict so it's preserved in the saved file.
    data["wall_duration_seconds"] = round(wall_elapsed, 2)

    print(f"[INFO]  Response received in {wall_elapsed:.2f}s (wall clock)")
    return data


# ---------------------------------------------------------------------------
# METRICS EXTRACTION
# ---------------------------------------------------------------------------

def extract_metrics(data: dict) -> dict:
    """
    Pull the performance numbers out of the Ollama response.
    
    Ollama returns durations in NANOSECONDS. We convert to seconds.
    
    Key fields from Ollama:
      total_duration      – total time Ollama spent on the request (ns)
      load_duration       – time to load the model into memory (ns)
      prompt_eval_count   – number of tokens in the prompt
      prompt_eval_duration– time to evaluate the prompt tokens (ns)
      eval_count          – number of tokens generated in the response
      eval_duration       – time spent generating the response tokens (ns)
    
    Returns:
        Dict with human-readable metrics and computed tokens/sec.
    """
    # Helper: safely convert nanoseconds → seconds, returning 0 if key missing.
    def ns_to_s(key):
        return round(data.get(key, 0) / 1_000_000_000, 4)

    total_duration_s  = ns_to_s("total_duration")
    load_duration_s   = ns_to_s("load_duration")
    prompt_eval_dur_s = ns_to_s("prompt_eval_duration")
    eval_duration_s   = ns_to_s("eval_duration")

    eval_count        = data.get("eval_count", 0)         # tokens generated
    prompt_eval_count = data.get("prompt_eval_count", 0)  # prompt tokens

    # Tokens per second = tokens generated / time spent generating.
    # Guard against division by zero if eval_duration is missing.
    tokens_per_sec = round(eval_count / eval_duration_s, 2) if eval_duration_s > 0 else 0

    return {
        "total_duration_s":   total_duration_s,
        "load_duration_s":    load_duration_s,
        "prompt_eval_count":  prompt_eval_count,
        "prompt_eval_dur_s":  prompt_eval_dur_s,
        "eval_count":         eval_count,
        "eval_duration_s":    eval_duration_s,
        "tokens_per_sec":     tokens_per_sec,
        "wall_duration_s":    data.get("wall_duration_seconds", 0),
    }


# ---------------------------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------------------------

def save_json(out_dir: str, name: str, data: dict):
    """
    Write the raw Ollama response JSON to disk.
    
    Args:
        out_dir: directory path, e.g. benchmark/results/gemma3_4b/
        name:    filename stem, e.g. "meal_001"
        data:    the full parsed Ollama response dict
    """
    path = os.path.join(out_dir, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        # indent=2 makes it human-readable; ensure_ascii=False preserves Unicode.
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] JSON  → {path}")
    return path


def save_markdown(out_dir: str, name: str, model: str,
                  prompt: str, metrics: dict, response_text: str):
    """
    Write a structured Markdown report to disk.
    
    The report contains:
      - Metadata header (model, date, prompt name)
      - The prompt used
      - The model's full response
      - Performance metrics table
    
    Args:
        out_dir:       directory path
        name:          filename stem, e.g. "meal_001"
        model:         model tag string
        prompt:        the original prompt text
        metrics:       dict from extract_metrics()
        response_text: the model's text answer
    """
    path = os.path.join(out_dir, f"{name}.md")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build the Markdown content as a multi-line string.
    content = f"""# Benchmark Report

| Field         | Value                        |
|---------------|------------------------------|
| **Model**     | `{model}`                    |
| **Prompt**    | `{name}`                     |
| **Date**      | {timestamp}                  |
| **Status**    | ✅ Completed                  |

---

## Prompt Used

```
{prompt}
```

---

## Model Response

{response_text}

---

## Performance Metrics

| Metric                  | Value                          |
|-------------------------|--------------------------------|
| Total Duration          | {metrics['total_duration_s']} s |
| Model Load Time         | {metrics['load_duration_s']} s  |
| Prompt Tokens           | {metrics['prompt_eval_count']}  |
| Prompt Eval Duration    | {metrics['prompt_eval_dur_s']} s|
| Response Tokens         | {metrics['eval_count']}         |
| Generation Duration     | {metrics['eval_duration_s']} s  |
| **Tokens / Second**     | **{metrics['tokens_per_sec']}** |
| Wall Clock Duration     | {metrics['wall_duration_s']} s  |

---

*Generated by Fitness-AI Benchmark System — run_benchmark.py*
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[SAVED] MD    → {path}")
    return path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    """
    Orchestrate the full benchmark run:
      1. Parse arguments
      2. Load the prompt text
      3. Call Ollama
      4. Extract metrics
      5. Save JSON
      6. Save Markdown
      7. Print summary to terminal
    """
    args = parse_args()

    # Derive a short "name" from the prompt path:
    # "meal/meal_001" → "meal_001"
    prompt_name = os.path.basename(args.prompt)

    print("=" * 60)
    print("  Fitness-AI Benchmark Runner")
    print("=" * 60)

    # Step 1: Load prompt
    prompt_text = load_prompt(args.prompt)

    # Qwen3: if --no_think is set, append the /no_think instruction.
    # This tells Qwen3 to skip its internal reasoning chain and answer directly.
    # Result: faster responses, more comparable to Gemma / Llama.
    if args.no_think:
        prompt_text = prompt_text + "\n\n/no_think"
        print("[INFO]  Thinking mode: DISABLED (--no_think)")
    else:
        print("[INFO]  Thinking mode: DEFAULT")

    # Step 2: Create output directory
    out_dir = ensure_output_dir(args.model)

    # Step 3: Call Ollama
    raw_data = call_ollama(
        args.host,
        args.model,
        prompt_text,
        timeout=args.timeout,
        no_think=args.no_think
    )

    # Step 4: Extract metrics
    metrics = extract_metrics(raw_data)

    # Step 5: Save raw JSON
    save_json(out_dir, prompt_name, raw_data)

    # Step 6: Save Markdown report
    response_text = raw_data.get("response", "[No response returned]")
    save_markdown(out_dir, prompt_name, args.model, prompt_text, metrics, response_text)

    # Step 7: Print summary table to the terminal
    print("\n" + "=" * 60)
    print("  BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"  Model            : {args.model}")
    print(f"  Prompt           : {prompt_name}")
    print(f"  Prompt Tokens    : {metrics['prompt_eval_count']}")
    print(f"  Response Tokens  : {metrics['eval_count']}")
    print(f"  Tokens/sec       : {metrics['tokens_per_sec']}")
    print(f"  Total Duration   : {metrics['total_duration_s']}s")
    print(f"  Wall Clock       : {metrics['wall_duration_s']}s")
    print("=" * 60)
    print("\n✅ Benchmark complete.\n")


# Standard Python entry-point guard.
# This prevents the code from running if the file is imported as a module.
if __name__ == "__main__":
    main()
