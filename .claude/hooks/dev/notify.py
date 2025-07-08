#!/usr/bin/env python
"""Notification handler for Claude agent input requests."""

import argparse
import json
import os
import sys
import subprocess
import random
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        """Dummy function when dotenv is not available."""
        pass


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
        self.log_dir = Path(os.getcwd()) / log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.log_path = self.log_dir / "notification.json"
        self.name_probability = name_probability
        
    def get_tts_script_path(self) -> Optional[str]:
        """
        Determine which TTS script to use based on available API keys.
        Priority order: ElevenLabs > OpenAI > pyttsx3
        """
        script_dir = Path(__file__).parent
        tts_dir = script_dir / "utils" / "tts"
        
        # Define TTS providers in priority order
        tts_providers = [
            {"env_key": "ELEVENLABS_API_KEY", "script": "elevenlabs_tts.py"},
            {"env_key": "OPENAI_API_KEY", "script": "openai_tts.py"},
            {"env_key": None, "script": "pyttsx3_tts.py"},  # No API key required
        ]
        
        # Check each provider in order
        for provider in tts_providers:
            # Skip if API key is required but not present
            if provider["env_key"] and not os.getenv(provider["env_key"]):
                continue
            
            # Check if script exists
            script_path = tts_dir / provider["script"]
            if script_path.exists():
                return str(script_path)
        
        return None
    
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
            tts_script = self.get_tts_script_path()
            if not tts_script:
                return  # No TTS scripts available
            
            message = self.create_notification_message()
            
            # Call the TTS script with the notification message
            subprocess.run(
                ["uv", "run", tts_script, message],
                capture_output=True,  # Suppress output
                timeout=10,  # 10-second timeout
                check=False
            )
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Fail silently if TTS encounters issues
            pass
        except Exception:
            # Fail silently for any other errors
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