"""
AI Coding Agent Launcher
==================
Start the complete AI coding agent system.

Usage:
    python launcher.py           # Start everything
    python launcher.py gui    # GUI only
    python launcher.py mcp   # MCP server only
    python launcher.py test  # Test the system
"""

import os
import sys
import json
import subprocess
import time
import webbrowser
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
CONFIG_FILE = PROJECT_DIR / "config" / "llm_config.json"


def load_config() -> dict:
    """Load config."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def start_ollama() -> bool:
    """Start Ollama service."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5
        )
        print("Ollama running")
        return True
    except:
        print("Starting Ollama...")
        try:
            subprocess.Popen(["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(3)
            return True
        except:
            print("Could not start Ollama")
            return False


def start_mcp() -> subprocess.Popen:
    """Start MCP server."""
    print("Starting MCP server...")
    try:
        proc = subprocess.Popen(
            [sys.executable, "brain_server.py"],
            cwd=PROJECT_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print(f"MCP server started (PID: {proc.pid})")
        return proc
    except Exception as e:
        print(f"MCP error: {e}")
        return None


def start_gui() -> subprocess.Popen:
    """Start Gradio GUI."""
    print("Starting Gradio GUI...")
    try:
        proc = subprocess.Popen(
            [sys.executable, "gui_chat.py"],
            cwd=PROJECT_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print(f"GUI started (PID: {proc.pid})")
        return proc
    except Exception as e:
        print(f"GUI error: {e}")
        return None


def open_browser(url: str = "http://localhost:7860"):
    """Open browser."""
    try:
        webbrowser.open(url)
        print(f"Opened {url}")
    except:
        pass


def test_system():
    """Test the complete system."""
    print("=" * 50)
    print("Testing AI Coding Agent")
    print("=" * 50)
    
    # Test 1: Files exist
    print("\n[1] Checking files...")
    files_to_check = [
        "brain_server.py",
        "gui_chat.py",
        "llm_client.py",
        "config/llm_config.json"
    ]
    for f in files_to_check:
        status = "[OK]" if (PROJECT_DIR / f).exists() else "[MISSING]"
        print(f"   {status} {f}")
    
    # Test 2: Ollama
    print("\n[2] Checking Ollama...")
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get("models", [])
            print(f"   [OK] Ollama running")
            print(f"   Models: {[m['name'] for m in models]}")
        else:
            print(f"   [WARN] Ollama returned {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Ollama not running: {e}")
    
    # Test 3: LM Studio
    print("\n[3] Checking LM Studio...")
    try:
        import requests
        r = requests.get("http://localhost:1234/v1/models", timeout=2)
        if r.status_code == 200:
            print(f"   [OK] LM Studio running")
        else:
            print(f"   [WARN] LM Studio returned {r.status_code}")
    except:
        print("   [INFO] LM Studio not running")
        print("   (Download from https://lmstudio.ai)")
    
    # Test 4: MCP Tools
    print("\n[4] Testing MCP imports...")
    try:
        sys.path.insert(0, str(PROJECT_DIR))
        import brain_server
        print(f"   [OK] brain_server loaded")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 5: Web Search
    print("\n[5] Testing Web Search...")
    try:
        sys.path.insert(0, str(PROJECT_DIR / "tools"))
        from web_search import WebSearch
        search = WebSearch()
        print(f"   [OK] web_search loaded")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n" + "=" * 50)
    print("System Status")
    print("=" * 50)
    print("""
To start the agent:
    
    Terminal 1 - MCP Server:
    python brain_server.py
    
    Terminal 2 - GUI:
    python gui_chat.py
    
    Then open: http://localhost:7860
    
For LM Studio (better performance):
    1. Download from https://lmstudio.ai
    2. Load a GGUF model (e.g., Phi-4, Qwen2.5)
    3. Click "Start Server" in LM Studio
""")
    
    return True


def main():
    """Main launcher."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if "test" in args:
        test_system()
        return
    
    if "gui" in args:
        start_gui()
        return
    
    if "mcp" in args:
        start_mcp()
        return
    
    # Start everything
    print("=" * 50)
    print("AI Coding Agent Launcher")
    print("=" * 50)
    
    # Check/start Ollama
    print("\nChecking Ollama...")
    start_ollama()
    
    # Start MCP
    print("\nStarting MCP server...")
    start_mcp()
    
    # Start GUI
    print("\nStarting GUI...")
    start_gui()
    
    # Open browser
    print("\nOpening browser...")
    open_browser()
    
    print("\n" + "=" * 50)
    print("AI Coding Agent Ready!")
    print("=" * 50)
    print("\nOpen http://localhost:7860 in your browser")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()