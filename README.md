# Powerful AI Coding Agent Brain

A complete $0 local AI coding ecosystem with semantic memory, self-reflection, and 8 powerful MCP tools.

## What's Built

| Component | Tool | Status |
|-----------|------|--------|
| **LLM Engine** | Ollama + qwen2.5-coder:1.5b | ✅ Running on CPU |
| **MCP Server** | FastMCP with 8 tools | ✅ Ready |
| **AI Brain** | ChromaDB-ready + file memory | ✅ Ready |
| **Claude Desktop** | MCP integration | ✅ Configured |

## Project Structure

```
ai-coding-ecosystem/
├── CLAUDE.md                    # AI Constitution (self-reflection rules)
├── brain_server.py              # MCP Server with 8 tools
├── config/
│   ├── claude_desktop_config.json   # Claude Desktop integration
│   └── settings.json           # Brain settings
├── knowledge/
│   ├── sessions/            # Conversation history
│   ├── patterns/           # Reusable solution patterns
│   └── projects/          # Project-specific context
└── tools/
    └── code_snippets.json   # Boilerplate code library
```

## 8 Powerful MCP Tools

| Tool | Purpose |
|------|--------|
| `search_knowledge` | Semantic search across sessions, patterns, projects |
| `get_code_snippet` | Fetch boilerplate code (Python, JS, TS, Go, Rust) |
| `save_session_memory` | Store task results to memory |
| `review_code` | Self-code review with issues/suggestions |
| `analyze_project` | Project structure and dependencies |
| `update_task_status` | Track multi-step tasks |
| `generate_docs` | Auto-generate documentation |
| `recall_pattern` | Find similar solved problems |

## How to Use

### 1. Install Dependencies
```powershell
pip install fastmcp chromadb
```

### 2. Integrate with Claude Desktop

Copy the contents of `config/claude_desktop_config.json` to your Claude Desktop MCP configuration:

**Location**: `%APPDATA%\Claude\claude_desktop_config.json`

### 3. Run the MCP Server
```powershell
python brain_server.py
```

### 4. Start Coding with Your AI Brain

Your agent now has:
- Access to 100+ code snippets
- Session memory that persists across conversations
- Self-review before submitting code
- Pattern recall for similar problems
- Project analysis capabilities

## Usage Examples

### Get Code Snippet
```
get_code_snippet(language="python", task="async")
```

### Save Session
```
save_session_memory(task="Created user API", result="POST /users endpoint working", tags="api,rest")
```

### Review Code
```
review_code(code="def bad(): except: pass", language="python")
```

### Search Knowledge
```
search_knowledge(query="async error handling", category="patterns")
```

---

## Performance Notes

**CPU-only Reality**:
- qwen2.5-coder:1.5b runs smoothly (3-5 tokens/sec)
- DeepSeek-Coder-V2:6.7b available when download completes
- Use for quick edits, not real-time chat

## Next Steps

1. Add more code snippets to `tools/code_snippets.json`
2. Build your pattern library by solving problems
3. Upgrade to GPU when available
4. Install Obsidian for visual note management

---

**Cost**: $0 | **Control**: 100% Local | **Power**: Maximum