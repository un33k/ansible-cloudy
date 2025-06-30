#!/usr/bin/env python3
"""
Test Runner for Claudia CLI

Run the Claudia test suite with various options.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run the test suite"""
    # Change to the claudia directory
    claudia_dir = Path(__file__).parent
    
    # Basic pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Run pytest
    print(f"Running tests from: {claudia_dir}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd, cwd=claudia_dir)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())