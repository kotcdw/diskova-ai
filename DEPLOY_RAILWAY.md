# DISKOVA+ Deployment Guide

## Option 1: Railway (Recommended - FREE)

### Step 1: Login to Railway
1. Go to https://railway.app
2. Click "Login" → Use GitHub account

### Step 2: Create Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub repository

### Step 3: Configure
1. Select the repository
2. Railway auto-detects Python
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn diskova.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables
1. Go to project Settings → Variables
2. Add:
   - `OPENAI_API_KEY` = your-openai-key
   - `LLM_PROVIDER` = openai

### Step 5: Deploy
1. Railway auto-deploys on push to main branch
2. Get URL from project Settings → Networking

---

## Option 2: Render.com (Easiest)

### Step 1: Create Account
1. Go to https://render.com
2. Login with GitHub

### Step 2: Create Web Service
1. Dashboard → "New +" → "Web Service"
2. Connect GitHub repo

### Step 3: Configure
- **Root Directory:** (leave empty)
- **Runtime:** Python 3.11
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn diskova.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Environment Variables
Add in Settings → Environment:
- `OPENAI_API_KEY` = your-key
- `PYTHON_VERSION` = 3.11

### Step 5: Deploy
Click "Create Web Service" → Done!

---

## Option 3: Vercel + Backend elsewhere

Deploy frontend to Vercel:
```bash
cd diskova/frontend
vercel --prod
```

---

## Verify Deployment

After deploying, test:
```
GET https://your-url.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

---

## Troubleshooting

| Error | Solution |
|-------|---------|
| Module not found | Check PYTHONPATH in Railway settings |
| OpenAI error | Verify API key is set |
| Timeout | Railway free tier has limits |

---

**Need help?** Share your GitHub repo and I'll create a PR with deployment config.