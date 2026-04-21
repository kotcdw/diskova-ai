"""
Secretary Module - Scheduling, Tasks, Reminders
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib


@dataclass
class Meeting:
    id: str
    title: str
    description: str
    participants: List[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    status: str = "scheduled"


@dataclass
class Reminder:
    id: str
    title: str
    message: str
    due_time: datetime
    repeat: Optional[str] = None
    status: str = "pending"


class SecretaryModule:
    def __init__(self, memory_manager):
        self.memory = memory_manager

    def create_meeting(
        self,
        user_id: str,
        title: str,
        participants: List[str],
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = ""
    ) -> Meeting:
        meeting_id = hashlib.md5(f"{title}{start_time.isoformat()}".encode()).hexdigest()[:8]
        
        meeting = Meeting(
            id=meeting_id,
            title=title,
            description=description,
            participants=participants,
            start_time=start_time,
            end_time=end_time,
            location=location
        )
        
        self.memory.store_preference(f"meeting_{meeting_id}", user_id, {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "participants": meeting.participants,
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat(),
            "location": meeting.location,
            "status": meeting.status
        })
        
        return meeting

    def get_meetings(self, user_id: str, date: Optional[datetime] = None) -> List[Dict]:
        return self.memory.get_preference(f"user_{user_id}_meetings", key="meetings", default=[])

    def create_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: List[str] = None
    ) -> Dict:
        task_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date.isoformat() if due_date else None,
            "tags": tags or [],
            "subtasks": [],
            "attachments": []
        }
        
        task = self.memory.add_task(user_id, task_data)
        return task

    def get_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict]:
        tasks = self.memory.get_tasks(user_id, status)
        
        if priority:
            tasks = [t for t in tasks if t.get("priority") == priority]
        
        return tasks

    def update_task_status(self, user_id: str, task_id: str, status: str) -> Optional[Dict]:
        return self.memory.update_task(user_id, task_id, {"status": status})

    def add_subtask(self, user_id: str, task_id: str, subtask: str) -> Optional[Dict]:
        task = None
        for t in self.memory.get_user_context(user_id).tasks:
            if t.get("id") == task_id:
                task = t
                break
        
        if task:
            subtasks = task.get("subtasks", [])
            subtasks.append({"title": subtask, "completed": False})
            task["subtasks"] = subtasks
            return task
        return None

    def create_reminder(
        self,
        user_id: str,
        title: str,
        message: str,
        due_time: datetime,
        repeat: Optional[str] = None
    ) -> Reminder:
        reminder_id = hashlib.md5(f"{title}{due_time.isoformat()}".encode()).hexdigest()[:8]
        
        reminder = Reminder(
            id=reminder_id,
            title=title,
            message=message,
            due_time=due_time,
            repeat=repeat
        )
        
        self.memory.store_preference(f"reminder_{reminder_id}", user_id, {
            "id": reminder.id,
            "title": reminder.title,
            "message": reminder.message,
            "due_time": reminder.due_time.isoformat(),
            "repeat": reminder.repeat,
            "status": reminder.status
        })
        
        return reminder

    def get_reminders(self, user_id: str) -> List[Dict]:
        reminders = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("reminder_") and isinstance(value, dict):
                reminders.append(value)
        
        return reminders

    def extract_tasks_from_text(self, text: str) -> List[Dict]:
        import re
        
        task_patterns = [
            r"(?:remind me to|make sure to|don't forget to)\s+(.+?)(?:\.|,|$)",
            r"(?:todo|task)\s*:?\s*(.+?)(?:\.|,|$)",
            r"(?:schedule|book)\s+(.+?)(?:\.|,|$)"
        ]
        
        tasks = []
        for pattern in task_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                tasks.append({
                    "title": match.strip(),
                    "extracted": True
                })
        
        return tasks