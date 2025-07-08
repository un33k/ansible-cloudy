#!/usr/bin/env python
"""Post-tool-use logger for tracking Claude tool usage events."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


class PostToolLogger:
    """Handles logging of post-tool-use events from Claude."""
    
    def __init__(self, log_dir: str = "logs", log_filename: str = "post.json"):
        """
        Initialize the post-tool logger.
        
        Args:
            log_dir: Directory for storing logs
            log_filename: Name of the log file
        """
        self.log_dir = Path(__file__).parent.parent / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / log_filename
    
    def load_existing_logs(self) -> List[Dict[str, Any]]:
        """Load existing log data from file."""
        if not self.log_path.exists():
            return []
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError, IOError):
            # Return empty list if file is corrupted or unreadable
            return []
    
    def save_logs(self, log_data: List[Dict[str, Any]]) -> None:
        """Save log data to file with proper formatting."""
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except IOError:
            # Fail silently if unable to write
            pass
    
    def log_event(self, event_data: Dict[str, Any]) -> None:
        """
        Log a single post-tool-use event.
        
        Args:
            event_data: The event data to log
        """
        # Load existing logs
        log_data = self.load_existing_logs()
        
        # Append new event
        log_data.append(event_data)
        
        # Save updated logs
        self.save_logs(log_data)
    
    def process_stdin(self) -> Optional[Dict[str, Any]]:
        """
        Read and parse JSON data from stdin.
        
        Returns:
            Parsed JSON data or None if parsing fails
        """
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError:
            return None
    
    def run(self) -> int:
        """
        Main processing method.
        
        Returns:
            Exit code (0 for success)
        """
        # Read input data
        input_data = self.process_stdin()
        
        # Log the event if we got valid data
        if input_data is not None:
            self.log_event(input_data)
        
        return 0


def main():
    """Main entry point for the post-tool logger."""
    try:
        # Create logger and run
        logger = PostToolLogger()
        exit_code = logger.run()
        sys.exit(exit_code)
        
    except Exception:
        # Exit cleanly on any unexpected error
        sys.exit(0)


if __name__ == '__main__':
    main()