#!/usr/bin/env python
"""Notification handler for Claude agent input requests."""

import argparse
import json
import os
import sys
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv


class NotificationHandler:
    """Handles notifications when Claude agent needs user input."""
    
    # Messages to skip TTS for
    SKIP_MESSAGES = {'Claude is waiting for your input'}
    
    def __init__(self, log_dir: str = "logs", name_probability: float = 0.3):
        """
        Initialize the notification handler.
        
        Args:
            log_dir: Directory for storing notification logs
            name_probability: Probability of including engineer name in message
        """
        # Use project root for logs directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.log_path = self.log_dir / "notify.json"
        self.name_probability = name_probability
        
    
    def create_notification_message(self) -> str:
        """Create the notification message, possibly including engineer name."""
        engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        
        # Include name with configured probability
        if engineer_name and random.random() < self.name_probability:
            return f"{engineer_name}, your agent needs your input"
        else:
            return "Your agent needs your input"
    
    def announce(self) -> None:
        """Announce the notification via TTS."""
        try:
            # Import the TTS module
            sys.path.insert(0, str(Path(__file__).parent))
            from tts import load_tts
            
            message = self.create_notification_message()
            
            # Use the TTS loader to speak
            tts = load_tts()
            tts.speak(message)
            
        except Exception:
            # Fail silently for any errors
            pass
    
    def log_notification(self, input_data: Dict[str, Any]) -> None:
        """Log the notification event."""
        # Read existing log data or initialize empty list
        log_data: List[Dict[str, Any]] = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
    
    def should_announce(self, input_data: Dict[str, Any]) -> bool:
        """Determine if TTS announcement should be made."""
        message = input_data.get('message', '')
        return message not in self.SKIP_MESSAGES
    
    def process(self, input_data: Dict[str, Any], notify_enabled: bool = False) -> None:
        """Process the notification event."""
        # Always log the notification
        self.log_notification(input_data)
        
        # Announce via TTS if enabled and appropriate
        if notify_enabled and self.should_announce(input_data):
            self.announce()


def main():
    """Main entry point for the notification handler."""
    # Load environment variables
    load_dotenv()
    
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Handle Claude agent notifications")
        parser.add_argument('--notify', action='store_true', help='Enable TTS notifications')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Create handler and process the notification
        handler = NotificationHandler()
        handler.process(input_data, notify_enabled=args.notify)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()