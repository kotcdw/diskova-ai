"""
Action (Execution) Layer
=========================
Tool calling - interacts with external services.
"""

import subprocess
import json
import requests
from typing import Dict, List, Optional, Callable
from pathlib import Path


class ToolRegistry:
    """Register and manage tools."""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register built-in tools."""
        
        # Import internet tools for better search
        try:
            from internet_tools import search_web as internet_search, get_weather, get_stock_price
            self.tools["search"] = internet_search
            self.tools["weather"] = get_weather
            self.tools["stock"] = get_stock_price
        except ImportError:
            pass
        
        # Add productivity tools
        try:
            from productivity import (
                add_reminder, list_reminders, complete_reminder,
                add_event, list_events,
                add_note, get_note, search_notes
            )
            self.tools["reminder"] = add_reminder
            self.tools["reminders"] = list_reminders
            self.tools["complete"] = complete_reminder
            self.tools["event"] = add_event
            self.tools["events"] = list_events
            self.tools["note"] = add_note
            self.tools["get_note"] = get_note
            self.tools["search_notes"] = search_notes
        except ImportError:
            pass
        
        # Fallback search if import fails
        if "search" not in self.tools:
            def search_web(query: str) -> str:
                """Search the web."""
                try:
                    response = requests.get(
                        "https://duckduckgo.com/",
                        params={"q": query, "format": "json"},
                        timeout=10
                    )
                    results = response.json().get("Results", [])
                    return "\n".join([r.get("text", "") for r in results[:5]]) or "No results"
                except Exception as e:
                    return f"Search error: {e}"
            self.tools["search"] = search_web
        
        def run_code(code: str, language: str = "python") -> str:
            """Execute code."""
            import tempfile
            import shutil
            
            runtimes = {
                "python": shutil.which("python") or "python",
                "javascript": shutil.which("node") or "node",
            }
            
            if language not in runtimes:
                return f"Unsupported: {language}"
            
            try:
                with tempfile.NamedTemporaryFile(mode="w", suffix=f".{language}", delete=False) as f:
                    f.write(code)
                    f.flush()
                    result = subprocess.run(
                        [runtimes[language], f.name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    Path(f.name).unlink()
                    return result.stdout or result.stderr
            except Exception as e:
                return f"Error: {e}"
        
        def get_time() -> str:
            """Get current time."""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        def calculate(expr: str) -> str:
            """Calculate expression."""
            try:
                result = eval(expr, {"__builtins__": {}}, {})
                return str(result)
            except:
                return "Invalid expression"
        
        def file_ops(operation: str, path: str, content: str = "") -> str:
            """File operations."""
            p = Path(path)
            
            op_map = {
                "read": lambda: p.read_text() if p.exists() else "File not found",
                "exists": lambda: str(p.exists()),
                "size": lambda: str(p.stat().st_size) if p.exists() else "0",
            }
            
            return op_map.get(operation, lambda: "Unknown op")()
        
        # Register tools
        self.tools["search_web"] = search_web
        self.tools["run_code"] = run_code
        self.tools["get_time"] = get_time
        self.tools["calculate"] = calculate
        self.tools["file_ops"] = file_ops
    
    def register(self, name: str, func: Callable):
        """Register custom tool."""
        self.tools[name] = func
    
    def call(self, tool_name: str, **kwargs) -> str:
        """Call a tool."""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return f"Tool error: {e}"
    
    def list_tools(self) -> List[str]:
        """List available tools."""
        return list(self.tools.keys())


class APIClient:
    """External API client."""
    
    def __init__(self):
        self.session = requests.Session()
    
    def call(self, method: str, url: str, **kwargs) -> Dict:
        """Make API call."""
        try:
            response = self.session.request(method, url, **kwargs)
            return {
                "success": response.status_code < 400,
                "status": response.status_code,
                "data": response.json() if response.ok else None,
                "error": response.text if not response.ok else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class ActionEngine:
    """Action execution engine."""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.api_client = APIClient()
    
    def execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute multiple tool calls."""
        results = []
        
        for call in tool_calls:
            name = call.get("name")
            args = call.get("args", {})
            
            result = self.registry.call(name, **args)
            results.append({
                "tool": name,
                "result": result
            })
        
        return results
    
    def determine_tool_use(self, intent: str, query: str) -> List[Dict]:
        """Determine which tools to use based on intent."""
        tool_map = {
            "search": [{"name": "search_web", "args": {"query": query}}],
            "code": [{"name": "run_code", "args": {"code": query}}],
            "calculate": [{"name": "calculate", "args": {"expr": query}}],
        }
        
        return tool_map.get(intent, [])


def get_action_engine() -> ActionEngine:
    """Get action engine."""
    return ActionEngine()


if __name__ == "__main__":
    print("Action (Execution) Layer")
    engine = get_action_engine()
    tools = engine.registry.list_tools()
    print(f"Tools: {tools}")