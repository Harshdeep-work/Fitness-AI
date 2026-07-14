"""
QLoRA Fine-Tuning Script for Gemma 3 on Indian Diet Data
=========================================================

This script fine-tunes Google's Gemma model on Indian diet/nutrition data
using QLoRA (Quantized Low-Rank Adaptation) for memory efficiency.

Requirements:
- GPU with at least 12GB VRAM (e.g., RTX 3090, T4, P100)
- Run on Google Colab, Kaggle, RunPod, or Vast.ai
- Install dependencies: pip install -r finetune_requirements.txt

Expected Training Time: 2-4 hours on RTX 3090
Expected Cost: $1-2 on budget cloud GPUs
"""

import torch
import os
import json
from datetime import datetime
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model Configuration
MODEL_NAME = "google/gemma-2-9b-it"  # Gemma 2 9B Instruction-tuned
# Alternative smaller models if memory is limited:
# MODEL_NAME = "google/gemma-2-2b-it"  # Gemma 2 2B (needs ~4GB VRAM)

# Dataset Configuration
DATASET_PATH = "../datasets/indian_diet_finetune.jsonl"
TEST_DATASET_PATH = "../datasets/indian_diet_test.jsonl"

# Output Configuration
OUTPUT_DIR = "./gemma3_indian_diet_qlora"
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "checkpoints")

# QLoRA Configuration
QLORA_CONFIG = {
    "r": 16,                          # Rank (8, 16, 32, 64)
    "lora_alpha": 32,                 # Scaling factor (usually 2x rank)
    "lora_dropout": 0.05,             # Dropout for regularization
    "target_modules": [               # Which layers to apply LoRA
        "q_proj",                     # Query projection
        "k_proj",                     # Key projection
        "v_proj",                     # Value projection
        "o_proj",                     # Output projection
        "gate_proj",                  # MLP gate
        "up_proj",                    # MLP up
        "down_proj",                  # MLP down
    ],
}

# Training Configuration
TRAINING_CONFIG = {
    "num_train_epochs": 3,            # Number of training epochs
    "per_device_train_batch_size": 2, # Batch size per GPU
    "gradient_accumulation_steps": 8, # Effective batch = 2*8 = 16
    "learning_rate": 2e-4,            # Learning rate for LoRA
    "lr_scheduler_type": "cosine",    # Learning rate scheduler
    "warmup_ratio": 0.03,             # Warmup steps
    "logging_steps": 10,              # Log every N steps
    "save_strategy": "epoch",         # Save checkpoints per epoch
    "max_seq_length": 512,            # Maximum sequence length
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_gpu():
    """Check if GPU is available and print info"""
    if not torch.cuda.is_available():
        print("❌ ERROR: No GPU detected!")
        print("This script requires a GPU to run.")
        print("\n💡 Solutions:")
        print("   1. Use Google Colab (free T4 GPU): https://colab.research.google.com/")
        print("   2. Use Kaggle (free P100/T4): https://www.kaggle.com/")
        print("   3. Rent GPU: RunPod ($0.34/hr), Vast.ai ($0.25/hr)")
        return False
    
    device_name = torch.cuda.get_device_name(0)
    vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    print("✅ GPU Detected!")
    print(f"   Device: {device_name}")
    print(f"   VRAM: {vram_total:.2f} GB\n")
    
    if vram_total < 12:
        print("⚠️  WARNING: Low VRAM detected")
        print("   Consider using smaller model or reducing batch size")
    
    return True

def format_instruction_gemma(sample):
    """Format instruction-response pair for Gemma chat template"""
    instruction = sample['instruction']
    output = sample['output']
    
    # Gemma chat template format
    return f"""<start_of_turn>user
{instruction}<end_of_turn>
<start_of_turn>model
{output}<end_of_turn>"""

def load_training_data():
    """Load and prepare training dataset"""
    print(f"📂 Loading dataset from: {DATASET_PATH}")
    
    # Load dataset
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
    
    print(f"✅ Loaded {len(dataset)} training examples")
    
    # Show sample
    print("\n📋 Sample training example:")
    print("─" * 60)
    sample = dataset[0]
    print(f"Instruction: {sample['instruction']}")
    print(f"Output: {sample['output'][:200]}...")
    print("─" * 60 + "\n")
    
    return dataset

def setup_model_and_tokenizer():
    """Load model with QLoRA quantization and tokenizer"""
    print("🤖 Loading model with 4-bit quantization...")
    
    # 4-bit quantization config for QLoRA
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,                      # Enable 4-bit loading
        bnb_4bit_use_double_quant=True,        # Double quantization
        bnb_4bit_quant_type="nf4",             # Normal Float 4-bit
        bnb_4bit_compute_dtype=torch.bfloat16  # Compute in bfloat16
    )
    
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"  # Recommended for decoder-only models
    
    print("✅ Model loaded and quantized\n")
    
    # Check memory usage
    memory_allocated = torch.cuda.memory_allocated() / 1024**3
    print(f"💾 GPU Memory Allocated: {memory_allocated:.2f} GB\n")
    
    return model, tokenizer

def setup_lora(model):
    """Apply LoRA adapters to the model"""
    print("🔧 Setting up LoRA adapters...")
    
    lora_config = LoraConfig(
        r=QLORA_CONFIG["r"],
        lora_alpha=QLORA_CONFIG["lora_alpha"],
        target_modules=QLORA_CONFIG["target_modules"],
        lora_dropout=QLORA_CONFIG["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    print("📊 Trainable Parameters:")
    model.print_trainable_parameters()
    print()
    
    return model

def train_model(model, tokenizer, dataset):
    """Train the model with SFTTrainer"""
    print("🚀 Starting training...\n")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=TRAINING_CONFIG["num_train_epochs"],
        per_device_train_batch_size=TRAINING_CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=TRAINING_CONFIG["gradient_accumulation_steps"],
        gradient_checkpointing=True,           # Save memory
        optim="paged_adamw_32bit",             # Memory-efficient optimizer
        learning_rate=TRAINING_CONFIG["learning_rate"],
        lr_scheduler_type=TRAINING_CONFIG["lr_scheduler_type"],
        warmup_ratio=TRAINING_CONFIG["warmup_ratio"],
        logging_steps=TRAINING_CONFIG["logging_steps"],
        logging_dir=os.path.join(OUTPUT_DIR, "logs"),
        save_strategy=TRAINING_CONFIG["save_strategy"],
        save_total_limit=3,                    # Keep only last 3 checkpoints
        fp16=False,
        bf16=True,                             # Use bfloat16 for stability
        max_grad_norm=0.3,                     # Gradient clipping
        max_steps=-1,
        group_by_length=True,                  # Efficiency improvement
        report_to="tensorboard",               # Use TensorBoard for logging
    )
    
    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        args=training_args,
        max_seq_length=TRAINING_CONFIG["max_seq_length"],
        formatting_func=format_instruction_gemma,
        dataset_text_field=None,
    )
    
    # Train
    start_time = datetime.now()
    print(f"⏰ Training started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    trainer.train()
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n✅ Training completed!")
    print(f"⏰ Duration: {duration}")
    print(f"📁 Model saved to: {OUTPUT_DIR}\n")
    
    return trainer

def save_model(trainer, tokenizer):
    """Save the final model and tokenizer"""
    print("💾 Saving final model...")
    
    # Save model
    trainer.save_model(OUTPUT_DIR)
    
    # Save tokenizer
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    # Save training config
    config = {
        "model_name": MODEL_NAME,
        "qlora_config": QLORA_CONFIG,
        "training_config": TRAINING_CONFIG,
        "dataset_size": len(trainer.train_dataset),
        "trained_at": datetime.now().isoformat(),
    }
    
    with open(os.path.join(OUTPUT_DIR, "training_config.json"), "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ All files saved to: {OUTPUT_DIR}")
    print(f"\n📦 Files created:")
    print(f"   - adapter_model.safetensors (LoRA adapters)")
    print(f"   - adapter_config.json (LoRA configuration)")
    print(f"   - tokenizer files")
    print(f"   - training_config.json (training metadata)")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main training pipeline"""
    print("=" * 70)
    print("QLoRA Fine-Tuning: Gemma 3 on Indian Diet Data")
    print("=" * 70 + "\n")
    
    # 1. Check GPU
    if not check_gpu():
        return
    
    # 2. Load dataset
    dataset = load_training_data()
    
    # 3. Load model and tokenizer
    model, tokenizer = setup_model_and_tokenizer()
    
    # 4. Setup LoRA
    model = setup_lora(model)
    
    # 5. Train
    trainer = train_model(model, tokenizer, dataset)
    
    # 6. Save
    save_model(trainer, tokenizer)
    
    print("\n" + "=" * 70)
    print("🎉 Fine-tuning completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Test the model: python inference.py")
    print("2. Compare with base model: python compare_models.py")
    print("3. Deploy in your backend: Update backend/main.py")

if __name__ == "__main__":
    main()
