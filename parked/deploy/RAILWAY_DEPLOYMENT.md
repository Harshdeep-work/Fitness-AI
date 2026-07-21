# Railway Deployment Guide

## 🚂 Deploy Full Fitness-AI to Railway

Railway supports full-stack deployment with:
✅ FastAPI backend
✅ Ollama AI model
✅ ChromaDB RAG system
✅ Static frontend
✅ Persistent storage

---

## 📋 Prerequisites

- GitHub repository: https://github.com/Harshdeep-work/Fitness-AI
- Railway account (free $5 credit): https://railway.app

---

## 🚀 Method 1: Deploy via Railway Dashboard (Recommended)

### Step 1: Sign Up / Login
1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose: `Harshdeep-work/Fitness-AI`
4. Click "Deploy Now"

### Step 3: Configure Environment (Important)

Railway will auto-detect Python and deploy, but you need to add Ollama:

**Option A: Without Ollama (Limited Functionality)**
- Deployment will work but AI responses will fail
- Frontend will show error when generating recommendations

**Option B: With Ollama (Full Functionality)** - See Section Below

### Step 4: Access Your App
1. Go to "Settings" tab
2. Find "Domains" section
3. Click "Generate Domain"
4. Your app will be at: `https://fitness-ai-production.up.railway.app`

---

## 🤖 Adding Ollama for Full AI Functionality

Railway doesn't natively support Ollama, so you have 2 options:

### Option 1: Use External Ollama Service

Deploy Ollama separately:
1. **Use Modal.com or Replicate** for Ollama hosting
2. Update `backend/main.py` with external URL:
   ```python
   ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
   ```
3. Add environment variable in Railway:
   - Key: `OLLAMA_URL`
   - Value: Your external Ollama URL

### Option 2: Use Alternative AI API

Replace Ollama with Hugging Face Inference API:

1. Get API key from: https://huggingface.co/settings/tokens

2. Update `backend/main.py`:
```python
import requests
import os

HF_API_KEY = os.environ.get("HF_API_KEY")

def generate_with_hf(prompt):
    response = requests.post(
        "https://api-inference.huggingface.co/models/google/gemma-2b-it",
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": prompt}
    )
    return response.json()
```

3. Add environment variable in Railway:
   - Key: `HF_API_KEY`
   - Value: Your Hugging Face API key

---

## 📦 Method 2: Deploy via Railway CLI

### Install Railway CLI
```bash
npm install -g @railway/cli
```

### Login
```bash
railway login
```

### Deploy
```bash
cd /home/hello/Fitness-AI
railway init
railway up
```

### Generate Domain
```bash
railway domain
```

---

## ⚙️ Environment Variables

Add these in Railway Dashboard → Variables:

### Required (for basic functionality)
```
PORT=8000
PYTHON_VERSION=3.10
```

### Optional (for full AI)
```
OLLAMA_URL=https://your-ollama-service.com
HF_API_KEY=hf_xxxxxxxxxxxxx
```

### Optional (for ChromaDB)
```
CHROMA_DB_PATH=/app/rag/chroma_db
```

---

## 🗄️ Persistent Storage (for ChromaDB)

Railway provides persistent volumes:

1. Go to your service → "Data" tab
2. Click "Add Volume"
3. Mount path: `/app/rag/chroma_db`
4. Size: 1GB (sufficient for RAG database)

This ensures ChromaDB data persists across deployments.

---

## 🔧 Configuration Files

Your repository already includes:

✅ `Procfile` - Tells Railway how to start the app
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

✅ `railway.json` - Railway configuration
✅ `nixpacks.toml` - Build configuration
✅ `backend/requirements.txt` - Python dependencies

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────┐
│      Railway Container          │
│                                 │
│  ┌──────────────────────────┐  │
│  │  FastAPI Backend         │  │
│  │  - Serves frontend       │  │
│  │  - API endpoints         │  │
│  │  - RAG system            │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Static Files            │  │
│  │  - frontend/             │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  ChromaDB (Volume)       │  │
│  │  - Persistent storage    │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
           ↓
      ┌──────────┐
      │  Ollama  │ (External service)
      │  or HF   │
      └──────────┘
```

---

## 🎯 Full Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Railway account
- [ ] Deploy from GitHub repo
- [ ] Generate domain
- [ ] Add volume for ChromaDB (1GB)
- [ ] Choose AI option:
  - [ ] Option A: Add external Ollama URL
  - [ ] Option B: Add Hugging Face API key
- [ ] Test frontend at your Railway URL
- [ ] Test AI generation
- [ ] Monitor logs for errors

---

## 🐛 Troubleshooting

### Issue: App not starting
**Check:** Logs in Railway dashboard
**Solution:** Ensure `Procfile` and `railway.json` are correct

### Issue: AI generation fails
**Check:** Ollama/HF API key configuration
**Solution:** Add proper environment variables

### Issue: ChromaDB errors
**Check:** Volume is mounted correctly
**Solution:** Add persistent volume at `/app/rag/chroma_db`

### Issue: Frontend shows but API fails
**Check:** CORS settings in `main.py`
**Solution:** Already configured with `allow_origins=["*"]`

---

## 💰 Cost Estimation

Railway Pricing:
- **Free Tier**: $5 credit/month
  - ~500 hours of usage
  - Good for development/testing

- **Hobby Plan**: $5/month
  - Unlimited usage
  - Perfect for personal projects

- **Pro Plan**: $20/month
  - Team features
  - Production-ready

**Your app will likely use:** ~$3-5/month on Hobby plan

---

## 📈 Monitoring

Railway provides:
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Network usage
- **Deployments**: History of all deployments
- **Health checks**: Auto-restart on failure

Access via: Railway Dashboard → Your Service → Tabs

---

## 🔄 Auto-Deploy on Git Push

Railway automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway detects the push and redeploys automatically! 🎉

---

## 🌐 Custom Domain (Optional)

1. Go to service → Settings → Domains
2. Click "Custom Domain"
3. Add your domain (e.g., `fitness-ai.com`)
4. Update DNS:
   - Type: CNAME
   - Name: @
   - Value: Your Railway domain

---

## 📚 Recommended Setup for Production

1. **Deploy to Railway** (full backend + frontend)
2. **Add Persistent Volume** (for ChromaDB)
3. **Use Hugging Face API** (easier than hosting Ollama)
4. **Enable Health Checks** (auto-restart on failure)
5. **Monitor Logs** (check for errors)
6. **Set up Custom Domain** (optional but professional)

---

## 🎓 Alternative: Hybrid Deployment

If Railway costs too much:

**Frontend**: Vercel/Netlify (free)
**Backend**: Railway (paid)

Update `frontend/app.js`:
```javascript
const API_URL = 'https://your-railway-app.railway.app/api/rag_generate';
```

---

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Open an issue in your repo

---

## ✅ Ready to Deploy?

**Quick Start:**
1. Go to https://railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub
4. Select `Fitness-AI`
5. Wait 2-3 minutes
6. Click "Generate Domain"
7. Visit your app! 🚀

Your full-stack AI app will be live with:
- ✅ Working frontend
- ✅ API backend
- ✅ RAG system (with volume)
- ⚠️ AI generation (needs Ollama/HF setup)

---

**Good luck with your deployment!** 🎉
