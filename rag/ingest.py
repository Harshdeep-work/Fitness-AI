import json
import os
import chromadb
from chromadb.utils import embedding_functions

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "indian_nutrition_guidelines.json")
DB_PATH = os.path.join(BASE_DIR, "rag", "chroma_db")

def ingest_data():
    print(f"Loading data from {DATASET_PATH}...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} nutrition guidelines.")

    # Initialize ChromaDB Persistent Client
    client = chromadb.PersistentClient(path=DB_PATH)

    # Use Ollama for embeddings
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text",
    )

    # Create or get collection
    collection = client.get_or_create_collection(
        name="nutrition_guidelines",
        embedding_function=ollama_ef
    )

    documents = []
    metadatas = []
    ids = []

    for i, item in enumerate(data):
        doc = f"Topic: {item['topic']}. Region: {item['region']}. Guideline: {item['content']}"
        documents.append(doc)
        metadatas.append({"topic": item["topic"], "region": item["region"]})
        ids.append(f"doc_{i}")

    print("Embedding and storing documents in ChromaDB...")
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully ingested {len(documents)} documents into ChromaDB at {DB_PATH}")

if __name__ == "__main__":
    ingest_data()
