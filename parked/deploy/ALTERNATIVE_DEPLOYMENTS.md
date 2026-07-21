# Alternative Deployment: Render.com

If Railway continues to have issues, use Render.com as a backup:

## 🚀 Deploy to Render (5 minutes)

### Step 1: Create Account
- Go to https://render.com
- Sign up with GitHub

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect GitHub: `Harshdeep-work/Fitness-AI`
3. Click "Connect"

### Step 3: Configure Service

**Name:** `fitness-ai`

**Environment:** `Python 3`

**Region:** `Oregon (US West)` or closest to you

**Branch:** `main`

**Root Directory:** Leave empty

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Plan:** Free

### Step 4: Environment Variables (Optional)
Add if needed:
- `PYTHON_VERSION` = `3.10.12`

### Step 5: Deploy
Click "Create Web Service" and wait 3-5 minutes.

---

## ✅ What Works on Render

✅ Full FastAPI backend
✅ Frontend served via backend
✅ All API endpoints
✅ Free tier (750 hours/month)
✅ Auto-deploy on git push
✅ Free SSL certificate

⚠️ Ollama won't work (same as Railway - needs external service)

---

## 🔗 After Deployment

Your app will be at: `https://fitness-ai.onrender.com`

---

## 💡 Alternative: Heroku

If both fail, try Heroku:
1. Create `requirements.txt` in root
2. Use Procfile (already created)
3. Deploy via Heroku CLI or dashboard

---

Choose whichever platform works best! All three support FastAPI + Python apps.
