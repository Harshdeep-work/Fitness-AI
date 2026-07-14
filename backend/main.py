import os
import sys
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add parent directory to path to import rag module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.retrieve import get_context

app = FastAPI(
    title="Fitness-AI API",
    description="Backend API for the Fitness Recommendation Engine",
    version="1.0.0"
)

# Configure CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from frontend directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "gemma3:4b"  # Defaulting to our selected production model


@app.get("/")
def root():
    """Serve the frontend HTML"""
    frontend_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Welcome to Fitness-AI API"}


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Fitness-AI Backend is running"}


@app.post("/api/generate")
def generate_response(request: GenerateRequest):
    """
    Proxy the request to the local Ollama instance.
    """
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=1200)
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "model": request.model,
            "response": data.get("response", ""),
            "duration": round(data.get("total_duration", 0) / 1e9, 2)
        }
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/rag_generate")
def rag_generate_response(request: GenerateRequest):
    """
    1. Retrieve relevant context from ChromaDB
    2. Augment the user's prompt with the context
    3. Generate the response using Ollama
    """
    # Step 1: Retrieve context
    context = get_context(request.prompt)
    
    # Step 2: Augment prompt
    augmented_prompt = f"""You are an expert AI Nutritionist. Use the following context to answer the user's request. If the context does not contain the answer, rely on your general knowledge but prioritize the context.

Context:
{context}

User Request: {request.prompt}
"""
    
    # Step 3: Generate response
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": request.model,
        "prompt": augmented_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=1200)
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "model": request.model,
            "retrieved_context": context,
            "response": data.get("response", ""),
            "duration": round(data.get("total_duration", 0) / 1e9, 2)
        }
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
