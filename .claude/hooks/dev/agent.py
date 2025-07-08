#!/usr/bin/env python
"""Agent hook for handling subagent completion events."""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        """Dummy function when dotenv is not available."""
        pass


class AgentHook:
    """Handles subagent completion events including logging and TTS announcements."""

    def __init__(self, log_dir: str = "logs"):
        """Initialize the agent hook with log directory."""
        self.log_dir = Path(__file__).parent.parent / log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.log_path = self.log_dir / "agent.json"

    def get_tts_script_path(self) -> Optional[str]:
        """
        Determine which TTS script to use based on available API keys.
        Priority order: ElevenLabs > OpenAI > pyttsx3
        """
        script_dir = Path(__file__).parent
        tts_dir = script_dir / "utils" / "tts"
        
        # Define TTS providers in priority order
        tts_providers = [
            {"env_key": "ELEVENLABS_API_KEY", "script": "elevenlabs.py"},
            {"env_key": "OPENAI_API_KEY", "script": "openai.py"},
            {"env_key": None, "script": "pyttsx3.py"},  # No API key required
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

    def announce_completion(self) -> None:
        """Announce subagent completion using the best available TTS service."""
        try:
            tts_script = self.get_tts_script_path()
            if not tts_script:
                return  # No TTS scripts available
            
            # Use fixed message for subagent completion
            completion_message = "Subagent Complete"
            
            # Call the TTS script with the completion message
            subprocess.run(
                ["uv", "run", tts_script, completion_message],
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