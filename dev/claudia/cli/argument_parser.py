"""
Claudia CLI Argument Parser
Handles command line argument parsing and configuration
"""

import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
claudia_dir = Path(__file__).parent.parent
cli_dir = Path(__file__).parent
sys.path.insert(0, str(claudia_dir))
sys.path.insert(0, str(cli_dir))

from utils.colors import Colors  # noqa: E402
from help_system import ColoredHelpFormatter  # noqa: E402


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}Claudia (Claude-inspired Infrastructure Assistant){Colors.NC}\n{Colors.YELLOW}Intelligent Infrastructure Management Made Intuitive{Colors.NC}",
        formatter_class=ColoredHelpFormatter,
        epilog=f"""
{Colors.YELLOW}Examples:{Colors.NC}
  {Colors.GREEN}claudia security --install{Colors.NC}         Setup server security (run first!)
  {Colors.GREEN}claudia base --install{Colors.NC}             Setup base configuration  
  {Colors.GREEN}claudia psql --install{Colors.NC}             Execute PostgreSQL installation
  {Colors.GREEN}claudia psql --install --port 5544{Colors.NC} Install PostgreSQL on custom port
  {Colors.GREEN}claudia psql --install --pgis{Colors.NC}      Install PostgreSQL with PostGIS
  {Colors.GREEN}claudia psql --adduser foo --password 1234{Colors.NC}  Create PostgreSQL user
  
  {Colors.GREEN}claudia redis --install --memory 512{Colors.NC}  Install Redis with 512MB memory
  {Colors.GREEN}claudia --list-services{Colors.NC}            Show all available services
  
  {Colors.GREEN}claudia dev validate{Colors.NC}               Run comprehensive validation
  {Colors.GREEN}claudia dev syntax{Colors.NC}                Quick syntax checking  
  {Colors.GREEN}claudia dev test{Colors.NC}                  Authentication testing

{Colors.YELLOW}Advanced:{Colors.NC}
  {Colors.GREEN}claudia psql --install -- --tags postgresql{Colors.NC}  Pass args to ansible-playbook
  {Colors.GREEN}claudia psql --install -- -e "admin_user=myuser"{Colors.NC}  Override variables
  {Colors.GREEN}claudia redis --install -- --skip-tags firewall{Colors.NC}  Skip specific tasks
  
{Colors.BLUE}Authentication Flow:{Colors.NC}
  1. {Colors.YELLOW}Security Setup{Colors.NC}: Uses root password, installs SSH keys
  2. {Colors.YELLOW}All Other Operations{Colors.NC}: Uses admin user with SSH keys only

{Colors.BLUE}Note:{Colors.NC} Use {Colors.CYAN}`--`{Colors.NC} to pass parameters directly to ansible-playbook
        """,
    )

    parser.add_argument(
        "service",
        nargs="?",
        help="Service name (psql, redis, nginx) or 'dev' for development commands",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        help="Development subcommand (when using 'dev')",
    )
    parser.add_argument(
        "--prod",
        "--production",
        action="store_true",
        help="Use production inventory instead of test",
    )
    parser.add_argument(
        "--check",
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (--check)",
    )
    parser.add_argument(
        "--list-services",
        "-l",
        action="store_true",
        help="List all available services and operations",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--install",
        "--run",
        action="store_true",
        help="Execute the recipe installation (required to run any recipe)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show Claudia version information",
    )

    return parser


def split_arguments():
    """Split command line arguments into claudia and ansible args"""
    # Parse arguments, splitting on -- for ansible args
    if "--" in sys.argv:
        split_idx = sys.argv.index("--")
        claudia_args = sys.argv[1:split_idx]
        ansible_args = sys.argv[split_idx + 1 :]
    else:
        claudia_args = sys.argv[1:]
        ansible_args = []
    
    return claudia_args, ansible_args


def parse_arguments(claudia_args):
    """Parse command line arguments"""
    # Parse claudia arguments
    parser = create_parser()
    args, remaining_args = parser.parse_known_args(claudia_args)
    
    return args, remaining_args
