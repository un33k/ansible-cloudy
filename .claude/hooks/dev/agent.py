#!/usr/bin/env python
"""Agent hook for handling subagent completion events."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv



class AgentHook:
    """Handles subagent completion events including logging and TTS announcements."""

    def __init__(self, log_dir: str = "logs"):
        """Initialize the agent hook with log directory."""
        # Use project root for logs directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.log_path = self.log_dir / "agent.json"

    def announce_completion(self) -> None:
        """Announce subagent completion using the best available TTS service."""
        try:
            # Import the TTS module
            sys.path.insert(0, str(Path(__file__).parent))
            from tts import load_tts
            
            # Use fixed message for subagent completion
            completion_message = "Subagent Complete"
            
            # Use the TTS loader to speak
            tts = load_tts()
            tts.speak(completion_message)
            
        except Exception:
            # Fail silently for any errors
            pass

    def log_event(self, input_data: Dict[str, Any]) -> None:
        """Log the subagent event to the log file."""
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

    def handle_chat_export(self, input_data: Dict[str, Any]) -> None:
        """Export transcript to chat.json if requested."""
        transcript_path = input_data.get('transcript_path')
        if not transcript_path or not os.path.exists(transcript_path):
            return
        
        # Read .jsonl file and convert to JSON array
        chat_data = []
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            chat_data.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass  # Skip invalid lines
            
            # Write to logs/chat.json
            chat_file = self.log_dir / 'chat.json'
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2)
        except Exception:
            pass  # Fail silently

    def process(self, input_data: Dict[str, Any], export_chat: bool = False) -> None:
        """Process the subagent completion event."""
        # Log the event
        self.log_event(input_data)
        
        # Handle chat export if requested
        if export_chat:
            self.handle_chat_export(input_data)
        
        # Announce completion
        self.announce_completion()


def main():
    """Main entry point for the agent hook."""
    # Load environment variables
    load_dotenv()
    
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Agent hook for subagent completion")
        parser.add_argument('--chat', action='store_true', help='Copy transcript to chat.json')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Create agent hook and process the event
        agent = AgentHook()
        agent.process(input_data, export_chat=args.chat)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()