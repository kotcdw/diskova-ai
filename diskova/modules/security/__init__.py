"""
Security Module - Authentication, Monitoring, Alerts
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import secrets


@dataclass
class LoginAttempt:
    user_id: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    location: Optional[str] = None


@dataclass
class SecurityAlert:
    id: str
    type: str
    severity: str
    message: str
    timestamp: datetime
    acknowledged: bool = False


class SecurityModule:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.failed_attempts: Dict[str, int] = {}
        self.lockout_until: Dict[str, datetime] = {}

    def track_login(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        location: Optional[str] = None
    ) -> LoginAttempt:
        attempt = LoginAttempt(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            success=success,
            location=location
        )
        
        self.memory.store_preference(f"login_{attempt.timestamp.timestamp()}", user_id, {
            "ip_address": attempt.ip_address,
            "user_agent": attempt.user_agent,
            "success": attempt.success,
            "timestamp": attempt.timestamp.isoformat(),
            "location": attempt.location
        })
        
        if not success:
            self._handle_failed_attempt(user_id)
        else:
            self._reset_failed_attempts(user_id)
        
        return attempt

    def _handle_failed_attempt(self, user_id: str):
        self.failed_attempts[user_id] = self.failed_attempts.get(user_id, 0) + 1
        
        if self.failed_attempts[user_id] >= 5:
            self.lockout_until[user_id] = datetime.now() + timedelta(minutes=30)
            self._create_alert(
                user_id=user_id,
                alert_type="account_locked",
                severity="high",
                message=f"Account locked due to {self.failed_attempts[user_id]} failed login attempts"
            )

    def _reset_failed_attempts(self, user_id: str):
        self.failed_attempts[user_id] = 0

    def is_locked_out(self, user_id: str) -> bool:
        if user_id in self.lockout_until:
            if datetime.now() > self.lockout_until[user_id]:
                del self.lockout_until[user_id]
                self.failed_attempts[user_id] = 0
                return False
            return True
        return False

    def get_login_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        history = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("login_") and isinstance(value, dict):
                history.append(value)
        
        return sorted(
            history,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:limit]

    def create_alert(
        self,
        user_id: str,
        alert_type: str,
        severity: str,
        message: str
    ) -> SecurityAlert:
        alert_id = hashlib.md5(f"{alert_type}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        alert = SecurityAlert(
            id=alert_id,
            type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )
        
        self.memory.store_preference(f"alert_{alert_id}", user_id, {
            "id": alert.id,
            "type": alert.type,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "acknowledged": alert.acknowledged
        })
        
        return alert

    def get_alerts(
        self,
        user_id: str,
        acknowledged: Optional[bool] = None,
        severity: Optional[str] = None
    ) -> List[Dict]:
        alerts = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("alert_") and isinstance(value, dict):
                alert = value
                
                if acknowledged is not None and alert.get("acknowledged") != acknowledged:
                    continue
                if severity and alert.get("severity") != severity:
                    continue
                
                alerts.append(alert)
        
        return sorted(
            alerts,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

    def acknowledge_alert(self, user_id: str, alert_id: str) -> bool:
        prefs = self.memory.get_user_context(user_id).preferences
        alert_key = f"alert_{alert_id}"
        
        if alert_key in prefs:
            prefs[alert_key]["acknowledged"] = True
            return True
        return False

    def generate_2fa_code(self, user_id: str) -> str:
        code = secrets.token_hex(3).upper()
        self.memory.store_preference(f"2fa_{user_id}", "current_code", code)
        self.memory.store_preference(f"2fa_{user_id}", "code_expiry", 
            (datetime.now() + timedelta(minutes=5)).isoformat())
        return code

    def verify_2fa_code(self, user_id: str, code: str) -> bool:
        stored_code = self.memory.get_preference(f"2fa_{user_id}", "current_code")
        expiry_str = self.memory.get_preference(f"2fa_{user_id}", "code_expiry")
        
        if not stored_code or not expiry_str:
            return False
        
        expiry = datetime.fromisoformat(expiry_str)
        if datetime.now() > expiry:
            return False
        
        return stored_code == code.upper()

    def check_suspicious_activity(self, user_id: str, ip_address: str) -> bool:
        history = self.get_login_history(user_id, limit=10)
        
        if len(history) < 2:
            return False
        
        recent_ips = set(h.get("ip_address") for h in history[:3])
        
        if ip_address not in recent_ips and len(recent_ips) > 1:
            self.create_alert(
                user_id=user_id,
                alert_type="suspicious_login",
                severity="medium",
                message=f"New login from different IP: {ip_address}"
            )
            return True
        
        return False
