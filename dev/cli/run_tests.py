#!/usr/bin/env python3
"""
Test Runner for CLI

Run the CLI test suite with various options.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run the test suite"""
    # Change to the cli directory
    cli_dir = Path(__file__).parent
    
    # Basic pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Run pytest
    print(f"Running tests from: {cli_dir}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd, cwd=cli_dir)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
