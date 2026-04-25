#!/usr/bin/env python
"""
Diskova+ AI - with OpenCode Zen Models
==============================
Created by: Joseph Amaning Kwarteng | Ghana
Version: 1.1 | Supports Ollama + OpenCode Zen

Models:
- Ollama (local, free): qwen2.5-coder:1.5b
- OpenCode Zen: GPT-5, Claude, Gemini, Qwen, etc.
"""

import gradio as gr
import requests
import os
import re
import asyncio

# ==================== CONFIGURATION ====================

# Default: Ollama (local, free)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

# OpenCode Zen Configuration
ZEN_API_KEY = os.environ.get("ZEN_API_KEY", "")  # Add your key here
ZEN_BASE_URL = "https://opencode.ai/zen/v1"

# Model Providers
PROVIDERS = {
    "ollama": {
        "name": "Ollama (Local)",
        "url": "http://localhost:11434",
        "model": "qwen2.5-coder:1.5b",
        "free": True,
    },
    "gpt-5-nano": {
        "name": "GPT-5 Nano (Zen)",
        "model": "opencode/gpt-5-nano",
        "free": True,  # Free model!
    },
    "gpt-5.4": {
        "name": "GPT-5.4 (Zen)",
        "model": "opencode/gpt-5.4",
        "free": False,
    },
    "claude-haiku-4.5": {
        "name": "Claude Haiku 4.5 (Zen)",
        "model": "opencode/claude-haiku-4-5",
        "free": False,
    },
    "gemini-3-flash": {
        "name": "Gemini 3 Flash (Zen)",
        "model": "opencode/gemini-3-flash",
        "free": False,
    },
    "qwen3.5-plus": {
        "name": "Qwen3.5 Plus (Zen)",
        "model": "opencode/qwen3.5-plus",
        "free": False,
    },
    "big-pickle": {
        "name": "Big Pickle (Zen)",
        "model": "opencode/big-pickle",
        "free": True,  # Free!
    },
}

# Creator Info
CREATOR = "Joseph Amaning Kwarteng"
CREATOR_LOCATION = "Ghana"
APP_NAME = "Diskova+ AI"

# ==================== VOICE SETUP ====================

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Note: Voice input requires 'pip install SpeechRecognition'. Using text mode.")

try:
    import pyaudio
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False

try:
    import edge_tts
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ==================== HELPER FUNCTIONS ====================

def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False


def check_ollama():
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except:
        return False


def web_search(query):
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        text = r.text
        results = re.findall(r'class="result__snippet">(.*?)</', text)
        if results:
            return " | ".join(results[:3])
        return "No results"
    except Exception as e:
        return f"Search error: {e}"


def get_weather(loc):
    try:
        r = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=10)
        if r.status_code == 200:
            d = r.json()
            c = d.get("current_condition", [{}])[0]
            temp = c.get("temp_C", "N/A")
            desc = c.get("weatherDesc", "N/A")
            if isinstance(desc, list):
                desc = desc[0].get("value", "N/A")
            return f"{loc}: {temp}C, {desc}"
    except Exception as e:
        return f"Weather error: {e}"


def get_stock(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d", timeout=10)
        if r.status_code == 200:
            d = r.json()
            p = d["chart"]["result"][0]["meta"]["regularMarketPrice"]
            return f"{sym}: ${p}"
    except:
        return f"{sym}: unavailable"


def voice_to_text():
    if not VOICE_AVAILABLE:
        return "Voice lib not installed. Run: pip install SpeechRecognition"
    if not MIC_AVAILABLE:
        return "Microphone needs PyAudio. Run: pip install pyaudio"
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return "No speech detected. Try again."
    except sr.UnknownValueError:
        return "Could not understand. Speak clearly."
    except Exception as e:
        return f"Voice error: {str(e)[:40]}"


async def text_to_speech(text):
    if not TTS_AVAILABLE:
        return None
    try:
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        await communicate.save("response.mp3")
        return "response.mp3"
    except:
        return None

# ==================== LLM CLIENTS ====================

def chat_ollama(message):
    """Chat using local Ollama"""
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": message}], "stream": False},
            timeout=120
        )
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "") or "No response"
    except Exception as e:
        return f"Ollama error: {str(e)[:60]}"


def chat_zen(message, model_id):
    """Chat using OpenCode Zen"""
    if not ZEN_API_KEY:
        return "Error: ZEN_API_KEY not set. Add your OpenCode Zen API key to environment variables."
    
    try:
        # Determine endpoint based on model
        if "claude" in model_id:
            endpoint = f"{ZEN_BASE_URL}/messages"
            payload = {
                "model": model_id,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": message}]
            }
            headers = {
                "Authorization": f"Bearer {ZEN_API_KEY}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        else:
            endpoint = f"{ZEN_BASE_URL}/chat/completions"
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 4096
            }
            headers = {
                "Authorization": f"Bearer {ZEN_API_KEY}",
                "Content-Type": "application/json"
            }
        
        r = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        
        if r.status_code == 200:
            data = r.json()
            if "claude" in model_id:
                return data.get("content", [{}])[0].get("text", "") or "No response"
            else:
                return data.get("choices", [{}])[0].get("message", {}).get("content", "") or "No response"
        else:
            return f"Zen error: {r.status_code} - {r.text[:100]}"
    except Exception as e:
        return f"Zen error: {str(e)[:60]}"


# ==================== MAIN CHAT ====================

def auto_detect_and_tool(message):
    msg = message.lower()
    
    # Help
    if "help" in msg or "what can you do" in msg:
        return "I can help with:\n- Weather, stocks, web search\n- Code questions\n- General chat\n- And more!"
    
    # Switch model
    if "use gpt" in msg or "switch to gpt" in msg:
        return f"Model switched to {PROVIDERS['gpt-5.4']['name']}"
    
    if "use claude" in msg or "switch to claude" in msg:
        return f"Model switched to {PROVIDERS['claude-haiku-4.5']['name']}"
    
    # Weather
    if "weather" in msg:
        loc = re.search(r'in\s+(\w+)', msg)
        location = loc.group(1) if loc else "Tokyo"
        return get_weather(location)
    
    # Stock
    if "stock" in msg or "$" in msg:
        symbols = re.findall(r'\b[A-Z]{2,5}\b', msg.upper())
        sym = symbols[0] if symbols else "AAPL"
        return get_stock(sym)
    
    # Search
    if "search" in msg or "find" in msg:
        query = message
        for w in ["search", "find", "look up"]:
            query = query.replace(w, "")
        return web_search(query.strip())
    
    return None


def chat(message, history, provider="ollama"):
    if not message.strip():
        return "", history
    
    msg_lower = message.lower().strip()
    
    # Identity - ALWAYS answer first, don't pass to LLM
    identity_triggers = ["what is your name", "who are you", "your name", "who created", "who made", "your creator"]
    if any(t in msg_lower for t in identity_triggers):
        history.append({"role": "user", "content": message})
        reply = "I am diskova+ AI, created by Joseph Amaning Kwarteng from Ghana. I use Ollama locally and OpenCode Zen for cloud models."
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    # Hello / greeting - ALWAYS answer first
    greeting_triggers = ["hello", "hi", "hey", "greetings"]
    if any(t in msg_lower for t in greeting_triggers):
        history.append({"role": "user", "content": message})
        reply = "Hello! I am diskova+ AI, created by Joseph Amaning Kwarteng from Ghana. How can I help you today?"
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    # Check tool first
    tool_result = auto_detect_and_tool(message)
    if tool_result:
        reply = tool_result
    else:
        # Use selected provider
        provider_config = PROVIDERS.get(provider, PROVIDERS["ollama"])
        
        if provider == "ollama":
            reply = chat_ollama(message)
        else:
            model_id = provider_config.get("model", "")
            reply = chat_zen(message, model_id)
    
    history.append({"role": "assistant", "content": reply})
    return "", history


# ==================== GUI ====================

internet_ok = check_internet()
ollama_ok = check_ollama()
status = "Online" if internet_ok else "Offline"
mic_status = "Ready" if MIC_AVAILABLE else "Needs PyAudio"
tts_status = "Ready" if TTS_AVAILABLE else "Not Installed"

with gr.Blocks(title=f"{APP_NAME}") as app:
    gr.Markdown(f"## {APP_NAME}\n**Creator: {CREATOR} | {CREATOR_LOCATION}**\n- Status: {status} | Ollama: {'Running' if ollama_ok else 'Not Running'}\n- Models: Ollama (free) + OpenCode Zen (cloud)")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=450)
            with gr.Row():
                msg = gr.Textbox(placeholder="Ask me anything...", label="Message", scale=5)
                btn_send = gr.Button("Send", variant="primary")
        
        with gr.Column(scale=1):
            gr.Markdown("### Model")
            provider_dropdown = gr.Dropdown(
                choices=list(PROVIDERS.keys()),
                value="ollama",
                label="Select Provider",
            )
            
            gr.Markdown("### Quick Actions")
            gr.Button("Weather", size="sm").click(lambda: "Tokyo weather", outputs=[msg])
            gr.Button("Stocks", size="sm").click(lambda: "AAPL stock", outputs=[msg])
            gr.Button("Search", size="sm").click(lambda: "Search for AI", outputs=[msg])
            
            gr.Markdown("### Voice Input")
            if VOICE_AVAILABLE and MIC_AVAILABLE:
                gr.Button("Record Mic", variant="stop").click(voice_to_text, outputs=msg)
            else:
                gr.Markdown("*Install SpeechRecognition + PyAudio for voice*")
            
            gr.Markdown("### Examples")
            gr.Examples(
                examples=[
                    ["What is your name?"],
                    ["Hello!"],
                    ["Weather in Tokyo"],
                    ["AAPL stock"],
                ],
                inputs=msg,
            )
    
    # Events
    btn_send.click(chat, [msg, chatbot, provider_dropdown], [msg, chatbot])
    msg.submit(chat, [msg, chatbot, provider_dropdown], [msg, chatbot])

print("=" * 50)
print(f"{APP_NAME}")
print(f"Creator: {CREATOR} | {CREATOR_LOCATION}")
print("=" * 50)
print("Models available:")
for k, v in PROVIDERS.items():
    print(f"  - {k}: {v['name']} {'(FREE)' if v.get('free') else ''}")
print("=" * 50)
print(f"GUI: http://localhost:7860")
app.launch(server_name="0.0.0.0", server_port=7860)