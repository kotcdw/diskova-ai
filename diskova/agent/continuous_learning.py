"""
Continuous Learning System
==========================
Feedback loop to improve agent based on user feedback.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class FeedbackStore:
    """Store and analyze user feedback."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("./data/feedback")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.data_dir / "feedback.json"
        self.feedback = self._load()
    
    def _load(self) -> List[Dict]:
        """Load feedback from file."""
        if self.feedback_file.exists():
            try:
                return json.loads(self.feedback_file.read_text())
            except:
                pass
        return []
    
    def _save(self):
        """Save feedback to file."""
        self.feedback_file.write_text(json.dumps(self.feedback, indent=2))
    
    def add(self, query: str, response: str, rating: int, feedback_type: str = "rating"):
        """Add new feedback."""
        self.feedback.append({
            "query": query,
            "response": response[:500] if len(response) > 500 else response,
            "rating": rating,
            "type": feedback_type,
            "timestamp": datetime.now().isoformat()
        })
        self.feedback = self.feedback[-100:]  # Keep last 100
        self._save()
    
    def get_average_rating(self) -> float:
        """Get average rating."""
        if not self.feedback:
            return 0
        ratings = [f["rating"] for f in self.feedback if "rating" in f]
        return sum(ratings) / len(ratings) if ratings else 0
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        """Get recent feedback."""
        return self.feedback[-n:]
    
    def get_low_rated(self, below: int = 3) -> List[Dict]:
        """Get low rated responses for analysis."""
        return [f for f in self.feedback if f.get("rating", 0) < below]


class LearningEngine:
    """Analyze feedback and improve agent behavior."""
    
    def __init__(self):
        self.feedback = FeedbackStore()
        self.improvements_file = Path("./data/feedback/improvements.json")
        self.improvements = self._load_improvements()
    
    def _load_improvements(self) -> Dict:
        """Load improvements from file."""
        if self.improvements_file.exists():
            try:
                return json.loads(self.improvements_file.read_text())
            except:
                pass
        return {
            "tone_adjustments": {},
            "style_adjustments": {},
            "avoid_phrases": [],
            "preferred_phrases": [],
        }
    
    def _save_improvements(self):
        """Save improvements."""
        self.improvements_file.write_text(json.dumps(self.improvements, indent=2))
    
    def learn_from_feedback(self, rating: int = None):
        """Analyze recent feedback and learn."""
        recent = self.feedback.get_recent(20)
        if rating is not None:
            recent = [f for f in recent if f.get("rating") == rating]
        
        for f in recent:
            query = f.get("query", "").lower()
            
            if f.get("rating", 0) <= 2:
                if len(query) < 50:
                    self.improvements["avoid_phrases"].append(query)
            
            if f.get("rating", 0) >= 4:
                if len(query) < 50:
                    if query not in self.improvements["preferred_phrases"]:
                        self.improvements["preferred_phrases"].append(query)
        
        self.improvements["avoid_phrases"] = list(set(self.improvements["avoid_phrases"]))[-20:]
        self.improvements["preferred_phrases"] = list(set(self.improvements["preferred_phrases"]))[-20:]
        self._save_improvements()
    
    def get_system_hint(self) -> str:
        """Get system hint based on learning."""
        hints = []
        
        if self.improvements.get("avoid_phrases"):
            hints.append(f"Avoid: {', '.join(self.improvements['avoid_phrases'][:3])}")
        
        avg = self.feedback.get_average_rating()
        if avg > 0:
            hints.append(f"Average user rating: {avg:.1f}/5")
        
        return " | ".join(hints) if hints else ""
    
    def should_retry(self, query: str, last_response: str) -> bool:
        """Check if query should be retried with different approach."""
        low_rated = self.feedback.get_low_rated()
        
        for f in low_rated:
            if f.get("query", "").lower() == query.lower():
                return True
        
        return False


def get_learning_engine() -> LearningEngine:
    """Get learning engine instance."""
    return LearningEngine()


if __name__ == "__main__":
    print("Continuous Learning System")
    engine = get_learning_engine()
    engine.feedback.add("test query", "test response", 5)
    engine.learn_from_feedback()
    print(f"Hint: {engine.get_system_hint()}")