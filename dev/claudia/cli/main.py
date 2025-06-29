"""
Claudia (Claude-inspired Infrastructure Assistant)
Intelligent Infrastructure Management Made Intuitive

Main CLI entry point that coordinates between modular components.
"""

import sys
import argparse
import re
from pathlib import Path

# Add parent directory to path for imports
claudia_dir = Path(__file__).parent.parent
sys.path.insert(0, str(claudia_dir))

from utils.colors import Colors, error  # noqa: E402
from utils.config import ClaudiaConfig, InventoryManager  # noqa: E402
from operations.recipes import RecipeFinder, RecipeHelpParser, list_recipes  # noqa: E402
from execution.ansible import AnsibleRunner, SmartSecurityRunner  # noqa: E402
from discovery.service_scanner import ServiceScanner  # noqa: E402
from operations.postgresql import PostgreSQLOperations  # noqa: E402
from operations.redis import RedisOperations  # noqa: E402
from operations.nginx import NginxOperations  # noqa: E402


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
            r"^  ((?:-[a-zA-Z-]+(?:, --[a-zA-Z-]+)?|--[a-zA-Z-]+(?:, -[a-zA-Z])?))(\s+)",
            f"  {Colors.CYAN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        return help_text


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


def _show_validate_help():
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


def main() -> None:
    """Main entry point for Claudia CLI"""

    # Parse arguments, splitting on -- for ansible args
    if "--" in sys.argv:
        split_idx = sys.argv.index("--")
        claudia_args = sys.argv[1:split_idx]
        ansible_args = sys.argv[split_idx + 1 :]
    else:
        claudia_args = sys.argv[1:]
        ansible_args = []

    # Check for service-specific help before parsing
    if len(claudia_args) >= 3 and claudia_args[0] == "dev" and claudia_args[2] in ["--help", "-h"]:
        # Handle dev subcommand help
        if claudia_args[1] == "validate":
            _show_validate_help()
            return
    elif len(claudia_args) >= 2 and claudia_args[1] in ["--help", "-h"] and claudia_args[0] not in ["dev"]:
        service_name = claudia_args[0]
        try:
            config = ClaudiaConfig()
            
            # Handle service-specific help
            if service_name == "psql":
                psql_ops = PostgreSQLOperations(config)
                psql_ops._show_psql_help()
                return
            elif service_name == "redis":
                redis_ops = RedisOperations(config)
                redis_ops._show_service_help()
                return
            elif service_name == "nginx":
                nginx_ops = NginxOperations(config)
                nginx_ops._show_service_help()
                return
            
            # Handle other services with recipe help
            finder = RecipeFinder(config)
            recipe_path = finder.find_recipe(service_name)
            if recipe_path:
                help_parser = RecipeHelpParser(config)
                help_parser.display_recipe_help(service_name, recipe_path)
                return
            else:
                error(f"Service '{service_name}' not found. Use 'claudia --list-services' to see available services.")
        except Exception as e:
            error(f"Configuration error: {e}")

    # Parse claudia arguments
    parser = create_parser()
    args, remaining_args = parser.parse_known_args(claudia_args)

    # Combine remaining args with original ansible args
    ansible_args.extend(remaining_args)

    # Handle version command
    if args.version:
        print(f"{Colors.CYAN}Claudia{Colors.NC} (Claude-inspired Infrastructure Assistant)")
        print(f"{Colors.YELLOW}Intelligent Infrastructure Management Made Intuitive{Colors.NC}")
        print(f"Version: 1.0.0")
        return

    # Initialize configuration
    try:
        config = ClaudiaConfig()
    except Exception as e:
        error(f"Configuration error: {e}")

    # Handle list services command
    if args.list_services:
        scanner = ServiceScanner(config)
        scanner.list_all_services()
        return

    # Handle dev commands (keep from Ali for now)
    if args.service == "dev":
        if not args.subcommand:
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
            return

        # Import dev tools
        from utils.dev_tools import DevTools
        dev_tools = DevTools(config)

        if args.subcommand == "validate":
            exit_code = dev_tools.validate_precommit()
        elif args.subcommand == "comprehensive":
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

    # Require service name if not listing or dev command
    if not args.service:
        parser.print_help()
        return

    # Handle PostgreSQL operations
    if args.service == "psql":
        psql_ops = PostgreSQLOperations(config)
        exit_code = psql_ops.handle_operation(args, ansible_args)
        sys.exit(exit_code)

    # Handle Redis operations
    if args.service == "redis":
        redis_ops = RedisOperations(config)
        exit_code = redis_ops.handle_operation(args, ansible_args)
        sys.exit(exit_code)

    # Handle Nginx operations
    if args.service == "nginx":
        nginx_ops = NginxOperations(config)
        exit_code = nginx_ops.handle_operation(args, ansible_args)
        sys.exit(exit_code)

    # For other services, fall back to recipe finder for now
    finder = RecipeFinder(config)
    recipe_path = finder.find_recipe(args.service)

    if not recipe_path:
        error(f"Service '{args.service}' not found. Use 'claudia --list-services' to see available services.")

    # Show service help by default
    if not args.install:
        help_parser = RecipeHelpParser(config)
        help_parser.display_recipe_help(args.service, recipe_path)
        return

    # Execute recipe
    inventory_manager = InventoryManager(config)
    runner = AnsibleRunner(config)

    if args.verbose:
        ansible_args.insert(0, "-v")

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
