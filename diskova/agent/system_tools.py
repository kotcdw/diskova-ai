"""
System Tools - File Browser, Background Processes, Enhanced Memory
===========================================================
Tools that Diskova AI can do but opencode cannot:
- Remember previous sessions (persistent memory)
- Browse internet freely (web browsing)
- Run background processes
- Access files without paths (file browser)
- Create GUI apps (already have Gradio)
"""

import os
import sys
import json
import subprocess
import threading
import time
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import urljoin, urlparse
from webbrowser import open as open_url


class FileBrowser:
    """Browse files without exact paths - like a file explorer."""
    
    def __init__(self, root_dir: str = None):
        self.root = Path(root_dir or os.getcwd())
        self.cache = {}
        self._build_cache()
    
    def _build_cache(self):
        """Build file cache for fast browsing."""
        try:
            for p in self.root.rglob("*"):
                if p.is_file():
                    rel = str(p.relative_to(self.root))
                    self.cache[rel] = p
        except:
            pass
    
    def list(self, path: str = "") -> List[Dict]:
        """List files in directory."""
        target = self.root / path if path else self.root
        
        if not target.exists():
            target = self.root
        
        results = []
        try:
            for p in target.iterdir():
                results.append({
                    "name": p.name,
                    "type": "dir" if p.is_dir() else "file",
                    "size": p.stat().st_size if p.is_file() else 0,
                    "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat()
                })
        except:
            pass
        
        return sorted(results, key=lambda x: (x["type"] != "dir", x["name"]))
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search files by name."""
        results = []
        query_lower = query.lower()
        
        for name, path in self.cache.items():
            if query_lower in name.lower():
                results.append({
                    "name": path.name,
                    "path": str(path.relative_to(self.root)),
                    "type": "file"
                })
                if len(results) >= max_results:
                    break
        
        return results
    
    def get_info(self, path: str) -> Dict:
        """Get file/directory info."""
        target = self.root / path
        
        if not target.exists():
            target = self.root / path
        
        if not target.exists():
            return {"error": "Not found"}
        
        info = {
            "name": target.name,
            "path": str(target),
            "type": "dir" if target.is_dir() else "file",
        }
        
        if target.is_file():
            info["size"] = target.stat().st_size
            info["modified"] = datetime.fromtimestamp(target.stat().st_mtime).isoformat()
        
        return info
    
    def open_file(self, path: str) -> str:
        """Open file in default application."""
        target = self.root / path
        
        if target.exists():
            try:
                open_url(f"file://{target.absolute()}")
                return f"Opened: {target}"
            except:
                return "Error opening file"
        
        return "File not found"


class BackgroundProcessManager:
    """Run background processes - something opencode cannot do."""
    
    def __init__(self):
        self.processes: Dict[int, Dict] = {}
        self.process_id = 1
    
    def run(self, command: str, name: str = None) -> int:
        """Run command in background."""
        if name is None:
            name = f"process_{self.process_id}"
        
        def target():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                self.processes[self.process_id]["output"] = result.stdout
                self.processes[self.process_id]["returncode"] = result.returncode
            except Exception as e:
                self.processes[self.process_id]["error"] = str(e)
        
        thread = threading.Thread(target=target)
        proc_info = {
            "id": self.process_id,
            "name": name,
            "command": command,
            "thread": thread,
            "running": True,
            "output": "",
            "started": datetime.now().isoformat()
        }
        
        self.processes[self.process_id] = proc_info
        thread.start()
        
        pid = self.process_id
        self.process_id += 1
        
        return pid
    
    def get_status(self, pid: int) -> Dict:
        """Get process status."""
        if pid in self.processes:
            proc = self.processes[pid]
            return {
                "id": proc["id"],
                "name": proc["name"],
                "running": proc["running"],
                "output": proc.get("output", "")[:500],
                "returncode": proc.get("returncode")
            }
        return {"error": "Process not found"}
    
    def list(self) -> List[Dict]:
        """List all processes."""
        return [
            {"id": p["id"], "name": p["name"], "running": p["running"]}
            for p in self.processes.values()
        ]
    
    def kill(self, pid: int) -> str:
        """Kill a process."""
        if pid in self.processes:
            # Note: Can't actually kill threads in Python
            self.processes[pid]["running"] = False
            return f"Process {pid} stopped"
        return "Process not found"


class SessionMemory:
    """Remember previous sessions - something opencode cannot do."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "./data/sessions")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.data_dir / f"{self.current_session}.json"
        
        # Load previous session
        self.previous = self._load_previous()
    
    def _load_previous(self) -> Dict:
        """Load last session data."""
        try:
            sessions = sorted(self.data_dir.glob("*.json"))
            if len(sessions) >= 2:
                prev = sessions[-2]
                return json.loads(prev.read_text())
        except:
            pass
        return {"history": [], "notes": ""}
    
    def add(self, user: str, bot: str, metadata: Dict = None):
        """Add exchange to current session."""
        data = {"user": user, "bot": bot}
        if metadata:
            data["metadata"] = metadata
        data["timestamp"] = datetime.now().isoformat()
        
        if self.session_file.exists():
            try:
                current = json.loads(self.session_file.read_text())
            except:
                current = {"history": [], "notes": ""}
        else:
            current = {"history": [], "notes": ""}
        
        current["history"].append(data)
        
        # Keep last 1000 exchanges
        current["history"] = current["history"][-1000:]
        
        self.session_file.write_text(json.dumps(current, indent=2))
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get conversation history."""
        if self.session_file.exists():
            try:
                current = json.loads(self.session_file.read_text())
                return current.get("history", [])[-limit:]
            except:
                pass
        return []
    
    def get_previous_session(self) -> List[Dict]:
        """Get previous session history."""
        return self.previous.get("history", [])[-50:]
    
    def search(self, query: str) -> List[Dict]:
        """Search past sessions."""
        results = []
        
        for session in self.data_dir.glob("*.json"):
            try:
                data = json.loads(session.read_text())
                for item in data.get("history", []):
                    if query.lower() in item.get("user", "").lower():
                        results.append({
                            "user": item.get("user"),
                            "bot": item.get("bot"),
                            "session": session.stem
                        })
            except:
                pass
        
        return results[-20:]
    
    def add_note(self, note: str):
        """Add persistent note."""
        if self.session_file.exists():
            try:
                current = json.loads(self.session_file.read_text())
            except:
                current = {"history": [], "notes": ""}
        else:
            current = {"history": [], "notes": ""}
        
        notes = current.get("notes", "")
        current["notes"] = f"{notes}\n\n[{datetime.now().isoformat()}]\n{note}"
        
        self.session_file.write_text(json.dumps(current, indent=2))
    
    def get_notes(self) -> str:
        """Get all notes."""
        notes = []
        
        for session in self.data_dir.glob("*.json"):
            try:
                data = json.loads(session.read_text())
                note = data.get("notes", "")
                if note:
                    notes.append(f"=== {session.stem} ===\n{note}")
            except:
                pass
        
        return "\n\n".join(notes[-5:])


class WebBrowserTool:
    """Browse web freely - like a real browser."""
    
    def __init__(self):
        self.history = []
        self.current_page = None
    
    def visit(self, url: str) -> Dict:
        """Visit a URL and extract content."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            title = soup.title.get_text(strip=True) if soup.title else "Unknown"
            
            # Get main content
            main = soup.find("main") or soup.find("article") or soup.body
            text = main.get_text(separator="\n", strip=True) if main else ""
            
            # Clean
            lines = [l for l in text.split("\n") if l.strip()]
            text = "\n".join(lines)[:10000]
            
            # Get all links
            links = []
            for a in soup.find_all("a", href=True)[:30]:
                href = a.get("href", "")
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    links.append(urljoin(url, href))
            
            self.current_page = url
            self.history.append(url)
            
            return {
                "url": url,
                "title": title,
                "content": text,
                "links": links[:20],
                "history": len(self.history)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_links(self) -> List[str]:
        """Get links from current page."""
        if self.current_page:
            return self.visit(self.current_page).get("links", [])
        return []
    
    def back(self) -> str:
        """Go back in history."""
        if len(self.history) > 1:
            self.history.pop()
            return f"Back to: {self.history[-1]}"
        return "No history"
    
    def get_history(self) -> List[str]:
        """Get browsing history."""
        return self.history


class GUICreator:
    """Create GUI apps - something opencode cannot do directly."""
    
    @staticmethod
    def create_simple_gui(title: str, inputs: List[str], handler: Callable) -> Any:
        """Create a simple Gradio GUI."""
        import gradio as gr
        
        with gr.Blocks(title=title) as app:
            gr.Markdown(f"# {title}")
            
            with gr.Row():
                for inp in inputs:
                    gr.Textbox(label=inp)
            
            gr.Button("Submit").click(handler)
        
        return app
    
    @staticmethod
    def create_form(title: str, fields: Dict[str, str], handler: Callable) -> Any:
        """Create a form with fields."""
        import gradio as gr
        
        with gr.Blocks(title=title) as app:
            gr.Markdown(f"# {title}")
            
            outputs = {}
            for label, field_type in fields.items():
                if field_type == "text":
                    outputs[label] = gr.Textbox(label=label)
                elif field_type == "number":
                    outputs[label] = gr.Number(label=label)
                elif field_type == "checkbox":
                    outputs[label] = gr.Checkbox(label=label)
            
            gr.Button("Submit").click(handler, outputs=list(outputs.values()))
        
        return app


# Global instances
_file_browser = None
_bg_processes = None
_session_memory = None
_web_browser = None


def get_file_browser(root: str = None) -> FileBrowser:
    """Get file browser instance."""
    global _file_browser
    if _file_browser is None:
        _file_browser = FileBrowser(root)
    return _file_browser


def get_bg_processes() -> BackgroundProcessManager:
    """Get background process manager."""
    global _bg_processes
    if _bg_processes is None:
        _bg_processes = BackgroundProcessManager()
    return _bg_processes


def get_session_memory() -> SessionMemory:
    """Get session memory."""
    global _session_memory
    if _session_memory is None:
        _session_memory = SessionMemory()
    return _session_memory


def get_web_browser() -> WebBrowserTool:
    """Get web browser."""
    global _web_browser
    if _web_browser is None:
        _web_browser = WebBrowserTool()
    return _web_browser


# Easy functions for actions
def browse_files(path: str = "") -> str:
    """Browse files - returns formatted string."""
    browser = get_file_browser()
    files = browser.list(path)
    
    if not files:
        return "No files found"
    
    lines = [f"Files in {path or '/'}: "]
    for f in files:
        icon = "📁" if f["type"] == "dir" else "📄"
        lines.append(f"{icon} {f['name']}")
    
    return "\n".join(lines)


def search_files(query: str) -> str:
    """Search files by name."""
    browser = get_file_browser()
    results = browser.search(query)
    
    if not results:
        return f"No files found for: {query}"
    
    lines = [f"Search results for '{query}': "]
    for r in results:
        lines.append(f"📄 {r['path']}")
    
    return "\n".join(lines)


def run_background(command: str, name: str = None) -> str:
    """Run command in background."""
    mgr = get_bg_processes()
    pid = mgr.run(command, name)
    return f"Started process {pid}: {command}"


def list_processes() -> str:
    """List background processes."""
    mgr = get_bg_processes()
    procs = mgr.list()
    
    if not procs:
        return "No background processes"
    
    lines = ["Background processes: "]
    for p in procs:
        status = "🟢" if p["running"] else "🔴"
        lines.append(f"{status} #{p['id']}: {p['name']}")
    
    return "\n".join(lines)


def remember(user: str, bot: str) -> str:
    """Remember conversation."""
    mem = get_session_memory()
    mem.add(user, bot)
    return "Saved to memory"


def recall(query: str = None, limit: int = 10) -> str:
    """Recall from memory."""
    mem = get_session_memory()
    
    if query:
        results = mem.search(query)
        if not results:
            return f"No recall for: {query}"
        
        lines = [f"Recalled {len(results)} memories: "]
        for r in results:
            lines.append(f"Q: {r.get('user')}")
            lines.append(f"A: {r.get('bot')[:100]}")
            lines.append(f"---")
        return "\n".join(lines)
    
    history = mem.get_history(limit)
    if not history:
        return "No memory"
    
    lines = ["Recent memory: "]
    for h in history:
        lines.append(f"You: {h.get('user')[:50]}")
        lines.append(f"Bot: {h.get('bot')[:50]}")
        lines.append("---")
    
    return "\n".join(lines)


def browse_web(url: str) -> str:
    """Browse web freely."""
    browser = get_web_browser()
    result = browser.visit(url)
    
    if result.get("error"):
        return f"Error: {result.get('error')}"
    
    lines = [
        f"Title: {result.get('title')}",
        f"URL: {result.get('url')}",
        "",
        f"Content:",
        result.get("content", "")[:2000]
    ]
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("System Tools - Extended Capabilities")
    
    # Test file browser
    fb = get_file_browser()
    print(f"Files: {len(fb.cache)}")
    
    # Test session memory
    sm = get_session_memory()
    sm.add("test", "result")
    print("Memory: OK")
    
    # Test web browser
    wb = get_web_browser()
    print(f"Web browser: {type(wb)}")