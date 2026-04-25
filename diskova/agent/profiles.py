"""
User Profiles
============
Hyper-personalization - user preferences, history, habits.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class UserProfile:
    """User profile with preferences and history."""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.profile_dir = Path("./data/profiles")
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.profile_file = self.profile_dir / f"{user_id}.json"
        self.profile = self._load()
    
    def _load(self) -> Dict:
        """Load profile from file."""
        if self.profile_file.exists():
            try:
                return json.loads(self.profile_file.read_text())
            except:
                pass
        return self._default_profile()
    
    def _default_profile(self) -> Dict:
        """Default profile structure."""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "preferences": {
                "language": "en",
                "tone": "friendly",
                "code_style": "python",
                "response_length": "medium",
                "tts_enabled": False,
            },
            "habits": {
                "common_queries": [],
                "time_of_use": {},
                "topics_of_interest": [],
            },
            "feedback": [],
            "history": [],
        }
    
    def _save(self):
        """Save profile to file."""
        self.profile_file.write_text(json.dumps(self.profile, indent=2))
    
    def update_preference(self, key: str, value: Any):
        """Update a preference."""
        self.profile["preferences"][key] = value
        self._save()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference."""
        return self.profile["preferences"].get(key, default)
    
    def add_query(self, query: str):
        """Add query to history."""
        history = self.profile["history"]
        history.append({
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 100
        self.profile["history"] = history[-100:]
        
        # Update common queries
        common = self.profile["habits"]["common_queries"]
        if query not in common:
            common.append(query)
        self.profile["habits"]["common_queries"] = common[:20]
        
        self._save()
    
    def add_feedback(self, query: str, response: str, rating: int, comment: str = ""):
        """Add feedback for learning."""
        self.profile["feedback"].append({
            "query": query,
            "response": response,
            "rating": rating,  # 1-5
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 50
        self.profile["feedback"] = self.profile["feedback"][-50:]
        self._save()
    
    def get_common_topics(self) -> list:
        """Get user's common topics."""
        return self.profile["habits"]["topics_of_interest"]
    
    def add_topic(self, topic: str):
        """Add topic of interest."""
        topics = self.profile["habits"]["topics_of_interest"]
        if topic not in topics:
            topics.append(topic)
        self.profile["habits"]["topics_of_interest"] = topics[:20]
        self._save()
    
    def get_personalized_prompt(self) -> str:
        """Generate personalized system prompt."""
        prefs = self.profile["preferences"]
        topics = self.get_common_topics()
        
        prompt = f"""You are talking to a user with these preferences:
- Language: {prefs.get('language', 'en')}
- Tone: {prefs.get('tone', 'friendly')}
- Code style: {prefs.get('code_style', 'python')}
- Response length: {prefs.get('response_length', 'medium')}
"""
        
        if topics:
            prompt += f"\nTopics of interest: {', '.join(topics[:5])}"
        
        return prompt


class ProfileManager:
    """Manage multiple user profiles."""
    
    def __init__(self):
        self.profiles_dir = Path("./data/profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def get_profile(self, user_id: str = "default") -> UserProfile:
        """Get or create user profile."""
        return UserProfile(user_id)
    
    def list_profiles(self) -> list:
        """List all profiles."""
        return [p.stem for p in self.profiles_dir.glob("*.json")]
    
    def delete_profile(self, user_id: str):
        """Delete a profile."""
        file = self.profiles_dir / f"{user_id}.json"
        if file.exists():
            file.unlink()


def get_profile(user_id: str = "default") -> UserProfile:
    """Get user profile."""
    return UserProfile(user_id)


if __name__ == "__main__":
    print("User Profiles")
    profile = get_profile("test")
    profile.update_preference("language", "en")
    profile.add_query("hello")
    profile.add_feedback("hello", "Hi!", 5, "Good")
    print(f"Profile: {profile.profile}")