# DISKOVA+ - African AI Operating System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.135-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/OpenAI-GPT-3.5-red" alt="OpenAI">
  <img src="https://img.shields.io/badge/Cost-$0-brightgreen" alt="Cost">
</p>

A lightweight, modular AI assistant built for Africa. Acts as your **secretary**, **analyst**, **writer**, **task manager**, and **business brain**.

---

## Features

| Module | Capabilities |
|--------|-------------|
| **Secretary** | Smart scheduling, task delegation, reminders |
| **Finance** | Budget tracking, cash flow forecasting |
| **Security** | Login monitoring, 2FA, anomaly alerts |
| **Knowledge** | News briefs, trend analysis, research |
| **Voice** | Speech-to-text, multilingual support |
| **Automation** | Workflows, triggers, auto-execution |

---

## Quick Start

### 1. Clone & Setup
```bash
cd diskova+
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run Server
```bash
python -m uvicorn diskova.main:app --port 8000
```

### 4. Open Frontend
- Navigate to `diskova/frontend/index.html` in your browser
- Or open `http://localhost:8000/docs` for API documentation

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/chat/message` | POST | Send message |
| `/api/chat/history/{user_id}` | GET | Get history |
| `/api/chat/task` | POST | Create task |
| `/api/chat/tasks/{user_id}` | GET | Get tasks |
| `/api/auth/register` | POST | Register user |
| `/api/auth/login` | POST | Login |
| `/api/modules/list` | GET | List modules |

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Frontend (HTML/React)          │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│          FastAPI Backend (Python)          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  Auth   │ │  Chat   │ │ Modules │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│        AI Core (Module Router + LLM)       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  GPT    │ │ Memory  │ │ Context │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│          10 Feature Modules             │
│  Secretary │ Finance │ Security │ More   │
└─────────────────────────────────────────┘
```

---

## Cost: $0

| Service | Free Tier |
|---------|----------|
| Vercel (Frontend) | 100GB bandwidth |
| Railway (Backend) | 500hrs |
| OpenAI | $5 free credits |
| Supabase | 500MB DB |
| Firebase | 1GB DB |

---

## Project Structure

```
diskova+/
├── SPEC.md              # Architecture spec
├── README.md           # This file
├── requirements.txt    # Python deps
├── .env.example       # Env template
└── diskova/
    ├── main.py        # FastAPI entry
    ├── core/
    │   ├── llm/      # AI routing
    │   └── memory/   # Context
    ├── modules/      # 10 modules
    ├── api/         # REST routes
    ├── db/          # Database
    └── frontend/
        └── index.html
```

---

## License

MIT License - Build freely, scale infinitely.

**Diskova+: Your African AI Brain for Work & Life**