# opencode - CLI Assistant Documentation

## What is opencode?

> **opencode** is an interactive CLI tool powered by a large language model (big-pickle).
> It assists users with software engineering tasks through conversation and tool execution.

- **Model**: big-pickle (opencode/big-pickle)
- **Platform**: Windows (win32)
- **Shell**: PowerShell
- **Working Directory**: user's workspace

---

## My Capabilities (Honest Assessment)

### What I CAN Do

| Category | Capabilities | Count |
|----------|--------------|-------|
| **File Operations** | Read, Write, Edit, Glob, Grep | 5 |
| **Code Analysis** | Parse Python AST, Count functions/classes | 3 |
| **Web Access** | WebFetch, WebSearch, CodeSearch | 3 |
| **Git Operations** | Status, Diff, Commit, Push, Log | 6 |
| **Process Execution** | Run commands, Install packages | 2 |
| **Skills** | 40+ specialized skills | 40+ |
| **Agent Tasks** | Launch sub-agents for research | 1 |

### What I CANNOT Do

- I cannot browse the internet freely (only via tools)
- I cannot access files without explicit paths
- I cannot remember previous sessions
- I cannot make changes to user's system without permission
- I cannot run background processes directly

---

## My Available Tools

### File Tools (5)

| Tool | Function |
|------|----------|
| **read** | Read file content (with line numbers) |
| **write** | Write/overwrite entire file |
| **edit** | Replace exact string in file |
| **glob** | Find files by pattern |
| **grep** | Search content in files |

### Agent Tools (1)

| Tool | Function |
|------|----------|
| **task** | Launch sub-agent for research/exploration |

### Web Tools (3)

| Tool | Function |
|------|----------|
| **webfetch** | Fetch URL content (markdown/text/html) |
| **websearch** | Search the web via Exa AI |
| **codesearch** | Search code documentation via Exa |

### Bash Tools (2)

| Tool | Function |
|------|----------|
| **bash** | Execute shell commands |
| **question** | Ask user for input |

### Skill Tools (1)

| Tool | Function |
|------|----------|
| **skill** | Load specialized skill instructions |

---

## Available Skills (40+)

### Azure Skills (25)

| Skill | Purpose |
|-------|---------|
| azure-ai | AI Search, Speech, OpenAI, Document AI |
| azure-aigateway | API Management as AI Gateway |
| azure-cloud-migrate | Cross-cloud migration |
| azure-compliance | Security auditing |
| azure-compute | VM recommendations |
| azure-cost-optimization | Cost analysis |
| azure-deploy | Execute Azure deployments |
| azure-diagnostics | Debug production issues |
| azure-hosted-copilot-sdk | GitHub Copilot SDK |
| azure-kusto | Kusto/ADX queries |
| azure-messaging | Event Hubs/Service Bus |
| azure-observability | Azure Monitor/App Insights |
| azure-prepare | Prepare Azure apps |
| azure-rbac | Role assignments |
| azure-resource-lookup | List Azure resources |
| azure-resource-visualizer | Diagram resources |
| azure-storage | Blob/File/Queue storage |
| azure-validate | Pre-deployment validation |
| capacity | OpenAI capacity discovery |
| customize | Custom model deployment |
| deploy-model | Deploy OpenAI models |
| entra-app-registration | App registration/OAuth |
| find-skills | Discover skills |
| microsoft-foundry | AI Foundry |
| preset | Quick deployment |
| skill-creator | Create skills |

### Other Skills (15)

| Skill | Purpose |
|-------|---------|
| appinsights-instrumentation | App Insights telemetry |
| code-review | Review code changes |
| playwright | Browser automation |

---

## Code Analysis Features

I can analyze Python code programmatically:

```python
import ast
from pathlib import Path

# Count:
# - Lines of code
# - Functions (def)
# - Classes (class)
# - Imports
# - Docstrings
```

### Metrics Extraction

```python
total_lines = 5,132     # From diskova/agent
total_functions = 266    # From diskova/agent
total_classes = 38      # From diskova/agent
total_tools = 50+       # From diskova/agent
```

---

## System Information

| Property | Value |
|----------|-------|
| Platform | win32 |
| Shell | PowerShell |
| Model | big-pickle |
| Working Directory | User's current directory |
| Git Repo | Detected if .git exists |

---

## Limitations

### Honest Limitations

1. **No persistent memory** - Each session starts fresh
2. **No internet browsing** - Must use websearch/webfetch
3. **No file system browsing** - Must provide exact paths
4. **No background processes** - Commands block until complete
5. **Windows only** - Current platform
6. **No GUI** - CLI tool only
7. **PowerShell only** - No bash emulation

### What I Don't Know

- I don't know what's in your mind
- I don't know your preferences unless told
- I don't know previous conversations
- I can't access other computers
- I can't run without tools

---

## Usage Patterns

### How I Work

1. **You ask** a question or request
2. **I think** about what tools needed
3. **I use** tools to gather info
4. **I respond** with answer/action

### Best Use Cases

| Use Case | Good? |
|---------|------|
| Code reviews | ✅ Yes |
| File operations | ✅ Yes |
| Git operations | ✅ Yes |
| Azure tasks | ✅ Yes (via skills) |
| Web research | ✅ Yes (limited) |
| Chat/companionship | ✅ Yes |
| System administration | ⚠️ Limited |
| GUI apps | ❌ No |
| Mobile apps | ❌ No |

---

## Statistics (My Implementation)

| Metric | Value |
|--------|-------|
| System Prompt Length | ~15,000 tokens |
| Tool Definitions | 12 tools |
| Skill Definitions | 40+ skills |
| Available Functions | Unlimited* |

*Unlimited through code execution

---

## Commands I Respond To

| Command Type | Example |
|-------------|---------|
| Questions | "What is X?" |
| Tasks | "Write code for X" |
| Search | "Find files containing X" |
| Analysis | "Count functions in X" |
| Azure | "Deploy to Azure" |
| Git | "Commit these changes" |

---

## Not Capabilities

| Misconception | Reality |
|--------------|---------|
| "I have unlimited tools" | Only 12 defined tools |
| "I can browse freely" | Only via websearch/webfetch |
| "I remember you" | No memory between sessions |
| "I can do anything" | Limited to toolset |
| "I'm a human" | I'm an AI assistant |

---

## How to Use Me Effectively

### Do

- ✅ Be specific about what you want
- ✅ Provide exact file paths
- ✅ Ask for clarification when needed
- ✅ Use skills for specialized tasks
- ✅ Check my work

### Don't

- ❌ Expect me to read minds
- ❌ Expect persistent memory
- ❌ Expect GUI capabilities
- ❌ Expect other OS support
- ❌ Expect unlimited internet

---

## Summary

| Category | Count |
|----------|-------|
| Core Tools | 12 |
| Skills Available | 40+ |
| Azure Integrations | 25 |
| Programming Languages | 1 (Python) |
| Maximum Functions | Unlimited |

**I am opencode - a helpful CLI assistant, not a magic wand.**

---

*Generated: April 2026*
*Tool: opencode CLI*
*Model: big-pickle*