# Fitness AI

Domain-focused Indian nutrition and fitness AI: **datasets → QLoRA fine-tune (Gemma) → RAG → evaluation**.

## Phase 0 — active workspace

Work here until the model and RAG pipeline are solid (Phases 1–5). App and cloud deploy are **parked** under `parked/`.

| Path | Purpose |
|------|---------|
| [`datasets/`](datasets/) | Recipes, guidelines, JSONL, dataset builders |
| [`models/`](models/) | Colab/local QLoRA, inference, deployment notes |
| [`rag/`](rag/) | Chroma ingest + retrieve (regenerate `chroma_db` locally) |
| [`benchmark/`](benchmark/) | Prompts, scores, model comparison |
| [`scripts/`](scripts/) | Fine-tuning setup helpers |

**Documentation (source of truth):**

- [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) — architecture and phases
- [`docs/PHASE_0_WORKSPACE.md`](docs/PHASE_0_WORKSPACE.md) — what to use vs what is parked
- [`models/README.md`](models/README.md) — fine-tuning and Colab

**Parked for Phase 6+:** [`parked/phase6_app/`](parked/phase6_app/) (API + UI). No cloud deploy configs in this repo.

## Quick commands

```bash
# Regenerate training JSONL
cd datasets && python create_finetune_dataset.py

# Build RAG index (after Ollama + nomic-embed-text for ingest)
cd rag && pip install chromadb && python ingest.py
cd ../datasets && python process_and_ingest.py

# Benchmark (Ollama models)
cd benchmark/scripts && python run_benchmark.py
```
