document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fitnessForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('spinner');
    
    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    const userSummary = document.getElementById('userSummary');
    const recommendationContent = document.getElementById('recommendationContent');
    const stepsDisplay = document.getElementById('stepsDisplay');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Collect all form data
        const formData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            height: parseInt(document.getElementById('height').value),
            weight: parseFloat(document.getElementById('weight').value),
            targetWeight: document.getElementById('targetWeight').value || null,
            region: document.getElementById('region').value,
            activityLevel: document.getElementById('activityLevel').value,
            occupation: document.getElementById('occupation').value,
            primaryGoal: document.getElementById('primaryGoal').value,
            timeline: document.getElementById('timeline').value,
            workoutDays: document.getElementById('workoutDays').value,
            dietType: document.getElementById('dietType').value,
            mealsPerDay: document.getElementById('mealsPerDay').value,
            foodAllergies: document.getElementById('foodAllergies').value || 'None',
            dislikedFoods: document.getElementById('dislikedFoods').value || 'None',
            medicalConditions: getSelectedOptions('medicalConditions'),
            medications: document.getElementById('medications').value || 'None',
            supplements: document.getElementById('supplements').value || 'None',
            sleepHours: document.getElementById('sleepHours').value,
            waterIntake: parseFloat(document.getElementById('waterIntake').value),
            stressLevel: document.getElementById('stressLevel').value,
            additionalNotes: document.getElementById('additionalNotes').value || 'None'
        };

        // Calculate BMI and other metrics
        const heightInMeters = formData.height / 100;
        const bmi = (formData.weight / (heightInMeters * heightInMeters)).toFixed(1);
        const bmr = calculateBMR(formData.weight, formData.height, formData.age, formData.gender);
        const tdee = calculateTDEE(bmr, formData.activityLevel);
        const recommendedSteps = calculateSteps(formData.activityLevel, formData.primaryGoal);

        // Construct comprehensive prompt
        const prompt = constructPrompt(formData, bmi, bmr, tdee);

        // Update UI
        submitBtn.disabled = true;
        btnText.textContent = 'Analyzing...';
        spinner.classList.remove('hidden');
        
        emptyState.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        loadingState.classList.remove('hidden');

        try {
            // Call Backend API
            const response = await fetch('/api/rag_generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model: "gemma3:4b"
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                // Display user summary
                displayUserSummary(formData, bmi, bmr, tdee);
                
                // Display recommendation
                recommendationContent.innerHTML = marked.parse(data.response);
                
                // Display steps recommendation
                displaySteps(recommendedSteps);
                
                // Show results
                loadingState.classList.add('hidden');
                resultsContainer.classList.remove('hidden');
            } else {
                throw new Error(data.message || 'Failed to generate recommendation');
            }
            
        } catch (error) {
            console.error('Error:', error);
            recommendationContent.innerHTML = `
                <div style="color: #ef4444; padding: 2rem; text-align: center;">
                    <h3>❌ Connection Error</h3>
                    <p>${error.message}</p>
                    <p style="margin-top: 1rem; font-size: 0.875rem; color: #64748b;">
                        Make sure the FastAPI backend is running on http://127.0.0.1:8000
                    </p>
                </div>
            `;
            loadingState.classList.add('hidden');
            resultsContainer.classList.remove('hidden');
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Generate Personalized Plan';
            spinner.classList.add('hidden');
        }
    });

    function getSelectedOptions(selectId) {
        const select = document.getElementById(selectId);
        const selected = Array.from(select.selectedOptions).map(opt => opt.value);
        return selected.length > 0 ? selected.join(', ') : 'None';
    }

    function calculateBMR(weight, height, age, gender) {
        // Mifflin-St Jeor Equation
        if (gender === 'Male') {
            return Math.round((10 * weight) + (6.25 * height) - (5 * age) + 5);
        } else {
            return Math.round((10 * weight) + (6.25 * height) - (5 * age) - 161);
        }
    }

    function calculateTDEE(bmr, activityLevel) {
        const multipliers = {
            'Sedentary': 1.2,
            'Lightly Active': 1.375,
            'Moderately Active': 1.55,
            'Very Active': 1.725,
            'Extremely Active': 1.9
        };
        return Math.round(bmr * (multipliers[activityLevel] || 1.2));
    }

    function calculateSteps(activityLevel, primaryGoal) {
        const baseSteps = {
            'Sedentary': 5000,
            'Lightly Active': 7500,
            'Moderately Active': 10000,
            'Very Active': 12500,
            'Extremely Active': 15000
        };
        
        let steps = baseSteps[activityLevel] || 8000;
        
        // Adjust for goal
        if (primaryGoal === 'Weight Loss') {
            steps += 2000;
        } else if (primaryGoal === 'Muscle Gain') {
            steps -= 1000;
        }
        
        return Math.max(5000, steps);
    }

    function constructPrompt(data, bmi, bmr, tdee) {
        return `
# Comprehensive Fitness and Nutrition Analysis

**CLIENT PROFILE:**
- Name: ${data.name}
- Age: ${data.age} years | Gender: ${data.gender}
- Height: ${data.height} cm | Weight: ${data.weight} kg
- BMI: ${bmi} | BMR: ${bmr} kcal/day | TDEE: ${tdee} kcal/day
- Target Weight: ${data.targetWeight || 'Not specified'}
- Location: ${data.region}, India

**LIFESTYLE:**
- Activity Level: ${data.activityLevel}
- Occupation: ${data.occupation}
- Workout Days: ${data.workoutDays} per week
- Sleep: ${data.sleepHours} per night
- Water Intake: ${data.waterIntake} liters/day
- Stress Level: ${data.stressLevel}

**FITNESS GOALS:**
- Primary Goal: ${data.primaryGoal}
- Timeline: ${data.timeline}

**DIETARY PREFERENCES:**
- Diet Type: ${data.dietType}
- Meals per Day: ${data.mealsPerDay}
- Food Allergies: ${data.foodAllergies}
- Dislikes: ${data.dislikedFoods}

**HEALTH CONDITIONS:**
- Medical Conditions: ${data.medicalConditions}
- Current Medications: ${data.medications}
- Supplements: ${data.supplements}

**ADDITIONAL NOTES:**
${data.additionalNotes}

---

**TASK:**
As an expert Indian nutrition and fitness AI, provide a comprehensive, personalized plan including:

1. **Health Assessment**: Analyze BMI, current fitness level, and health status
2. **Calorie & Macro Targets**: Based on goal (weight loss/gain/maintenance)
3. **Detailed Meal Plan**: 
   - ${data.mealsPerDay} meals per day
   - Region-specific foods from ${data.region}
   - ${data.dietType} options only
   - Consider food allergies and dislikes
4. **Sample Meal Schedule**: Specific Indian recipes with portion sizes
5. **Workout Recommendations**: Based on ${data.workoutDays} workout days
6. **Lifestyle Adjustments**: Sleep, stress, hydration tips
7. **Medical Considerations**: Address ${data.medicalConditions} if applicable
8. **Progress Tracking**: What to monitor weekly

**IMPORTANT:**
- Use authentic ${data.region} cuisine and ingredients
- Provide practical, actionable advice
- Include specific portion sizes and macro breakdowns
- Consider medical conditions: ${data.medicalConditions}
- Use local terminology for foods

Generate a complete, professional nutrition and fitness plan now.`;
    }

    function displayUserSummary(data, bmi, bmr, tdee) {
        let bmiCategory = 'Normal';
        if (bmi < 18.5) bmiCategory = 'Underweight';
        else if (bmi >= 25 && bmi < 30) bmiCategory = 'Overweight';
        else if (bmi >= 30) bmiCategory = 'Obese';

        const targetCalories = calculateTargetCalories(tdee, data.primaryGoal);

        userSummary.innerHTML = `
            <h3>👤 ${data.name}'s Profile Summary</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <label>BMI</label>
                    <div class="value">${bmi} <span style="font-size: 0.875rem;">(${bmiCategory})</span></div>
                </div>
                <div class="summary-item">
                    <label>BMR</label>
                    <div class="value">${bmr} <span style="font-size: 0.875rem;">kcal/day</span></div>
                </div>
                <div class="summary-item">
                    <label>TDEE</label>
                    <div class="value">${tdee} <span style="font-size: 0.875rem;">kcal/day</span></div>
                </div>
                <div class="summary-item">
                    <label>Goal</label>
                    <div class="value" style="font-size: 0.875rem;">${data.primaryGoal}</div>
                </div>
                <div class="summary-item">
                    <label>Target Calories</label>
                    <div class="value">${targetCalories} <span style="font-size: 0.875rem;">kcal</span></div>
                </div>
                <div class="summary-item">
                    <label>Region</label>
                    <div class="value" style="font-size: 0.875rem;">${data.region}</div>
                </div>
            </div>
        `;
    }

    function calculateTargetCalories(tdee, goal) {
        if (goal === 'Weight Loss') {
            return tdee - 500;
        } else if (goal === 'Muscle Gain') {
            return tdee + 300;
        } else {
            return tdee;
        }
    }

    function displaySteps(steps) {
        stepsDisplay.innerHTML = `
            <h3>🚶‍♂️ Daily Activity Target</h3>
            <div class="steps-value">${steps.toLocaleString()}</div>
            <div class="steps-label">Recommended Steps per Day</div>
        `;
    }
});
