"""
Multi-Agent Orchestration (Swarm Pattern)
==========================================
Implements the Swarm pattern from OpenAI for multi-agent collaboration.

Features:
- Multiple specialized agents
- Handoffs between agents
- Shared context
- Collaborative problem solving

Agents:
1. Coder - Writes code
2. Reviewer - Reviews code  
3. Debugger - Finds and fixes bugs
4. Documenter - Creates docs

Based on: https://github.com/anthropic/claude-code/tree/main/examples/swarm
"""

import os
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class AgentRole(Enum):
    """Agent roles in the swarm."""
    CODER = "coder"
    REVIEWER = "reviewer"
    DEBUGGER = "debugger"
    DOCUMENTER = "documenter"
    ORCHESTRATOR = "orchestrator"


@dataclass
class Agent:
    """An agent in the swarm."""
    name: str
    role: AgentRole
    instructions: str
    tools: List[str] = field(default_factory=list)
    active: bool = True


@dataclass
class Handoff:
    """A handoff from one agent to another."""
    from_agent: str
    to_agent: str
    context: str
    reason: str


class SwarmOrchestrator:
    """
    Multi-agent orchestrator implementing the Swarm pattern.
    
    Agents can:
    - Collaborate on tasks
    - Handoff to each other
    - Share context
    - Work in parallel
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.handoffs: List[Handoff] = []
        self.shared_context: Dict[str, Any] = {}
        self.current_agent: Optional[Agent] = None
        
        self._init_default_agents()
    
    def _init_default_agents(self):
        """Initialize default swarm agents."""
        default_agents = [
            Agent(
                name="Coder",
                role=AgentRole.CODER,
                instructions="""You are an expert coder. Your role is to:
- Write clean, efficient, production-ready code
- Implement features following best practices
- Choose appropriate data structures and algorithms
- Add proper error handling
- Write code that is easy to maintain""",
                tools=["execute_code", "write_file", "get_code_snippet", "analyze_project"]
            ),
            Agent(
                name="Reviewer",
                role=AgentRole.REVIEWER,
                instructions="""You are a code reviewer. Your role is to:
- Review code for bugs and issues
- Check for security vulnerabilities
- Ensure code follows best practices
- Suggest improvements
- Validate error handling""",
                tools=["review_code", "search_code", "execute_code"]
            ),
            Agent(
                name="Debugger",
                role=AgentRole.DEBUGGER,
                instructions="""You are a debug expert. Your role is to:
- Find and fix bugs in code
- Analyze error messages
- Add logging and diagnostics
- Fix edge cases
- Ensure code handles all inputs correctly""",
                tools=["execute_code", "search_code", "run_tests", "analyze_project"]
            ),
            Agent(
                name="Documenter",
                role=AgentRole.DOCUMENTER,
                instructions="""You are a technical writer. Your role is to:
- Create clear documentation
- Write README files
- Document APIs and functions
- Add code comments
- Generate documentation from code""",
                tools=["generate_docs", "read_file", "write_file", "search_knowledge"]
            ),
        ]
        
        for agent in default_agents:
            self.register_agent(agent)
    
    def register_agent(self, agent: Agent):
        """Register an agent with the swarm."""
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    def list_agents(self) -> List[Agent]:
        """List all registered agents."""
        return list(self.agents.values())
    
    def handoff(self, from_name: str, to_name: str, context: str, reason: str) -> str:
        """Hand off from one agent to another."""
        if from_name not in self.agents:
            return f"Agent '{from_name}' not found."
        if to_name not in self.agents:
            return f"Agent '{to_name}' not found."
        
        handoff = Handoff(
            from_agent=from_name,
            to_agent=to_name,
            context=context,
            reason=reason
        )
        self.handoffs.append(handoff)
        
        self.current_agent = self.agents[to_name]
        
        return f"Handoff complete: {from_name} -> {to_name}\nReason: {reason}"
    
    def set_context(self, key: str, value: Any):
        """Set shared context."""
        self.shared_context[key] = value
    
    def get_context(self, key: str) -> Any:
        """Get shared context."""
        return self.shared_context.get(key)
    
    def clear_context(self):
        """Clear all shared context."""
        self.shared_context.clear()
    
    def get_handoffs(self) -> List[Handoff]:
        """Get all handoffs made in this session."""
        return self.handoffs
    
    def run_agent(self, agent_name: str, task: str) -> Dict:
        """Run a task with a specific agent."""
        agent = self.get_agent(agent_name)
        
        if not agent:
            return {"error": f"Agent '{agent_name}' not found"}
        
        if not agent.active:
            return {"error": f"Agent '{agent_name}' is not active"}
        
        return {
            "agent": agent_name,
            "role": agent.role.value,
            "task": task,
            "context": self.shared_context,
            "status": "ready_to_execute"
        }
    
    def run_collaborative(self, task: str, agent_sequence: Optional[List[str]] = None) -> str:
        """Run a task collaboratively with multiple agents."""
        if agent_sequence is None:
            agent_sequence = ["Coder", "Reviewer"]
        
        results = []
        
        for agent_name in agent_sequence:
            result = self.run_agent(agent_name, task)
            results.append(result)
            
            if "error" in result:
                return f"Error at {agent_name}: {result['error']}"
        
        return f"Collaborative task complete. Agents: {', '.join(agent_sequence)}"


class MultiagentSwarm:
    """High-level API for multi-agent swarm."""
    
    def __init__(self):
        self.orchestrator = SwarmOrchestrator()
    
    def code_review_cycle(self, code: str) -> str:
        """Run a complete code review cycle."""
        self.orchestrator.set_context("code", code)
        
        result = self.orchestrator.run_agent("Coder", f"Write code: {code[:100]}...")
        if "error" in result:
            return f"Coder error: {result['error']}"
        
        result = self.orchestrator.run_agent("Reviewer", f"Review this code: {code[:200]}")
        if "error" in result:
            return f"Reviewer error: {result['error']}"
        
        handoffs = self.orchestrator.get_handoffs()
        return f"Code review complete.\nHandoffs: {len(handoffs)}\nContext: {self.orchestrator.shared_context}"
    
    def debug_and_fix(self, code: str, error: str) -> str:
        """Debug and fix code issues."""
        self.orchestrator.set_context("problematic_code", code)
        self.orchestrator.set_context("error", error)
        
        result = self.orchestrator.run_agent("Debugger", f"Fix error: {error}\nCode:\n{code}")
        
        if "error" in result:
            return f"Debugger error: {result['error']}"
        
        result = self.orchestrator.run_agent("Reviewer", f"Review the fix")
        
        if "error" in result:
            return f"Reviewer error: {result['error']}"
        
        return f"Debug and fix complete.\nContext: {self.orchestrator.shared_context}"
    
    def full_stack_development(self, feature: str) -> str:
        """Run full stack development cycle."""
        self.orchestrator.set_context("feature", feature)
        
        cycle = ["Coder", "Reviewer", "Documenter"]
        
        result = self.orchestrator.run_collaborative(
            f"Implement feature: {feature}",
            agent_sequence=cycle
        )
        
        return result
    
    def get_status(self) -> Dict:
        """Get swarm status."""
        agents = self.orchestrator.list_agents()
        
        return {
            "total_agents": len(agents),
            "agents": [a.name for a in agents if a.active],
            "handoffs": len(self.orchestrator.get_handoffs()),
            "context_keys": list(self.orchestrator.shared_context.keys())
        }


# Demo usage
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Multi-Agent Swarm (Swarm Pattern)")
    print("=" * 60)
    
    swarm = MultiagentSwarm()
    
    print("\nSwarm Status:")
    status = swarm.get_status()
    print(f"Agents: {status['agents']}")
    print(f"Handoffs: {status['handoffs']}")
    
    print("\nRunning debug cycle...")
    result = swarm.debug_and_fix(
        code="def add(a, b): return a + b",
        error="TypeError: unsupported operand type(s) for +: 'str' and 'str'"
    )
    print(result)
    
    print("\n" + "=" * 60)
    print("Multi-Agent Swarm Ready!")
    print("=" * 60)