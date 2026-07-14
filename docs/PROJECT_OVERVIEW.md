# Fitness AI - Complete Project Overview

## 🎯 Project Goal
To build a production-grade, highly accurate, culturally-aware Fitness Recommendation Engine using **Local Large Language Models (LLMs)** on consumer-grade CPU hardware (16GB RAM). The system is designed to provide hyper-personalized, regional Indian meal plans while strictly avoiding AI hallucinations through the use of RAG (Retrieval-Augmented Generation).

---

## 🛠️ Phase 1: Local LLM Infrastructure
The first phase was dedicated to understanding how to run powerful AI models entirely offline without relying on cloud APIs like OpenAI. 
- **Ollama**: We utilized Ollama as our local model server because of its efficiency in running quantized models.
- **Quantization (GGUF)**: We learned how 4-bit quantization allows massive models (like a 4 Billion parameter model) to compress down to ~3GB so they can run smoothly on CPU/RAM without requiring an expensive NVIDIA GPU.

---

## ⚖️ Phase 2: Model Selection & Benchmarking Pipeline
To scientifically select the best model for our backend, we built an automated testing suite inside the `benchmark/` folder.

### 1. The Models Tested
- **Gemma 3 4B**: Google's efficient model.
- **Qwen3 4B**: Alibaba's highly logical model.
- **Llama 3.2 3B**: Meta's ultra-fast edge model.
- **Mistral 7B**: A powerful open-weight model (too heavy for 16GB RAM alongside the backend).

### 2. The Benchmark Suite
We built Python scripts to automate the evaluation process:
- `run_benchmark.py`: Sends diverse edge-case prompts (e.g., "PCOS diet in Maharashtra", "Diabetic Punjabi Diet") to the models and measures **Tokens Per Second (TPS)** and response latency.
- `evaluate.py`: Uses a keyword-based strict grading system to score the AI's output from 0-100 based on structural adherence, medical safety, and regional accuracy.
- `compare_models.py`: Combines Quality (70%) and Speed (30%) to output a final ranking.

### 3. The Winner: Gemma 3 4B
Gemma 3 4B was selected as the **Production Model** because it provided the best balance of speed (6.15 TPS) and quality (75%), and fits perfectly in ~3.3GB of RAM, leaving plenty of room for our vector database and backend server. 

---

## 🧠 Phase 3: Backend, RAG, and Frontend
Phase 3 transformed our raw AI models into a real, usable software application.

### 1. The FastAPI Backend (`backend/`)
We built a robust Python backend using FastAPI. 
- It acts as a secure middleware. 
- It exposes standard REST API endpoints (`/api/generate` and `/api/rag_generate`).
- It prevents the frontend from ever talking directly to the raw Ollama instance.

### 2. The RAG Pipeline (`rag/` and `datasets/`)
To prevent the AI from giving generic or factually incorrect advice, we built a **Retrieval-Augmented Generation** system.
- **The Vector Database**: We installed `ChromaDB` to store our data locally.
- **The Embeddings**: We used Ollama to pull `nomic-embed-text`, a model specifically designed to convert text into math (vectors) so the database can search it instantly.
- **The Data (The "Textbook")**:
  1. We created `indian_nutrition_guidelines.json` to enforce strict rules (e.g., Macro splits for muscle gain vs. fat loss).
  2. We wrote a Python data pipeline to download a real Hugging Face dataset containing 6,800+ real Indian recipes, extracted the diet and ingredients using `pandas`, and ingested 1,000 of them into ChromaDB.
- **The RAG Process**: When a user asks for a meal plan, the backend first queries ChromaDB, retrieves the medical rules and real recipes, glues them to the user's prompt, and forces Gemma 3 to read them before answering.

### 3. The UI (`frontend/`)
We built a visually stunning, Vanilla HTML/CSS/JS Single Page Application to test the API.
- Uses modern **Glassmorphism** and dark-mode aesthetics.
- Captures User Profile data (Age, Gender, Region, Goal, Medical Conditions).
- Connects asynchronously to the FastAPI RAG endpoint to render the final, region-specific meal plan.

---

## 📂 Project Directory Structure

```text
Fitness-AI/
│
├── backend/                  # The FastAPI Server
│   ├── main.py               # API Endpoints & RAG augmentation logic
│   ├── requirements.txt      # Python dependencies
│   └── venv/                 # Virtual environment
│
├── benchmark/                # The Automated Evaluation Suite
│   ├── prompts/              # Test cases (meal, medical, etc.)
│   ├── results/              # JSON/Markdown output from model tests
│   └── scripts/              # run_benchmark.py, evaluate.py, etc.
│
├── datasets/                 # Raw Data for RAG
│   ├── indian_nutrition_guidelines.json  # Strict Medical/Macro Rules
│   ├── indian_recipes.csv                # Real HF recipe database
│   └── process_and_ingest.py             # Script to clean & embed data
│
├── docs/                     # Documentation
│   ├── how_rag_works.md      # Architecture diagram of RAG
│   ├── phase_3_backend_rag.md
│   └── PROJECT_OVERVIEW.md   # This file
│
├── frontend/                 # Web Interface
│   ├── index.html            # UI Structure
│   ├── style.css             # Glassmorphism styling
│   └── app.js                # Logic to HTMLcall FastAPI
│
└── rag/                      # RAG Infrastructure
    ├── chroma_db/            # The physical vector database files
    ├── ingest.py             # Script to load data into ChromaDB
    └── retrieve.py           # Script to query ChromaDB for context
```

---

## 🚀 Next Steps (Phase 4)
- **Structured Output**: Forcing Gemma to return strict JSON (instead of Markdown) so the frontend can build custom UI cards.
- **Dockerization**: Containerizing the Backend, ChromaDB, and Frontend for cloud deployment.
- **Fine-Tuning**: Using LoRA to permanently train Gemma 3 on Indian diets so it requires less RAG context.
