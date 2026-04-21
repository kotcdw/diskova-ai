# DISKOVA+ Deployment Scripts

## Railway Deployment (Recommended - FREE)

### Prerequisites
1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login:
```bash
railway login
```

3. Initialize project:
```bash
cd diskova+
railway init
```

### Deploy
```bash
railway up
```

### Set Environment Variables
```bash
railway variables set OPENAI_API_KEY=your-key
railway variables set LLM_PROVIDER=openai
```

### Get URL
```bash
railway domain
```

---

## Render Deployment (Alternative - FREE)

1. Go to https://render.com
2. Connect GitHub repo
3. Create Web Service
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn diskova.main:app --host 0.0.0.0 --port $PORT`
5. Add env vars in dashboard

---

## Docker Deployment

### Build
```bash
docker build -t diskova-plus .
```

### Run
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  diskova-plus
```

### Docker Compose
```yaml
version: '3.8'
services:
  diskova:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

---

## Railway Commands Reference

| Command | Description |
|---------|-------------|
| `railway login` | Login to Railway |
| `railway init` | Initialize project |
| `railway up` | Deploy |
| `railway down` | Stop service |
| `railway logs` | View logs |
| `railway status` | Check status |
| `railway shell` | Open shell |
| `railway variables` | Manage vars |