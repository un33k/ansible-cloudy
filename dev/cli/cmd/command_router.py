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
from operations.recipes import RecipeFinder  # noqa: E402
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
    
    def handle_list_services(self):
        """Handle --list command"""
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
        elif service_name == "docker":
            from operations.docker import DockerOperations
            docker_ops = DockerOperations(config)
            exit_code = docker_ops.handle_operation(args, ansible_args)
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
        elif service_name == "ssh":
            from operations.ssh import SSHOperations
            ssh_ops = SSHOperations(config)
            exit_code = ssh_ops.handle_operation(args, ansible_args)
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
        
        # If --install not specified, argparse will have shown help already
        if not hasattr(args, 'install') or not args.install:
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
