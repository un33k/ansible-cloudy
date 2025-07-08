#!/usr/bin/env python
"""Pre-tool-use validator for Claude tool calls."""

import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_blocked: bool
    message: str = ""
    exit_code: int = 0


class PreToolValidator:
    """Validates and logs Claude tool usage before execution."""
    
    # Tools that can access files
    FILE_ACCESS_TOOLS = {'Read', 'Edit', 'MultiEdit', 'Write', 'Bash'}
    
    # Tools that directly manipulate files
    FILE_MANIPULATION_TOOLS = {'Read', 'Edit', 'MultiEdit', 'Write'}
    
    # Dangerous rm command patterns
    DANGEROUS_RM_PATTERNS = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf, rm -fr, rm -Rf, etc.
        r'\brm\s+--recursive\s+--force|\brm\s+--force\s+--recursive',  # long form
        r'\brm\s+-[rf]\s+.*-[rf]',  # rm -r ... -f or rm -f ... -r
    ]
    
    # Dangerous paths for rm commands
    DANGEROUS_PATHS = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~',           # Home directory
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards in general rm -rf context
        r'\.',          # Current directory
        r'\.\s*$',      # Current directory at end of command
    ]
    
    # Patterns for .env file access
    ENV_FILE_PATTERNS = [
        r'\b\.env\b(?!\.sample)',  # .env but not .env.sample
        r'(cat|echo|touch|cp|mv)\s+.*\.env\b(?!\.sample)',  # commands with .env
    ]
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the validator with log directory."""
        # Use project root for logs directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "pre.json"
    
    def is_dangerous_rm_command(self, command: str) -> bool:
        """
        Check if a command is a dangerous rm command.
        
        Args:
            command: The bash command to check
            
        Returns:
            True if the command is dangerous
        """
        # Normalize command by removing extra spaces and converting to lowercase
        normalized = ' '.join(command.lower().split())
        
        # Check for dangerous rm patterns
        if any(re.search(pattern, normalized) for pattern in self.DANGEROUS_RM_PATTERNS):
            return True
        
        # Check for rm with recursive flag targeting dangerous paths
        if re.search(r'\brm\s+.*-[a-z]*r', normalized):  # If rm has recursive flag
            return any(re.search(path, normalized) for path in self.DANGEROUS_PATHS)
        
        return False
    
    def is_env_file_access(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        Check if a tool is trying to access .env files.
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters for the tool
            
        Returns:
            True if accessing .env files
        """
        if tool_name not in self.FILE_ACCESS_TOOLS:
            return False
        
        # Check file paths for file-based tools
        if tool_name in self.FILE_MANIPULATION_TOOLS:
            file_path = tool_input.get('file_path', '')
            if '.env' in file_path and not file_path.endswith('.env.sample'):
                return True
        
        # Check bash commands for .env file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            return any(re.search(pattern, command) for pattern in self.ENV_FILE_PATTERNS)
        
        return False
    
    def validate_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> ValidationResult:
        """
        Validate a tool call for security issues.
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters for the tool
            
        Returns:
            ValidationResult with blocking status and message
        """
        # Check for .env file access
        if self.is_env_file_access(tool_name, tool_input):
            return ValidationResult(
                is_blocked=True,
                message="BLOCKED: Access to .env files containing sensitive data is prohibited\n"
                        "Use .env.sample for template files instead",
                exit_code=2
            )
        
        # Check for dangerous rm commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if self.is_dangerous_rm_command(command):
                return ValidationResult(
                    is_blocked=True,
                    message="BLOCKED: Dangerous rm command detected and prevented",
                    exit_code=2
                )
        
        # Validation passed
        return ValidationResult(is_blocked=False)
    
    def log_tool_call(self, input_data: Dict[str, Any]) -> None:
        """Log the tool call to file."""
        # Load existing logs
        log_data: List[Dict[str, Any]] = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, ValueError, IOError):
                log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Save logs
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Fail silently if unable to write
    
    def process(self, input_data: Dict[str, Any]) -> int:
        """
        Process and validate a tool call.
        
        Args:
            input_data: The tool call data
            
        Returns:
            Exit code (0 for success, 2 for blocked)
        """
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Validate the tool call
        validation = self.validate_tool_call(tool_name, tool_input)
        
        if validation.is_blocked:
            # Print error message to stderr
            print(validation.message, file=sys.stderr)
            return validation.exit_code
        
        # Log the tool call
        self.log_tool_call(input_data)
        
        return 0


def main():
    """Main entry point for the pre-tool validator."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Create validator and process
        validator = PreToolValidator()
        exit_code = validator.process(input_data)
        
        sys.exit(exit_code)
        
    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()