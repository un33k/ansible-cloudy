"""
CLI Argument Parser
Handles command line argument parsing and configuration
"""

import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
cli_dir = Path(__file__).parent.parent
cmd_dir = Path(__file__).parent
sys.path.insert(0, str(cli_dir))
sys.path.insert(0, str(cmd_dir))

from utils.colors import Colors  # noqa: E402
from help_system import ColoredHelpFormatter  # noqa: E402


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser with subparsers"""
    parser = argparse.ArgumentParser(
        prog='cli',
        description=f"{Colors.CYAN}CLI - Intelligent Infrastructure Management{Colors.NC}\n{Colors.YELLOW}Made Intuitive{Colors.NC}",
        formatter_class=ColoredHelpFormatter,
        epilog=f"""
{Colors.YELLOW}Quick Start:{Colors.NC}
  {Colors.GREEN}cli security --install{Colors.NC}         Setup server security (run first!)
  {Colors.GREEN}cli base --install{Colors.NC}             Setup base configuration
  {Colors.GREEN}cli psql --install{Colors.NC}             Install PostgreSQL
  {Colors.GREEN}cli finalize --install{Colors.NC}         Finalize with upgrades

{Colors.YELLOW}Getting Help:{Colors.NC}
  {Colors.GREEN}cli --help{Colors.NC}                     Show this help
  {Colors.GREEN}cli <service> --help{Colors.NC}           Show service-specific help
  {Colors.GREEN}cli dev --help{Colors.NC}                 Show development commands
  {Colors.GREEN}cli dev <command> --help{Colors.NC}       Show specific dev command help

{Colors.BLUE}Note:{Colors.NC} Use {Colors.CYAN}`--`{Colors.NC} to pass parameters directly to ansible-playbook
        """,
    )
    # Add global options
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show CLI version information",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all available services and commands",
    )
    
    # Create subparsers for services
    subparsers = parser.add_subparsers(
        title="Services",
        description="Available services and commands",
        dest="service",
        help="Service or command to run",
        metavar="<service>"
    )
    
    # Add common arguments parent parser (for shared args across services)
    common_parser = argparse.ArgumentParser(add_help=False)
    
    # Environment selection arguments (mutually exclusive)
    env_group = common_parser.add_mutually_exclusive_group()
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
    
    # Common arguments for all services
    common_parser.add_argument(
        "-i", "--inventory",
        dest="inventory_path",
        help="Custom inventory file path",
    )
    common_parser.add_argument(
        "-e", "--extra-vars",
        dest="extra_vars_file",
        help="Extra variables file path (e.g., vault file)",
    )
    common_parser.add_argument(
        "--check",
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no changes)",
    )
    common_parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    common_parser.add_argument(
        "-H", "--host",
        dest="target_host",
        help="Target host IP address (overrides inventory)",
    )
    
    # Service installation parent parser
    install_parser = argparse.ArgumentParser(add_help=False, parents=[common_parser])
    install_parser.add_argument(
        "--install",
        "--run",
        action="store_true",
        help="Execute the service installation",
    )
    
    return parser, subparsers, common_parser, install_parser


def register_service_subparsers(subparsers, common_parser, install_parser):
    """Register all service subparsers"""
    
    # Security service
    security_parser = subparsers.add_parser(
        'security',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Server security hardening',
        description=f"{Colors.CYAN}Security Service - Enterprise-grade security hardening{Colors.NC}"
    )
    security_parser.add_argument(
        '--verify',
        action='store_true',
        help='Run security verification checks'
    )
    security_parser.add_argument(
        '--production-hardening',
        action='store_true',
        help='Use production security hardening'
    )
    
    # Base service
    base_parser = subparsers.add_parser(  # noqa: F841
        'base',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Base system configuration',
        description=f"{Colors.CYAN}Base Service - System foundation setup{Colors.NC}"
    )
    
    # Finalize service
    finalize_parser = subparsers.add_parser(
        'finalize',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Finalize server with upgrades and optional reboot',
        description=f"{Colors.CYAN}Finalize Service - System upgrades and reboot management{Colors.NC}",
        epilog=f"""
{Colors.YELLOW}Reboot Behavior:{Colors.NC}
  • {Colors.GREEN}No --reboot{Colors.NC}: Never reboot (default)
  • {Colors.GREEN}--reboot{Colors.NC}: Reboot only if system requires it
  • {Colors.GREEN}--reboot --force{Colors.NC}: Always reboot regardless

{Colors.YELLOW}Examples:{Colors.NC}
  {Colors.GREEN}cli finalize --install{Colors.NC}                      Run upgrades (no reboot)
  {Colors.GREEN}cli finalize --install --reboot{Colors.NC}             Reboot if system needs it
  {Colors.GREEN}cli finalize --install --reboot --force{Colors.NC}     Force reboot after upgrades
        """
    )
    finalize_parser.add_argument(
        '--skip-upgrade',
        action='store_true',
        help='Skip system upgrades'
    )
    finalize_parser.add_argument(
        '--reboot',
        action='store_true',
        help='Reboot if system requires it (default: no reboot)'
    )
    finalize_parser.add_argument(
        '--force',
        action='store_true',
        help='Force reboot even if not required (use with --reboot)'
    )
    
    # PostgreSQL service
    psql_parser = subparsers.add_parser(
        'psql',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='PostgreSQL database server',
        description=f"{Colors.CYAN}PostgreSQL Service - Database server with PostGIS support{Colors.NC}"
    )
    psql_parser.add_argument(
        '--port',
        type=int,
        metavar='PORT',
        help='PostgreSQL port (default: 5432)'
    )
    psql_parser.add_argument(
        '--pgis',
        action='store_true',
        help='Install PostGIS extension'
    )
    psql_parser.add_argument(
        '--pgvector',
        action='store_true',
        help='Install pgvector extension'
    )
    # PostgreSQL operations
    psql_parser.add_argument('--adduser', metavar='USERNAME', help='Create PostgreSQL user')
    psql_parser.add_argument('--password', metavar='PASSWORD', help='User password')
    psql_parser.add_argument('--delete-user', metavar='USERNAME', help='Delete PostgreSQL user')
    psql_parser.add_argument('--list-users', action='store_true', help='List all users')
    psql_parser.add_argument('--adddb', metavar='DATABASE', help='Create database')
    psql_parser.add_argument('--owner', metavar='OWNER', help='Database owner')
    psql_parser.add_argument('--delete-db', metavar='DATABASE', help='Delete database')
    psql_parser.add_argument('--list-databases', action='store_true', help='List all databases')
    psql_parser.add_argument('--database', metavar='DATABASE', help='Target database for operations')
    # Extension management
    psql_parser.add_argument('--enable-extension', metavar='EXTENSION', help='Enable PostgreSQL extension')
    psql_parser.add_argument('--disable-extension', metavar='EXTENSION', help='Disable PostgreSQL extension')
    psql_parser.add_argument('--list-extensions', action='store_true', help='List all extensions')
    psql_parser.add_argument('--verify-extensions', action='store_true', help='Verify pgvector and PostGIS status')
    
    # Redis service
    redis_parser = subparsers.add_parser(
        'redis',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Redis cache server',
        description=f"{Colors.CYAN}Redis Service - In-memory data structure store{Colors.NC}"
    )
    redis_parser.add_argument(
        '--memory',
        type=int,
        metavar='MB',
        help='Redis memory limit in MB (default: 512)'
    )
    redis_parser.add_argument(
        '--port',
        type=int,
        metavar='PORT',
        help='Redis port (default: 6379)'
    )
    
    # Nginx service
    nginx_parser = subparsers.add_parser(
        'nginx',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Nginx web server and load balancer',
        description=f"{Colors.CYAN}Nginx Service - High-performance web server{Colors.NC}"
    )
    nginx_parser.add_argument(
        '--port',
        type=int,
        metavar='PORT',
        help='HTTP port (default: 80)'
    )
    
    # Django service
    django_parser = subparsers.add_parser(  # noqa: F841
        'django',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Django web application framework',
        description=f"{Colors.CYAN}Django Service - Python web framework deployment{Colors.NC}"
    )
    
    # Node.js service
    nodejs_parser = subparsers.add_parser(  # noqa: F841
        'nodejs',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='Node.js application runtime',
        description=f"{Colors.CYAN}Node.js Service - JavaScript runtime environment{Colors.NC}"
    )
    
    # PgBouncer service
    pgbouncer_parser = subparsers.add_parser(  # noqa: F841
        'pgbouncer',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='PostgreSQL connection pooler',
        description=f"{Colors.CYAN}PgBouncer Service - Lightweight connection pooler for PostgreSQL{Colors.NC}"
    )
    
    # OpenVPN service
    openvpn_parser = subparsers.add_parser(  # noqa: F841
        'openvpn',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='OpenVPN server',
        description=f"{Colors.CYAN}OpenVPN Service - Virtual private network server{Colors.NC}"
    )
    
    # SSH service - port management
    ssh_parser = subparsers.add_parser(
        'ssh',
        parents=[common_parser],
        formatter_class=ColoredHelpFormatter,
        help='SSH port management',
        description=f"{Colors.CYAN}SSH Service - Change SSH port{Colors.NC}",
        epilog=f"""
{Colors.YELLOW}Examples:{Colors.NC}
  {Colors.GREEN}cli ssh --new-port 3333{Colors.NC}                    Change to port 3333 (reads current from vault)
  {Colors.GREEN}cli ssh --old-port 22 --new-port 3333{Colors.NC}     Explicitly specify old and new ports

{Colors.YELLOW}Important:{Colors.NC}
  • Connection will drop when SSH restarts - this is normal
  • UFW is automatically updated (old port removed, new port added)
  • Update vault_ssh_port in your .vault/*.yml file after the change
        """
    )
    ssh_parser.add_argument(
        '--old-port',
        type=int,
        metavar='PORT',
        help='Current SSH port (default: read from vault)'
    )
    ssh_parser.add_argument(
        '--new-port',
        type=int,
        metavar='PORT',
        required=True,
        help='New SSH port'
    )
    
    # Keep harden for backward compatibility but mark as deprecated
    harden_parser = subparsers.add_parser(
        'harden',
        parents=[common_parser],
        formatter_class=ColoredHelpFormatter,
        help='[DEPRECATED] Use "cli ssh" instead',
        description=f"{Colors.YELLOW}[DEPRECATED]{Colors.NC} {Colors.CYAN}This command is deprecated. Use 'cli ssh' for port changes.{Colors.NC}"
    )
    harden_parser.add_argument(
        '--from-port',
        type=int,
        metavar='PORT',
        required=True,
        help='Current SSH port'
    )
    harden_parser.add_argument(
        '--to-port',
        type=int,
        metavar='PORT',
        required=True,
        help='New SSH port'
    )
    
    # pgvector service
    pgvector_parser = subparsers.add_parser(  # noqa: F841
        'pgvector',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='PostgreSQL pgvector extension',
        description=f"{Colors.CYAN}pgvector Service - Vector similarity search for PostgreSQL{Colors.NC}"
    )
    
    # PostGIS service
    postgis_parser = subparsers.add_parser(  # noqa: F841
        'postgis',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='PostGIS spatial database extension',
        description=f"{Colors.CYAN}PostGIS Service - Geographic objects for PostgreSQL{Colors.NC}"
    )
    
    # Standalone service
    standalone_parser = subparsers.add_parser(  # noqa: F841
        'standalone',
        parents=[install_parser],
        formatter_class=ColoredHelpFormatter,
        help='All-in-one server setup',
        description=f"{Colors.CYAN}Standalone Service - Complete server with all services{Colors.NC}"
    )
    
    return subparsers


def register_dev_subparsers(subparsers):
    """Register development command subparsers"""
    
    # Dev command with its own subcommands
    dev_parser = subparsers.add_parser(
        'dev',
        formatter_class=ColoredHelpFormatter,
        help='Development and validation commands',
        description=f"{Colors.CYAN}Development Commands - Code quality and validation tools{Colors.NC}"
    )
    
    dev_subparsers = dev_parser.add_subparsers(
        title="Development Commands",
        dest="subcommand",
        help="Development command to run",
        metavar="<command>"
    )
    
    # Precommit
    precommit_parser = dev_subparsers.add_parser(
        'precommit',
        formatter_class=ColoredHelpFormatter,
        help='Run all pre-commit checks',
        description=f"{Colors.CYAN}Pre-commit Checks - Run all validation before committing{Colors.NC}"
    )
    precommit_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Validate
    validate_parser = dev_subparsers.add_parser(
        'validate',
        formatter_class=ColoredHelpFormatter,
        help='Ansible structural validation',
        description=f"{Colors.CYAN}Structural Validation - Validate Ansible project structure{Colors.NC}"
    )
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Syntax
    syntax_parser = dev_subparsers.add_parser(
        'syntax',
        formatter_class=ColoredHelpFormatter,
        help='Quick syntax checking',
        description=f"{Colors.CYAN}Syntax Check - Quick YAML syntax validation{Colors.NC}"
    )
    syntax_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Test
    test_parser = dev_subparsers.add_parser(
        'test',
        formatter_class=ColoredHelpFormatter,
        help='Authentication flow testing',
        description=f"{Colors.CYAN}Authentication Test - Test server authentication setup{Colors.NC}",
        epilog=f"""\n{Colors.YELLOW}Examples:{Colors.NC}
  {Colors.GREEN}cli dev test{Colors.NC}                                    Run authentication test
  {Colors.GREEN}cli dev test --check{Colors.NC}                            Dry run test
  {Colors.GREEN}cli dev test -- -e "vault_ssh_port=22"{Colors.NC}         Override SSH port
  {Colors.GREEN}cli dev test -- -e "ansible_host=192.168.1.100"{Colors.NC} Test specific server

{Colors.YELLOW}Variable Overrides:{Colors.NC}
  Pass Ansible variables after {Colors.CYAN}--{Colors.NC} to customize test parameters:
  • vault_ssh_port=22                   SSH port (default from vault)
  • ansible_host="10.10.10.199"         Target server IP
  • vault_grunt_user="myuser"           Grunt username
  • vault_grunt_password="secret"       Grunt password
        """
    )
    test_parser.add_argument('--check', '--dry-run', action='store_true', help='Dry run mode')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Lint
    lint_parser = dev_subparsers.add_parser(
        'lint',
        formatter_class=ColoredHelpFormatter,
        help='Ansible linting',
        description=f"{Colors.CYAN}Ansible Lint - Code quality and best practices{Colors.NC}"
    )
    lint_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Yamlint
    yamlint_parser = dev_subparsers.add_parser(
        'yamlint',
        formatter_class=ColoredHelpFormatter,
        help='YAML formatting validation',
        description=f"{Colors.CYAN}YAML Lint - YAML syntax and formatting checks{Colors.NC}"
    )
    yamlint_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Flake8
    flake8_parser = dev_subparsers.add_parser(
        'flake8',
        formatter_class=ColoredHelpFormatter,
        help='Python code quality checks',
        description=f"{Colors.CYAN}Flake8 - Python code style and quality validation{Colors.NC}"
    )
    flake8_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Spell
    spell_parser = dev_subparsers.add_parser(
        'spell',
        formatter_class=ColoredHelpFormatter,
        help='Documentation spelling checks',
        description=f"{Colors.CYAN}Spell Check - Documentation and comment spelling validation{Colors.NC}"
    )
    spell_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    return dev_parser


def split_arguments():
    """Split command line arguments into cli and ansible args"""
    # Parse arguments, splitting on -- for ansible args
    if "--" in sys.argv:
        split_idx = sys.argv.index("--")
        cli_args = sys.argv[1:split_idx]
        ansible_args = sys.argv[split_idx + 1 :]
    else:
        cli_args = sys.argv[1:]
        ansible_args = []
    
    return cli_args, ansible_args


def parse_arguments(cli_args):
    """Parse command line arguments"""
    # Create parser with subparsers
    parser, subparsers, common_parser, install_parser = create_parser()
    
    # Register all service subparsers
    register_service_subparsers(subparsers, common_parser, install_parser)
    
    # Register dev subparsers
    register_dev_subparsers(subparsers)
    
    # Parse arguments
    args = parser.parse_args(cli_args)
    
    return args, []  # No more remaining_args with proper subparsers
