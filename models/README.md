# QLoRA Fine-Tuning for Gemma 3 on Indian Diet Data

This directory contains scripts and configurations for fine-tuning Google's Gemma model on Indian diet and nutrition data using QLoRA (Quantized Low-Rank Adaptation).

## 🎯 Why Fine-Tuning?

**Problem with Base Model + RAG:**
- Generic responses that lack cultural context
- Inconsistent terminology for Indian foods
- Requires large RAG context every time
- Higher inference costs

**Benefits After Fine-Tuning:**
- ✅ Understands Indian ingredients natively (dal, roti, jowar, etc.)
- ✅ Regional food knowledge (Maharashtra vs Tamil Nadu cuisines)
- ✅ Consistent medical/nutrition advice
- ✅ Reduced RAG context needed
- ✅ Faster inference, lower costs

## 📋 Prerequisites

### Hardware Requirements
- **GPU**: Minimum 12GB VRAM (RTX 3090, T4, P100, A100)
- **RAM**: 16GB system RAM
- **Storage**: 20GB free space

### No GPU? Use Cloud:
| Service | GPU | VRAM | Cost | Free Tier |
|---------|-----|------|------|-----------|
| **Google Colab Pro** | T4 | 16GB | $9.99/month | Yes (limited) |
| **Kaggle** | P100/T4 | 16GB | FREE | 30hrs/week |
| **RunPod** | RTX 3090 | 24GB | $0.34/hr | No |
| **Vast.ai** | Various | 12-24GB | $0.25-0.50/hr | No |
| **Lambda Labs** | A100 | 40GB | $1.10/hr | No |

**Recommended for beginners:** Kaggle (free) or Google Colab Pro ($10/month)

## 🚀 Quick Start

### Step 1: Prepare Dataset
```bash
# Already done! Dataset created with 2,228 examples
cd /home/hello/Fitness-AI/datasets
ls -lh indian_diet_finetune.jsonl  # Training data
ls -lh indian_diet_test.jsonl      # Test data
```

### Step 2: Upload to Cloud GPU

**Option A: Google Colab**
1. Go to https://colab.research.google.com/
2. Upload these files:
   - `models/train_qlora.py`
   - `models/finetune_requirements.txt`
   - `datasets/indian_diet_finetune.jsonl`
   - `datasets/indian_diet_test.jsonl`
3. Change runtime: Runtime → Change runtime type → T4 GPU

**Option B: Kaggle**
1. Go to https://www.kaggle.com/
2. Create new notebook
3. Enable GPU: Settings → Accelerator → GPU T4 x2
4. Upload files to Kaggle dataset

**Option C: RunPod/Vast.ai**
1. Rent a GPU instance (RTX 3090 recommended)
2. SSH into instance
3. Clone your repository or upload files

### Step 3: Install Dependencies
```bash
pip install -r finetune_requirements.txt
```

This installs:
- `torch` - PyTorch for deep learning
- `transformers` - Hugging Face model library
- `peft` - Parameter-Efficient Fine-Tuning (LoRA)
- `bitsandbytes` - 4-bit quantization
- `trl` - Transformer Reinforcement Learning
- `datasets` - Dataset management
- `accelerate` - Distributed training utilities

### Step 4: Start Training
```bash
cd models
python train_qlora.py
```

**Expected Output:**
```
======================================================================
QLoRA Fine-Tuning: Gemma 3 on Indian Diet Data
======================================================================

✅ GPU Detected!
   Device: NVIDIA GeForce RTX 3090
   VRAM: 24.00 GB

📂 Loading dataset from: ../datasets/indian_diet_finetune.jsonl
✅ Loaded 2228 training examples

🤖 Loading model with 4-bit quantization...
✅ Model loaded and quantized

💾 GPU Memory Allocated: 5.23 GB

🔧 Setting up LoRA adapters...
📊 Trainable Parameters:
trainable params: 42,467,328 || all params: 9,242,467,328 || trainable%: 0.46%

🚀 Starting training...
⏰ Training started at: 2026-07-14 14:30:00

Epoch 1/3: 100%|██████████| 557/557 [45:23<00:00, 4.89s/it]
Epoch 2/3: 100%|██████████| 557/557 [45:11<00:00, 4.87s/it]
Epoch 3/3: 100%|██████████| 557/557 [45:08<00:00, 4.86s/it]

✅ Training completed!
⏰ Duration: 2:15:42
📁 Model saved to: ./gemma3_indian_diet_qlora

🎉 Fine-tuning completed successfully!
```

**Training Time Estimates:**
- RTX 3090: 2-3 hours
- T4 (Colab): 4-5 hours
- P100 (Kaggle): 3-4 hours
- A100: 1-2 hours

**Cost Estimates:**
- Kaggle: $0 (free)
- Google Colab Pro: $10/month (unlimited)
- RunPod RTX 3090: $0.68-1.02 total
- Vast.ai RTX 4090: $0.50-1.00 total

### Step 5: Test the Model
```bash
# Test with predefined queries
python inference.py --mode test

# Interactive chat mode
python inference.py --mode interactive

# Test base model for comparison
python inference.py --mode test --base
```

### Step 6: Compare Base vs Fine-Tuned
```bash
python compare_models.py
```

This generates a detailed comparison showing:
- Side-by-side responses
- Keyword relevance scores
- Response time comparison
- Overall improvement metrics

## 📊 Expected Results

### Before Fine-Tuning (Base Model):
```
Query: What are good protein sources for vegetarians in Gujarat?

Base Model: "Vegetarians can get protein from sources like legumes,
nuts, seeds, tofu, and dairy products. Beans, lentils, chickpeas are
excellent choices..."
```
❌ Generic, no regional knowledge

### After Fine-Tuning:
```
Query: What are good protein sources for vegetarians in Gujarat?

Fine-Tuned Model: "In Gujarat, besan (chickpea flour) is an excellent
protein source providing 21g protein per 100g. It's commonly used in
Besan Chilla for breakfast. Other options include moong dal, chana dal,
and dhokla made from fermented chickpea batter..."
```
✅ Specific, culturally aware, practical

## 📁 Output Files

After training, you'll find these files in `./gemma3_indian_diet_qlora/`:

```
gemma3_indian_diet_qlora/
├── adapter_model.safetensors    # LoRA adapter weights (~85MB)
├── adapter_config.json          # LoRA configuration
├── tokenizer.json               # Tokenizer
├── tokenizer_config.json        # Tokenizer config
├── special_tokens_map.json      # Special tokens
├── training_config.json         # Training metadata
└── checkpoints/                 # Intermediate checkpoints
    ├── checkpoint-557/          # Epoch 1
    ├── checkpoint-1114/         # Epoch 2
    └── checkpoint-1671/         # Epoch 3
```

**Important:** Only the adapter files are needed for deployment (~85MB), not the full model (9GB).

## 🔧 Configuration Options

### Adjust Training Parameters

Edit `train_qlora.py`:

```python
# For faster training (less quality)
TRAINING_CONFIG = {
    "num_train_epochs": 2,              # Reduce epochs
    "per_device_train_batch_size": 4,   # Increase if you have VRAM
    "learning_rate": 3e-4,              # Higher learning rate
}

# For better quality (slower)
TRAINING_CONFIG = {
    "num_train_epochs": 5,              # More epochs
    "per_device_train_batch_size": 1,   # Reduce if OOM
    "learning_rate": 1e-4,              # Lower learning rate
}

# Adjust LoRA rank (higher = more parameters)
QLORA_CONFIG = {
    "r": 32,  # Increase from 16 (doubles parameters)
}
```

### Memory Issues?

**If you get "CUDA out of memory" error:**

1. **Reduce batch size:**
```python
"per_device_train_batch_size": 1,
"gradient_accumulation_steps": 16,  # Maintain effective batch size
```

2. **Use smaller model:**
```python
MODEL_NAME = "google/gemma-2-2b-it"  # 2B instead of 9B
```

3. **Reduce sequence length:**
```python
"max_seq_length": 256,  # Reduce from 512
```

## 📥 Download Fine-Tuned Model

After training on cloud GPU, download the model:

```bash
# From Colab/Kaggle, zip and download
!zip -r gemma3_indian_diet_qlora.zip gemma3_indian_diet_qlora/

# Or use Colab files panel:
# Right-click → Download
```

**Transfer to your local machine:**
```bash
# Upload to your project
cp -r gemma3_indian_diet_qlora /home/hello/Fitness-AI/models/
```

## 🔄 Use in Your Backend

### Option 1: Convert to GGUF for Ollama (CPU Deployment)

```bash
# Merge LoRA adapters with base model
python -c "
from peft import PeftModel
from transformers import AutoModelForCausalLM

base = AutoModelForCausalLM.from_pretrained('google/gemma-2-9b-it')
model = PeftModel.from_pretrained(base, './gemma3_indian_diet_qlora')
model = model.merge_and_unload()
model.save_pretrained('./gemma3_indian_diet_merged')
"

# Convert to GGUF (requires llama.cpp)
# Then import to Ollama
ollama create gemma3-indian-diet -f Modelfile
```

### Option 2: Serve with GPU

Update your `backend/main.py` to use Hugging Face instead of Ollama:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load once at startup
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-9b-it",
    device_map="auto"
)
model = PeftModel.from_pretrained(model, "./models/gemma3_indian_diet_qlora")
tokenizer = AutoTokenizer.from_pretrained("./models/gemma3_indian_diet_qlora")

@app.post("/api/generate")
def generate(request: GenerateRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"response": response}
```

## 🐛 Troubleshooting

### "No GPU detected"
- Check runtime type in Colab/Kaggle
- Verify with: `nvidia-smi`

### "CUDA out of memory"
- Reduce batch size to 1
- Use smaller model (2B instead of 9B)
- Reduce max_seq_length

### "Module not found"
- Run: `pip install -r finetune_requirements.txt`

### Model not loading
- Ensure training completed successfully
- Check that `adapter_model.safetensors` exists

### Poor quality after fine-tuning
- Increase training epochs (3 → 5)
- Increase dataset size
- Adjust learning rate (try 1e-4)

## 📚 Next Steps

1. **Evaluate on test set:** Use `indian_diet_test.jsonl` for validation
2. **Iterate on dataset:** Add more regional examples, edge cases
3. **Experiment with hyperparameters:** Try different ranks, learning rates
4. **Deploy:** Integrate into your backend API
5. **Monitor:** Track user feedback and model performance

## 🔗 Resources

- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [Gemma Model Card](https://huggingface.co/google/gemma-2-9b-it)
- [TRL Documentation](https://huggingface.co/docs/trl)

## ❓ FAQ

**Q: Can I fine-tune without GPU?**
A: No, GPU is required for practical training times. Use free cloud options like Kaggle.

**Q: How much does fine-tuning cost?**
A: $0 on Kaggle/Colab Free, or $1-2 on budget cloud GPUs.

**Q: Can I use the fine-tuned model on CPU?**
A: Yes! Convert to GGUF format and use with Ollama (your current setup).

**Q: Do I need to retrain if I add more data?**
A: Yes, but you can start from the previous checkpoint to speed up training.

**Q: Is QLoRA worse than full fine-tuning?**
A: Only 1-2% quality difference, negligible for domain-specific tasks like this.

---

**Need Help?** Open an issue or check the troubleshooting section above.
