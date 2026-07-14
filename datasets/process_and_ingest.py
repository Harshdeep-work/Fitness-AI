import pandas as pd
import os
import chromadb
from chromadb.utils import embedding_functions

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "datasets", "indian_recipes.csv")
DB_PATH = os.path.join(BASE_DIR, "rag", "chroma_db")

def parse_recipe_text(text):
    """
    Parses the raw text which is formatted like:
    ### TranslatedIngredients: ... ### PrepTimeInMins: ... ### Diet: ...
    Returns a dictionary of the fields.
    """
    if not isinstance(text, str):
        return {}
        
    parts = text.split("###")
    recipe_data = {}
    
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            recipe_data[key.strip()] = value.strip()
            
    return recipe_data

def ingest_real_dataset():
    print(f"Loading dataset from {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print(f"Loaded {len(df)} total recipes.")
    
    # We will only ingest 150 recipes to keep the embedding fast for this demonstration
    # We will ingest 1000 recipes to provide a massive variety for recommendations
    sample_df = df.head(1000)
    
    # Initialize ChromaDB Persistent Client
    client = chromadb.PersistentClient(path=DB_PATH)

    # Use Ollama for embeddings
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text",
    )

    # Create a new collection for real recipes
    collection = client.get_or_create_collection(
        name="real_indian_recipes",
        embedding_function=ollama_ef
    )

    documents = []
    metadatas = []
    ids = []

    print("Parsing recipes...")
    for index, row in sample_df.iterrows():
        recipe_dict = parse_recipe_text(row['text'])
        
        # Only ingest if we have the critical fields
        if 'Diet' in recipe_dict and 'TranslatedIngredients' in recipe_dict:
            diet = recipe_dict.get('Diet', 'Unknown')
            cuisine = recipe_dict.get('Cuisine', 'Indian')
            ingredients = recipe_dict.get('TranslatedIngredients', '')
            
            # Create a dense paragraph for the embedding model to understand
            doc = f"This is a {diet} recipe from {cuisine} cuisine. Ingredients: {ingredients}."
            
            documents.append(doc)
            metadatas.append({"diet": diet, "cuisine": cuisine})
            ids.append(f"real_recipe_{index}")

    print(f"Embedding {len(documents)} real recipes into ChromaDB... (This may take a minute)")
    
    # Upsert in batches to avoid overwhelming the Ollama API
    batch_size = 50
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        print(f"  -> Processing batch {i} to {end_idx}...")
        collection.upsert(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
        
    print(f"✅ Successfully ingested {len(documents)} real recipes into ChromaDB!")

if __name__ == "__main__":
    ingest_real_dataset()
