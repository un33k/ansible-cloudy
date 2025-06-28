"""
Ali (Ansible Line Interpreter) - Simplified Ansible CLI for Cloudy

Main orchestrator that coordinates between modular components.
"""

import sys
import argparse
import re

from colors import Colors, error
from config import AliConfig, InventoryManager
from recipes import RecipeFinder, RecipeHelpParser, list_recipes
from runners import AnsibleRunner, SmartSecurityRunner
from dev_tools import DevTools, list_dev_commands


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter with colors"""

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = f"{Colors.CYAN}usage:{Colors.NC} "
        return super()._format_usage(usage, actions, groups, prefix)

    def format_help(self):
        help_text = super().format_help()
        # Add colors to section headers
        help_text = help_text.replace(
            "positional arguments:",
            f"{Colors.BLUE}positional arguments:{Colors.NC}",
        )
        help_text = help_text.replace(
            "options:", f"{Colors.BLUE}options:{Colors.NC}"
        )

        # Color individual arguments and options

        # Color positional arguments (like "command", "subcommand")
        help_text = re.sub(
            r"^  (command|subcommand)(\s+)",
            f"  {Colors.GREEN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        # Color option flags (handle both "-h, --help" and "--list, -l" patterns)
        help_text = re.sub(
            r"^  ((?:-[a-zA-Z-]+(?:, --[a-zA-Z-]+)?|--[a-zA-Z-]+(?:, -[a-zA-Z])?))(\s+)",
            f"  {Colors.CYAN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        return help_text


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}Ali (Ansible Line Interpreter) - Simplified Ansible CLI{Colors.NC}",
        formatter_class=ColoredHelpFormatter,
        epilog=f"""
{Colors.YELLOW}Examples:{Colors.NC}
  {Colors.GREEN}ali security{Colors.NC}                    Show security recipe help and configuration
  {Colors.GREEN}ali security --install{Colors.NC}          Execute security setup on test environment
  {Colors.GREEN}ali security --verify{Colors.NC}           Run security verification/check
  {Colors.GREEN}ali base --install{Colors.NC}              Execute base server configuration
  {Colors.GREEN}ali psql --install{Colors.NC}              Execute PostgreSQL installation
  {Colors.GREEN}ali django --install --prod{Colors.NC}     Execute django recipe on production
  {Colors.GREEN}ali redis --install --check{Colors.NC}     Dry run redis recipe installation
  {Colors.GREEN}ali nginx --install -- --tags ssl{Colors.NC}  Execute nginx with --tags ssl passed to ansible-playbook
  {Colors.GREEN}ali --list{Colors.NC}                      Show all available recipes
  
  {Colors.GREEN}ali dev validate{Colors.NC}                Run comprehensive validation
  {Colors.GREEN}ali dev syntax{Colors.NC}                 Quick syntax checking  
  {Colors.GREEN}ali dev yaml{Colors.NC}                   YAML syntax validation
  {Colors.GREEN}ali dev lint{Colors.NC}                   Complete linting (YAML + Ansible)
  {Colors.GREEN}ali dev test{Colors.NC}                   Authentication testing
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        help="Recipe name or 'dev' for development commands",
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
        "--list",
        "-l",
        action="store_true",
        help="List all available recipes or dev commands",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run security verification instead of initial setup (security only)",
    )
    parser.add_argument(
        "--install",
        "--run",
        action="store_true",
        help="Execute the recipe (required to run any recipe)",
    )

    return parser


def main() -> None:
    """Main entry point for Ali CLI"""

    # Parse arguments, splitting on -- for ansible args
    if "--" in sys.argv:
        split_idx = sys.argv.index("--")
        ali_args = sys.argv[1:split_idx]
        ansible_args = sys.argv[split_idx + 1 :]
    else:
        ali_args = sys.argv[1:]
        ansible_args = []

    # Check for recipe-specific help before parsing
    if len(ali_args) >= 2 and ali_args[1] in ["--help", "-h"]:
        recipe_name = ali_args[0]
        # Initialize config to find recipe
        try:
            config = AliConfig()
            finder = RecipeFinder(config)
            recipe_path = finder.find_recipe(recipe_name)
            if recipe_path:
                help_parser = RecipeHelpParser(config)
                help_parser.display_recipe_help(recipe_name, recipe_path)
                return
            else:
                # Recipe not found, show error then general help
                print(
                    f"{Colors.RED}(✗){Colors.NC} {Colors.YELLOW}{recipe_name}{Colors.NC} {Colors.RED}not found{Colors.NC}:\n"
                )
                parser = create_parser()
                parser.print_help()
                return
        except:
            pass  # Fall back to normal help

    # Parse ali arguments
    parser = create_parser()
    args, remaining_args = parser.parse_known_args(ali_args)

    # Combine remaining args with original ansible args
    ansible_args.extend(remaining_args)

    # Initialize configuration
    try:
        config = AliConfig()
    except Exception as e:
        error(f"Configuration error: {e}")

    # Handle list command
    if args.list:
        if args.command == "dev":
            list_dev_commands()
        else:
            list_recipes(config)
        return

    # Handle dev commands
    if args.command == "dev":
        if not args.subcommand:
            list_dev_commands()
            return

        dev_tools = DevTools(config)

        # Route to appropriate dev command
        if args.subcommand == "validate":
            exit_code = dev_tools.validate()
        elif args.subcommand == "syntax":
            exit_code = dev_tools.syntax()
        elif args.subcommand == "yaml":
            exit_code = dev_tools.yaml()
        elif args.subcommand == "lint":
            exit_code = dev_tools.lint()
        elif args.subcommand == "test":
            exit_code = dev_tools.test(ansible_args)
        elif args.subcommand == "spell":
            exit_code = dev_tools.spell()
        else:
            error(
                f"Unknown dev command '{args.subcommand}'. Use 'ali dev --list' to see available commands."
            )

        sys.exit(exit_code)

    # Require recipe name if not listing or dev command
    if not args.command:
        parser.print_help()
        return

    # Find the recipe
    finder = RecipeFinder(config)
    recipe_path = finder.find_recipe(args.command)

    # Check if help is requested for this recipe
    if "--help" in ansible_args or "-h" in ansible_args:
        if recipe_path:
            help_parser = RecipeHelpParser(config)
            help_parser.display_recipe_help(args.command, recipe_path)
            return
        else:
            # Show "not found" error then general help
            print(f"{Colors.RED}✗{Colors.NC} {args.command} not found:")
            parser.print_help()
            return

    if not recipe_path:
        error(
            f"Recipe '{args.command}' not found. Use 'ali --list' to see available recipes."
        )

    # Get inventory and runner
    inventory_manager = InventoryManager(config)
    runner = AnsibleRunner(config)

    # Add verbose flag if requested
    if args.verbose:
        ansible_args.insert(0, "-v")

    # Check if execution is requested, otherwise show help
    execution_requested = args.install or args.verify
    
    if not execution_requested:
        # Show recipe help by default
        help_parser = RecipeHelpParser(config)
        help_parser.display_recipe_help(args.command, recipe_path)
        return

    # Handle smart security execution
    if args.command == "security":
        if args.verify:
            # Run security verification/check recipe directly
            inventory_path = inventory_manager.get_inventory_path(args.prod)
            exit_code = runner.run_recipe(
                recipe_path="core/security-verify.yml",
                inventory_path=inventory_path,
                extra_args=ansible_args,
                dry_run=args.check,
            )
        else:
            # Run smart security detection
            smart_security = SmartSecurityRunner(config, inventory_manager, runner)
            exit_code = smart_security.run_smart_security(
                production=args.prod, extra_args=ansible_args, dry_run=args.check
            )
    else:
        # Run regular recipe
        inventory_path = inventory_manager.get_inventory_path(args.prod)
        exit_code = runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=ansible_args,
            dry_run=args.check,
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
