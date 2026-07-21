# Phase 0 — Workspace layout

Phase 0 narrows day-to-day work to **model + data + RAG + benchmarks**. The web app lives under `parked/phase6_app/` until Phase 6+.

## Active paths (use these)

```
Fitness-AI/
├── datasets/          # CSV, JSON guidelines, JSONL, create_finetune_dataset.py
├── models/            # colab_finetune.py, train_qlora.py, inference.py, README
├── rag/
│   ├── ingest.py
│   ├── retrieve.py
│   └── chroma_db/     # local only — regenerate; not required in git
├── benchmark/         # prompts, scripts, results, scores
├── scripts/           # e.g. prepare_finetuning.sh
└── docs/
    ├── PROJECT_OVERVIEW.md   # primary architecture doc
    └── PHASE_0_WORKSPACE.md    # this file
```

### Supplementary docs (optional)

- `how_rag_works.md`
- `before_after_examples.md`

## Parked paths (Phase 6+)

```
parked/
├── README.md
└── phase6_app/
    ├── frontend/      # HTML/CSS/JS UI
    └── backend/       # FastAPI + Ollama integration
```

### Restore the app locally (when ready)

```bash
cd parked/phase6_app/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# From repo root, serve with paths as originally documented in PROJECT_OVERVIEW
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Update static file paths in `main.py` if you move `frontend/` back to repo root.

## RAG database

`rag/chroma_db/` is generated data. After clone:

1. `cd rag && python ingest.py`
2. `cd datasets && python process_and_ingest.py`

Requires embedding setup described in `docs/how_rag_works.md` (Ollama `nomic-embed-text` for current ingest scripts).

## Phase checklist

| Phase | Focus | Location |
|-------|--------|----------|
| 0 | Layout (this doc) | `docs/PHASE_0_WORKSPACE.md` |
| 1 | Datasets | `datasets/` |
| 2 | QLoRA / Colab | `models/` |
| 3 | Eval | `benchmark/` |
| 4 | RAG refresh | `rag/` |
| 5 | User persona (schema + prompts) | TBD under `datasets/` or new `persona/` |
| 6+ | API + UI (local) | `parked/phase6_app/` |
