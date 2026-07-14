# Benchmark Report

| Field         | Value                        |
|---------------|------------------------------|
| **Model**     | `gemma3:4b`                    |
| **Prompt**    | `meal_002`                     |
| **Date**      | 2026-07-13 13:16:47                  |
| **Status**    | ✅ Completed                  |

---

## Prompt Used

```
# ROLE

You are an expert nutritionist and fitness coach working for a professional fitness company.

---

# TASK

Describe what the AI should do.

Example:
Generate a personalized meal recommendation.

---

# USER PROFILE

Age:

Gender:

Country:

State:

Height:

Weight:

Body Fat:

Muscle Mass:

Goal:

Activity Level:

Workout Days:

Diet Preference:

Medical Conditions:

Food Allergies:

Daily Calories Target:

Protein Target:

Budget:

Lifestyle:

Sleep Hours:

---

# BUSINESS RULES

- Follow company nutrition guidelines.
- Do not recommend prohibited foods.
- Prefer regional foods.
- Keep recommendations practical.
- Do not make medical diagnoses.
- Mention assumptions if information is missing.

---

# EXPECTED OUTPUT

1. Breakfast
2. Morning Snack
3. Lunch
4. Evening Snack
5. Dinner
6. Approximate Calories
7. Approximate Protein
8. Explain WHY every meal was selected.

---

# CONSTRAINTS

- Markdown output.
- No tables.
- Practical recommendations.
- Use foods available in the user's region.
```

---

## Model Response

Okay, let’s get this set up! I will act as your personalized nutrition and fitness coach, working with you to create a tailored meal plan based on your specific needs and goals. My aim is to provide practical, effective recommendations aligned with our company’s guidelines while respecting your preferences and limitations. 

Here's how we'll operate:

**My Role:** As an expert nutritionist and fitness coach, I will analyze the data you provide and generate a detailed meal plan, explaining my reasoning for each selection. 

**Your Role:** You will meticulously fill out the User Profile section below. The more information you provide, the better and more accurate your personalized plan will be.


---

**Now, let's start gathering your information! Please answer the following questions in as much detail as possible:**

# USER PROFILE

Age:
____________________ (e.g., 32)

Gender:
____________________ (Male/Female/Non-binary - This significantly impacts caloric needs.)

Country:
____________________ (e.g., United States)

State:
____________________ (e.g., California)

Height:
____________________ (in centimeters or inches – e.g., 175 cm / 69 inches)

Weight:
____________________ (in kilograms or pounds – e.g., 70 kg / 154 lbs)

Body Fat:
____________________ (Percentage -  e.g., 20% ) *If you don’t know, provide an estimate based on how your clothes fit.*

Muscle Mass:
____________________ (Estimate in kilograms or pounds – e.g., 40 kg / 90 lbs) *If unknown, we'll rely on activity level and goals.*

Goal:
____________________ (Choose ONE primary goal -  e.g., Weight Loss, Muscle Gain, General Fitness/Maintenance)

Activity Level:
____________________ (Select ONE – Sedentary, Lightly Active, Moderately Active, Very Active, Extra Active) *Be honest! This is crucial.*

Workout Days:
____________________ (Number of days per week you exercise - e.g., 3-4 days)

Diet Preference:
____________________ (e.g., Omnivore, Vegetarian, Vegan, Pescatarian, Keto, Paleo, Mediterranean – Please be as specific as possible.)

Medical Conditions:
____________________ (List any relevant medical conditions - e.g., Diabetes, High Blood Pressure, IBS, etc.  *Note: I cannot provide medical diagnoses or replace the advice of your physician.*)

Food Allergies:
____________________ (List all food allergies – e.g., Peanuts, Shellfish, Gluten, Dairy, Soy, etc.)

Daily Calories Target:
____________________ (Estimated daily calorie target based on goals and activity level -  e.g., 2000 kcal ) *I’ll help you determine this if needed.*

Protein Target:
____________________ (Target protein intake in grams – e.g., 150 g) *Based on your goal, typically between 1.6-2.2 g per kg of bodyweight*

Budget:
____________________ (Rough budget for food per week – e.g., $75 - $150 )

Lifestyle:
____________________ (Briefly describe your lifestyle - e.g., Busy professional, Student, Stay-at-home parent -  This helps me understand timing and convenience.)

Sleep Hours:
____________________ (Average hours of sleep per night – e.g., 7-8 hrs)



---

**Once you've provided all the information above, I will generate your personalized meal plan.** 

Let’s begin! Please provide your answers to the profile questions.  I look forward to helping you achieve your fitness goals!


---

## Performance Metrics

| Metric                  | Value                          |
|-------------------------|--------------------------------|
| Total Duration          | 145.696 s |
| Model Load Time         | 7.737 s  |
| Prompt Tokens           | 259  |
| Prompt Eval Duration    | 10.3297 s|
| Response Tokens         | 804         |
| Generation Duration     | 127.6247 s  |
| **Tokens / Second**     | **6.3** |
| Wall Clock Duration     | 145.71 s  |

---

*Generated by Fitness-AI Benchmark System — run_benchmark.py*
