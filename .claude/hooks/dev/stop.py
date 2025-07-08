#!/usr/bin/env python
"""Stop hook processor for Claude sessions."""

import argparse
import json
import os
import sys
import random
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


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
        self.log_dir = Path(__file__).parent.parent / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "stop.json"
        
        # Setup paths for utility scripts
        self.script_dir = Path(__file__).parent
        self.tts_dir = self.script_dir / "utils" / "tts"
        self.llm_dir = self.script_dir / "utils" / "llm"
        
        # Configuration
        self.config = CompletionConfig(
            messages=self.DEFAULT_COMPLETION_MESSAGES,
            tts_priority=self.TTS_PRIORITY,
            llm_priority=self.LLM_PRIORITY
        )
    
    def get_tts_script_path(self) -> Optional[str]:
        """
        Determine which TTS script to use based on available API keys.
        
        Returns:
            Path to the TTS script or None if not available
        """
        script_mapping = {
            'elevenlabs': ('ELEVENLABS_API_KEY', 'elevenlabs.py'),
            'openai': ('OPENAI_API_KEY', 'openai.py'),
            'pytts': (None, 'pytts.py')  # No API key required
        }
        
        for service in self.config.tts_priority:
            env_key, script_name = script_mapping.get(service, (None, None))
            if script_name:
                # Check if API key exists (if required)
                if env_key is None or os.getenv(env_key):
                    script_path = self.tts_dir / script_name
                    if script_path.exists():
                        return str(script_path)
        
        return None
    
    def get_llm_completion_message(self) -> str:
        """
        Generate completion message using available LLM services.
        
        Returns:
            Generated or fallback completion message
        """
        script_mapping = {
            'openai': ('OPENAI_API_KEY', 'oai.py'),
            'anthropic': ('ANTHROPIC_API_KEY', 'anth.py')
        }
        
        for service in self.config.llm_priority:
            env_key, script_name = script_mapping.get(service, (None, None))
            if script_name and os.getenv(env_key):
                script_path = self.llm_dir / script_name
                if script_path.exists():
                    try:
                        result = subprocess.run(
                            [sys.executable, str(script_path), "--completion"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            return result.stdout.strip()
                    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                        continue
        
        # Fallback to random predefined message
        return random.choice(self.config.messages)
    
    def announce_completion(self) -> None:
        """Announce completion using the best available TTS service."""
        try:
            tts_script = self.get_tts_script_path()
            if not tts_script:
                return  # No TTS scripts available
            
            # Get completion message (LLM-generated or fallback)
            completion_message = self.get_llm_completion_message()
            
            # Call the TTS script with the completion message
            subprocess.run(
                [sys.executable, tts_script, completion_message],
                capture_output=True,  # Suppress output
                timeout=10  # 10-second timeout
            )
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass  # Fail silently if TTS encounters issues
        except Exception:
            pass  # Fail silently for any other errors
    
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