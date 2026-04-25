#!/usr/bin/env python
"""
PowerfulBrain AI Coding Agent - GUI Chat Interface
=====================================
A beautiful Gradio-based chat interface for your AI coding agent.
Features:
- Beautiful dark UI
- Real-time streaming responses
- Code syntax highlighting
- Tool usage visualization
- Session history

Run with: python gui_chat.py
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from threading import Thread
import time

# Gradio for UI
try:
    import gradio as gr
except ImportError:
    print("Installing Gradio...")
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr

# Try to import our brain server modules
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Global state
current_model = "qwen2.5-coder:1.5b"
conversation_history = []
session_start = datetime.now().strftime("%Y-%m-%d %H:%M")

# Colors for dark theme
BG_COLOR = "#0e0e0f"
CARD_COLOR = "#1a1a1f"
ACCENT_COLOR = "#6366f1"
TEXT_COLOR = "#e2e8f0"
MUTED_COLOR = "#64748b"


def check_ollama_running():
    """Check if Ollama is running."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "qwen2.5-coder" in result.stdout or "llama" in result.stdout or "codellama" in result.stdout
    except Exception:
        return False


def get_available_models():
    """Get list of available Ollama models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        models = []
        for line in result.stdout.split('\n')[1:]:
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        return models if models else ["qwen2.5-coder:1.5b"]
    except Exception:
        return ["qwen2.5-coder:1.5b"]


def generate_response_streaming(message, history, model选择=None):
    """Generate streaming response using Ollama."""
    global conversation_history
    
    # Build context from history
    context = "\n".join([
        f"User: {h[0]}\nAssistant: {h[1]}" 
        for h in history[-5:] if len(h) > 1
    ])
    
    # Full prompt
    prompt = f"""You are a powerful local AI coding assistant with access to tools.

Your capabilities:
- Write, review, and debug code
- Execute Python, JavaScript, Bash commands
- Search and analyze codebases
- Read/write files
- Run tests
- Use git versioning
- Create project scaffolds
- Generate documentation

Always provide detailed, accurate code and explanations.

Previous conversation:
{context}

User: {message}
Assistant: """
    
    model = model选择 or current_model
    
    try:
        # Start Ollama process
        process = subprocess.Popen(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        output_parts = []
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                if line and not line.startswith('Ollama'):
                    output_parts.append(line)
                    # Yield each chunk for streaming
                    yield "".join(output_parts)
            
            # Check if process ended
            if process.poll() is not None:
                break
        
        # Get any remaining output
        remaining, _ = process.communicate()
        if remaining:
            output_parts.append(remaining.strip())
        
        full_response = "".join(output_parts)
        
    except FileNotFoundError:
        full_response = "⚠️ Ollama not found. Please install Ollama from https://ollama.com"
    except subprocess.TimeoutExpired:
        full_response = "⏱️ Response timed out. The model might be loading..."
    except Exception as e:
        full_response = f"❌ Error: {str(e)}"
    
    # Add to conversation
    conversation_history.append([message, full_response])
    
    yield full_response


def generate_response_simple(message, history, model选择=None):
    """Simple non-streaming response."""
    response = ""
    for chunk in generate_response_streaming(message, history, model选择):
        response = chunk
    return response


def create_tool_card(tool_name, description, status="ready"):
    """Create a visual card for a tool."""
    status_emoji = "🟢" if status == "ready" else "🔴"
    return f"""
<div style="
    background: {CARD_COLOR};
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
    border: 1px solid #333;
">
    <b>{status_emoji} {tool_name}</b><br>
    <small style="color: {MUTED_COLOR}">{description}</small>
</div>
"""


def get_tools_html():
    """Get HTML for tools display."""
    tools = [
        ("🔍 search_knowledge", "Semantic search across knowledge base"),
        ("💾 get_code_snippet", "Fetch code boilerplates (100+)"),
        ("📝 save_session_memory", "Store task results"),
        ("🔎 review_code", "Self-code review"),
        ("📊 analyze_project", "Project structure analysis"),
        ("✅ update_task_status", "Track multi-step tasks"),
        ("📚 generate_docs", "Auto-generate documentation"),
        ("🧠 recall_pattern", "Find similar solved problems"),
        ("⚡ execute_code", "Run Python/JS/Bash code"),
        ("🧪 run_tests", "Run pytest/jest tests"),
        ("📁 read_file", "Read file contents"),
        ("✏️ write_file", "Write content to file"),
        ("📂 list_files", "List project files"),
        ("🔀 git_command", "Git version control"),
        ("🔍 search_code", "Search code patterns"),
        ("📄 get_file_info", "File information"),
        ("🏗️ create_project_scaffold", "Create new projects"),
    ]
    
    html = '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">'
    for tool, desc in tools:
        html += f'<div style="background: {CARD_COLOR}; padding: 12px; border-radius: 8px; border: 1px solid #333;">'
        html += f'<b style="color: {ACCENT_COLOR}">{tool}</b><br>'
        html += f'< small style="color: {MUTED_COLOR}">{desc}</small>'
        html += '</div>'
    html += '</div>'
    
    return html


def chat_fn(message, history, model选择=None):
    """Main chat function with streaming."""
    if not message:
        return "", history
    
    # Display thinking indicator
    thinking_msg = "🤔 Thinking..."
    
    # Enable streaming
    response = ""
    for chunk in generate_response_streaming(message, history or [], model选择):
        response = chunk
        yield response
    
    return response


def clear_session():
    """Clear the current session."""
    global conversation_history
    conversation_history = []
    return [], ""


# Custom CSS for beautiful UI
custom_css = f"""
<style>
body {{
    background: {BG_COLOR} !important;
}}

.gradio-container {{
    background: {BG_COLOR} !important;
}}

.main {{
    background: {BG_COLOR} !important;
}}

.chat-message {{
    background: {CARD_COLOR} !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
}}

.user-message {{
    background: {ACCENT_COLOR}20 !important;
    border-left: 3px solid {ACCENT_COLOR} !important;
}}

.bot-message {{
    background: {CARD_COLOR} !important;
    border-left: 3px solid #22c55e !important;
}}

.prose {{
    color: {TEXT_COLOR} !important;
}}

code {{
    background: #1e1e2e !important;
    padding: 2px 6px;
    border-radius: 4px;
}}

button.primary {{
    background: {ACCENT_COLOR} !important;
    border: none !important;
}}

button.secondary {{
    background: {CARD_COLOR} !important;
    border: 1px solid #333 !important;
}}

.tool-card {{
    background: {CARD_COLOR};
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}}

.stats {{
    background: {CARD_COLOR};
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}}

.header {{
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #1a1a2e 0%, #0e0e0f 100%);
    border-radius: 12px;
    margin-bottom: 20px;
}}

.status-indicator {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 8px;
}}

.model-selector {{
    background: {CARD_COLOR};
    border-radius: 8px;
    padding: 10px;
}}
</style>
"""


def create_gui():
    """Create the Gradio GUI."""
    
    # Get available models
    models = get_available_models()
    default_model = models[0] if models else "qwen2.5-coder:1.5b"
    
    # Check Ollama status
    ollama_status = "🟢 Running" if check_ollama_running() else "🔴 Not Running"
    model_info = f"**{default_model}**" if check_ollama_running() else "⚠️ Install Ollama"
    
    # Build GUI
    with gr.Blocks(
        title="PowerfulBrain AI Coding Agent",
        theme=gr.themes.Soft(
            primary_hue="indigo",
        ),
        css=custom_css,
    ) as app:
        
        # Header
        gr.HTML(f"""
        <div class="header">
            <h1 style="color: {TEXT_COLOR}; margin: 0;">
                🧠 PowerfulBrain AI Coding Agent
            </h1>
            <p style="color: {MUTED_COLOR}; margin: 10px 0;">
                A complete local AI coding ecosystem
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 15px;">
                <span>🤖 Model: {model_info}</span>
                <span>📡 Ollama: {ollama_status}</span>
                <span>🕐 Session: {session_start}</span>
            </div>
        </div>
        """)
        
        with gr.Row():
            # Left sidebar - Tools
            with gr.Column(scale=1):
                gr.HTML(f"""
                <div style="background: {CARD_COLOR}; padding: 15px; border-radius: 12px;">
                    <h3 style="color: {TEXT_COLOR}; margin: 0 0 15px 0;">
                        🔧 Available Tools
                    </h3>
                    {get_tools_html()}
                </div>
                """)
                
                # Stats
                gr.HTML(f"""
                <div class="stats" style="margin-top: 15px;">
                    <h4 style="color: {TEXT_COLOR};">📊 Session Stats</h4>
                    <p>Messages: <span id="msg_count">0</span></p>
                    <p>Tools: <b>17</b></p>
                    <p>Snippets: <b>100+</b></p>
                </div>
                """)
                
                # Quick actions
                gr.Button("🗑️ Clear Session", variant="secondary", size="sm").click(
                    clear_session,
                    outputs=[gr.Chatbot(), gr.Textbox()],
                    show_progress=False
                )
            
            # Main chat area
            with gr.Column(scale=3):
                # Model selector
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=models,
                        value=default_model,
                        label="AI Model",
                        interactive=True
                    )
                
                # Chat interface
                chatbot = gr.Chatbot(
                    height=500,
                    avatar_images=(None, None),
                )
                
                # Input area
                with gr.Row():
                    msg_input = gr.Textbox(
                        show_label=False,
                        placeholder="Ask me anything about coding...",
                        scale=4,
                        container=True
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Examples
                gr.Examples(
                    examples=[
                        ["Write a Python function to calculate fibonacci numbers"],
                        ["How do I create an async API endpoint in FastAPI?"],
                        ["Review this code and suggest improvements"],
                        ["Create a new Python project scaffold"],
                        ["Search my knowledge base for patterns"],
                    ],
                    inputs=msg_input,
                )
        
        # Event handlers
        submit_btn.click(
            chat_fn,
            inputs=[msg_input, chatbot, model_dropdown],
            outputs=[msg_input, chatbot]
        )
        
        msg_input.submit(
            chat_fn,
            inputs=[msg_input, chatbot, model_dropdown],
            outputs=[msg_input, chatbot]
        )
        
        # Clear on new message
        msg_input.change(
            lambda: "",
            outputs=msg_input
        )
    
    return app


def main():
    """Main entry point."""
    print("=" * 60)
    print("PowerfulBrain AI Coding Agent - GUI")
    print("=" * 60)
    
    # Create and launch GUI
    app = create_gui()
    
    print("\nStarting GUI...")
    print("URL: http://localhost:7860")
    print("\nPress Ctrl+C to stop\n")
    
    # Open browser automatically
    try:
        webbrowser.open("http://localhost:7860")
    except:
        pass
    
    # Launch the app
    app.launch(
        server_name="localhost",
        server_port=7860,
        share=False,
        inbrowser=False,  # We opened manually above
        show_error=True
    )


if __name__ == "__main__":
    main()