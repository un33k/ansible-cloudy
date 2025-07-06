"""
CLI - Intelligent Infrastructure Management Made Intuitive

Main CLI entry point that coordinates between modular components.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
cli_dir = Path(__file__).parent.parent
cmd_dir = Path(__file__).parent
sys.path.insert(0, str(cli_dir))
sys.path.insert(0, str(cmd_dir))

from argument_parser import (  # noqa: E402
    split_arguments, 
    parse_arguments, 
    create_parser,
    register_service_subparsers,
    register_dev_subparsers
)
from command_router import CommandRouter  # noqa: E402
from dev_commands import DevCommandsHandler  # noqa: E402
from help_system import show_version  # noqa: E402
from utils.config import CliConfig  # noqa: E402
from utils.colors import error  # noqa: E402
import os  # noqa: E402


def check_virtual_environment():
    """Check if running in a virtual environment"""
    # Check for common virtual environment indicators
    in_venv = any([
        os.environ.get('VIRTUAL_ENV'),  # Standard venv/virtualenv
        os.environ.get('CONDA_DEFAULT_ENV'),  # Conda
        hasattr(sys, 'real_prefix'),  # Old virtualenv
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix  # venv
    ])
    
    if not in_venv:
        error("❌ Virtual environment not activated!")
        print("\nPlease activate the virtual environment first:")
        print("  source .venv/bin/activate")
        print("\nOr if using conda:")
        print("  conda activate your-env-name")
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI"""
    
    # Check virtual environment first
    check_virtual_environment()
    
    # Split arguments first
    cli_args, ansible_args = split_arguments()
    
    # Initialize command router
    router = CommandRouter()
    
    # Parse arguments with new subparser system
    try:
        args, _ = parse_arguments(cli_args)
    except SystemExit:
        # argparse calls sys.exit on error or help
        return
    
    # Handle version command
    if hasattr(args, 'version') and args.version:
        show_version()
        return
    
    # Handle list services command
    if hasattr(args, 'list_services') and args.list_services:
        router.handle_list_services()
        return
    
    # If no service specified, show main help
    if not hasattr(args, 'service') or not args.service:
        parser, subparsers, common_parser, install_parser = create_parser()
        register_service_subparsers(subparsers, common_parser, install_parser)
        register_dev_subparsers(subparsers)
        parser.print_help()
        return
    
    # Handle dev commands
    if args.service == "dev":
        config = router.initialize_config()
        dev_handler = DevCommandsHandler(config)
        dev_handler.handle_dev_commands(args, ansible_args)
        return
    
    # Handle service-specific operations
    if router.handle_service_operation(args.service, args, ansible_args):
        return
    
    # Handle generic services using recipe finder
    router.handle_generic_service(args.service, args, ansible_args)


if __name__ == "__main__":
    main()
