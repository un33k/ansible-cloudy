"""
CLI Development Commands Handler
Handles all development and validation commands
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
cli_dir = Path(__file__).parent.parent
cmd_dir = Path(__file__).parent
sys.path.insert(0, str(cli_dir))
sys.path.insert(0, str(cmd_dir))

from utils.colors import error  # noqa: E402


class DevCommandsHandler:
    """Handles development commands routing and execution"""
    
    def __init__(self, config):
        self.config = config
    
    def handle_dev_commands(self, args, ansible_args):
        """Handle all development commands"""
        if not args.subcommand:
            # Help is handled by argparse
            return
        
        # Import dev tools
        from utils.dev_tools import DevTools  # noqa: E402
        dev_tools = DevTools(self.config)
        
        # Route to appropriate dev command
        if args.subcommand == "precommit":
            exit_code = dev_tools.validate_precommit()
        elif args.subcommand == "validate":
            exit_code = dev_tools.validate()
        elif args.subcommand == "comprehensive":
            # Keep for backward compatibility
            exit_code = dev_tools.validate()
        elif args.subcommand == "syntax":
            exit_code = dev_tools.syntax()
        elif args.subcommand == "test":
            exit_code = dev_tools.test(ansible_args)
        elif args.subcommand == "lint":
            exit_code = dev_tools.lint()
        elif args.subcommand == "yamlint":
            exit_code = dev_tools.yamlint()
        elif args.subcommand == "flake8":
            exit_code = dev_tools.flake8()
        elif args.subcommand == "spell":
            exit_code = dev_tools.spell()
        else:
            error(f"Unknown dev command '{args.subcommand}'")
        
        sys.exit(exit_code)
