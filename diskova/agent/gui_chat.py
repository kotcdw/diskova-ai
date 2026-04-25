#!/usr/bin/env python
"""Diskova AI - Auto-Internet GUI"""

import gradio as gr
import requests
import os
import re

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")


def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        try:
            requests.get("https://api.github.com", timeout=3)
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


def auto_detect_and_tool(message):
    """Auto-detect request type and get info"""
    msg = message.lower()
    
    # Weather
    if "weather" in msg:
        loc = re.search(r'in\s+(\w+)', msg) or re.search(r'(\w+)\s+weather', msg)
        location = loc.group(1) if loc else "Tokyo"
        return get_weather(location)
    
    # Stock
    if "stock" in msg or "price" in msg or "$" in msg:
        sym = re.search(r'([A-Z]{1,5})\s*(?:stock|price|\$)', msg.upper()) or re.search(r'^([A-Z]+)', msg.upper())
        if not sym:
            symbols = re.findall(r'\b[A-Z]{2,5}\b', msg.upper())
            sym = symbols[0] if symbols else "AAPL"
        else:
            sym = sym.group(1)
        return get_stock(sym)
    
    # Search
    if "search" in msg or "find" in msg or "look up" in msg:
        query = message
        for w in ["search", "find", "look up", "for"]:
            query = query.replace(w, "")
        return web_search(query.strip())
    
    # Translate
    if "translate" in msg or "japanese" in msg or "spanish" in msg or "french" in msg:
        return f"Translation: {message} (demo mode)"
    
    return None


def chat(message, history):
    if not message.strip():
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    # Auto-check for tool requests
    tool_result = auto_detect_and_tool(message)
    if tool_result:
        reply = tool_result
    else:
        # Call Ollama
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": message}], "stream": False},
                timeout=120
            )
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "") or "No response"
        except Exception as e:
            reply = f"Ollama error: {str(e)[:60]}"
    
    history.append({"role": "assistant", "content": reply})
    return "", history
    
    history.append([message, None])
    reply = "Thinking..."
    
    # Auto-check for tool requests
    tool_result = auto_detect_and_tool(message)
    if tool_result:
        reply = tool_result
    else:
        # Call Ollama
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": message}], "stream": False},
                timeout=120
            )
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "") or "No response"
        except Exception as e:
            reply = f"Ollama error: {str(e)[:60]}"
    
    history[-1][1] = reply
    return "", history


internet_ok = check_internet()
status = "Online" if internet_ok else "Offline"

with gr.Blocks(title="Diskova AI") as app:
    gr.Markdown(f"## Diskova AI\n**Status: {status} | Model: {OLLAMA_MODEL} | Internet: Auto-connected**")
    
    chatbot = gr.Chatbot(height=500)
    with gr.Row():
        msg = gr.Textbox(placeholder="Ask me anything... (auto-searches web, weather, stocks)", scale=5)
        btn = gr.Button("Send", variant="primary")
    
    gr.Examples(
        examples=[
            ["Hello!"],
            ["Weather in Tokyo"],
            ["AAPL stock price"],
            ["Search for AI trends 2026"],
            ["Translate hello to Japanese"],
        ],
        inputs=msg,
    )
    
    btn.click(chat, [msg, chatbot], [msg, chatbot])
    msg.submit(chat, [msg, chatbot], [msg, chatbot])

print("Diskova AI: http://localhost:7860")
app.launch(server_name="0.0.0.0", server_port=7860)