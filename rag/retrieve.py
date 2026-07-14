import os
import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rag", "chroma_db")

def get_context(query_text: str, n_results: int = 2) -> str:
    """
    Search ChromaDB for the most relevant nutrition guidelines.
    Returns the concatenated text of the top matches.
    """
    client = chromadb.PersistentClient(path=DB_PATH)
    
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text",
    )
    
    rules_collection = client.get_collection(
        name="nutrition_guidelines",
        embedding_function=ollama_ef
    )
    
    recipes_collection = client.get_collection(
        name="real_indian_recipes",
        embedding_function=ollama_ef
    )
    
    rules_results = rules_collection.query(
        query_texts=[query_text],
        n_results=2
    )
    
    recipes_results = recipes_collection.query(
        query_texts=[query_text],
        n_results=3
    )
    
    # Extract the documents
    rules_docs = rules_results.get("documents", [[]])[0]
    recipes_docs = recipes_results.get("documents", [[]])[0]
    
    all_docs = rules_docs + recipes_docs
    
    if not all_docs:
        return "No relevant context found."
        
    context = "\n\n".join(all_docs)
    return context

if __name__ == "__main__":
    # Test the retrieval
    test_query = "What should a vegan eat in Tamil Nadu?"
    print(f"Query: {test_query}\n")
    print("Retrieved Context:")
    print(get_context(test_query))
