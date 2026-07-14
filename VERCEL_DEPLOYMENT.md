# Vercel Deployment Guide

## 🚀 Deploy Fitness-AI to Vercel

### Prerequisites
- GitHub account with repository: https://github.com/Harshdeep-work/Fitness-AI
- Vercel account (free): https://vercel.com/signup

---

## Method 1: Deploy via Vercel Dashboard (Easiest)

### Step 1: Sign Up / Login to Vercel
1. Go to https://vercel.com
2. Click "Sign Up" and choose "Continue with GitHub"
3. Authorize Vercel to access your GitHub account

### Step 2: Import Project
1. Click "Add New" → "Project"
2. Find and select your repository: `Harshdeep-work/Fitness-AI`
3. Click "Import"

### Step 3: Configure Project
**Framework Preset:** Other  
**Root Directory:** `./` (leave as default)  
**Build Command:** (leave empty)  
**Output Directory:** `frontend`  

### Step 4: Deploy
1. Click "Deploy"
2. Wait 1-2 minutes for deployment
3. Your app will be live at: `https://fitness-ai-xxx.vercel.app`

---

## Method 2: Deploy via Vercel CLI

### Install Vercel CLI
```bash
npm install -g vercel
```

### Login to Vercel
```bash
vercel login
```

### Deploy
```bash
cd /home/hello/Fitness-AI
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- What's your project's name? **Fitness-AI**
- In which directory is your code located? **./frontend**

---

## ⚠️ Important: Backend Limitations

Vercel's free tier has limitations for the AI backend:

### Current Setup
The deployed version will show a placeholder response because:
- Ollama requires a persistent server (not serverless)
- ChromaDB requires file system access
- Free tier has execution time limits (10 seconds)

### Solutions for Full Functionality

#### Option 1: Use External AI API
Deploy Ollama on a separate service:
- **Railway** (recommended): https://railway.app
- **Fly.io**: https://fly.io
- **Render**: https://render.com

Then update `api/generate.py` with the external API URL.

#### Option 2: Use Hugging Face Inference API
Replace Ollama with Hugging Face:
```python
import requests

HF_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
response = requests.post(
    "https://api-inference.huggingface.co/models/google/gemma-2b",
    headers={"Authorization": f"Bearer {HF_API_KEY}"},
    json={"inputs": prompt}
)
```

Add environment variable in Vercel:
- Go to Project Settings → Environment Variables
- Add `HUGGINGFACE_API_KEY` with your API key

#### Option 3: Hybrid Deployment
- **Frontend**: Vercel (static files)
- **Backend**: Railway/Render/Fly.io (FastAPI + Ollama + RAG)

Update `frontend/app.js` API URL to point to your backend URL.

---

## 🔧 Environment Variables (Optional)

If using external services, add these in Vercel Project Settings:

```
OLLAMA_API_URL=https://your-ollama-server.com
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
```

---

## 📝 Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

---

## 🐛 Troubleshooting

### Issue: API returns placeholder response
**Solution:** Configure external AI service (see Options above)

### Issue: 404 errors
**Solution:** Check `vercel.json` routes configuration

### Issue: CORS errors
**Solution:** Ensure API functions include CORS headers (already added)

---

## 🎯 Recommended Architecture

For production deployment:

```
┌─────────────────┐
│  Vercel         │
│  (Frontend)     │ ← User visits
└────────┬────────┘
         │
         ↓ API Calls
┌─────────────────┐
│  Railway/Render │
│  (Backend)      │ ← FastAPI + Ollama + RAG
│  - FastAPI      │
│  - Ollama       │
│  - ChromaDB     │
└─────────────────┘
```

---

## 📊 Deployment Status

Once deployed, your app will be available at:
- **Production URL**: `https://fitness-ai.vercel.app`
- **Preview URLs**: Generated for each git push

---

## 🔄 Auto-Deployment

Vercel automatically deploys when you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Vercel will detect the push and deploy automatically!

---

## 📚 Next Steps

1. Deploy to Vercel using Method 1
2. Test the frontend (will show placeholder)
3. Set up external backend (Railway recommended)
4. Update API endpoint in frontend
5. Redeploy and test full functionality

---

**Need help?** Check Vercel docs: https://vercel.com/docs
