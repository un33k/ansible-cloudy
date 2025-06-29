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
    print(f"{Colors.CYAN}Claudia Development - Pre-Commit Validation{Colors.NC}")
    print(f"{Colors.YELLOW}Essential validation suite to run before every commit{Colors.NC}\n")
    
    print(f"{Colors.BLUE}Usage:{Colors.NC}")
    print(f"  {Colors.GREEN}./claudia dev validate{Colors.NC}                # Run pre-commit validation suite")
    print(f"  {Colors.GREEN}./claudia dev validate --help{Colors.NC}        # Show this help\n")
    
    print(f"{Colors.BLUE}What it runs:{Colors.NC}")
    print(f"  1. {Colors.GREEN}Syntax Check{Colors.NC}     - Validates all Ansible YAML files")
    print(f"  2. {Colors.GREEN}Ansible Linting{Colors.NC}  - Code quality and best practices")
    print(f"  3. {Colors.GREEN}YAML Formatting{Colors.NC} - Consistent formatting validation\n")
    
    print(f"{Colors.BLUE}📊 Command Priority Reference:{Colors.NC}")
    print(f"┌─────────────┬──────────────────┬─────────────────────────────────────┬─────────────────────┐")
    print(f"│ {Colors.BLUE}Priority{Colors.NC}     │ {Colors.BLUE}Command{Colors.NC}           │ {Colors.BLUE}Purpose{Colors.NC}                              │ {Colors.BLUE}Required?{Colors.NC}           │")
    print(f"├─────────────┼──────────────────┼─────────────────────────────────────┼─────────────────────┤")
    print(f"│ 🔴 Critical  │ dev validate     │ Pre-commit validation suite         │ ✅ Yes               │")
    print(f"│ 🟡 Important │ dev comprehensive│ Full structure validation           │ 📋 Before releases   │")
    print(f"│ 🟡 Important │ dev yamlint      │ YAML formatting                     │ 📋 Recommended       │")
    print(f"│ 🟢 Optional  │ dev flake8       │ Python code quality                 │ 📋 If CLI changes    │")
    print(f"│ 🟢 Optional  │ dev spell        │ Documentation spelling              │ 📋 If docs changes   │")
    print(f"│ 🔵 Testing   │ dev test         │ Authentication testing              │ ❓ If server available│")
    print(f"└─────────────┴──────────────────┴─────────────────────────────────────┴─────────────────────┘\n")
    
    print(f"{Colors.BLUE}💡 Recommendations:{Colors.NC}")
    print(f"  {Colors.GREEN}Before every commit:{Colors.NC}")
    print(f"    ./claudia dev validate")
    print(f"")
    print(f"  {Colors.GREEN}Before testing deployment:{Colors.NC}")
    print(f"    ./claudia dev test         # Test authentication flow")
    print(f"")
    print(f"  {Colors.GREEN}For comprehensive validation:{Colors.NC}")
    print(f"    ./claudia dev comprehensive")
    print(f"    ./claudia dev yamlint")
    print(f"    ./claudia dev flake8       # If you modified CLI code")
    print(f"    ./claudia dev spell        # If you modified documentation\n")
    
    print(f"{Colors.BLUE}⚡ Pro Tips:{Colors.NC}")
    print(f"  • {Colors.CYAN}./claudia dev validate{Colors.NC} is designed to be fast for frequent use")
    print(f"  • Run {Colors.CYAN}./claudia dev test{Colors.NC} separately when you have server access")
    print(f"  • Use {Colors.CYAN}./claudia dev comprehensive{Colors.NC} for thorough validation before releases")
    print(f"  • All commands respect obsolete vault environment variable detection")


def show_dev_commands_help():
    """Show development commands help"""
    print(f"{Colors.CYAN}Claudia Development Commands{Colors.NC}")
    print(f"  {Colors.GREEN}claudia dev validate{Colors.NC}    Pre-commit validation suite (recommended)")
    print(f"  {Colors.GREEN}claudia dev comprehensive{Colors.NC} Comprehensive validation (includes structure)")
    print(f"  {Colors.GREEN}claudia dev syntax{Colors.NC}     Quick syntax checking")
    print(f"  {Colors.GREEN}claudia dev test{Colors.NC}       Authentication testing")
    print(f"  {Colors.GREEN}claudia dev lint{Colors.NC}       Ansible linting")
    print(f"  {Colors.GREEN}claudia dev yamlint{Colors.NC}    YAML linting")
    print(f"  {Colors.GREEN}claudia dev flake8{Colors.NC}     Python code linting")
    print(f"  {Colors.GREEN}claudia dev spell{Colors.NC}      Spell checking")
    print(f"")
    print(f"{Colors.YELLOW}💡 Use {Colors.GREEN}./claudia dev validate --help{Colors.NC} for detailed guidance{Colors.NC}")


def show_version():
    """Show version information"""
    print(f"{Colors.CYAN}Claudia{Colors.NC} (Claude-inspired Infrastructure Assistant)")
    print(f"{Colors.YELLOW}Intelligent Infrastructure Management Made Intuitive{Colors.NC}")
    print(f"Version: 1.0.0")
