"""
Inference Script for Fine-Tuned Gemma Model
===========================================

Test the fine-tuned model with Indian diet queries.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import sys

# Configuration
BASE_MODEL_NAME = "google/gemma-2-9b-it"
FINE_TUNED_PATH = "./gemma3_indian_diet_qlora"

# Test queries
TEST_QUERIES = [
    "What are good protein sources for vegetarians in Gujarat?",
    "Suggest a breakfast for diabetes management in Maharashtra",
    "How can I build muscle on a North Indian vegetarian diet?",
    "What should I eat for PCOS in Tamil Nadu?",
    "Give me a fat loss meal plan for Punjab",
    "What are pre-workout foods in Indian cuisine?",
    "Suggest a South Indian diabetic-friendly dinner",
    "How do I make a high-protein vegetarian lunch?",
]

def load_model(use_finetuned=True):
    """Load base model or fine-tuned model"""
    print(f"\n{'='*70}")
    if use_finetuned:
        print("Loading FINE-TUNED model...")
    else:
        print("Loading BASE model...")
    print(f"{'='*70}\n")
    
    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    # Load LoRA adapters if using fine-tuned
    if use_finetuned:
        try:
            model = PeftModel.from_pretrained(model, FINE_TUNED_PATH)
            print("✅ LoRA adapters loaded successfully\n")
        except Exception as e:
            print(f"❌ Error loading adapters: {e}")
            print("Make sure you've trained the model first!")
            sys.exit(1)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        FINE_TUNED_PATH if use_finetuned else BASE_MODEL_NAME
    )
    
    return model, tokenizer

def generate_response(model, tokenizer, query, max_new_tokens=300):
    """Generate response for a query"""
    # Format as Gemma chat template
    prompt = f"""<start_of_turn>user
{query}<end_of_turn>
<start_of_turn>model
"""
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the model's response
    if "<start_of_turn>model" in response:
        response = response.split("<start_of_turn>model")[-1].strip()
    
    return response

def interactive_mode(model, tokenizer):
    """Interactive chat with the model"""
    print("\n" + "="*70)
    print("Interactive Mode - Type your questions (or 'quit' to exit)")
    print("="*70 + "\n")
    
    while True:
        query = input("\n💬 You: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        print("\n🤖 Model: ", end="", flush=True)
        response = generate_response(model, tokenizer, query)
        print(response)

def test_mode(model, tokenizer):
    """Test model with predefined queries"""
    print("\n" + "="*70)
    print("Testing Fine-Tuned Model with Indian Diet Queries")
    print("="*70)
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'─'*70}")
        print(f"Query {i}/{len(TEST_QUERIES)}: {query}")
        print(f"{'─'*70}")
        
        response = generate_response(model, tokenizer, query)
        print(f"\n{response}\n")

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test fine-tuned Gemma model")
    parser.add_argument(
        "--mode",
        choices=["test", "interactive"],
        default="test",
        help="test: Run predefined queries, interactive: Chat mode"
    )
    parser.add_argument(
        "--base",
        action="store_true",
        help="Use base model instead of fine-tuned (for comparison)"
    )
    
    args = parser.parse_args()
    
    # Check GPU
    if not torch.cuda.is_available():
        print("❌ ERROR: No GPU detected!")
        print("This script requires a GPU to run the model.")
        sys.exit(1)
    
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    
    # Load model
    use_finetuned = not args.base
    model, tokenizer = load_model(use_finetuned)
    
    # Run selected mode
    if args.mode == "test":
        test_mode(model, tokenizer)
    else:
        interactive_mode(model, tokenizer)

if __name__ == "__main__":
    main()
