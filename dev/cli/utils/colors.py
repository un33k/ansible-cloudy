"""
Terminal color utilities for CLI
"""

import sys


class Colors:
    """ANSI color codes for terminal output"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def log(message: str, color: str = Colors.GREEN) -> None:
    """Print colored log message"""
    print(f"\n{color}✓{Colors.NC} {message}\n")


def warn(message: str) -> None:
    """Print warning message"""
    print(f"\n{Colors.YELLOW}⚠{Colors.NC} {message}\n")


def error(message: str) -> None:
    """Print error message and exit"""
    print(f"\n{Colors.RED}✗{Colors.NC} {message}\n")
    sys.exit(1)


def info(message: str) -> None:
    """Print info message"""
    print(f"\n{Colors.BLUE}ℹ{Colors.NC} {message}\n")
