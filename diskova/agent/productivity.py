"""
Productivity Tools - Email, Calendar, Reminders
==========================================
Tools for managing email, calendar events, and reminders.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class ReminderManager:
    """Manage reminders and to-dos."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "./data/reminders")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reminders_file = self.data_dir / "reminders.json"
        self.reminders = self._load()
    
    def _load(self) -> List[Dict]:
        """Load reminders from file."""
        if self.reminders_file.exists():
            try:
                return json.loads(self.reminders_file.read_text())
            except:
                pass
        return []
    
    def _save(self):
        """Save reminders to file."""
        self.reminders_file.write_text(json.dumps(self.reminders, indent=2))
    
    def add(
        self,
        text: str,
        due: str = None,
        priority: str = "medium",
        category: str = "task"
    ) -> Dict:
        """Add a new reminder."""
        reminder = {
            "id": len(self.reminders) + 1,
            "text": text,
            "due": due,
            "priority": priority,
            "category": category,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        self._save()
        return reminder
    
    def complete(self, reminder_id: int) -> bool:
        """Mark reminder as completed."""
        for r in self.reminders:
            if r.get("id") == reminder_id:
                r["completed"] = True
                r["completed_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def delete(self, reminder_id: int) -> bool:
        """Delete a reminder."""
        self.reminders = [r for r in self.reminders if r.get("id") != reminder_id]
        self._save()
        return True
    
    def get_pending(self, category: str = None) -> List[Dict]:
        """Get pending reminders."""
        pending = [r for r in self.reminders if not r.get("completed")]
        if category:
            pending = [r for r in pending if r.get("category") == category]
        return sorted(pending, key=lambda x: (x.get("priority") == "low", x.get("id")))
    
    def get_all(self) -> List[Dict]:
        """Get all reminders."""
        return self.reminders
    
    def clear_completed(self):
        """Clear completed reminders."""
        self.reminders = [r for r in self.reminders if not r.get("completed")]
        self._save()


class CalendarManager:
    """Manage calendar events."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "./data/calendar")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "events.json"
        self.events = self._load()
    
    def _load(self) -> List[Dict]:
        """Load events from file."""
        if self.events_file.exists():
            try:
                return json.loads(self.events_file.read_text())
            except:
                pass
        return []
    
    def _save(self):
        """Save events to file."""
        self.events_file.write_text(json.dumps(self.events, indent=2))
    
    def add(
        self,
        title: str,
        date: str = None,
        time: str = None,
        duration: int = 60,
        description: str = "",
        location: str = ""
    ) -> Dict:
        """Add a new event."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        event = {
            "id": len(self.events) + 1,
            "title": title,
            "date": date,
            "time": time,
            "duration": duration,
            "description": description,
            "location": location,
            "created_at": datetime.now().isoformat()
        }
        self.events.append(event)
        self._save()
        return event
    
    def delete(self, event_id: int) -> bool:
        """Delete an event."""
        self.events = [e for e in self.events if e.get("id") != event_id]
        self._save()
        return True
    
    def get_upcoming(self, days: int = 7) -> List[Dict]:
        """Get upcoming events."""
        now = datetime.now()
        upcoming = []
        
        for event in self.events:
            try:
                event_date = datetime.strptime(event.get("date", ""), "%Y-%m-%d")
                if (event_date - now).days <= days:
                    upcoming.append(event)
            except:
                pass
        
        return sorted(upcoming, key=lambda x: x.get("date", ""))
    
    def get_today(self) -> List[Dict]:
        """Get today's events."""
        today = datetime.now().strftime("%Y-%m-%d")
        return [e for e in self.events if e.get("date") == today]
    
    def get_by_date(self, date: str) -> List[Dict]:
        """Get events by date."""
        return [e for e in self.events if e.get("date") == date]


class NoteManager:
    """Manage notes and quick notes."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "./data/notes")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.notes_file = self.data_dir / "notes.json"
        self.notes = self._load()
    
    def _load(self) -> Dict:
        """Load notes from file."""
        if self.notes_file.exists():
            try:
                return json.loads(self.notes_file.read_text())
            except:
                pass
        return {}
    
    def _save(self):
        """Save notes to file."""
        self.notes_file.write_text(json.dumps(self.notes, indent=2))
    
    def add(self, title: str, content: str, category: str = "general") -> Dict:
        """Add a note."""
        note = {
            "id": len(self.notes) + 1,
            "title": title,
            "content": content,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.notes[str(note["id"])] = note
        self._save()
        return note
    
    def get(self, note_id: int = None) -> Optional[Dict]:
        """Get a note by ID or latest."""
        if note_id:
            return self.notes.get(str(note_id))
        if self.notes:
            return self.notes[sorted(self.notes.keys(), key=int)[-1]]
        return None
    
    def update(self, note_id: int, content: str = None, title: str = None) -> bool:
        """Update a note."""
        key = str(note_id)
        if key in self.notes:
            if content:
                self.notes[key]["content"] = content
            if title:
                self.notes[key]["title"] = title
            self.notes[key]["updated_at"] = datetime.now().isoformat()
            self._save()
            return True
        return False
    
    def delete(self, note_id: int) -> bool:
        """Delete a note."""
        key = str(note_id)
        if key in self.notes:
            del self.notes[key]
            self._save()
            return True
        return False
    
    def search(self, query: str) -> List[Dict]:
        """Search notes."""
        results = []
        query = query.lower()
        for note in self.notes.values():
            if query in note.get("title", "").lower() or query in note.get("content", "").lower():
                results.append(note)
        return results


# Global instances
_reminder_mgr = None
_calendar_mgr = None
_note_mgr = None


def get_reminder_manager() -> ReminderManager:
    """Get reminder manager."""
    global _reminder_mgr
    if _reminder_mgr is None:
        _reminder_mgr = ReminderManager()
    return _reminder_mgr


def get_calendar_manager() -> CalendarManager:
    """Get calendar manager."""
    global _calendar_mgr
    if _calendar_mgr is None:
        _calendar_mgr = CalendarManager()
    return _calendar_mgr


def get_note_manager() -> NoteManager:
    """Get note manager."""
    global _note_mgr
    if _note_mgr is None:
        _note_mgr = NoteManager()
    return _note_mgr


# Easy functions
def add_reminder(text: str, due: str = None, priority: str = "medium") -> str:
    """Add reminder."""
    mgr = get_reminder_manager()
    reminder = mgr.add(text, due, priority)
    return f"Reminder added: #{reminder['id']} - {reminder['text']}"


def list_reminders(category: str = None) -> str:
    """List reminders."""
    mgr = get_reminder_manager()
    pending = mgr.get_pending(category)
    if not pending:
        return "No pending reminders."
    
    lines = ["Reminders:"]
    for r in pending:
        lines.append(f"{r['id']}. [{r['priority']}] {r['text']}")
        if r.get("due"):
            lines.append(f"   Due: {r['due']}")
    return "\n".join(lines)


def complete_reminder(reminder_id: int) -> str:
    """Complete reminder."""
    mgr = get_reminder_manager()
    if mgr.complete(reminder_id):
        return f"Reminder #{reminder_id} completed!"
    return f"Reminder #{reminder_id} not found."


def add_event(title: str, date: str = None, time: str = None, duration: int = 60) -> str:
    """Add calendar event."""
    mgr = get_calendar_manager()
    event = mgr.add(title, date, time, duration)
    return f"Event added: {event['title']} on {event['date']} at {event['time']}"


def list_events(days: int = 7) -> str:
    """List upcoming events."""
    mgr = get_calendar_manager()
    events = mgr.get_upcoming(days)
    if not events:
        return "No upcoming events."
    
    lines = [f"Upcoming events (next {days} days):"]
    for e in events:
        lines.append(f"{e['date']} {e.get('time', '')}: {e['title']}")
    return "\n".join(lines)


def add_note(title: str, content: str) -> str:
    """Add a note."""
    mgr = get_note_manager()
    note = mgr.add(title, content)
    return f"Note saved: #{note['id']} - {note['title']}"


def get_note(note_id: int = None) -> str:
    """Get a note."""
    mgr = get_note_manager()
    note = mgr.get(note_id)
    if note:
        return f"{note['title']}\n{note['content']}"
    return "No note found."


def search_notes(query: str) -> str:
    """Search notes."""
    mgr = get_note_manager()
    results = mgr.search(query)
    if not results:
        return f"No notes found for: {query}"
    
    lines = [f"Found {len(results)} notes:"]
    for n in results:
        lines.append(f"#{n['id']}: {n['title']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Productivity Tools")
    
    # Test reminders
    mgr = get_reminder_manager()
    mgr.add("Test reminder", priority="high")
    print(f"Reminders: {len(mgr.get_pending())}")
    
    # Test calendar
    cal = get_calendar_manager()
    cal.add("Test event", date="2026-04-26", time="10:00")
    print(f"Events today: {len(cal.get_today())}")
    
    # Test notes
    notes = get_note_manager()
    notes.add("Test Note", "This is a test note.")
    print(f"Notes: {len(notes.notes)}")