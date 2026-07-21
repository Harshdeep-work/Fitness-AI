# ChromaDB data (local)

This folder is **generated** by ingest scripts. It is listed in `.gitignore` so clones stay small.

## Regenerate

From repository root:

```bash
cd rag
pip install chromadb
python ingest.py

cd ../datasets
python process_and_ingest.py
```

Embedding setup must match `rag/ingest.py` and `datasets/process_and_ingest.py` (typically Ollama with `nomic-embed-text`).

## If the folder is empty

`retrieve.py` will fail until ingest completes. That is expected on a fresh checkout.
