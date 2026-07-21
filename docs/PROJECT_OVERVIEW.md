# 🏋️ Fitness AI — Complete Project Documentation

> **Personalized Indian Nutrition & Fitness Recommendations powered by Fine-tuned Gemma 3:4b + RAG**

---

## Phase 0 — current focus

Day-to-day work is **model + data + RAG + benchmark** only. The web app is under `parked/phase6_app/` until Phase 6+.

| Active | Parked |
|--------|--------|
| `datasets/`, `models/`, `rag/`, `benchmark/` | `parked/phase6_app/` (frontend + backend) |

See **[PHASE_0_WORKSPACE.md](./PHASE_0_WORKSPACE.md)** for the full layout and restore instructions.

> **Note:** Sections below that mention `backend/` and `frontend/` at repo root describe the Phase 6 app; those paths are now `parked/phase6_app/backend/` and `parked/phase6_app/frontend/`.

---

## Table of Contents

1. [Project Summary](#project-summary)
2. [Architecture Overview](#architecture-overview)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Phase 1 — Dataset](#phase-1--dataset)
6. [Phase 2 — Fine-Tuning with QLoRA/LoRA](#phase-2--fine-tuning-with-qloralore)
7. [Phase 3 — RAG System](#phase-3--rag-system)
8. [Phase 4 — Backend API](#phase-4--backend-api)
9. [Phase 5 — Frontend](#phase-5--frontend)
10. [What is LoRA? Why did we use it?](#what-is-lora-why-did-we-use-it)
11. [What is QLoRA?](#what-is-qlora)
12. [Why Fine-Tune at all?](#why-fine-tune-at-all)
13. [Base vs Fine-Tuned — What's the difference?](#base-vs-fine-tuned--whats-the-difference)
14. [What is RAG and why combine it with Fine-Tuning?](#what-is-rag-and-why-combine-it-with-fine-tuning)
15. [Data Flow — End to End](#data-flow--end-to-end)
16. [Tools & Libraries Reference](#tools--libraries-reference)
17. [How to Run Locally](#how-to-run-locally)
18. [Deployment Options](#deployment-options)

---

## Project Summary

Fitness AI is an end-to-end AI system that generates **personalized Indian nutrition and fitness plans**. A user fills in their profile (age, weight, goal, region, medical conditions, diet type, etc.) and the system returns a detailed, region-specific meal and workout plan.

The system is unique because it:
- Uses a **fine-tuned version of Gemma 3:4b** — trained on Indian diet data
- Combines that fine-tuned model with a **RAG (Retrieval-Augmented Generation)** pipeline
- Knows about **regional Indian cuisines** (Maharashtra, Punjab, Tamil Nadu, Kerala, etc.)
- Is **medically aware** (diabetes, PCOS, hypertension, thyroid, etc.)
- Runs **100% locally** using Ollama — no cloud API costs

---

## Architecture Overview

```
User (Browser)
     │
     ▼
Frontend (HTML/CSS/JS)        ← Port 8000 (served by FastAPI)
     │  POST /api/rag_generate
     ▼
FastAPI Backend (Python)       ← Orchestrates everything
     │
     ├──► ChromaDB (RAG)       ← Semantic search for nutrition guidelines + recipes
     │         │
     │    nomic-embed-text     ← Embedding model (via Ollama)
     │
     └──► Ollama               ← Runs gemma3:4b locally
               │
          Fine-tuned Gemma 3:4b  ← Our specialized model
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM Runtime** | Ollama | Run LLMs locally without GPU (CPU inference) |
| **Base Model** | Gemma 3:4b (Google) | Foundation language model |
| **Fine-tuning method** | QLoRA (4-bit) | Train the model on our data efficiently |
| **LoRA library** | PEFT (HuggingFace) | Apply LoRA adapters |
| **Training framework** | TRL + SFTTrainer | Supervised fine-tuning |
| **Quantization** | BitsAndBytes | 4-bit NF4 quantization |
| **Vector DB** | ChromaDB | Store and search nutrition embeddings |
| **Embedding model** | nomic-embed-text | Convert text to vectors for RAG |
| **Backend** | FastAPI (Python) | REST API server |
| **Frontend** | Vanilla HTML/CSS/JS | User interface |
| **Web server** | Uvicorn | ASGI server for FastAPI |
| **Markdown rendering** | marked.js (CDN) | Render AI responses in browser |

---

## Project Structure

```
Fitness-AI/
│
├── datasets/                   # Training data + builders (Phase 1)
├── models/                     # QLoRA / Colab / inference (Phase 2)
├── rag/                        # ingest.py, retrieve.py, chroma_db/ (Phase 4)
├── benchmark/                  # Evaluation (Phase 3)
├── scripts/                    # Fine-tuning helpers
├── docs/                       # PROJECT_OVERVIEW.md, PHASE_0_WORKSPACE.md
├── README.md                   # Phase 0 entry point
│
└── parked/                     # Phase 6+ (not active in Phase 0)
    └── phase6_app/
        ├── backend/            # FastAPI API server
        └── frontend/           # Web UI
```

<details>
<summary>Legacy full tree (pre–Phase 0 paths)</summary>

```
Fitness-AI/
│
├── backend/                    # → now parked/phase6_app/backend/
│   ├── main.py                 # API routes, CORS, static file serving
│   ├── requirements.txt        # Backend Python dependencies
│   └── venv/                   # Python virtual environment
│
├── frontend/                   # Web UI (served by FastAPI)
│   ├── index.html              # Main page, form with all user fields
│   ├── style.css               # All styling (dark/light theme)
│   └── app.js                  # Form logic, API calls, result rendering
│
├── rag/                        # Retrieval-Augmented Generation
│   ├── ingest.py               # Load data into ChromaDB
│   ├── retrieve.py             # Query ChromaDB for relevant context
│   └── chroma_db/              # Persistent vector database (local files)
│
├── models/                     # Fine-tuning scripts
│   ├── train_qlora.py          # Main QLoRA training script
│   ├── colab_finetune.py       # Google Colab version
│   ├── inference.py            # Test/run the fine-tuned model
│   ├── compare_models.py       # Base vs fine-tuned comparison
│   ├── finetune_requirements.txt # GPU training dependencies
│   ├── DEPLOYMENT_GUIDE.md     # How to deploy the fine-tuned model
│   └── README.md               # Step-by-step fine-tuning guide
│
├── datasets/                   # Training data
│   ├── indian_recipes.csv              # 12MB — thousands of Indian recipes
│   ├── indian_nutrition_guidelines.json # Curated nutrition rules by region/condition
│   ├── indian_diet_finetune.jsonl      # 3.7MB — generated training examples
│   ├── indian_diet_test.jsonl          # Test set (50 examples)
│   ├── create_finetune_dataset.py      # Script that generated the JSONL
│   └── process_and_ingest.py          # Script to ingest recipes into ChromaDB
│
├── benchmark/                  # Model evaluation framework
│   ├── benchmark_specification.md
│   ├── prompts/                # Test prompts
│   ├── results/                # Model outputs
│   ├── scores/                 # Evaluation scores
│   └── scripts/                # Benchmark automation
│
├── docs/                       # Documentation (you are here)
│   ├── PROJECT_OVERVIEW.md     # This file
│   ├── how_rag_works.md
│   ├── qlora_finetuning_summary.md
│   ├── pipeline_visual.md
│   └── PHASE_0_WORKSPACE.md
│
├── scripts/
│   └── prepare_finetuning.sh   # Shell script to set up fine-tuning env
```

</details>

---

## Phase 1 — Dataset

### What data do we use?

**1. `indian_recipes.csv` (12 MB)**
- Thousands of real Indian recipes scraped and compiled
- Fields: ingredients, instructions, cuisine, diet type, prep time, cook time, servings, course

**2. `indian_nutrition_guidelines.json`**
- Hand-curated nutrition guidelines organized by topic and region
- Topics: protein sources, fat loss, muscle gain, diabetes, PCOS, hypertension, pre/post-workout
- Regions: Maharashtra, Gujarat, Punjab, Tamil Nadu, Karnataka, Kerala, West Bengal, Andhra Pradesh

**3. `indian_diet_finetune.jsonl` (3.7 MB — auto-generated)**
- **~10,000+ instruction-response pairs** created by `create_finetune_dataset.py`
- Three sources:
  - Nutrition guidelines → converted to Q&A format (3 question variations per guideline)
  - Recipes → converted to "how do I make X?" format (4 variations per recipe)
  - Synthetic queries → 200 auto-generated diet planning scenarios
- Format: `{"instruction": "...", "output": "..."}` — standard SFT format

### How the dataset was created

```python
# create_finetune_dataset.py
# Converts nutrition guidelines → instruction-response pairs
for guideline in nutrition_guidelines:
    questions = ["What are good protein sources in Gujarat?", ...]
    for question in questions:
        training_data.append({"instruction": question, "output": guideline["content"]})

# Converts recipes → instruction-response pairs
for recipe in recipes_sample:
    questions = ["How do I make Punjabi Main Course?", ...]
    training_data.append({"instruction": question, "output": structured_recipe})

# Synthetic diet planning queries
for _ in range(200):
    region = random.choice(regions)
    goal = random.choice(goals)
    training_data.append({"instruction": f"Suggest {diet} breakfast for {goal} in {region}", ...})
```

---

## Phase 2 — Fine-Tuning with QLoRA/LoRA

### Files involved
- `models/train_qlora.py` — main training script
- `models/colab_finetune.py` — Google Colab version
- `models/finetune_requirements.txt` — GPU dependencies
- `datasets/indian_diet_finetune.jsonl` — training data

### Training Configuration

| Parameter | Value | Why |
|---|---|---|
| Base model | `google/gemma-2-9b-it` | Instruction-tuned, strong base |
| Quantization | 4-bit NF4 (BitsAndBytes) | Reduces 18GB model to ~5GB VRAM |
| LoRA rank (r) | 16 | Balance between capacity and efficiency |
| LoRA alpha | 32 | Scaling = 2× rank (standard practice) |
| LoRA dropout | 0.05 | Light regularization |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj | All attention + MLP layers |
| Epochs | 3 | Enough to learn without overfitting |
| Batch size | 2 × 8 grad accum = 16 effective | Memory-efficient |
| Learning rate | 2e-4 | Standard for LoRA |
| Scheduler | Cosine | Smooth decay |
| Max sequence length | 512 tokens | Covers our prompt+response length |
| Optimizer | paged_adamw_32bit | Memory-efficient Adam |

### What gets saved after training

```
gemma3_indian_diet_qlora/
├── adapter_model.safetensors   # The LoRA weight deltas (~50-200MB)
├── adapter_config.json         # LoRA configuration
├── tokenizer files             # Same as base model
└── training_config.json        # Metadata (date, params, dataset size)
```

The key insight: **only the adapter files are saved**, not the full model weights. The adapters are then merged with the base model at inference time.

### Where is training run?

The model is too large to train on a CPU. Training requires a GPU:

| Platform | GPU | VRAM | Cost | Time |
|---|---|---|---|---|
| Google Colab | T4 | 16GB | Free | 4-6 hrs |
| Google Colab Pro | A100 | 40GB | $10/mo | 2-3 hrs |
| RunPod | RTX 3090 | 24GB | ~$1 total | 2-4 hrs |
| Vast.ai | RTX 4090 | 24GB | ~$0.75 total | 1-2 hrs |
| Kaggle | P100/T4 | 16GB | Free | 4-6 hrs |

---

## Phase 3 — RAG System

### What is the problem RAG solves?

Even after fine-tuning, the model's knowledge is **frozen at training time**. If we want to look up a specific recipe or a specific nutritional guideline dynamically, we need RAG.

RAG = **Give the model fresh context at query time** by searching a database.

### Files involved
- `rag/ingest.py` — loads data into ChromaDB
- `rag/retrieve.py` — searches ChromaDB and returns relevant context
- `rag/chroma_db/` — the local vector database (persistent files)
- `datasets/process_and_ingest.py` — ingests recipes into ChromaDB

### Two ChromaDB Collections

**1. `nutrition_guidelines`**
- Contains: curated nutrition rules from `indian_nutrition_guidelines.json`
- Format: `"Topic: protein. Region: Gujarat. Guideline: Besan (chickpea flour) is the primary protein source..."`
- Retrieved: 2 most relevant documents per query

**2. `real_indian_recipes`**
- Contains: actual recipes from `indian_recipes.csv`
- Format: structured recipe text with ingredients and instructions
- Retrieved: 3 most relevant recipes per query

### Embedding Model: `nomic-embed-text`

- Runs locally via Ollama (no internet needed)
- Converts text → 768-dimensional vectors
- Used both at **ingest time** (to store) and **query time** (to search)
- Semantic search: "protein breakfast Tamil Nadu" finds "pesarattu" and "idli-sambar" even without exact keyword match

### How retrieve.py works

```python
def get_context(query_text: str, n_results: int = 2) -> str:
    # 1. Embed the user's query using nomic-embed-text
    # 2. Search nutrition_guidelines collection → top 2 results
    # 3. Search real_indian_recipes collection → top 3 results
    # 4. Concatenate all 5 documents into one context string
    # 5. Return context to the backend
    return "\n\n".join(rules_docs + recipes_docs)
```

---

## Phase 4 — Backend API

### File: `backend/main.py`

FastAPI application with 4 endpoints:

| Endpoint | Method | What it does |
|---|---|---|
| `/` | GET | Serves `frontend/index.html` |
| `/style.css` | GET | Serves frontend CSS |
| `/app.js` | GET | Serves frontend JavaScript |
| `/health` | GET | Health check → `{"status": "ok"}` |
| `/api/generate` | POST | Direct Ollama call (no RAG) |
| `/api/rag_generate` | POST | RAG + Ollama call (main endpoint) |

### `/api/rag_generate` — The Main Endpoint

```
1. Receive {prompt, model} from frontend
2. Call rag/retrieve.py → get 5 relevant documents from ChromaDB
3. Build augmented prompt:
      "You are an expert AI Nutritionist.
       Context: [5 retrieved documents]
       User Request: [original prompt]"
4. POST augmented prompt to Ollama → gemma3:4b
5. Return {status, response, retrieved_context, duration}
```

### Request/Response Format

**Request:**
```json
{
  "prompt": "# Comprehensive Fitness Analysis\n**CLIENT PROFILE:** ...",
  "model": "gemma3:4b"
}
```

**Response:**
```json
{
  "status": "success",
  "model": "gemma3:4b",
  "retrieved_context": "Topic: protein. Region: Gujarat...",
  "response": "## Your Personalized Fitness Plan\n...",
  "duration": 45.3
}
```

### CORS Configuration
All origins are allowed (`*`) so the frontend can call the API from any port during development.

---

## Phase 5 — Frontend

### Files: `frontend/index.html`, `frontend/style.css`, `frontend/app.js`

### Form Fields Collected

**Basic Information:** Name, Age, Gender, Height, Weight, Target Weight

**Location & Lifestyle:** Indian State/Region, Activity Level, Occupation Type

**Fitness Goals:** Primary Goal, Timeline, Workout Days per Week

**Diet Preferences:** Diet Type (Veg/Vegan/Non-veg/Jain etc.), Meals per Day, Food Allergies, Disliked Foods

**Health Conditions:** Medical Conditions (multi-select), Medications, Supplements

**Additional:** Sleep Hours, Water Intake, Stress Level, Additional Notes

### Calculations done in the browser (app.js)

| Metric | Formula |
|---|---|
| BMI | weight / (height_m)² |
| BMR | Mifflin-St Jeor equation (different for male/female) |
| TDEE | BMR × activity multiplier (1.2 to 1.9) |
| Target Calories | TDEE ± 500 (based on goal) |
| Recommended Steps | Base steps by activity level ± goal adjustment |

### Prompt Construction

The frontend builds a structured markdown prompt before sending to the backend:

```
# Comprehensive Fitness and Nutrition Analysis

**CLIENT PROFILE:**
- Name, Age, Gender, Height, Weight
- BMI, BMR, TDEE (pre-calculated)
- Target Weight, Region

**LIFESTYLE:** Activity level, occupation, sleep, water, stress

**FITNESS GOALS:** Goal, timeline, workout days

**DIETARY PREFERENCES:** Diet type, meals, allergies, dislikes

**HEALTH CONDITIONS:** Medical conditions, medications, supplements

**TASK:** Provide: Health Assessment, Calorie Targets, Meal Plan,
Sample Schedule, Workout Recommendations, Lifestyle tips...
```

---

## What is LoRA? Why did we use it?

### The Problem with Full Fine-Tuning

A full fine-tuning of Gemma 3:4b would:
- Require updating **all 4 billion parameters**
- Need **80+ GB of GPU VRAM** (impossible on consumer hardware)
- Cost hundreds of dollars in cloud GPU time
- Produce a 16GB+ model file

### What LoRA Does

**LoRA = Low-Rank Adaptation**

Instead of updating all weights, LoRA:
1. **Freezes** all original model weights
2. **Adds tiny trainable matrices** next to specific layers
3. The added matrices are **low-rank** (much smaller than the original)

Mathematically, for a weight matrix W:
```
New output = W·x + (B·A)·x × (alpha/r)
             ↑           ↑
        frozen        trainable
        (original)    (LoRA adapter, ~1% of params)
```

Where:
- `A` is a matrix of shape `[r, input_dim]` — initialized randomly
- `B` is a matrix of shape `[output_dim, r]` — initialized to zero
- `r` = rank (we use 16) — controls how many parameters to train
- `alpha` = scaling factor (we use 32)

### Which layers get LoRA adapters?

We target all attention and MLP projection layers:
- `q_proj`, `k_proj`, `v_proj`, `o_proj` — attention layers
- `gate_proj`, `up_proj`, `down_proj` — feedforward MLP layers

### Trainable Parameters with LoRA

| | Parameters | Size |
|---|---|---|
| Full model | ~4 billion | ~16 GB |
| LoRA adapters only | ~20–40 million (< 1%) | ~50–200 MB |

**Result:** We train less than 1% of the model's parameters, but the model learns our domain.

---

## What is QLoRA?

QLoRA = **Q**uantized LoRA

It adds one more step on top of LoRA: **quantize the frozen base model to 4-bit**.

### 4-bit Quantization (NF4)

Instead of storing each weight as a 32-bit float (4 bytes), we store it as a 4-bit integer (0.5 bytes).

```
Memory reduction: 32-bit → 4-bit = 8× smaller
Gemma 3:4b in 4-bit: ~2.5 GB VRAM instead of 16 GB
```

We use **NF4 (Normal Float 4)** quantization — optimized for weights that follow a normal distribution (which neural network weights typically do).

### Double Quantization

We also apply double quantization — quantizing the quantization constants themselves, saving another ~0.5 GB.

### BF16 Compute

Even though weights are stored in 4-bit, computations happen in **bfloat16** (16-bit) for stability and accuracy.

### Summary: QLoRA Stack

```
Base Model: stored in 4-bit NF4  ← nearly no VRAM
LoRA Adapters: trained in bf16   ← tiny additional VRAM
Gradients: only for adapter params ← minimal VRAM
Result: train a 9B model on a 12GB GPU
```

---

## Why Fine-Tune at all?

### The Problem with a Generic Model

If you ask the base Gemma 3:4b: *"Suggest a protein-rich breakfast for a diabetic person in Tamil Nadu"*, it might:
- Give generic Western advice (eggs, chicken breast, protein shake)
- Not know local terms like pesarattu, ragi, kozhukattai
- Not apply correct macros for South Indian diabetic diet
- Give generic diabetes advice without regional cultural context

### What Fine-Tuning Changes

After training on ~10,000 Indian diet-specific instruction-response pairs, the model:
- **Knows Indian food vocabulary**: ragi, jowar, besan, bajra, poha, thalipeeth, pesarattu, etc.
- **Understands regional cuisines**: knows that Tamil Nadu uses rice + sambar, Punjab uses roti + dal, etc.
- **Applies correct medical nutrition guidelines** for Indian conditions
- **Formats responses** consistently — with sections, bullet points, macro breakdowns
- **Speaks the right language** — uses Indian measurements, Indian food contexts

---

## Base vs Fine-Tuned — What's the difference?

### Example Query
*"Suggest a muscle gain breakfast for a vegetarian in Punjab"*

**Base Gemma 3:4b response:**
```
For muscle gain, I recommend:
- Greek yogurt with granola
- Eggs (3 whole eggs + 2 whites)
- Protein shake with milk
- Oatmeal with berries
```

**Fine-Tuned Gemma 3:4b response:**
```
## Punjabi Muscle Gain Breakfast (Vegetarian)

**Macro Targets:** ~600 kcal | Protein: 40g | Carbs: 60g | Fat: 20g

**Meal Option 1:**
- Paneer bhurji (200g paneer) with 2 whole wheat rotis
- Glass of full-fat milk (250ml)
- 5 soaked almonds

**Meal Option 2:**
- Dal (chana dal) with brown rice
- Curd (200g) on the side
- Mixed sabzi (seasonal vegetables)

**Why this works for Punjab:**
Paneer is the highest-protein food in Punjabi cuisine (~18g/100g).
Chana dal provides slow-digesting protein + complex carbs...
```

### Benchmark Results (from `models/compare_models.py`)

The comparison script tests 8 categories:
- Regional Protein Sources
- Diabetes Management
- Muscle Building
- PCOS Management
- Fat Loss
- Pre-Workout Nutrition
- Recipe Knowledge
- Specific Conditions

Expected improvement: **+20–40% keyword relevance score** on Indian-specific queries.

---

## What is RAG and why combine it with Fine-Tuning?

### Fine-Tuning alone has limitations

Fine-tuning teaches the model **how to respond** (style, format, domain knowledge). But:
- The model can still **hallucinate** specific nutritional values
- Its knowledge is frozen at the time of training
- It cannot look up a **specific recipe** dynamically

### RAG alone has limitations

RAG retrieves real documents and injects them as context. But:
- A generic model doesn't know how to **interpret** Indian nutrition terms
- The model response style may be inconsistent
- Without domain knowledge, the model may ignore or misuse the retrieved context

### Fine-Tuning + RAG = Best of both worlds

| Capability | Fine-Tuning | RAG | Combined |
|---|---|---|---|
| Indian food vocabulary | ✅ | ❌ | ✅ |
| Consistent response format | ✅ | ❌ | ✅ |
| Accurate specific facts | ⚠️ | ✅ | ✅ |
| Real recipe lookup | ❌ | ✅ | ✅ |
| Up-to-date guidelines | ❌ | ✅ | ✅ |
| Medical condition awareness | ✅ | ✅ | ✅✅ |

---

## Data Flow — End to End

```
1. USER fills form in browser
        │
2. app.js calculates BMI, BMR, TDEE
        │
3. app.js builds a structured markdown prompt
        │
4. POST /api/rag_generate → FastAPI backend
        │
5. backend calls rag/retrieve.py
        │
6. retrieve.py embeds the prompt using nomic-embed-text (via Ollama)
        │
7. ChromaDB returns top 2 nutrition rules + top 3 recipes
        │
8. backend builds augmented prompt:
        "You are an expert nutritionist.
         Context: [retrieved documents]
         User Request: [original prompt]"
        │
9. backend POSTs to Ollama → gemma3:4b
        │
10. Ollama runs inference (30-90 seconds on CPU)
        │
11. backend returns JSON response to frontend
        │
12. app.js renders markdown response using marked.js
        │
13. USER sees their personalized plan with:
        - BMI/BMR/TDEE summary card
        - Full nutrition + workout plan (markdown)
        - Daily step target
```

---

## Tools & Libraries Reference

### Runtime

| Tool | Version | Role |
|---|---|---|
| **Ollama** | Latest | Local LLM server, runs gemma3:4b and nomic-embed-text |
| **gemma3:4b** | Google | The fine-tuned language model |
| **nomic-embed-text** | Latest | Embedding model for RAG |
| **ChromaDB** | Latest | Local vector database |

### Backend

| Library | Version | Role |
|---|---|---|
| `fastapi` | 0.100.1 | Web framework |
| `uvicorn` | 0.23.2 | ASGI server |
| `pydantic` | 1.10.13 | Request/response validation |
| `requests` | 2.32.3 | HTTP calls to Ollama |
| `chromadb` | Latest | ChromaDB Python client |

### Fine-Tuning (GPU only)

| Library | Version | Role |
|---|---|---|
| `torch` | ≥2.1.0 | Deep learning framework |
| `transformers` | ≥4.38.0 | Load Gemma model + tokenizer |
| `peft` | ≥0.8.0 | LoRA implementation |
| `bitsandbytes` | ≥0.42.0 | 4-bit quantization |
| `accelerate` | ≥0.26.0 | Distributed training utilities |
| `datasets` | ≥2.16.0 | Load JSONL training data |
| `trl` | ≥0.7.10 | SFTTrainer for supervised fine-tuning |
| `tensorboard` | ≥2.15.0 | Training visualization |

### Frontend

| Tool | Role |
|---|---|
| Vanilla HTML5 | Structure |
| Vanilla CSS3 | Styling (custom dark theme) |
| Vanilla JavaScript (ES6) | Form logic, API calls |
| `marked.js` (CDN) | Render AI markdown response in browser |
| Google Fonts (Inter) | Typography |

---

## How to Run Locally

### Prerequisites
- Ollama installed: https://ollama.ai
- Python 3.10+
- 8GB+ RAM (for gemma3:4b CPU inference)

### Step 1 — Pull models
```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### Step 2 — Ingest data into ChromaDB
```bash
cd rag
pip install chromadb
python ingest.py
cd ../datasets
python process_and_ingest.py   # ingests recipes
```

### Step 3 — Start Backend (Phase 6+; app is parked)

```bash
cd parked/phase6_app/backend
pip install -r requirements.txt
source venv/bin/activate   # if you use a venv
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4 — Open Browser
```
http://localhost:8000
```

Everything — frontend, backend, API — runs on port 8000 when using the parked app.

---

## Deployment

This project targets **local Ollama + optional fine-tuned adapters** (`models/DEPLOYMENT_GUIDE.md`). Cloud Railway/Render configs were removed; hosting a GPU + Ollama stack is a separate Phase 6+ decision.

---

## Key Design Decisions

1. **Why Gemma 3:4b?** — Small enough to run on CPU (8–16GB RAM), large enough for quality output. Benchmarked against llama3.2:3b and qwen3:4b.

2. **Why not use OpenAI/Gemini API?** — Privacy (user health data), zero API cost, fully offline capability.

3. **Why QLoRA instead of full fine-tuning?** — Makes it possible to fine-tune on a single consumer GPU or cheap cloud GPU ($1-2 total cost vs $50-100+).

4. **Why ChromaDB?** — Local, no server setup needed, persistent, Python-native, works without Docker.

5. **Why Vanilla JS (no React)?** — Simplicity. The frontend is a single-page form. No build step, no npm, instantly served.

6. **Why FastAPI serves the frontend too?** — Single server, no CORS issues, no separate static server needed. The frontend calls `/api/rag_generate` as a relative URL.
