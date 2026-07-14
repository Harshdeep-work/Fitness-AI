"""
Generate fine-tuning dataset for QLoRA training on Indian diet data
Converts existing recipes and nutrition guidelines into instruction-response format
"""

import json
import pandas as pd
import random
from pathlib import Path

# Load existing data
nutrition_guidelines = json.load(open('indian_nutrition_guidelines.json'))
recipes_df = pd.read_csv('indian_recipes.csv')

# Sample 500 recipes (adjust based on your needs)
recipes_sample = recipes_df.sample(n=min(500, len(recipes_df)), random_state=42)

training_data = []

# 1. Convert nutrition guidelines to instruction-response pairs
for guideline in nutrition_guidelines:
    topic = guideline['topic']
    region = guideline['region']
    content = guideline['content']
    
    # Generate different question variations
    questions = []
    
    if 'protein' in topic.lower():
        questions = [
            f"What are good protein sources in {region}?",
            f"Suggest protein-rich foods for {region}",
            f"How can I get enough protein in a {region} diet?",
        ]
    elif 'diabetes' in topic.lower():
        questions = [
            f"What should a diabetic person eat in {region}?",
            f"Suggest diabetes-friendly meals for {region}",
            f"How to manage diabetes through diet in {region}?",
        ]
    elif 'pcos' in topic.lower():
        questions = [
            f"What foods are good for PCOS in {region}?",
            f"Suggest a PCOS diet plan for {region}",
            f"How to manage PCOS through diet in {region}?",
        ]
    elif 'muscle gain' in topic.lower():
        questions = [
            f"What should I eat for muscle building in {region}?",
            f"Suggest a muscle gain diet for {region}",
            f"What macros do I need for muscle growth?",
        ]
    elif 'fat loss' in topic.lower():
        questions = [
            f"What should I eat for weight loss in {region}?",
            f"Suggest a fat loss diet for {region}",
            f"What macros do I need for cutting?",
        ]
    elif 'hypertension' in topic.lower():
        questions = [
            f"What foods help control high blood pressure?",
            f"Suggest a diet for hypertension management",
        ]
    elif 'pre-workout' in topic.lower():
        questions = [
            f"What should I eat before a workout?",
            f"Suggest Indian pre-workout meals",
        ]
    elif 'post-workout' in topic.lower():
        questions = [
            f"What should I eat after a workout?",
            f"Suggest Indian post-workout meals",
        ]
    else:
        questions = [f"Tell me about {topic} in {region}"]
    
    # Add to training data
    for question in questions:
        training_data.append({
            "instruction": question,
            "output": content
        })

# 2. Convert recipes to instruction-response pairs
for idx, recipe_row in recipes_sample.iterrows():
    recipe_text = recipe_row['text']
    
    # Parse the recipe text
    try:
        parts = {}
        for field in ['TranslatedIngredients', 'PrepTimeInMins', 'CookTimeInMins', 'Servings', 'Cuisine', 'Course', 'Diet', 'TranslatedInstructions']:
            if f'### {field}:' in recipe_text:
                start_idx = recipe_text.find(f'### {field}:') + len(f'### {field}:')
                end_idx = recipe_text.find('###', start_idx)
                if end_idx == -1:
                    end_idx = len(recipe_text)
                parts[field] = recipe_text[start_idx:end_idx].strip()
        
        ingredients = parts.get('TranslatedIngredients', '')
        instructions = parts.get('TranslatedInstructions', '')
        diet = parts.get('Diet', 'Vegetarian')
        cuisine = parts.get('Cuisine', 'Indian')
        course = parts.get('Course', 'Main Course')
        prep_time = parts.get('PrepTimeInMins', '30')
        cook_time = parts.get('CookTimeInMins', '30')
        
        # Extract recipe name from ingredients (first item before first comma)
        name_match = ingredients.split(',')[0] if ',' in ingredients else cuisine + ' Recipe'
        name = f"{cuisine} {course}"
        
    except:
        continue
    
    # Clean up the data
    if not instructions or len(instructions) < 50:
        continue
    
    # Generate recipe queries
    recipe_questions = [
        f"How do I make {cuisine} {course.lower()}?",
        f"Give me a {diet.lower()} recipe from {cuisine}",
        f"What's a good {course.lower()} recipe?",
        f"Suggest a {diet.lower()} {course.lower()} recipe from {cuisine}",
    ]
    
    # Create structured output
    recipe_output = f"""Here's a {cuisine} {course} recipe:

**Ingredients:**
{ingredients}

**Instructions:**
{instructions}

**Details:**
- Cuisine: {cuisine}
- Course: {course}
- Diet: {diet}
- Prep Time: {prep_time} mins
- Cook Time: {cook_time} mins
"""
    
    for question in recipe_questions:
        training_data.append({
            "instruction": question,
            "output": recipe_output
        })

# 3. Add synthetic diet planning queries
regions = ['Maharashtra', 'Gujarat', 'Punjab', 'Tamil Nadu', 'Karnataka', 'West Bengal', 'Kerala', 'Andhra Pradesh']
goals = ['muscle gain', 'fat loss', 'maintenance', 'diabetes management', 'PCOS management']
meal_times = ['breakfast', 'lunch', 'dinner', 'snack']
dietary_prefs = ['vegetarian', 'non-vegetarian', 'vegan', 'eggetarian']

for _ in range(200):  # Generate 200 synthetic queries
    region = random.choice(regions)
    goal = random.choice(goals)
    meal_time = random.choice(meal_times)
    diet_pref = random.choice(dietary_prefs)
    
    question = f"Suggest a {diet_pref} {meal_time} for {goal} in {region}"
    
    # Create contextual response
    if goal == 'muscle gain':
        macro_advice = "Focus on high protein (1.6-2.2g/kg body weight), moderate carbs for energy, and healthy fats. Aim for 300-500 calorie surplus."
    elif goal == 'fat loss':
        macro_advice = "Prioritize protein (40% of calories) to preserve muscle, moderate carbs (30%), and fats (30%). Maintain 300-500 calorie deficit."
    elif goal == 'diabetes management':
        macro_advice = "Choose low glycemic index foods, limit refined carbs, include fiber-rich foods, and monitor portion sizes."
    elif goal == 'PCOS management':
        macro_advice = "Focus on low GI foods, include anti-inflammatory foods, omega-3 fatty acids, and avoid processed foods."
    else:
        macro_advice = "Maintain balanced macros: 30% protein, 40% carbs, 30% fats for overall health."
    
    output = f"""For {goal} in {region}, here's a {diet_pref} {meal_time} suggestion:

**Nutritional Strategy:**
{macro_advice}

**Regional Considerations:**
Choose local ingredients from {region} cuisine that are fresh and culturally appropriate.

**Sample {meal_time.capitalize()}:**
"""
    
    # Add region-specific food suggestions
    if region == 'Maharashtra':
        output += "- Jowar bhakri with dal and vegetables\n- Poha with peanuts and vegetables\n- Thalipeeth with curd"
    elif region == 'Gujarat':
        output += "- Thepla with curd\n- Dhokla with green chutney\n- Handvo with vegetables"
    elif region == 'Punjab':
        output += "- Paneer bhurji with whole wheat roti\n- Dal with brown rice\n- Chole with roti"
    elif region == 'Tamil Nadu':
        output += "- Idli with sambar\n- Pesarattu with chutney\n- Ragi dosa with vegetables"
    elif region == 'Karnataka':
        output += "- Ragi mudde with sambar\n- Akki roti with vegetables\n- Jolada rotti with palya"
    elif region == 'West Bengal':
        output += "- Macher jhol with rice\n- Cholar dal with luchi\n- Shukto with rice"
    elif region == 'Kerala':
        output += "- Puttu with kadala curry\n- Appam with stew\n- Fish curry with rice"
    else:  # Andhra Pradesh
        output += "- Pesarattu with ginger chutney\n- Ragi sangati with sambar\n- Gongura dal with rice"
    
    training_data.append({
        "instruction": question,
        "output": output
    })

# Shuffle the data
random.shuffle(training_data)

# Save as JSONL for fine-tuning
output_file = 'indian_diet_finetune.jsonl'
with open(output_file, 'w', encoding='utf-8') as f:
    for item in training_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Created fine-tuning dataset with {len(training_data)} examples")
print(f"✅ Saved to: {output_file}")

# Create a small test set
test_data = training_data[:50]
with open('indian_diet_test.jsonl', 'w', encoding='utf-8') as f:
    for item in test_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Created test set with {len(test_data)} examples")

# Print statistics
print(f"\n📊 Dataset Statistics:")
print(f"   Total examples: {len(training_data)}")
print(f"   From nutrition guidelines: {len(nutrition_guidelines) * 3}")
print(f"   From recipes: {len(recipes_sample) * 4}")
print(f"   Synthetic queries: 200")
print(f"   Test set size: {len(test_data)}")
