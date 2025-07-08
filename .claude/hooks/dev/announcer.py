#!/usr/bin/env python
"""Shared announcement system for Claude hooks."""

import os
import sys
import random
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum
from dotenv import load_dotenv


class EventType(Enum):
    """Types of events that can be announced."""
    BLOCKED = "blocked"
    UNAUTHORIZED = "unauthorized"
    ERROR = "error"
    ATTENTION = "attention"
    SUCCESS = "success"
    WARNING = "warning"


class EventAnnouncer:
    """Handles TTS announcements for various event types."""
    
    # Event-specific message templates
    EVENT_MESSAGES = {
        EventType.BLOCKED: [
            "Command blocked for safety",
            "Operation prevented",
            "Access denied for security",
            "Command not allowed",
            "Blocked for your protection"
        ],
        EventType.UNAUTHORIZED: [
            "Unauthorized access attempted",
            "Permission denied",
            "Access not permitted",
            "Authorization required",
            "Insufficient permissions"
        ],
        EventType.ERROR: [
            "Error occurred",
            "Operation failed",
            "Something went wrong",
            "Task failed",
            "Error detected"
        ],
        EventType.ATTENTION: [
            "Needs your attention",
            "Review required",
            "Your input needed",
            "Check this please",
            "Attention required"
        ],
        EventType.SUCCESS: [
            "Operation successful",
            "Task completed",
            "Success",
            "Done",
            "Completed successfully"
        ],
        EventType.WARNING: [
            "Warning",
            "Caution advised",
            "Please be aware",
            "Warning issued",
            "Take note"
        ]
    }
    
    def __init__(self, include_name_probability: float = 0.3):
        """
        Initialize the event announcer.
        
        Args:
            include_name_probability: Probability of including engineer name
        """
        load_dotenv()
        self.include_name_probability = include_name_probability
        self.engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        
        # Setup logging
        project_root = Path(__file__).parent.parent.parent.parent
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
    
    def get_message(self, event_type: EventType, custom_message: Optional[str] = None) -> str:
        """
        Get announcement message for an event type.
        
        Args:
            event_type: Type of event
            custom_message: Optional custom message to use instead
            
        Returns:
            Message to announce
        """
        if custom_message:
            base_message = custom_message
        else:
            messages = self.EVENT_MESSAGES.get(event_type, ["Event occurred"])
            base_message = random.choice(messages)
        
        # Optionally prepend engineer name
        if self.engineer_name and random.random() < self.include_name_probability:
            return f"{self.engineer_name}, {base_message.lower()}"
        
        return base_message
    
    def announce(self, event_type: EventType, custom_message: Optional[str] = None) -> bool:
        """
        Announce an event via TTS.
        
        Args:
            event_type: Type of event to announce
            custom_message: Optional custom message
            
        Returns:
            True if announcement was successful
        """
        try:
            # Import TTS module
            sys.path.insert(0, str(Path(__file__).parent))
            from tts import load_tts
            
            # Get message
            message = self.get_message(event_type, custom_message)
            
            # Try to speak
            tts = load_tts()
            success = tts.speak(message)
            
            # Log attempt
            self._log_announcement(event_type, message, success)
            
            return success
            
        except Exception as e:
            # Log failure
            self._log_announcement(event_type, "TTS failed", False, str(e))
            return False
    
    def _log_announcement(self, event_type: EventType, message: str, success: bool, error: Optional[str] = None) -> None:
        """Log announcement attempt."""
        try:
            with open(self.log_dir / "announcements.log", "a") as f:
                status = "SUCCESS" if success else "FAILED"
                error_msg = f" - {error}" if error else ""
                f.write(f"[{event_type.value}] {status}: {message}{error_msg}\n")
        except:
            pass  # Fail silently


def announce_event(event_type: EventType, custom_message: Optional[str] = None) -> bool:
    """
    Convenience function to announce an event.
    
    Args:
        event_type: Type of event to announce
        custom_message: Optional custom message
        
    Returns:
        True if announcement was successful
    """
    announcer = EventAnnouncer()
    return announcer.announce(event_type, custom_message)


if __name__ == "__main__":
    # Test the announcer
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python announcer.py <event_type> [custom_message]")
        print(f"Event types: {', '.join(e.value for e in EventType)}")
        sys.exit(1)
    
    try:
        event_type = EventType(sys.argv[1])
        custom_message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        
        success = announce_event(event_type, custom_message)
        sys.exit(0 if success else 1)
        
    except ValueError:
        print(f"Invalid event type. Choose from: {', '.join(e.value for e in EventType)}")
        sys.exit(1)