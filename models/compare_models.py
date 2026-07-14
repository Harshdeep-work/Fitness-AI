"""
Compare Base vs Fine-Tuned Model
=================================

Side-by-side comparison of responses from base and fine-tuned models.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import json
from datetime import datetime

# Configuration
BASE_MODEL_NAME = "google/gemma-2-9b-it"
FINE_TUNED_PATH = "./gemma3_indian_diet_qlora"
OUTPUT_FILE = "model_comparison_results.json"

# Comparison test cases
TEST_CASES = [
    {
        "category": "Regional Protein Sources",
        "query": "What are good protein sources for vegetarians in Gujarat?",
        "expected_keywords": ["besan", "chana", "chickpea", "dal", "protein"]
    },
    {
        "category": "Diabetes Management",
        "query": "Suggest a breakfast for diabetes management in Maharashtra",
        "expected_keywords": ["jowar", "low glycemic", "bhakri", "diabetes", "fiber"]
    },
    {
        "category": "Muscle Building",
        "query": "How can I build muscle on a North Indian vegetarian diet?",
        "expected_keywords": ["paneer", "dal", "protein", "rajma", "muscle", "macros"]
    },
    {
        "category": "PCOS Management",
        "query": "What should I eat for PCOS in Tamil Nadu?",
        "expected_keywords": ["low gi", "fiber", "south indian", "millet"]
    },
    {
        "category": "Fat Loss",
        "query": "Give me a fat loss meal plan for Punjab",
        "expected_keywords": ["calorie deficit", "protein", "vegetables", "dal"]
    },
    {
        "category": "Pre-Workout Nutrition",
        "query": "What are good pre-workout foods in Indian cuisine?",
        "expected_keywords": ["banana", "poha", "carb", "energy", "pre-workout"]
    },
    {
        "category": "Recipe Knowledge",
        "query": "How do I make a high-protein South Indian breakfast?",
        "expected_keywords": ["idli", "dosa", "sambar", "protein", "pesarattu"]
    },
    {
        "category": "Specific Condition",
        "query": "What foods should a hypertensive patient avoid?",
        "expected_keywords": ["sodium", "salt", "blood pressure", "potassium"]
    },
]

def load_models():
    """Load both base and fine-tuned models"""
    print("Loading models...")
    print("This may take a few minutes...\n")
    
    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # Load base model
    print("1️⃣ Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    base_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    print("✅ Base model loaded\n")
    
    # Load fine-tuned model
    print("2️⃣ Loading fine-tuned model...")
    finetuned_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    finetuned_model = PeftModel.from_pretrained(finetuned_model, FINE_TUNED_PATH)
    finetuned_tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_PATH)
    print("✅ Fine-tuned model loaded\n")
    
    return (base_model, base_tokenizer), (finetuned_model, finetuned_tokenizer)

def generate_response(model, tokenizer, query, max_new_tokens=250):
    """Generate response from a model"""
    prompt = f"""<start_of_turn>user
{query}<end_of_turn>
<start_of_turn>model
"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    import time
    start_time = time.time()
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    duration = time.time() - start_time
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract model response
    if "<start_of_turn>model" in response:
        response = response.split("<start_of_turn>model")[-1].strip()
    
    return response, duration

def check_keywords(response, keywords):
    """Check how many expected keywords are in the response"""
    response_lower = response.lower()
    found = [kw for kw in keywords if kw.lower() in response_lower]
    return found, len(found) / len(keywords) if keywords else 0

def compare_models(base_info, finetuned_info):
    """Run comparison on all test cases"""
    base_model, base_tokenizer = base_info
    finetuned_model, finetuned_tokenizer = finetuned_info
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "model_name": BASE_MODEL_NAME,
        "finetuned_path": FINE_TUNED_PATH,
        "test_cases": []
    }
    
    print("=" * 100)
    print("COMPARISON: Base Model vs Fine-Tuned Model")
    print("=" * 100 + "\n")
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'─' * 100}")
        print(f"Test {i}/{len(TEST_CASES)}: {test_case['category']}")
        print(f"Query: {test_case['query']}")
        print(f"{'─' * 100}\n")
        
        # Get base model response
        print("🔵 BASE MODEL:")
        base_response, base_time = generate_response(
            base_model, base_tokenizer, test_case['query']
        )
        print(base_response)
        print(f"\n⏱️  Time: {base_time:.2f}s")
        
        base_keywords, base_score = check_keywords(
            base_response, test_case['expected_keywords']
        )
        print(f"📊 Keyword Match: {len(base_keywords)}/{len(test_case['expected_keywords'])} ({base_score*100:.0f}%)")
        
        print("\n" + "─" * 100 + "\n")
        
        # Get fine-tuned model response
        print("🟢 FINE-TUNED MODEL:")
        ft_response, ft_time = generate_response(
            finetuned_model, finetuned_tokenizer, test_case['query']
        )
        print(ft_response)
        print(f"\n⏱️  Time: {ft_time:.2f}s")
        
        ft_keywords, ft_score = check_keywords(
            ft_response, test_case['expected_keywords']
        )
        print(f"📊 Keyword Match: {len(ft_keywords)}/{len(test_case['expected_keywords'])} ({ft_score*100:.0f}%)")
        
        # Store results
        results["test_cases"].append({
            "category": test_case['category'],
            "query": test_case['query'],
            "base_model": {
                "response": base_response,
                "time_seconds": base_time,
                "keywords_found": base_keywords,
                "keyword_score": base_score
            },
            "finetuned_model": {
                "response": ft_response,
                "time_seconds": ft_time,
                "keywords_found": ft_keywords,
                "keyword_score": ft_score
            },
            "improvement": {
                "keyword_score_delta": ft_score - base_score,
                "time_delta": ft_time - base_time
            }
        })
        
        # Show improvement
        print("\n" + "─" * 100)
        score_diff = (ft_score - base_score) * 100
        if score_diff > 0:
            print(f"✅ IMPROVEMENT: +{score_diff:.0f}% keyword relevance")
        elif score_diff < 0:
            print(f"⚠️  REGRESSION: {score_diff:.0f}% keyword relevance")
        else:
            print(f"➡️  NO CHANGE in keyword relevance")
        print("─" * 100)
    
    return results

def generate_summary(results):
    """Generate summary statistics"""
    print("\n\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100 + "\n")
    
    base_scores = [tc['base_model']['keyword_score'] for tc in results['test_cases']]
    ft_scores = [tc['finetuned_model']['keyword_score'] for tc in results['test_cases']]
    
    avg_base = sum(base_scores) / len(base_scores) * 100
    avg_ft = sum(ft_scores) / len(ft_scores) * 100
    improvement = avg_ft - avg_base
    
    base_times = [tc['base_model']['time_seconds'] for tc in results['test_cases']]
    ft_times = [tc['finetuned_model']['time_seconds'] for tc in results['test_cases']]
    
    avg_base_time = sum(base_times) / len(base_times)
    avg_ft_time = sum(ft_times) / len(ft_times)
    
    print(f"📊 Keyword Relevance Score:")
    print(f"   Base Model:       {avg_base:.1f}%")
    print(f"   Fine-Tuned Model: {avg_ft:.1f}%")
    print(f"   Improvement:      {'+' if improvement > 0 else ''}{improvement:.1f}%\n")
    
    print(f"⏱️  Average Response Time:")
    print(f"   Base Model:       {avg_base_time:.2f}s")
    print(f"   Fine-Tuned Model: {avg_ft_time:.2f}s\n")
    
    # Count wins
    wins = sum(1 for tc in results['test_cases'] 
               if tc['finetuned_model']['keyword_score'] > tc['base_model']['keyword_score'])
    ties = sum(1 for tc in results['test_cases'] 
               if tc['finetuned_model']['keyword_score'] == tc['base_model']['keyword_score'])
    losses = len(results['test_cases']) - wins - ties
    
    print(f"🏆 Head-to-Head:")
    print(f"   Fine-Tuned Wins:  {wins}/{len(results['test_cases'])}")
    print(f"   Ties:             {ties}/{len(results['test_cases'])}")
    print(f"   Base Model Wins:  {losses}/{len(results['test_cases'])}\n")
    
    # Overall verdict
    print("=" * 100)
    if improvement > 10:
        print("✅ VERDICT: Fine-tuning shows SIGNIFICANT improvement")
    elif improvement > 0:
        print("✅ VERDICT: Fine-tuning shows improvement")
    elif improvement > -5:
        print("⚠️  VERDICT: Fine-tuning shows minimal change")
    else:
        print("❌ VERDICT: Fine-tuning needs adjustment")
    print("=" * 100 + "\n")

def main():
    """Main execution"""
    # Check GPU
    if not torch.cuda.is_available():
        print("❌ ERROR: No GPU detected!")
        return
    
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}\n")
    
    # Load models
    base_info, finetuned_info = load_models()
    
    # Run comparison
    results = compare_models(base_info, finetuned_info)
    
    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {OUTPUT_FILE}")
    
    # Generate summary
    generate_summary(results)

if __name__ == "__main__":
    main()
