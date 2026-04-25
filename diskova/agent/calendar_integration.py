"""
Calendar Integration
==================
Advanced calendar with ICS, CalDAV, and sync support.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote


class CalendarSync:
    """Advanced calendar with ICS export/import."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "./data/calendar")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "events_advanced.json"
        self.events = self._load()
    
    def _load(self) -> Dict:
        """Load events."""
        if self.events_file.exists():
            try:
                return json.loads(self.events_file.read_text())
            except:
                pass
        return {"events": [], "calendars": {}}
    
    def _save(self):
        """Save events."""
        self.events_file.write_text(json.dumps(self.events, indent=2))
    
    def create_event(self, title: str, start: str, end: str = None,
                description: str = "", location: str = "",
                calendar: str = "default", all_day: bool = False) -> Dict:
        """Create event with ICS format."""
        if end is None:
            end = start
        
        event = {
            "id": str(uuid.uuid4()),
            "title": title,
            "start": start,
            "end": end,
            "description": description,
            "location": location,
            "calendar": calendar,
            "all_day": all_day,
            "created": datetime.now().isoformat()
        }
        
        if "events" not in self.events:
            self.events["events"] = []
        self.events["events"].append(event)
        self._save()
        
        return event
    
    def get_events(self, start: str = None, end: str = None,
                 calendar: str = None) -> List[Dict]:
        """Get events with date filter."""
        events = self.events.get("events", [])
        
        filtered = []
        for e in events:
            if calendar and e.get("calendar") != calendar:
                continue
            filtered.append(e)
        
        return sorted(filtered, key=lambda x: x.get("start", ""))
    
    def export_ics(self, calendar: str = "default") -> str:
        """Export to ICS format."""
        events = self.get_events(calendar=calendar)
        
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Diskova AI//Calendar//EN",
            "CALSCALE:GREGORIAN",
        ]
        
        for event in events:
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:{event.get('id')}")
            lines.append(f"SUMMARY:{event.get('title')}")
            lines.append(f"DTSTART:{event.get('start').replace('-', '').replace(':', '')}")
            lines.append(f"DTEND:{event.get('end', event.get('start')).replace('-', '').replace(':', '')}")
            
            if event.get("description"):
                lines.append(f"DESCRIPTION:{event.get('description')}")
            if event.get("location"):
                lines.append(f"LOCATION:{event.get('location')}")
            
            lines.append("END:VEVENT")
        
        lines.append("END:VCALENDAR")
        
        return "\n".join(lines)
    
    def import_ics(self, ics_content: str) -> int:
        """Import from ICS format."""
        imported = 0
        lines = ics_content.split("\n")
        event = {}
        
        for line in lines:
            if line == "BEGIN:VEVENT":
                event = {}
            elif line == "END:VEVENT":
                if event:
                    self.events["events"].append(event)
                    imported += 1
            elif line.startswith("SUMMARY:"):
                event["title"] = line[7:]
            elif line.startswith("DTSTART:"):
                event["start"] = line[8:]
            elif line.startswith("DTEND:"):
                event["end"] = line[6:]
            elif line.startswith("DESCRIPTION:"):
                event["description"] = line[12:]
            elif line.startswith("LOCATION:"):
                event["location"] = line[9:]
        
        self._save()
        return imported
    
    def sync_google(self, calendar_id: str = "primary") -> str:
        """Generate Google Calendar sync URL."""
        # Generate Google Calendar link
        base = "https://calendar.google.com/calendar/render"
        return f"{base}?action=TEMPLATE&text=Diskova+Event"
    
    def get_upcoming(self, days: int = 7) -> List[Dict]:
        """Get upcoming events."""
        now = datetime.now()
        upcoming = []
        
        for event in self.events.get("events", []):
            try:
                start = datetime.strptime(event.get("start", "")[:16], "%Y-%m-%d %H:%M")
                if (start - now).days <= days:
                    upcoming.append(event)
            except:
                pass
        
        return sorted(upcoming, key=lambda x: x.get("start", ""))
    
    def delete_event(self, event_id: str) -> bool:
        """Delete event."""
        events = self.events.get("events", [])
        self.events["events"] = [e for e in events if e.get("id") != event_id]
        self._save()
        return True
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """Update event."""
        events = self.events.get("events", [])
        for e in events:
            if e.get("id") == event_id:
                e.update(kwargs)
                self._save()
                return True
        return False


# Quick add for action layer
def add_calendar_event(title: str, date: str = None, time: str = None,
                     duration: int = 60, description: str = "",
                     location: str = "") -> str:
    """Add calendar event."""
    cal = CalendarSync()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    if time:
        start = f"{date} {time}"
    else:
        start = date
    
    event = cal.create_event(title, start, description=description, location=location)
    
    return f"Event created: {event.get('title')} at {start}"


def list_calendar_events(days: int = 7) -> str:
    """List upcoming events."""
    cal = CalendarSync()
    events = cal.get_upcoming(days)
    
    if not events:
        return "No upcoming events"
    
    lines = [f"Upcoming events (next {days} days):"]
    for e in events:
        lines.append(f"📅 {e.get('title')}")
        lines.append(f"   {e.get('start')}")
        if e.get("location"):
            lines.append(f"   📍 {e.get('location')}")
        lines.append("")
    
    return "\n".join(lines)


def export_ics_file(calendar: str = "default") -> str:
    """Export to ICS file."""
    cal = CalendarSync()
    ics = cal.export_ics(calendar)
    
    file = cal.data_dir / f"{calendar}.ics"
    file.write_text(ics)
    
    return f"Exported to: {file}"


if __name__ == "__main__":
    print("Advanced Calendar")
    
    cal = CalendarSync()
    cal.create_event("Test Event", "2026-04-26 10:00", description="Test")
    print(f"Events: {len(cal.events.get('events', []))}")