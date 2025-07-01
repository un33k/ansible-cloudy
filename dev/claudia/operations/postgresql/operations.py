"""
PostgreSQL Operations Main Handler

Coordinates PostgreSQL operations by delegating to specialized handlers.
"""

from typing import List
from pathlib import Path
import yaml

from utils.colors import error
from utils.config import ClaudiaConfig, InventoryManager
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

    def __init__(self, config: ClaudiaConfig):
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
        
        # Show connection info if performing actual operations
        if args.install or self.arg_parser.detect_operation(ansible_args):
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
        
        # Handle recipe installation
        if args.install:
            return self.recipe_handler.handle_recipe_install(args, ansible_args, psql_args)
        
        # Handle granular operations
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
