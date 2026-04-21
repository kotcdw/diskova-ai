"""
Automation Module - Workflows & Triggers
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import hashlib
import json


@dataclass
class Workflow:
    id: str
    name: str
    trigger: Dict
    actions: List[Dict]
    enabled: bool
    created_at: datetime


@dataclass
class AutomationRule:
    id: str
    name: str
    condition: str
    action: str
    enabled: bool


class AutomationModule:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.workflow_handlers: Dict[str, Callable] = {}

    def create_workflow(
        self,
        user_id: str,
        name: str,
        trigger: Dict,
        actions: List[Dict]
    ) -> Workflow:
        workflow_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        workflow = Workflow(
            id=workflow_id,
            name=name,
            trigger=trigger,
            actions=actions,
            enabled=True,
            created_at=datetime.now()
        )
        
        self.memory.store_preference(f"workflow_{workflow_id}", user_id, {
            "id": workflow.id,
            "name": workflow.name,
            "trigger": workflow.trigger,
            "actions": workflow.actions,
            "enabled": workflow.enabled,
            "created_at": workflow.created_at.isoformat()
        })
        
        return workflow

    def get_workflows(self, user_id: str) -> List[Dict]:
        workflows = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("workflow_") and isinstance(value, dict):
                workflows.append(value)
        
        return workflows

    def execute_workflow(self, workflow_id: str, user_id: str, context: Dict) -> Dict:
        prefs = self.memory.get_user_context(user_id).preferences
        workflow_data = prefs.get(f"workflow_{workflow_id}")
        
        if not workflow_data:
            return {"error": "Workflow not found"}
        
        results = []
        for action in workflow_data.get("actions", []):
            result = self._execute_action(action, context)
            results.append(result)
        
        return {"workflow_id": workflow_id, "results": results}

    def _execute_action(self, action: Dict, context: Dict) -> Dict:
        action_type = action.get("type", "")
        
        if action_type == "send_email":
            return {"status": "sent", "action": "email_sent"}
        elif action_type == "create_task":
            return {"status": "created", "action": "task_created"}
        elif action_type == "notify":
            return {"status": "notified", "action": "notification_sent"}
        else:
            return {"status": "executed", "action": action_type}

    def create_rule(
        self,
        user_id: str,
        name: str,
        condition: str,
        action: str
    ) -> AutomationRule:
        rule_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        rule = AutomationRule(
            id=rule_id,
            name=name,
            condition=condition,
            action=action,
            enabled=True
        )
        
        self.memory.store_preference(f"rule_{rule_id}", user_id, {
            "id": rule.id,
            "name": rule.name,
            "condition": rule.condition,
            "action": rule.action,
            "enabled": rule.enabled
        })
        
        return rule

    def get_rules(self, user_id: str) -> List[Dict]:
        rules = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("rule_") and isinstance(value, dict):
                rules.append(value)
        
        return rules

    def trigger_rule(self, user_id: str, rule_id: str, data: Dict) -> Dict:
        prefs = self.memory.get_user_context(user_id).preferences
        rule_data = prefs.get(f"rule_{rule_id}")
        
        if not rule_data:
            return {"error": "Rule not found"}
        
        return {"triggered": True, "action": rule_data.get("action")}

    def toggle_workflow(self, user_id: str, workflow_id: str, enabled: bool) -> bool:
        prefs = self.memory.get_user_context(user_id).preferences
        key = f"workflow_{workflow_id}"
        
        if key in prefs:
            prefs[key]["enabled"] = enabled
            return True
        return False
