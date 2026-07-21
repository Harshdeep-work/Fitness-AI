# Fitness AI Frontend - Comprehensive Version

## 🎯 Features

### Extensive Input Collection
- **Basic Information**: Name, Age, Gender, Height, Weight, Target Weight
- **Location & Lifestyle**: Region, Activity Level, Occupation
- **Fitness Goals**: Primary Goal, Timeline, Workout Days
- **Diet Preferences**: Diet Type, Meals/Day, Allergies, Dislikes
- **Health Conditions**: Medical Conditions, Medications, Supplements
- **Additional Details**: Sleep, Water Intake, Stress Level, Notes

### Intelligent Calculations
- ✅ BMI (Body Mass Index)
- ✅ BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
- ✅ TDEE (Total Daily Energy Expenditure)
- ✅ Target Calories based on goal
- ✅ Recommended Daily Steps

### Professional Display
- User Profile Summary Card
- Detailed AI Recommendations
- Steps Recommendation Display
- Region-specific meal plans
- Medical condition-aware advice

---

## 🚀 How to Use

### Step 1: Start the Backend

```bash
cd /home/hello/Fitness-AI/backend
source venv/bin/activate
python main.py
```

Backend will run on: `http://127.0.0.1:8000`

### Step 2: Open the Frontend

Option A - Direct File (Simple):
```bash
cd /home/hello/Fitness-AI/frontend
google-chrome index.html  # or firefox index.html
```

Option B - HTTP Server (Recommended):
```bash
cd /home/hello/Fitness-AI/frontend
python3 -m http.server 8080
```
Then open: `http://localhost:8080`

### Step 3: Fill the Form

1. Enter all required fields (marked with *)
2. Provide as much detail as possible for accurate recommendations
3. Click "Generate Personalized Plan"
4. Wait 30-90 seconds for AI to analyze and generate

### Step 4: View Results

You'll see:
- Your profile summary with BMI, BMR, TDEE
- Comprehensive nutrition and fitness plan
- Daily steps recommendation
- Region-specific meal suggestions

---

## 📋 Form Fields Explained

### Basic Information
- **Name**: Your full name
- **Age**: Used for BMR calculation
- **Gender**: Affects BMR formula
- **Height**: In centimeters (e.g., 170 cm = 5'7")
- **Weight**: Current weight in kg
- **Target Weight**: Optional goal weight

### Location & Lifestyle
- **Region**: Your Indian state (affects meal recommendations)
- **Activity Level**: How active you are daily
- **Occupation**: Affects daily calorie needs

### Fitness Goals
- **Primary Goal**: Weight loss, muscle gain, etc.
- **Timeline**: How fast you want results
- **Workout Days**: Current workout frequency

### Diet Preferences
- **Diet Type**: Vegetarian, Vegan, Non-veg, etc.
- **Meals per Day**: 2-6 meals
- **Food Allergies**: Lactose, gluten, nuts, etc.
- **Dislikes**: Foods you don't eat

### Health Conditions
- **Medical Conditions**: Diabetes, PCOS, Thyroid, etc.
- **Medications**: Current prescriptions
- **Supplements**: Whey, vitamins, etc.

### Additional Details
- **Sleep Hours**: Affects recovery and metabolism
- **Water Intake**: Current hydration level
- **Stress Level**: Impacts cortisol and weight
- **Notes**: Any other information

---

## 🧮 Calculations

### BMI (Body Mass Index)
```
BMI = weight (kg) / (height (m))²
```
Categories:
- < 18.5: Underweight
- 18.5-24.9: Normal
- 25-29.9: Overweight
- ≥ 30: Obese

### BMR (Basal Metabolic Rate)
Using Mifflin-St Jeor Equation:

**For Men:**
```
BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age) + 5
```

**For Women:**
```
BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age) - 161
```

### TDEE (Total Daily Energy Expenditure)
```
TDEE = BMR × Activity Multiplier
```

Activity Multipliers:
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extremely Active: 1.9

### Target Calories
- **Weight Loss**: TDEE - 500 kcal
- **Muscle Gain**: TDEE + 300 kcal
- **Maintenance**: TDEE

### Recommended Steps
Base Steps by Activity Level + Goal Adjustment:
- Sedentary: 5,000 steps
- Lightly Active: 7,500 steps
- Moderately Active: 10,000 steps
- Very Active: 12,500 steps
- Extremely Active: 15,000 steps

Plus:
- Weight Loss: +2,000 steps
- Muscle Gain: -1,000 steps

---

## 🎨 Design Features

### Responsive Design
- Desktop: Two-column layout
- Tablet: Single column
- Mobile: Optimized forms

### Visual Elements
- Professional gradient headers
- Card-based design
- Smooth animations
- Loading states
- Progress indicators

### User Experience
- Clear labels and placeholders
- Required field indicators
- Form validation
- Error handling
- Scroll to results

---

## 🔧 Technical Details

### Technologies
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid & Flexbox
- **JavaScript (Vanilla)**: No frameworks, pure JS
- **Marked.js**: Markdown to HTML conversion

### API Integration
- **Endpoint**: `POST http://127.0.0.1:8000/api/rag_generate`
- **Payload**: Comprehensive prompt with all user data
- **Response**: Markdown-formatted recommendations

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 📱 Screenshots

### Input Form
- Organized into 6 sections
- Clear visual hierarchy
- Professional styling

### Output Display
- User summary card with key metrics
- Full AI recommendations
- Steps display card

---

## 🐛 Troubleshooting

### "Connection Error"
**Problem**: Cannot connect to backend
**Solution**: 
1. Ensure backend is running: `python backend/main.py`
2. Check URL: `http://127.0.0.1:8000`
3. Check CORS settings in backend

### Form Won't Submit
**Problem**: Submit button disabled
**Solution**: Fill all required fields (marked with *)

### Recommendations Look Wrong
**Problem**: Formatting issues
**Solution**: 
1. Ensure `marked.js` is loaded
2. Check browser console for errors
3. Clear browser cache

### Steps Not Showing
**Problem**: Steps display is blank
**Solution**: Check that activity level and goal are selected

---

## 🚀 Future Enhancements

### Planned Features
- [ ] Save user profiles (localStorage)
- [ ] Download plan as PDF
- [ ] Share plan via link
- [ ] Progress tracking dashboard
- [ ] Multiple language support
- [ ] Meal prep grocery list
- [ ] Recipe suggestions with images
- [ ] Calorie calculator built-in
- [ ] Exercise video recommendations

---

## 📞 Support

### Getting Help
1. Check troubleshooting section
2. Review browser console for errors
3. Verify backend is running correctly
4. Check that Ollama model is available

### Files Structure
```
frontend/
├── index.html      # Main HTML with comprehensive form
├── style.css       # Modern, responsive styling
├── app.js          # Form handling and calculations
└── README.md       # This file
```

---

## ✅ Testing Checklist

Before using with real users:

- [ ] Backend running and responding
- [ ] All form fields working
- [ ] BMI calculation correct
- [ ] BMR calculation correct
- [ ] TDEE calculation correct
- [ ] Steps recommendation showing
- [ ] Recommendations displaying
- [ ] Responsive on mobile
- [ ] Error handling working
- [ ] Loading states showing

---

**Version**: 2.0  
**Last Updated**: July 14, 2026  
**Status**: Production Ready ✅
