"""
PostgreSQL Operations Main Handler

Coordinates PostgreSQL operations by delegating to specialized handlers.
"""

from typing import List, Dict, Any
from pathlib import Path
import yaml

from utils.colors import error
from utils.config import CliConfig, InventoryManager
from execution.ansible import AnsibleRunner
from execution.dependency_manager import DependencyManager
from discovery.service_scanner import ServiceScanner
from operations.recipes import RecipeFinder, RecipeHelpParser

from .arguments import PostgreSQLArgumentParser
from .help_display import PostgreSQLHelpDisplay
from .granular_handler import PostgreSQLGranularHandler
from .recipe_handler import PostgreSQLRecipeHandler


class PostgreSQLOperations:
    """Handle PostgreSQL operations - both recipes and granular tasks"""

    def __init__(self, config: CliConfig):
        self.config = config
        self.inventory_manager = InventoryManager(config)
        self.runner = AnsibleRunner(config)
        self.dependency_manager = DependencyManager(config)
        self.scanner = ServiceScanner(config)
        
        # Initialize handlers
        self.arg_parser = PostgreSQLArgumentParser()
        self.help_display = PostgreSQLHelpDisplay(self.scanner)
        self.granular_handler = PostgreSQLGranularHandler(config, self.runner, self.inventory_manager)
        self.recipe_handler = PostgreSQLRecipeHandler(config, self.dependency_manager, self.inventory_manager)

    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route PostgreSQL operation to appropriate handler"""
        
        # Detect operation from parsed args
        operation = self._detect_parsed_operation(args)
        
        # Show connection info if performing actual operations
        if args.install or operation or self.arg_parser.detect_operation(ansible_args):
            from utils.connection_manager import ConnectionManager
            conn_manager = ConnectionManager(self.config)
            # Get host and port from inventory for connection info
            environment = self.inventory_manager.get_environment_from_args(args)
            inventory_path = self.inventory_manager.get_inventory_path(
                environment=environment,
                custom_path=getattr(args, 'inventory_path', None)
            )
            host, ansible_port = self._extract_host_and_port_from_inventory(inventory_path)
            if host and ansible_port:
                conn_info = conn_manager.get_connection_info(host, ansible_port)
                print(f"🔍 {conn_info}")
        
        # Extract PostgreSQL-specific arguments
        psql_args = self.arg_parser.extract_psql_args(ansible_args)
        
        # Add parsed args to psql_args
        self._add_parsed_args_to_psql_args(args, psql_args)
        
        # Handle recipe installation
        if args.install:
            return self.recipe_handler.handle_recipe_install(args, ansible_args, psql_args)
        
        # Handle granular operations from parsed args first
        if operation:
            return self.granular_handler.handle_granular_operation(operation, args, ansible_args, psql_args)
        
        # Handle granular operations from ansible args
        operation = self.arg_parser.detect_operation(ansible_args)
        if operation:
            return self.granular_handler.handle_granular_operation(operation, args, ansible_args, psql_args)
        
        # Default: show help
        return self.help_display.show_help()
    
    def _extract_host_and_port_from_inventory(self, inventory_path: str) -> tuple:
        """Extract the primary host IP and ansible_port from inventory file"""
        try:
            with open(inventory_path) as f:
                inventory = yaml.safe_load(f)
            
            # Get ansible_port from global vars (fallback to 22)
            ansible_port = inventory.get('all', {}).get('vars', {}).get('ansible_port', 22)
            
            # Look for ansible_host in the first host entry
            hosts = inventory.get('all', {}).get('hosts', {})
            for host_name, host_config in hosts.items():
                if 'ansible_host' in host_config:
                    return host_config['ansible_host'], ansible_port
            
            return None, None
        except Exception:
            return None, None
    
    def _detect_parsed_operation(self, args) -> str:
        """Detect operation from parsed arguments"""
        # Check for extension operations
        if hasattr(args, 'verify_extensions') and args.verify_extensions:
            return 'verify-extensions'
        if hasattr(args, 'list_extensions') and args.list_extensions:
            return 'list-extensions'
        if hasattr(args, 'enable_extension') and args.enable_extension:
            return 'enable-extension'
        if hasattr(args, 'disable_extension') and args.disable_extension:
            return 'disable-extension'
        
        # Check for other operations
        if hasattr(args, 'list_users') and args.list_users:
            return 'list-users'
        if hasattr(args, 'list_databases') and args.list_databases:
            return 'list-databases'
        if hasattr(args, 'adduser') and args.adduser:
            return 'adduser'
        if hasattr(args, 'delete_user') and args.delete_user:
            return 'delete-user'
        if hasattr(args, 'adddb') and args.adddb:
            return 'adddb'
        if hasattr(args, 'delete_db') and args.delete_db:
            return 'delete-db'
        
        return None
    
    def _add_parsed_args_to_psql_args(self, args, psql_args: Dict[str, Any]):
        """Add parsed arguments to psql_args dictionary"""
        # Extension operations
        if hasattr(args, 'enable_extension') and args.enable_extension:
            psql_args['extension_name'] = args.enable_extension
            psql_args['operation'] = 'enable-extension'
        elif hasattr(args, 'disable_extension') and args.disable_extension:
            psql_args['extension_name'] = args.disable_extension
            psql_args['operation'] = 'disable-extension'
        
        # Database parameter
        if hasattr(args, 'database') and args.database:
            psql_args['database'] = args.database
        
        # User operations
        if hasattr(args, 'adduser') and args.adduser:
            psql_args['username'] = args.adduser
        if hasattr(args, 'delete_user') and args.delete_user:
            psql_args['username'] = args.delete_user
        if hasattr(args, 'password') and args.password:
            psql_args['password'] = args.password
        
        # Database operations
        if hasattr(args, 'adddb') and args.adddb:
            psql_args['database'] = args.adddb
        if hasattr(args, 'delete_db') and args.delete_db:
            psql_args['database'] = args.delete_db
        if hasattr(args, 'owner') and args.owner:
            psql_args['owner'] = args.owner
