"""
PostgreSQL Recipe Handler

Handles PostgreSQL recipe installation with dependency management.
"""

from typing import Dict, Any, List
from utils.colors import error
from utils.config import ClaudiaConfig, InventoryManager
from execution.dependency_manager import DependencyManager
from operations.recipes import RecipeFinder


class PostgreSQLRecipeHandler:
    """Handle PostgreSQL recipe installation"""
    
    def __init__(self, config: ClaudiaConfig, dependency_manager: DependencyManager, inventory_manager: InventoryManager):
        self.config = config
        self.dependency_manager = dependency_manager
        self.inventory_manager = inventory_manager
    
    def handle_recipe_install(self, args, ansible_args: List[str], psql_args: Dict[str, Any]) -> int:
        """Handle PostgreSQL recipe installation with automatic dependencies"""
        
        # Build Ansible extra vars from psql_args
        extra_vars = []
        if 'database_port' in psql_args:
            extra_vars.extend(["-e", f"database_port={psql_args['database_port']}"])
        if psql_args.get('setup_postgis'):
            extra_vars.extend(["-e", "setup_postgis=true"])
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            extra_vars.insert(0, "-v")
        
        # Execute with automatic dependency resolution (security → base → psql)
        full_extra_args = extra_vars + [arg for arg in ansible_args if arg not in ['--port', '--pgis'] and not arg.isdigit()]
        
        environment = self.inventory_manager.get_environment_from_args(args)
        
        return self.dependency_manager.execute_with_dependencies(
            service_name="psql",
            environment=environment,
            custom_inventory=getattr(args, 'inventory_path', None),
            extra_vars_file=getattr(args, 'extra_vars_file', None),
            extra_args=full_extra_args,
            dry_run=args.check,
            target_host=getattr(args, 'target_host', None),
        )