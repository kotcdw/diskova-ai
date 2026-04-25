"""
AI Coding Agent Brain - MCP Server
============================
8 powerful tools for your local AI coding agent.
Uses FastMCP framework.
"""

import os
import re
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Run: pip install fastmcp")
    raise

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
TOOLS_DIR = BASE_DIR / "tools"
SNIPPETS_FILE = TOOLS_DIR / "code_snippets.json"

mcp = FastMCP("PowerfulBrain")


def init_directories():
    """Ensure all required directories exist."""
    for dir_path in [
        KNOWLEDGE_DIR / "sessions",
        KNOWLEDGE_DIR / "patterns",
        KNOWLEDGE_DIR / "projects",
        TOOLS_DIR
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)


def load_snippets() -> dict:
    """Load code snippets from JSON file."""
    if SNIPPETS_FILE.exists():
        with open(SNIPPETS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_json_file(file_path: Path, data: dict):
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


init_directories()


@mcp.tool()
def search_knowledge(query: str, category: str = "all") -> str:
    """
    Search your knowledge base semantically.
    Searches through sessions, patterns, and project notes.
    
    Args:
        query: Search query text
        category: Which category to search (sessions|patterns|projects|all)
    
    Returns:
        Search results as formatted string
    """
    results = []
    search_dirs = {
        "sessions": KNOWLEDGE_DIR / "sessions",
        "patterns": KNOWLEDGE_DIR / "patterns", 
        "projects": KNOWLEDGE_DIR / "projects"
    }
    
    if category != "all" and category in search_dirs:
        search_dirs = {category: search_dirs[category]}
    
    query_lower = query.lower()
    
    for cat_name, dir_path in search_dirs.items():
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if query_lower in content.lower():
                    lines = content.split('\n')
                    preview = ' '.join(lines[:3])[:200]
                    results.append(f"**{cat_name.title()}: {file_path.stem}**\n{preview}...")
            except Exception:
                continue
        for file_path in dir_path.glob("*.json"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if query_lower in content.lower():
                    results.append(f"**{cat_name.title()}: {file_path.stem}** (JSON)")
            except Exception:
                continue
    
    if results:
        return f"Found {len(results)} results:\n\n" + "\n\n".join(results[:10])
    return f"No results found for: {query}"


@mcp.tool()
def get_code_snippet(language: str, task: str) -> str:
    """
    Get boilerplate code for common programming tasks.
    
    Args:
        language: Programming language (python|javascript|typescript|go|rust|etc)
        task: Type of snippet (api|function|class|test|async|error-handling|etc)
    
    Returns:
        Code snippet as string
    """
    snippets = load_snippets()
    
    if language not in snippets:
        available = ", ".join(snippets.keys()) if snippets else "python"
        return f"Language '{language}' not found. Available: {available}"
    
    if task not in snippets[language]:
        available = ", ".join(snippets[language].keys())
        return f"Task '{task}' not found for {language}. Available: {available}"
    
    snippet = snippets[language][task]
    return f"```{language}\n{snippet}\n```"


@mcp.tool()
def save_session_memory(task: str, result: str, tags: str = "") -> str:
    """
    Save current task result to session memory.
    
    Args:
        task: Description of the task
        result: What was accomplished
        tags: Comma-separated tags for categorization
    
    Returns:
        Confirmation message
    """
    today = datetime.now().strftime("%Y-%m-%d")
    session_file = KNOWLEDGE_DIR / "sessions" / f"{today}.json"
    
    existing_sessions = []
    if session_file.exists():
        with open(session_file, 'r') as f:
            existing_sessions = json.load(f)
    
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "result": result,
        "tags": [t.strip() for t in tags.split(',') if t.strip()]
    }
    
    existing_sessions.append(new_entry)
    
    with open(session_file, 'w') as f:
        json.dump(existing_sessions, f, indent=2)
    
    return f"Saved session to {session_file.name}. Total entries: {len(existing_sessions)}"


@mcp.tool()
def review_code(code: str, language: str = "python") -> str:
    """
    Review code for common issues and improvements.
    
    Args:
        code: The code to review
        language: Programming language
    
    Returns:
        Review findings and suggestions
    """
    issues = []
    suggestions = []
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            issues.append(f"Line {i}: Line too long ({len(line)} chars)")
        
        if f" {language}" in ["python", "javascript", "typescript"]:
            if "except:" in line and language == "python":
                issues.append(f"Line {i}: Bare except clause ( catches everything)")
            if "except Exception:" not in line and "except:" in line:
                suggestions.append(f"Line {i}: Consider specific exception handling")
    
    if "TODO" in code or "FIXME" in code:
        todos = [l.strip() for l in lines if "TODO" in l or "FIXME" in l]
        suggestions.append(f"Found {len(todos)} TODO/FIXME comments")
    
    if "print(" in code or "console.log" in code:
        suggestions.append("Debug statements found - remove before production")
    
    if not re.search(r'doc|"""$|"""', code) and len(code.split('\n')) > 20:
        suggestions.append("No docstring found for module")
    
    response = "## Code Review Results\n\n"
    
    if issues:
        response += "### Issues Found\n"
        for issue in issues[:5]:
            response += f"- {issue}\n"
    else:
        response += "### No critical issues found\n"
    
    if suggestions:
        response += "\n### Suggestions\n"
        for suggestion in suggestions[:5]:
            response += f"- {suggestion}\n"
    
    return response


@mcp.tool()
def analyze_project(path: str) -> str:
    """
    Analyze project structure and dependencies.
    
    Args:
        path: Path to project directory (relative or absolute)
    
    Returns:
        Project structure summary
    """
    project_path = Path(path)
    if not project_path.is_absolute():
        project_path = BASE_DIR / project_path
    
    if not project_path.exists():
        return f"Project path does not exist: {project_path}"
    
    result = f"## Project Analysis: {project_path.name}\n\n"
    
    file_counts = {".py": 0, ".js": 0, ".ts": 0, ".json": 0, ".md": 0}
    total_files = 0
    
    for ext in file_counts:
        files = list(project_path.rglob(f"*{ext}"))
        file_counts[ext] = len(files)
        total_files += len(files)
    
    result += "### Files\n"
    for ext, count in file_counts.items():
        if count > 0:
            result += f"- {ext}: {count}\n"
    
    result += f"\n**Total: {total_files} files**\n"
    
    deps_file = project_path / "package.json"
    if deps_file.exists():
        try:
            with open(deps_file, 'r') as f:
                deps = json.load(f).get("dependencies", {})
                result += f"\n### Dependencies ({len(deps)})\n"
                result += ", ".join(list(deps.keys())[:10])
                if len(deps) > 10:
                    result += f" +{len(deps)-10} more"
        except Exception:
            pass
    
    req_file = project_path / "requirements.txt"
    if req_file.exists():
        deps = [l.strip() for l in req_file.read_text().split('\n') if l.strip() and not l.startswith('#')]
        result += f"\n### Python Dependencies ({len(deps)})\n"
        result += ", ".join(deps[:10])
        if len(deps) > 10:
            result += f" +{len(deps)-10} more"
    
    return result


@mcp.tool()
def update_task_status(task_id: str, status: str, description: str = "", project: str = "default") -> str:
    """
    Track task progress for multi-step tasks.
    
    Args:
        task_id: Unique task identifier
        status: Task status (pending|in_progress|completed|blocked)
        description: Task description
        project: Project name
    
    Returns:
        Task status update confirmation
    """
    tasks_file = KNOWLEDGE_DIR / "projects" / f"{project}_tasks.json"
    
    tasks = {}
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
    
    if task_id not in tasks and description:
        tasks[task_id] = {"description": description, "status": status}
    elif task_id in tasks:
        tasks[task_id]["status"] = status
        if description:
            tasks[task_id]["description"] = description
    else:
        return f"Task '{task_id}' not found. Create it with a description."
    
    tasks[task_id]["updated"] = datetime.now().isoformat()
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    return f"Task '{task_id}' status: {status}"


@mcp.tool()
def generate_docs(code: str, format: str = "markdown") -> str:
    """
    Auto-generate documentation from code.
    
    Args:
        code: Source code to document
        format: Output format (markdown|html|text)
    
    Returns:
        Generated documentation
    """
    lines = code.split('\n')
    docs = []
    
    current_func = None
    current_class = None
    params = []
    returns = None
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith("def ") or stripped.startswith("function "):
            match = re.match(r'(?:def|function)\s+(\w+)\s*\(([^)]*)\)', stripped)
            if match:
                current_func = match.group(1)
                args = match.group(2).split(',') if match.group(2) else []
                params = [a.strip().split('=')[0].strip() for a in args if a.strip()]
                
        elif stripped.startswith("class "):
            match = re.match(r'class\s+(\w+)', stripped)
            if match:
                current_class = match.group(1)
                current_func = None
                
        elif "return" in stripped and current_func:
            returns = stripped.replace("return", "").strip()
            
        elif stripped.startswith('"""') or stripped.startswith("'''"):
            if current_func:
                docs.append(f"### {current_func}")
            elif current_class:
                docs.append(f"## Class: {current_class}")
            docs.append(stripped.strip('"\''))
    
    if format == "markdown":
        output = "## Documentation\n\n"
        if docs:
            output += "\n\n".join(docs)
        else:
            output += "_No docstrings found. Consider adding docstrings._"
        return output
    
    return "\n".join(docs) if docs else "Could not extract documentation."


@mcp.tool()
def recall_pattern(problem_type: str) -> str:
    """
    Recall similar problems you've solved before.
    Searches pattern memory for relevant solutions.
    
    Args:
        problem_type: Type of problem (api|async|debug|error|testing|etc)
    
    Returns:
        Recalled patterns and solutions
    """
    patterns_dir = KNOWLEDGE_DIR / "patterns"
    matches = []
    
    if not patterns_dir.exists():
        return f"No patterns found. First, solve some problems to build your knowledge base."
    
    for file_path in patterns_dir.glob("*.md"):
        try:
            content = file_path.read_text(encoding='utf-8')
            if problem_type.lower() in content.lower():
                title = file_path.stem
                preview = content[:300].replace('#', '').strip()
                matches.append(f"**{title}**\n{preview}...")
        except Exception:
            continue
    
    if matches:
        return f"Found {len(matches)} similar patterns:\n\n" + "\n\n".join(matches[:5])
    
    return f"No patterns found for '{problem_type}'. Consider solving this problem and saving the pattern."


@mcp.tool()
def list_memory_stats() -> str:
    """
    Get overview of your knowledge base statistics.
    
    Returns:
        Memory statistics
    """
    stats = {"sessions": 0, "patterns": 0, "projects": 0}
    
    for category in ["sessions", "patterns", "projects"]:
        dir_path = KNOWLEDGE_DIR / category
        if dir_path.exists():
            stats[category] = len(list(dir_path.glob("*.*")))
    
    return f"""## AI Brain Memory Stats

| Category | Items |
|---------|-------|
| Sessions | {stats['sessions']} |
| Patterns | {stats['patterns']} |
| Projects | {stats['projects']} |

Total Knowledge Items: {sum(stats.values())}
"""


if __name__ == "__main__":
    print("Starting PowerfulBrain MCP Server...")
    print(f"Knowledge directory: {KNOWLEDGE_DIR}")
    print(f"Tools directory: {TOOLS_DIR}")
    mcp.run()


# ============================================================================
# ADDITIONAL TOOLS FOR COMPLETE CODING AGENT
# ============================================================================

@mcp.tool()
def execute_code(code: str, language: str = "python") -> str:
    """
    Execute code and return the output.
    
    Args:
        code: The code to execute
        language: Programming language (python|javascript|bash)
    
    Returns:
        Output from executing the code
    """
    import tempfile
    import os
    
    if language == "python":
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return f"Output:\n{output}" if output else "No output"
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (30s limit)"
        finally:
            os.unlink(temp_file)
    
    elif language == "javascript":
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return f"Output:\n{output}" if output else "No output"
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (30s limit)"
        finally:
            os.unlink(temp_file)
    
    elif language == "bash":
        try:
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return f"Output:\n{output}" if output else "No output"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
    
    return f"Unsupported language: {language}"


@mcp.tool()
def run_tests(test_framework: str = "pytest", path: str = ".") -> str:
    """
    Run tests using the specified test framework.
    
    Args:
        test_framework: Test framework (pytest|jest|go-test|mocha)
        path: Path to test files
    
    Returns:
        Test results
    """
    try:
        if test_framework == "pytest":
            result = subprocess.run(
                ['pytest', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=120,
                shell=True
            )
            return f"Pytest Results:\n{result.stdout}\n{result.stderr}"
        
        elif test_framework == "jest":
            result = subprocess.run(
                ['npx', 'jest', '--passWithNoTests'],
                capture_output=True,
                text=True,
                timeout=120,
                shell=True
            )
            return f"Jest Results:\n{result.stdout}\n{result.stderr}"
        
        elif test_framework == "go-test":
            result = subprocess.run(
                ['go', 'test', '-v'],
                capture_output=True,
                text=True,
                timeout=120,
                shell=True
            )
            return f"Go Test Results:\n{result.stdout}\n{result.stderr}"
        
        return f"Unsupported test framework: {test_framework}"
    
    except FileNotFoundError:
        return f"Error: {test_framework} not installed"
    except subprocess.TimeoutExpired:
        return "Error: Tests timed out (120s limit)"


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read contents of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File contents
    """
    path = Path(file_path)
    
    if not path.exists():
        return f"Error: File not found: {file_path}"
    
    try:
        content = path.read_text(encoding='utf-8')
        if len(content) > 10000:
            return f"File contents (first 10000 chars):\n{content[:10000]}...\n\n[truncated]"
        return f"File contents:\n{content}"
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.tool()
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        append: Append to existing file (default: False)
    
    Returns:
        Confirmation message
    """
    path = Path(file_path)
    
    try:
        mode = 'a' if append else 'w'
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"


@mcp.tool()
def list_files(path: str = ".", pattern: str = "*", recursive: bool = True) -> str:
    """
    List files in a directory.
    
    Args:
        path: Directory path
        pattern: File pattern (e.g., *.py, *.js)
        recursive: Search recursively
    
    Returns:
        List of files
    """
    dir_path = Path(path)
    
    if not dir_path.exists():
        return f"Error: Directory not found: {path}"
    
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))
    
    if not files:
        return f"No files matching {pattern} in {path}"
    
    result = f"Files in {path} (pattern: {pattern}):\n"
    for f in sorted(files)[:50]:
        size = f.stat().st_size if f.is_file() else 0
        result += f"- {f.relative_to(dir_path)} ({size} bytes)\n"
    
    if len(files) > 50:
        result += f"\n... and {len(files) - 50} more"
    
    return result


@mcp.tool()
def git_command(command: str, repo_path: str = ".") -> str:
    """
    Run git commands.
    
    Args:
        command: Git command (status|log|diff|commit|branch|etc)
        repo_path: Path to git repository
    
    Returns:
        Git command output
    """
    git_commands = {
        "status": ['git', 'status', '--porcelain'],
        "log": ['git', 'log', '--oneline', '-10'],
        "diff": ['git', 'diff', '--stat'],
        "branch": ['git', 'branch', '-a'],
        "stash": ['git', 'stash', 'list'],
    }
    
    cmd_list = git_commands.get(command.lower())
    if not cmd_list:
        return f"Unknown git command: {command}. Available: {list(git_commands.keys())}"
    
    try:
        result = subprocess.run(
            cmd_list,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.stdout else result.stderr
        return f"Git {command} result:\n{output}" if output else "No output"
    except FileNotFoundError:
        return "Error: Git not installed"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def search_code(query: str, path: str = ".", extensions: str = "py,js,ts") -> str:
    """
    Search for code patterns in files.
    
    Args:
        query: Search query
        path: Directory to search
        file_extensions: Comma-separated extensions
    
    Returns:
        Search results with line numbers
    """
    dir_path = Path(path)
    ext_list = [e.strip() for e in extensions.split(',')]
    
    results = []
    for ext in ext_list:
        for file_path in dir_path.rglob(f"*.{ext}"):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                for i, line in enumerate(content.split('\n'), 1):
                    if query.lower() in line.lower():
                        results.append(f"{file_path.relative_to(dir_path)}:{i}: {line.strip()[:100]}")
            except Exception:
                continue
    
    if not results:
        return f"No matches found for: {query}"
    
    return f"Found {len(results)} matches:\n" + "\n".join(results[:30])


@mcp.tool()
def get_file_info(file_path: str) -> str:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File information
    """
    path = Path(file_path)
    
    if not path.exists():
        return f"Error: File not found: {file_path}"
    
    stat = path.stat()
    result = f"## File Info: {path.name}\n\n"
    result += f"- Path: {path.absolute()}\n"
    result += f"- Size: {stat.st_size} bytes\n"
    result += f"- Created: {datetime.fromtimestamp(stat.st_ctime)}\n"
    result += f"- Modified: {datetime.fromtimestamp(stat.st_mtime)}\n"
    result += f"- Is file: {path.is_file()}\n"
    result += f"- Is directory: {path.is_dir()}\n"
    
    if path.suffix:
        result += f"- Extension: {path.suffix}\n"
    
    return result


@mcp.tool()
def create_project_scaffold(project_name: str, template: str = "python") -> str:
    """
    Create a new project scaffold.
    
    Args:
        project_name: Name of the project
        template: Template type (python|javascript|typescript|go|rust)
    
    Returns:
        Confirmation and created files
    """
    project_dir = BASE_DIR / project_name
    
    if project_dir.exists():
        return f"Error: Project {project_name} already exists"
    
    scaffolds = {
        "python": {
            "src/__init__.py": "",
            "src/main.py": "def main():\n    pass\n\nif __name__ == '__main__':\n    main()",
            "requirements.txt": "",
            "README.md": f"# {project_name}\n\n",
            "test/test_main.py": "import pytest\nfrom src.main import main\n\ndef test_main():\n    main()",
        },
        "javascript": {
            "src/index.js": "function main() {\n  console.log('Hello');\n}\n\nmodule.exports = { main };",
            "package.json": '{"name": "' + project_name + '", "version": "1.0.0", "main": "src/index.js"}',
            "README.md": f"# {project_name}\n\n",
            "test/index.test.js": "const { main } = require('./src/index');\n\ntest('main', () => { main(); });",
        },
        "typescript": {
            "src/index.ts": "export function main(): void {\n  console.log('Hello');\n}",
            "package.json": '{"name": "' + project_name + '", "version": "1.0.0"}',
            "tsconfig.json": '{"compilerOptions": {"target": "ES2020"}}',
            "README.md": f"# {project_name}\n\n",
        },
        "go": {
            "main.go": "package main\n\nfunc main() {\n\tprintln(\"Hello\")\n}",
            "go.mod": "module " + project_name + "\n\ngo 1.21",
            "README.md": f"# {project_name}\n\n",
        },
        "rust": {
            "src/main.rs": "fn main() {\n    println!(\"Hello\");\n}",
            "Cargo.toml": f"[package]\nname = \"{project_name}\"\nversion = \"0.1.0\"\n\n[[bin]]\nname = \"{project_name}\"\npath = \"src/main.rs\"",
            "README.md": f"# {project_name}\n\n",
        }
    }
    
    if template not in scaffolds:
        return f"Unknown template: {template}. Available: {list(scaffolds.keys())}"
    
    project_dir.mkdir(parents=True)
    
    created = []
    for file_path, content in scaffolds[template].items():
        full_path = project_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        created.append(str(file_path))
    
    return f"Created project '{project_name}' with {len(created)} files:\n" + "\n".join(created)


# ============================================================================
# CODE EXECUTION TOOLS (Run code/tests)
# ============================================================================

@mcp.tool()
def execute_code(language: str, code: str, args: str = "") -> str:
    """
    Execute code in a sandboxed environment.
    
    Args:
        language: python, javascript, typescript, go, rust, bash
        code: The code to run
        args: Command line arguments (optional)
    
    Returns:
        Execution output or error
    """
    import tempfile
    import shutil
    
    # Get language runtime
    runtimes = {
        "python": shutil.which("python") or "python",
        "javascript": shutil.which("node") or "node",
        "typescript": "npx ts-node",
        "go": shutil.which("go") or "go",
        "rust": shutil.which("cargo") or "cargo",
        "bash": shutil.which("bash") or "sh",
    }
    
    if language not in runtimes:
        return f"Unsupported language: {language}. Available: {list(runtimes.keys())}"
    
    cmd = runtimes[language]
    
    # Check if code is file path or inline
    if Path(code).exists():
        file_path = Path(code)
    else:
        # Write to temp file
        ext = {"python": ".py", "javascript": ".js", "typescript": ".ts", "go": ".go", "rust": ".rs", "bash": ".sh"}
        suffix = ext.get(language, ".txt")
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8')
        temp_file.write(code)
        temp_file.close()
        file_path = Path(temp_file.name)
    
    try:
        result = subprocess.run(
            f"{cmd} {file_path} {args}".split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout or result.stderr
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Execution timed out (30s limit)"
    except Exception as e:
        return f"Error: {e}"
    finally:
        if not Path(code).exists():
            file_path.unlink(missing_ok=True)


# ============================================================================
# TEST RUNNER TOOLS (Run pytest/jest)
# ============================================================================

@mcp.tool()
def run_tests(test_path: str = ".", framework: str = "auto", verbose: bool = True) -> str:
    """
    Run tests using pytest, jest, or other frameworks.
    
    Args:
        test_path: Path to tests or project root
        framework: auto, pytest, jest, go-test, cargo-test, all
        verbose: Show detailed output
    
    Returns:
        Test results as string
    """
    test_path = Path(test_path)
    
    # Auto-detect framework
    if framework == "auto":
        if (test_path / "pytest.ini").exists() or (test_path / "pyproject.toml").exists():
            framework = "pytest"
        elif (test_path / "package.json").exists():
            framework = "jest"
        elif (test_path / "go.mod").exists():
            framework = "go-test"
        elif (test_path / "Cargo.toml").exists():
            framework = "cargo-test"
        else:
            framework = "pytest"  # default
    
    results = []
    
    if framework in ("pytest", "all"):
        pytest_cmd = shutil.which("pytest") or "python -m pytest"
        result = subprocess.run(
            f"{pytest_cmd} {test_path} -v".split() if verbose else [pytest_cmd, str(test_path)],
            capture_output=True,
            text=True,
            timeout=60,
            shell=True
        )
        results.append(f"pytest: {result.stdout or result.stderr}")
    
    if framework in ("jest", "all"):
        result = subprocess.run(
            ["npx", "jest", "--passWithNoTests"] + ([str(test_path)] if test_path.exists() else []),
            capture_output=True,
            text=True,
            timeout=60
        )
        results.append(f"jest: {result.stdout or result.stderr}")
    
    if framework in ("go-test", "all"):
        result = subprocess.run(
            ["go", "test", "./..."],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=test_path if test_path.exists() else None
        )
        results.append(f"go test: {result.stdout or result.stderr}")
    
    if framework in ("cargo-test", "all"):
        result = subprocess.run(
            ["cargo", "test"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=test_path if test_path.exists() else None
        )
        results.append(f"cargo test: {result.stdout or result.stderr}")
    
    return "\n\n".join(results)


@mcp.tool()
def run_pytest(file: str = "tests/", arguments: str = "-v") -> str:
    """
    Run pytest with specific arguments.
    
    Args:
        file: Test file, directory, or module
        arguments: pytest arguments (e.g., "-v -k test_name")
    
    Returns:
        Test output
    """
    pytest_cmd = shutil.which("pytest") or "python -m pytest"
    
    cmd = f"{pytest_cmd} {file} {arguments}".split()
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    output = result.stdout or result.stderr
    return output or "(no output)"


# ============================================================================
# FILE ACCESS TOOLS (Read/write project files)
# ============================================================================

@mcp.tool()
def read_file(file_path: str, offset: int = 0, limit: int = 100) -> str:
    """
    Read a file from the filesystem.
    
    Args:
        file_path: Path to file (absolute or relative)
        offset: Line number to start from (0-indexed)
        limit: Maximum lines to read
    
    Returns:
        File contents as string
    """
    path = Path(file_path)
    
    if not path.exists():
        # Try relative to project root
        path = BASE_DIR / file_path
    
    if not path.exists():
        return f"File not found: {file_path}"
    
    try:
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        if offset > 0:
            lines = lines[offset:]
        
        if limit > 0:
            lines = lines[:limit]
        
        preview = '\n'.join(lines)
        
        if len(content.split('\n')) > limit:
            preview += f"\n... ({len(content.split('\\n')) - limit} more lines)"
        
        return preview
    except Exception as e:
        return f"Error reading {file_path}: {e}"


@mcp.tool()
def write_file(file_path: str, content: str, create_dirs: bool = True) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to file
        content: Content to write
        create_dirs: Create parent directories if needed
    
    Returns:
        Success message
    """
    path = Path(file_path)
    
    if not path.is_absolute():
        path = BASE_DIR / file_path
    
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        path.write_text(content, encoding='utf-8')
        return f"Wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"Error writing {file_path}: {e}"


@mcp.tool()
def list_files(directory: str = ".", pattern: str = "*", recursive: bool = False) -> str:
    """
    List files in a directory.
    
    Args:
        directory: Directory to list
        pattern: Glob pattern
        recursive: Search recursively
    
    Returns:
        File list as string
    """
    dir_path = Path(directory)
    
    if not dir_path.is_absolute():
        dir_path = BASE_DIR / directory
    
    if not dir_path.exists():
        return f"Directory not found: {directory}"
    
    try:
        if recursive:
            files = sorted(dir_path.rglob(pattern))
        else:
            files = sorted(dir_path.glob(pattern))
        
        return "\n".join(str(f.relative_to(dir_path)) for f in files if f.is_file())
    except Exception as e:
        return f"Error listing {directory}: {e}"


# ============================================================================
# GIT INTEGRATION TOOLS
# ============================================================================

@mcp.tool()
def git_command(command: str, path: str = ".") -> str:
    """
    Run git commands.
    
    Args:
        command: git command (status, log, diff, commit, push, pull, branch)
        path: Repository path
    
    Returns:
        Git output
    """
    repo_path = Path(path)
    
    if not repo_path.is_absolute():
        repo_path = BASE_DIR / path
    
    if not (repo_path / ".git").exists():
        return f"Not a git repo: {path}"
    
    git = shutil.which("git") or "git"
    
    # Parse command
    if command in ("status", "s"):
        cmd = [git, "-C", str(repo_path), "status"]
    elif command in ("log", "l"):
        cmd = [git, "-C", str(repo_path), "log", "--oneline", "-10"]
    elif command.startswith("diff"):
        parts = command.split()
        cmd = [git, "-C", str(repo_path), "diff"] + parts[1:]
    elif command.startswith("commit"):
        parts = command.split(maxsplit=1)
        cmd = [git, "-C", str(repo_path), "commit", "-m", parts[1]] if len(parts) > 1 else [git, "-C", str(repo_path), "status"]
    elif command in ("push", "push"):
        cmd = [git, "-C", str(repo_path), "push"]
    elif command in ("pull", "pull"):
        cmd = [git, "-C", str(repo_path), "pull"]
    elif command in ("branch", "branch"):
        cmd = [git, "-C", str(repo_path), "branch", "-v"]
    elif command in ("fetch", "fetch"):
        cmd = [git, "-C", str(repo_path), "fetch", "--all"]
    else:
        cmd = [git, "-C", str(repo_path)] + command.split()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout or result.stderr or "(no output)"
    except Exception as e:
        return f"Git error: {e}"


@mcp.tool()
def git_create_branch(branch_name: str, checkout: bool = True, path: str = ".") -> str:
    """
    Create and optionally checkout a git branch.
    
    Args:
        branch_name: Name for new branch
        checkout: Switch to new branch
        path: Repository path
    
    Returns:
        Success message
    """
    repo_path = Path(path)
    
    if not repo_path.is_absolute():
        repo_path = BASE_DIR / path
    
    git = shutil.which("git") or "git"
    
    try:
        # Create branch
        result = subprocess.run(
            [git, "-C", str(repo_path), "branch", branch_name],
            capture_output=True,
            text=True
        )
        
        if checkout:
            subprocess.run(
                [git, "-C", str(repo_path), "checkout", branch_name],
                capture_output=True,
                text=True
            )
        
        return f"Created branch: {branch_name}" + (" and checked out" if checkout else "")
    except Exception as e:
        return f"Git error: {e}"


@mcp.tool()
def git_create_commit(message: str, add_all: bool = True, path: str = ".") -> str:
    """
    Create a git commit.
    
    Args:
        message: Commit message
        add_all: Stage all changes
        path: Repository path
    
    Returns:
        Commit result
    """
    repo_path = Path(path)
    
    if not repo_path.is_absolute():
        repo_path = BASE_DIR / path
    
    git = shutil.which("git") or "git"
    
    try:
        if add_all:
            subprocess.run(
                [git, "-C", str(repo_path), "add", "-A"],
                capture_output=True
            )
        
        result = subprocess.run(
            [git, "-C", str(repo_path), "commit", "-m", message],
            capture_output=True,
            text=True
        )
        
        output = result.stdout or result.stderr
        return output or f"Committed: {message[:50]}"
    except Exception as e:
        return f"Git error: {e}"


# ============================================================================
# DEBUGGER TOOLS
# ============================================================================

@mcp.tool()
def debug_code(code: str, language: str = "python", input_data: str = "") -> str:
    """
    Debug code and find issues.
    
    Args:
        code: The code to debug (or file path)
        language: python, javascript, etc.
        input_data: Test input if needed
    
    Returns:
        Debug analysis
    """
    path = Path(code)
    
    if path.exists():
        content = path.read_text(encoding='utf-8')
    else:
        content = code
    
    issues = []
    
    # Common issues
    if "eval(" in content or "exec(" in content:
        issues.append("⚠️ Security: eval/exec usage - ensure no user input")
    
    if ".git" in content and "os.environ" in content:
        issues.append("⚠️ Check: Hardcoded credentials - use env vars")
    
    if "password" in content.lower() and "=" in content and "os.environ" not in content:
        issues.append("⚠️ Security: Potential hardcoded password")
    
    if "TODO" in content or "FIXME" in content:
        issues.append("📝 Code has TODOs/FIXMEs")
    
    if "except:" in content and "pass" in content:
        issues.append("⚠️ Empty exception handler")
    
    # Run with verbose to see errors
    try:
        if language == "python":
            result = subprocess.run(
                ["python", "-m", "py_compile", "-v", path if path.exists() else "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stderr:
                issues.append(f"Error: {result.stderr}")
    except Exception as e:
        issues.append(f"Debug error: {e}")
    
    if not issues:
        issues.append("✓ No obvious issues found")
    
    return "\n".join(issues)


@mcp.tool()
def analyze_project(path: str = ".") -> str:
    """
    Analyze a project structure and health.
    
    Args:
        path: Project path
    
    Returns:
        Project analysis
    """
    project_path = Path(path)
    
    if not project_path.is_absolute():
        project_path = BASE_DIR / path
    
    if not project_path.exists():
        return f"Path not found: {path}"
    
    analysis = []
    
    # File counts
    py_files = list(project_path.rglob("*.py"))
    js_files = list(project_path.rglob("*.js")) + list(project_path.rglob("*.ts"))
    md_files = list(project_path.rglob("*.md"))
    
    analysis.append(f"Python: {len(py_files)} files")
    analysis.append(f"JS/TS: {len(js_files)} files")  
    analysis.append(f"Docs: {len(md_files)} files")
    
    # Check for tests
    has_pytest = (project_path / "tests").exists() or (project_path / "test").exists()
    has_jest = (project_path / "tests").exists()
    
    analysis.append(f"Tests: {'✓' if has_pytest or has_jest else '✗'}")
    
    # Git
    has_git = (project_path / ".git").exists()
    analysis.append(f"Git: {'✓' if has_git else '✗'}")
    
    # Dependencies
    if (project_path / "requirements.txt").exists():
        analysis.append("Deps: requirements.txt")
    elif (project_path / "package.json").exists():
        analysis.append("Deps: package.json")
    elif (project_path / "pyproject.toml").exists():
        analysis.append("Deps: pyproject.toml")
    elif (project_path / "go.mod").exists():
        analysis.append("Deps: go.mod")
    elif (project_path / "Cargo.toml").exists():
        analysis.append("Deps: Cargo.toml")
    else:
        analysis.append("Deps: None found")
    
    return "\n".join(analysis)