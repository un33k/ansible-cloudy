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
  {Colors.GREEN}cli security --install{Colors.NC}         Setup server security (run first!)
  {Colors.GREEN}cli base --install --prod{Colors.NC}      Setup base config in production
  {Colors.GREEN}cli psql --install --ci{Colors.NC}        Install PostgreSQL in CI environment
  {Colors.GREEN}cli psql --install --port 5544{Colors.NC} Install PostgreSQL on custom port
  {Colors.GREEN}cli psql --install --pgis{Colors.NC}      Install PostgreSQL with PostGIS
  {Colors.GREEN}cli psql --adduser foo --password 1234{Colors.NC}  Create PostgreSQL user
  
  {Colors.GREEN}cli redis --install --memory 512{Colors.NC}  Install Redis with 512MB memory
  {Colors.GREEN}cli --list-services{Colors.NC}            Show all available services
  
  {Colors.GREEN}cli dev validate{Colors.NC}               Run comprehensive validation
  {Colors.GREEN}cli dev syntax{Colors.NC}                Quick syntax checking  
  {Colors.GREEN}cli dev test{Colors.NC}                  Authentication testing

{Colors.YELLOW}Environment Selection:{Colors.NC}
  {Colors.GREEN}cli security --install --dev{Colors.NC}   Use development environment (default)
  {Colors.GREEN}cli security --install --prod{Colors.NC}  Use production environment
  {Colors.GREEN}cli security --install --ci{Colors.NC}    Use CI environment
  {Colors.GREEN}cli security --install -i my-inventory.yml{Colors.NC}  Use custom inventory
  {Colors.GREEN}cli security --install -e vault/prod.yml{Colors.NC}    Use custom vault file

{Colors.YELLOW}Advanced:{Colors.NC}
  {Colors.GREEN}cli psql --install -- --tags postgresql{Colors.NC}  Pass args to ansible-playbook
  {Colors.GREEN}cli psql --install -- -e "grunt_user=myuser"{Colors.NC}  Override variables
  {Colors.GREEN}cli redis --install -- --skip-tags firewall{Colors.NC}  Skip specific tasks
  
{Colors.BLUE}Authentication Flow:{Colors.NC}
  1. {Colors.YELLOW}Security Setup{Colors.NC}: Uses root password, installs SSH keys
  2. {Colors.YELLOW}All Other Operations{Colors.NC}: Uses grunt user with SSH keys only

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
    # Environment selection arguments (mutually exclusive)
    env_group = parser.add_mutually_exclusive_group()
    env_group.add_argument(
        "--prod",
        "--production",
        action="store_true",
        help="Use production environment (inventory/prod.yml)",
    )
    env_group.add_argument(
        "--dev",
        "--development",
        action="store_true",
        help="Use development environment (inventory/dev.yml) [default]",
    )
    env_group.add_argument(
        "--ci",
        "--continuous-integration",
        action="store_true",
        help="Use CI environment (inventory/ci.yml)",
    )
    
    # Inventory and extra vars arguments
    parser.add_argument(
        "-i", "--inventory",
        dest="inventory_path",
        help="Custom inventory file path (overrides environment selection)",
    )
    parser.add_argument(
        "-e", "--extra-vars",
        dest="extra_vars_file",
        help="Extra variables file path (e.g., vault file)",
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
    parser.add_argument(
        "-H", "--host",
        dest="target_host",
        help="Target host IP address (overrides inventory)",
    )

    return parser


def split_arguments():
    """Split command line arguments into cli and ansible args"""
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
    # Parse cli arguments
    parser = create_parser()
    args, remaining_args = parser.parse_known_args(claudia_args)
    
    return args, remaining_args
