# Fine-Tune Gemma 3 on Indian Diet Data - Google Colab Notebook
# =============================================================
# 
# This notebook fine-tunes Gemma using QLoRA on Google Colab
# 
# Steps:
# 1. Upload your dataset files
# 2. Run all cells in order
# 3. Download the fine-tuned model
# 
# Runtime: Change to T4 GPU (Runtime → Change runtime type → T4)

# ============================================================================
# CELL 1: Check GPU
# ============================================================================

!nvidia-smi

# ============================================================================
# CELL 2: Install Dependencies
# ============================================================================

!pip install -q torch transformers peft bitsandbytes accelerate datasets trl sentencepiece protobuf

# ============================================================================
# CELL 3: Upload Dataset
# ============================================================================

from google.colab import files
import os

print("📤 Upload your training dataset (indian_diet_finetune.jsonl)")
uploaded = files.upload()

# Verify upload
for filename in uploaded.keys():
    print(f"✅ Uploaded: {filename} ({len(uploaded[filename])} bytes)")

# ============================================================================
# CELL 4: Configuration
# ============================================================================

# Model Configuration
MODEL_NAME = "google/gemma-2-9b-it"
DATASET_PATH = "indian_diet_finetune.jsonl"
OUTPUT_DIR = "./gemma3_indian_diet_qlora"

# Training Configuration
NUM_EPOCHS = 3
BATCH_SIZE = 2
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 512

print(f"✅ Configuration set:")
print(f"   Model: {MODEL_NAME}")
print(f"   Dataset: {DATASET_PATH}")
print(f"   Epochs: {NUM_EPOCHS}")
print(f"   Batch Size: {BATCH_SIZE}")

# ============================================================================
# CELL 5: Load Model with QLoRA
# ============================================================================

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

print("🤖 Loading model with 4-bit quantization...")

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

# Prepare for training
model = prepare_model_for_kbit_training(model)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Check memory
memory_allocated = torch.cuda.memory_allocated() / 1024**3
print(f"✅ Model loaded! GPU Memory: {memory_allocated:.2f} GB")

# ============================================================================
# CELL 6: Apply LoRA Adapters
# ============================================================================

# LoRA configuration
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ============================================================================
# CELL 7: Load Dataset
# ============================================================================

from datasets import load_dataset

print(f"📂 Loading dataset: {DATASET_PATH}")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
print(f"✅ Loaded {len(dataset)} examples")

# Show sample
print("\n📋 Sample:")
print(f"Instruction: {dataset[0]['instruction']}")
print(f"Output: {dataset[0]['output'][:150]}...")

# ============================================================================
# CELL 8: Format Data for Gemma
# ============================================================================

def format_instruction_gemma(sample):
    """Format for Gemma chat template"""
    return f"""<start_of_turn>user
{sample['instruction']}<end_of_turn>
<start_of_turn>model
{sample['output']}<end_of_turn>"""

print("✅ Data formatter ready")

# ============================================================================
# CELL 9: Setup Training
# ============================================================================

from transformers import TrainingArguments
from trl import SFTTrainer

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    optim="paged_adamw_32bit",
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    logging_steps=10,
    save_strategy="epoch",
    fp16=False,
    bf16=True,
    max_grad_norm=0.3,
    group_by_length=True,
    report_to="none",  # Disable wandb
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=MAX_SEQ_LENGTH,
    formatting_func=format_instruction_gemma,
)

print("✅ Trainer initialized")

# ============================================================================
# CELL 10: Start Training
# ============================================================================

print("🚀 Starting training...")
print("This will take 2-4 hours depending on GPU")
print("You can close this tab - training will continue")

trainer.train()

print("\n✅ Training completed!")

# ============================================================================
# CELL 11: Save Model
# ============================================================================

# Save model
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"✅ Model saved to: {OUTPUT_DIR}")

# ============================================================================
# CELL 12: Test the Model
# ============================================================================

print("🧪 Testing the fine-tuned model...")

# Test query
test_query = "What are good protein sources for vegetarians in Gujarat?"

prompt = f"""<start_of_turn>user
{test_query}<end_of_turn>
<start_of_turn>model
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
    )

response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(f"\nQuery: {test_query}")
print(f"\nResponse: {response}")

# ============================================================================
# CELL 13: Download Model
# ============================================================================

# Zip the model directory
!zip -r gemma3_indian_diet_qlora.zip {OUTPUT_DIR}

print("\n📥 Downloading model...")
from google.colab import files
files.download('gemma3_indian_diet_qlora.zip')

print("✅ Download started! Check your browser downloads.")
print("\n🎉 Fine-tuning complete!")
print("\nNext steps:")
print("1. Extract the zip file on your local machine")
print("2. Use inference.py to test the model")
print("3. Deploy in your Fitness-AI backend")
