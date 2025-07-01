"""
Claudia CLI Help System
Provides colored help formatting and command-specific help displays
"""

import argparse
import re
from pathlib import Path
import sys

# Add parent directory to path for imports
claudia_dir = Path(__file__).parent.parent
sys.path.insert(0, str(claudia_dir))

from utils.colors import Colors  # noqa: E402


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter with colors"""

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = f"\n\n{Colors.CYAN}Usage:{Colors.NC} "
        return super()._format_usage(usage, actions, groups, prefix)

    def format_help(self):
        help_text = super().format_help()
        # Add initial newline for spacing
        help_text = "\n" + help_text
        # Add colors to section headers
        help_text = help_text.replace(
            "positional arguments:",
            f"{Colors.BLUE}positional arguments:{Colors.NC}",
        )
        help_text = help_text.replace(
            "options:", f"{Colors.BLUE}options:{Colors.NC}"
        )

        # Color individual arguments and options
        help_text = re.sub(
            r"^  (command|subcommand)(\s+)",
            f"  {Colors.GREEN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        # Color option flags
        help_text = re.sub(
            r"^  ((?:-[a-zA-Z-]+(?:, --[a-zA-Z-]+)?|--[a-zA-Z-]+(?:, -[a-zA-Z])?))(\\s+)",
            f"  {Colors.CYAN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        return help_text


def show_validate_help():
    """Show detailed help for the validate command"""
    print(f"{Colors.CYAN}Claudia Development - Structural Validation{Colors.NC}")
    print(f"{Colors.YELLOW}Ansible structural validation using validate.py{Colors.NC}\n")
    
    print(f"{Colors.BLUE}Usage:{Colors.NC}")
    print(f"  {Colors.GREEN}cli dev validate{Colors.NC}                # Run structural validation")
    print(f"  {Colors.GREEN}cli dev validate --help{Colors.NC}        # Show this help\n")
    
    print(f"{Colors.BLUE}What it does:{Colors.NC}")
    print(f"  • Validates Ansible project structure")
    print(f"  • Checks task file organization")
    print(f"  • Verifies template references")
    print(f"  • Ensures proper directory layout\n")
    
    print(f"{Colors.BLUE}📊 Command Priority Reference:{Colors.NC}")
    print(f"┌─────────────┬──────────────────┬─────────────────────────────────────┬─────────────────────┐")
    print(f"│ {Colors.BLUE}Priority{Colors.NC}     │ {Colors.BLUE}Command{Colors.NC}           │ {Colors.BLUE}Purpose{Colors.NC}                              │ {Colors.BLUE}Required?{Colors.NC}           │")
    print(f"├─────────────┼──────────────────┼─────────────────────────────────────┼─────────────────────┤")
    print(f"│ 🔴 Critical  │ dev precommit    │ All validation checks (pre-commit)  │ ✅ Yes               │")
    print(f"│ 🟡 Important │ dev validate     │ Structural validation               │ 📋 Before releases   │")
    print(f"│ 🟡 Important │ dev yamlint      │ YAML formatting                     │ 📋 Recommended       │")
    print(f"│ 🟢 Optional  │ dev flake8       │ Python code quality                 │ 📋 If CLI changes    │")
    print(f"│ 🟢 Optional  │ dev spell        │ Documentation spelling              │ 📋 If docs changes   │")
    print(f"│ 🔵 Testing   │ dev test         │ Authentication testing              │ ❓ If server available│")
    print(f"└─────────────┴──────────────────┴─────────────────────────────────────┴─────────────────────┘\n")
    
    print(f"{Colors.BLUE}💡 Recommendations:{Colors.NC}")
    print(f"  {Colors.GREEN}Before every commit:{Colors.NC}")
    print(f"    cli dev precommit         # Run all validation checks")
    print(f"")
    print(f"  {Colors.GREEN}Before testing deployment:{Colors.NC}")
    print(f"    cli dev test              # Test authentication flow")
    print(f"")
    print(f"  {Colors.GREEN}For structural validation:{Colors.NC}")
    print(f"    cli dev validate          # Check project structure")
    print(f"")
    print(f"  {Colors.GREEN}For specific checks:{Colors.NC}")
    print(f"    cli dev syntax            # Quick syntax check")
    print(f"    cli dev lint              # Ansible linting")
    print(f"    cli dev yamlint           # YAML formatting")
    print(f"    cli dev flake8            # Python code quality")
    print(f"    cli dev spell             # Documentation spelling\n")
    
    print(f"{Colors.BLUE}⚡ Pro Tips:{Colors.NC}")
    print(f"  • {Colors.CYAN}cli dev precommit{Colors.NC} runs all checks - use before committing")
    print(f"  • {Colors.CYAN}cli dev validate{Colors.NC} focuses on structural validation only")
    print(f"  • Run {Colors.CYAN}cli dev test{Colors.NC} separately when you have server access")
    print(f"  • All commands respect obsolete vault environment variable detection")


def show_dev_commands_help():
    """Show development commands help"""
    print(f"{Colors.CYAN}Claudia Development Commands{Colors.NC}")
    print(f"  {Colors.GREEN}cli dev precommit{Colors.NC}      Run all validation checks before commit")
    print(f"  {Colors.GREEN}cli dev validate{Colors.NC}       Ansible structural validation")
    print(f"  {Colors.GREEN}cli dev syntax{Colors.NC}         Quick syntax checking")
    print(f"  {Colors.GREEN}cli dev test{Colors.NC}           Authentication testing")
    print(f"  {Colors.GREEN}cli dev lint{Colors.NC}           Ansible linting")
    print(f"  {Colors.GREEN}cli dev yamlint{Colors.NC}        YAML linting")
    print(f"  {Colors.GREEN}cli dev flake8{Colors.NC}         Python code linting")
    print(f"  {Colors.GREEN}cli dev spell{Colors.NC}          Spell checking")
    print(f"")
    print(f"{Colors.YELLOW}💡 Use {Colors.GREEN}cli dev precommit{Colors.NC} to run all checks before committing{Colors.NC}")


def show_version():
    """Show version information"""
    print(f"{Colors.CYAN}Claudia{Colors.NC} (Claude-inspired Infrastructure Assistant)")
    print(f"{Colors.YELLOW}Intelligent Infrastructure Management Made Intuitive{Colors.NC}")
    print(f"Version: 1.0.0")
