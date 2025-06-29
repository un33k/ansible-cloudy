"""
Claudia CLI Command Router
Routes commands to appropriate handlers and manages service operations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
claudia_dir = Path(__file__).parent.parent
cli_dir = Path(__file__).parent
sys.path.insert(0, str(claudia_dir))
sys.path.insert(0, str(cli_dir))

from utils.colors import error  # noqa: E402
from utils.config import ClaudiaConfig  # noqa: E402
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
                self.config = ClaudiaConfig()
            except Exception as e:
                error(f"Configuration error: {e}")
        return self.config
    
    def handle_help_requests(self, claudia_args):
        """Handle service-specific help requests before main parsing"""
        # Check for dev subcommand help
        if len(claudia_args) >= 3 and claudia_args[0] == "dev" and claudia_args[2] in ["--help", "-h"]:
            if claudia_args[1] == "validate":
                show_validate_help()
                return True
        
        # Check for service-specific help
        elif len(claudia_args) >= 2 and claudia_args[1] in ["--help", "-h"] and claudia_args[0] not in ["dev"]:
            service_name = claudia_args[0]
            config = self.initialize_config()
            
            try:
                # Handle service-specific help
                if service_name == "psql":
                    psql_ops = PostgreSQLOperations(config)
                    psql_ops._show_psql_help()
                    return True
                elif service_name == "redis":
                    redis_ops = RedisOperations(config)
                    redis_ops._show_service_help()
                    return True
                elif service_name == "nginx":
                    nginx_ops = NginxOperations(config)
                    nginx_ops._show_service_help()
                    return True
                
                # Handle other services with recipe help
                finder = RecipeFinder(config)
                recipe_path = finder.find_recipe(service_name)
                if recipe_path:
                    help_parser = RecipeHelpParser(config)
                    help_parser.display_recipe_help(service_name, recipe_path)
                    return True
                else:
                    error(f"Service '{service_name}' not found. Use 'claudia --list-services' to see available services.")
            except Exception as e:
                error(f"Configuration error: {e}")
        
        return False
    
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
        elif service_name == "redis":
            redis_ops = RedisOperations(config)
            exit_code = redis_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        elif service_name == "nginx":
            nginx_ops = NginxOperations(config)
            exit_code = nginx_ops.handle_operation(args, ansible_args)
            sys.exit(exit_code)
        else:
            return False  # Service not handled by specific operations
        
        return True
    
    def handle_generic_service(self, service_name, args, ansible_args):
        """Handle generic services using recipe finder"""
        from utils.config import InventoryManager  # noqa: E402
        from execution.ansible import AnsibleRunner  # noqa: E402
        
        config = self.initialize_config()
        finder = RecipeFinder(config)
        recipe_path = finder.find_recipe(service_name)
        
        if not recipe_path:
            error(f"Service '{service_name}' not found. Use 'claudia --list-services' to see available services.")
        
        # Show service help by default
        if not args.install:
            help_parser = RecipeHelpParser(config)
            help_parser.display_recipe_help(service_name, recipe_path)
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
