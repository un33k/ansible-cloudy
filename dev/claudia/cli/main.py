"""
Claudia (Claude-inspired Infrastructure Assistant)
Intelligent Infrastructure Management Made Intuitive

Main CLI entry point that coordinates between modular components.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
claudia_dir = Path(__file__).parent.parent
cli_dir = Path(__file__).parent
sys.path.insert(0, str(claudia_dir))
sys.path.insert(0, str(cli_dir))

from argument_parser import split_arguments, parse_arguments, create_parser  # noqa: E402
from command_router import CommandRouter  # noqa: E402
from dev_commands import DevCommandsHandler  # noqa: E402
from help_system import show_version  # noqa: E402
from utils.config import ClaudiaConfig  # noqa: E402


def main() -> None:
    """Main entry point for Claudia CLI"""
    
    # Split arguments first
    claudia_args, ansible_args = split_arguments()
    
    # Initialize command router
    router = CommandRouter()
    
    # Handle help requests before main parsing
    if router.handle_help_requests(claudia_args):
        return
    
    # Parse arguments now
    args, remaining_args = parse_arguments(claudia_args)
    ansible_args.extend(remaining_args)
    
    # Handle version command
    if args.version:
        show_version()
        return
    
    # Handle list services command
    if args.list_services:
        router.handle_list_services()
        return
    
    # Handle dev commands
    if args.service == "dev":
        config = router.initialize_config()
        dev_handler = DevCommandsHandler(config)
        dev_handler.handle_dev_commands(args, ansible_args)
        return
    
    # Require service name if not listing or dev command
    if not args.service:
        parser = create_parser()
        parser.print_help()
        return
    
    # Handle service-specific operations
    if router.handle_service_operation(args.service, args, ansible_args):
        return
    
    # Handle generic services using recipe finder
    router.handle_generic_service(args.service, args, ansible_args)


if __name__ == "__main__":
    main()
