# Parked assets (Phase 6+)

These directories were moved out of the repo root during **Phase 0** so AI work (`datasets/`, `models/`, `rag/`, `benchmark/`) stays obvious and uncluttered.

| Path | What it is | When to use |
|------|------------|-------------|
| `phase6_app/frontend/` | Static web UI | After fine-tuned model + persona API are ready |
| `phase6_app/backend/` | FastAPI, Ollama, RAG endpoint | Same |

**Active documentation** remains at:

- `docs/PROJECT_OVERVIEW.md`
- `models/README.md`
- `docs/PHASE_0_WORKSPACE.md`

To bring the app back to the root (optional):

```bash
# From repo root — only if you want the old layout
git mv parked/phase6_app/frontend .
git mv parked/phase6_app/backend .
```

Then fix any paths in `backend/main.py` if you moved folders.
