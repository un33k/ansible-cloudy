#!/usr/bin/env python
"""Stop hook processor for Claude sessions."""

import argparse
import json
import os
import sys
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class CompletionConfig:
    """Configuration for completion announcements."""
    messages: List[str]
    tts_priority: List[str]
    llm_priority: List[str]


class StopHookProcessor:
    """Processes stop hooks for Claude sessions."""
    
    # Default completion messages
    DEFAULT_COMPLETION_MESSAGES = [
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!"
    ]
    
    # TTS service priority order
    TTS_PRIORITY = ['elevenlabs', 'openai', 'pytts']
    
    # LLM service priority order
    LLM_PRIORITY = ['openai', 'anthropic']
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the stop hook processor.
        
        Args:
            log_dir: Directory for storing logs
        """
        # Use project root for logs directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "stop.json"
        
        # Setup paths for utility scripts
        self.script_dir = Path(__file__).parent
        
        # Configuration
        self.config = CompletionConfig(
            messages=self.DEFAULT_COMPLETION_MESSAGES,
            tts_priority=self.TTS_PRIORITY,
            llm_priority=self.LLM_PRIORITY
        )
    
    
    def get_llm_completion_message(self) -> str:
        """
        Generate completion message.
        
        Returns:
            Fallback completion message (LLM integration removed)
        """
        # LLM integration has been removed - just use predefined messages
        return random.choice(self.config.messages)
    
    def announce_completion(self) -> None:
        """Announce completion using the best available TTS service."""
        try:
            # Import the TTS module
            sys.path.insert(0, str(Path(__file__).parent))
            from tts import load_tts
            
            # Get completion message
            completion_message = self.get_llm_completion_message()
            
            # Use the TTS loader to speak
            tts = load_tts()
            available = tts.list_available()
            speak_result = tts.speak(completion_message)
            
            if not speak_result:
                # Debug: log the failure
                with open(self.log_dir / "tts_debug.log", "a") as f:
                    f.write(f"TTS failed to speak: {completion_message}\n")
                    f.write(f"Available providers: {available}\n")
                    f.write(f"Speak result: {speak_result}\n")
            
        except Exception as e:
            # Debug: log the exception
            with open(self.log_dir / "tts_debug.log", "a") as f:
                f.write(f"TTS exception: {str(e)}\n")
    
    def log_session_data(self, input_data: Dict[str, Any]) -> None:
        """
        Log session data to file.
        
        Args:
            input_data: The session data to log
        """
        # Read existing log data or initialize empty list
        log_data: List[Dict[str, Any]] = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, ValueError, IOError):
                log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Fail silently if unable to write
    
    def handle_chat_export(self, transcript_path: str) -> None:
        """
        Export transcript to chat.json format.
        
        Args:
            transcript_path: Path to the transcript file
        """
        if not os.path.exists(transcript_path):
            return
        
        chat_data: List[Dict[str, Any]] = []
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
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Fail silently
    
    def process(self, input_data: Dict[str, Any], args: argparse.Namespace) -> int:
        """
        Process the stop hook.
        
        Args:
            input_data: The input data from Claude
            args: Command line arguments
            
        Returns:
            Exit code (0 for success)
        """
        # Log session data
        self.log_session_data(input_data)
        
        # Handle chat export if requested
        if args.chat and 'transcript_path' in input_data:
            self.handle_chat_export(input_data['transcript_path'])
        
        # Announce completion
        self.announce_completion()
        
        return 0


def main():
    """Main entry point for the stop hook processor."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Stop hook processor for Claude sessions")
        parser.add_argument('--chat', action='store_true', help='Copy transcript to chat.json')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Create processor and process
        processor = StopHookProcessor()
        exit_code = processor.process(input_data, args)
        
        sys.exit(exit_code)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()