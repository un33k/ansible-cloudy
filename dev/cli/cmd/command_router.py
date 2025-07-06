"""
CLI Command Router
Routes commands to appropriate handlers and manages service operations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
cli_dir = Path(__file__).parent.parent
cmd_dir = Path(__file__).parent
sys.path.insert(0, str(cli_dir))
sys.path.insert(0, str(cmd_dir))

from utils.colors import error  # noqa: E402
from utils.config import CliConfig  # noqa: E402
from operations.recipes import RecipeFinder, RecipeHelpParser  # noqa: E402
from operations.postgresql import PostgreSQLOperations  # noqa: E402
from operations.redis import RedisOperations  # noqa: E402
from operations.nginx import NginxOperations  # noqa: E402
from discovery.service_scanner import ServiceScanner  # noqa: E402
from help_system import show_validate_help  # noqa: E402


class CommandRouter:
    """Routes commands to appropriate handlers"""
    
    def __init__(self):
        self.config = None
    
    def initialize_config(self):
        """Initialize configuration if not already done"""
        if not self.config:
            try:
                self.config = CliConfig()
            except Exception as e:
                error(f"Configuration error: {e}")
        return self.config
    
    def handle_help_requests(self, cli_args):
        """Handle service-specific help requests before main parsing"""
        # Check for dev subcommand help
        if len(cli_args) >= 3 and cli_args[0] == "dev" and cli_args[2] in ["--help", "-h"]:
            subcommand = cli_args[1]
            if subcommand == "validate":
                show_validate_help()
                return True
            elif subcommand == "precommit":
                self._show_precommit_help()
                return True
            elif subcommand == "test":
                self._show_dev_test_help()
                return True
            elif subcommand in ["syntax", "lint", "yamlint", "flake8", "spell", "comprehensive"]:
                self._show_dev_command_help(subcommand)
                return True
        
        # Check for service-specific help
        elif len(cli_args) >= 2 and cli_args[1] in ["--help", "-h"] and cli_args[0] not in ["dev"]:
            service_name = cli_args[0]
            config = self.initialize_config()
            
            try:
                # Handle service-specific help
                if service_name == "psql":
                    psql_ops = PostgreSQLOperations(config)
                    psql_ops._show_psql_help()
                    return True
                elif service_name == "pgvector":
                    from operations.pgvector import PgVectorOperations
                    pgvector_ops = PgVectorOperations(config)
                    pgvector_ops.show_help()
                    return True
                elif service_name == "redis":
                    redis_ops = RedisOperations(config)
                    redis_ops._show_service_help()
                    return True
                elif service_name == "nginx":
                    nginx_ops = NginxOperations(config)
                    nginx_ops._show_service_help()
                    return True
                elif service_name == "nodejs":
                    from operations.nodejs import NodeJSOperations
                    nodejs_ops = NodeJSOperations(config)
                    nodejs_ops.show_help()
                    return True
                elif service_name == "standalone":
                    from operations.standalone import StandaloneOperations
                    standalone_ops = StandaloneOperations(config)
                    standalone_ops.show_help()
                    return True
                elif service_name == "harden":
                    from operations.harden import HardenOperations
                    harden_ops = HardenOperations(config)
                    harden_ops.show_help()
                    return True
                elif service_name == "finalize":
                    from operations.finalize import FinalizeService
                    finalize_ops = FinalizeService(config, "finalize")
                    finalize_ops._show_service_help()
                    return True
                
                # Handle other services with recipe help
                finder = RecipeFinder(config)
                recipe_path = finder.find_recipe(service_name)
                if recipe_path:
                    help_parser = RecipeHelpParser(config)
                    help_parser.display_recipe_help(service_name, recipe_path)
                    return True
                else:
                    error(f"Service '{service_name}' not found. Use 'cli --list-services' to see available services.")
            except Exception as e:
                error(f"Configuration error: {e}")
        
        return False
    
    def _show_dev_test_help(self):
        """Show help for dev test command"""
        from utils.colors import Colors
        
        print(f"""
{Colors.CYAN}cli dev test{Colors.NC} - Authentication Flow Testing

{Colors.YELLOW}DESCRIPTION:{Colors.NC}
    Tests the authentication setup process to validate server configuration.
    Verifies grunt user creation, SSH keys, firewall, and sudo access.

{Colors.YELLOW}USAGE:{Colors.NC}
    cli dev test [OPTIONS] [-- ANSIBLE_ARGS]

{Colors.YELLOW}OPTIONS:{Colors.NC}
    --check, --dry-run    Run in check mode (don't make changes)
    --verbose, -v         Show detailed Ansible task output
    -h, --help           Show this help message

{Colors.YELLOW}EXAMPLES:{Colors.NC}
    cli dev test                           # Run authentication test
    cli dev test --check                   # Dry run test
    cli dev test --verbose                 # Show detailed output
    cli dev test -- -e "vault_ssh_port=22" # Override SSH port

{Colors.YELLOW}CONFIGURABLE VARIABLES:{Colors.NC}
    Override test parameters using Ansible variable syntax:

    {Colors.GREEN}Connection Settings:{Colors.NC}
    • vault_root_password="newpass"     Root password for initial connection
    • vault_ssh_port=22                 SSH port (default: 2222)
    • ansible_host="10.10.10.199"       Target server IP address

    {Colors.GREEN}Admin User Configuration:{Colors.NC}
    • vault_grunt_user="myuser"         Grunt username (default: grunt)
    • vault_grunt_password="secret"     Grunt user password
    • admin_groups="admin,sudo"         User groups (default: admin,www-data)

    {Colors.GREEN}SSH & Security:{Colors.NC}
    • ssh_port=2222                     SSH port configuration
    • grunt_user="myuser"               Grunt username for test
    • admin_password="secure123"        Admin password for test

{Colors.YELLOW}VARIABLE OVERRIDE EXAMPLES:{Colors.NC}
    # Test with standard SSH port
    cli dev test -- -e "vault_ssh_port=22"
    
    # Test with different grunt user
    cli dev test -- -e "vault_grunt_user=deploy" -e "grunt_user=deploy"
    
    # Test with custom server
    cli dev test -- -e "ansible_host=192.168.1.100" -e "vault_ssh_port=22"
    
    # Multiple overrides
    cli dev test -- -e "vault_root_password=mypass" -e "vault_ssh_port=22" -e "grunt_user=myuser"

{Colors.YELLOW}WHAT IT TESTS:{Colors.NC}
    • Server connectivity and authentication
    • Admin user creation and configuration
    • SSH key installation and validation
    • Firewall configuration
    • Sudo access verification
    • Security configuration validation

{Colors.YELLOW}AUTHENTICATION:{Colors.NC}
    • Uses root credentials from .vault/dev.yml for initial connection
    • Tests grunt user setup and SSH key authentication
    • Validates two-phase authentication model

{Colors.YELLOW}VAULT CONFIGURATION:{Colors.NC}
    Automatically loads credentials from .vault/dev.yml if present.
    Common vault variables:
    • vault_root_password: Root password for initial connection
    • vault_grunt_password: Grunt user password
    • vault_grunt_user: Grunt username
    • vault_ssh_port: SSH port configuration

{Colors.YELLOW}INVENTORY TARGETS:{Colors.NC}
    Test runs against 'security_targets' group in inventory/dev.yml
    • Uses root user with password authentication
    • Configures grunt user with SSH keys
    • Tests firewall and security settings
""")
    
    def _show_precommit_help(self):
        """Show help for dev precommit command"""
        from utils.colors import Colors
        
        print(f"""
{Colors.CYAN}cli dev precommit{Colors.NC} - Run all validation checks before commit

{Colors.YELLOW}DESCRIPTION:{Colors.NC}
    Runs a comprehensive suite of validation checks to ensure code quality
    before committing. This is the recommended command to run before any commit.

{Colors.YELLOW}USAGE:{Colors.NC}
    cli dev precommit [OPTIONS]

{Colors.YELLOW}OPTIONS:{Colors.NC}
    --verbose, -v         Show detailed output
    -h, --help           Show this help message

{Colors.YELLOW}WHAT IT RUNS:{Colors.NC}
    1. {Colors.GREEN}Syntax Check{Colors.NC}     - Validates all Ansible YAML files
    2. {Colors.GREEN}Ansible Linting{Colors.NC}  - Code quality and best practices
    3. {Colors.GREEN}YAML Formatting{Colors.NC}  - Consistent formatting validation
    4. {Colors.GREEN}Python Quality{Colors.NC}   - Flake8 code quality checks
    5. {Colors.GREEN}Spell Check{Colors.NC}      - Documentation spelling validation

{Colors.YELLOW}EXAMPLES:{Colors.NC}
    cli dev precommit                   # Run all pre-commit checks
    cli dev precommit --verbose         # Show detailed output

{Colors.YELLOW}EXIT CODES:{Colors.NC}
    0 - All checks passed
    1 - One or more checks failed

{Colors.YELLOW}TIPS:{Colors.NC}
    • This command runs all validation checks in sequence
    • Any failed check will be clearly indicated
    • Use individual commands (syntax, lint, etc.) to debug specific issues
    • For structural validation only, use 'cli dev validate'
""")
    
    def _show_dev_command_help(self, command):
        """Show help for specific dev commands"""
        from utils.colors import Colors
        
        descriptions = {
            "syntax": "Quick syntax checking of Ansible playbooks",
            "lint": "Ansible linting with project configuration",
            "yamlint": "YAML linting with project configuration", 
            "flake8": "Python code linting with flake8",
            "spell": "Spell checking with cspell configuration",
            "comprehensive": "Comprehensive validation using validate.py script"
        }
        
        desc = descriptions.get(command, f"Development command: {command}")
        
        print(f"""
{Colors.CYAN}cli dev {command}{Colors.NC} - {desc}

{Colors.YELLOW}USAGE:{Colors.NC}
    cli dev {command} [OPTIONS]

{Colors.YELLOW}OPTIONS:{Colors.NC}
    --verbose, -v         Show detailed output
    -h, --help           Show this help message

{Colors.YELLOW}EXAMPLES:{Colors.NC}
    cli dev {command}                      # Run {command} check
    cli dev {command} --verbose            # Show detailed output
""")
    
    def handle_list_services(self):
        """Handle --list-services command"""
        config = self.initialize_config()
        scanner = ServiceScanner(config)
        scanner.list_all_services()
    
    def handle_service_operation(self, service_name, args, ansible_args):
        """Handle service-specific operations"""
        config = self.initialize_config()
        
        if service_name == "psql":
            psql_ops = PostgreSQLOperations(config)
            exit_code = psql_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "pgvector":
            from operations.pgvector import PgVectorOperations
            pgvector_ops = PgVectorOperations(config)
            exit_code = pgvector_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "redis":
            redis_ops = RedisOperations(config)
            exit_code = redis_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "nginx":
            nginx_ops = NginxOperations(config)
            exit_code = nginx_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "nodejs":
            from operations.nodejs import NodeJSOperations
            nodejs_ops = NodeJSOperations(config)
            exit_code = nodejs_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "standalone":
            from operations.standalone import StandaloneOperations
            standalone_ops = StandaloneOperations(config)
            exit_code = standalone_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "harden":
            from operations.harden import HardenOperations
            harden_ops = HardenOperations(config)
            exit_code = harden_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "finalize":
            from operations.finalize import FinalizeService
            finalize_ops = FinalizeService(config, "finalize")
            exit_code = finalize_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        else:
            return False  # Service not handled by specific operations
        
        return True
    
    def handle_generic_service(self, service_name, args, ansible_args):
        """Handle generic services using recipe finder with dependency management"""
        from utils.config import InventoryManager  # noqa: E402
        from execution.dependency_manager import DependencyManager  # noqa: E402
        
        config = self.initialize_config()
        finder = RecipeFinder(config)
        recipe_path = finder.find_recipe(service_name)
        
        if not recipe_path:
            error(f"Service '{service_name}' not found. Use 'cli --list-services' to see available services.")
        
        # Show service help by default
        if not args.install:
            help_parser = RecipeHelpParser(config)
            help_parser.display_recipe_help(service_name, recipe_path)
            return
        
        # Execute recipe with dependency management
        dependency_manager = DependencyManager(config)
        
        if args.verbose:
            ansible_args.insert(0, "-v")
        
        environment = self._get_environment(args)
        
        # Check if we need production hardening for security
        if service_name == 'security' and getattr(args, 'production_hardening', False):
            ansible_args.extend(['-e', 'use_production_hardening=true'])
        
        exit_code = dependency_manager.execute_with_dependencies(
            service_name=service_name,
            environment=environment,
            custom_inventory=getattr(args, 'inventory_path', None),
            extra_vars_file=getattr(args, 'extra_vars_file', None),
            extra_args=ansible_args,
            dry_run=args.check,
            target_host=getattr(args, 'target_host', None),
        )
        
        sys.exit(exit_code)
    
    def _get_environment(self, args):
        """Get environment from parsed arguments"""
        if hasattr(args, 'prod') and args.prod:
            return 'prod'
        elif hasattr(args, 'ci') and args.ci:
            return 'ci'
        elif hasattr(args, 'dev') and args.dev:
            return 'dev'
        else:
            return 'dev'  # Default to dev
