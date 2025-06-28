"""
Terminal color utilities for Ali CLI
"""

import sys

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log(message: str, color: str = Colors.GREEN) -> None:
    """Print colored log message"""
    print(f"{color}✓{Colors.NC} {message}")

def warn(message: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")

def error(message: str) -> None:
    """Print error message and exit"""
    print(f"{Colors.RED}✗{Colors.NC} {message}")
    sys.exit(1)

def info(message: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")