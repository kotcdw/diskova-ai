# Diskova AI 🧠

**Created by Joseph Amaning Kwarteng** | Ghana, West Africa

---

## About

Diskova AI is a lightweight desktop AI assistant built to help with everyday tasks through conversation and background learning. Runs entirely locally with Ollama - **$0 cost**.

## Vision

> "African AI Operating System for Work & Life"

## Core Capabilities

| Layer | Functions |
|-------|-----------|
| **Perception** | Text, Voice (STT), Image input |
| **Brain** | NLP, Reasoning, Memory (ChromaDB) |
| **Action** | 80+ tools, Web search, Weather, Stocks |
| **Response** | Text, TTS, Markdown |

## Features

### ✅ Working Now
- [x] Chat interface (Gradio GUI)
- [x] Auto-Internet (weather, stocks, search)
- [x] Voice input (SpeechRecognition)
- [x] Voice output (Edge TTS)
- [x] System tray (background)
- [x] Auto-start on boot
- [x] File monitoring
- [x] Notifications
- [x] Chat history saving
- [x] Continuous learning

### ⏳ Coming
- [ ] Wake word: "hey diskova"
- [ ] Desktop widget overlay
- [ ] WhatsApp integration
- [ ] Mobile app

## Quick Start

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com | sh

# 2. Pull model
ollama pull qwen2.5-coder:1.5b

# 3. Run GUI
cd diskova/agent
python gui_chat.py
```

Open: **http://localhost:7860**

## Desktop Mode

```bash
python diskova/agent/desktop_assistant.py
```

- System tray icon
- Auto-start on boot
- Background learning
- Voice activation

## Architecture

```
User Input → Perception → Brain → Action → Response
   (Text/Voice)      ↓        ↓       ↓
                 NLP      Tools   Output
                 Memory  Search  TTS
                 Reason  Code   Format
```

## Stack (All Free)

| Component | Technology |
|-----------|------------|
| LLM | Ollama (local) |
| GUI | Gradio |
| Vector DB | ChromaDB |
| Voice | SpeechRecognition + Edge TTS |
| Tray | pystray |

## Cost: $0

No API keys, no cloud fees - everything runs locally.

---

**Creator:** Joseph Amaning Kwarteng  
**From:** Ghana, West Africa  
**Mission:** Affordable AI for Africa & Beyond 🌍

*Built with 💙 in Ghana*