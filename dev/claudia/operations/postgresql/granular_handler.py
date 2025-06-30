"""
PostgreSQL Granular Operations Handler

Handles individual PostgreSQL operations like user/database management.
"""

from typing import Dict, Any, List
from pathlib import Path
from utils.colors import error
from utils.config import ClaudiaConfig, InventoryManager
from execution.ansible import AnsibleRunner


class PostgreSQLGranularHandler:
    """Handle granular PostgreSQL operations"""
    
    def __init__(self, config: ClaudiaConfig, runner: AnsibleRunner, inventory_manager: InventoryManager):
        self.config = config
        self.runner = runner
        self.inventory_manager = inventory_manager
    
    def handle_granular_operation(self, operation: str, args, ansible_args: List[str], psql_args: Dict[str, Any]) -> int:
        """Handle granular PostgreSQL operations"""
        
        # Map operations to task files
        operation_map = {
            'adduser': 'create-user.yml',
            'delete-user': 'delete-user.yml', 
            'list-users': 'list-users.yml',
            'list-databases': 'list-databases.yml',
            'adddb': 'create-database.yml',
            'delete-db': 'delete-database.yml',
            'dump-database': 'dump-database.yml',
            'change-password': 'change-user-password.yml',
            'grant-privileges': 'grant-privileges.yml',
            'install-postgis': 'install-postgis.yml',
            'get-installed-version': 'get-installed-version.yml',
            'get-latest-version': 'get-latest-version.yml',
            'install-client': 'install-client.yml',
            'configure-port': 'configure-port.yml',
            'create-cluster': 'create-cluster.yml',
            'remove-cluster': 'remove-cluster.yml',
            'install-repo': 'install-repo.yml',
        }
        
        task_file = operation_map.get(operation)
        if not task_file:
            error(f"Unknown PostgreSQL operation: {operation}")
        
        # Build task path
        task_path = self.config.base_dir / "cloudy" / "tasks" / "db" / "postgresql" / task_file
        
        if not task_path.exists():
            error(f"Task file not found: {task_path}")
        
        # Build extra vars
        extra_vars = []
        
        if operation == 'adduser':
            if 'username' not in psql_args or 'password' not in psql_args:
                error("--adduser requires both --password")
            extra_vars.extend(["-e", f"username={psql_args['username']}"])
            extra_vars.extend(["-e", f"password={psql_args['password']}"])
            if 'database' in psql_args:
                extra_vars.extend(["-e", f"database={psql_args['database']}"])
                
        elif operation == 'delete-user':
            if 'username' not in psql_args:
                error("--delete-user requires a username")
            extra_vars.extend(["-e", f"username={psql_args['username']}"])
            
        elif operation == 'adddb':
            if 'database' not in psql_args:
                error("--adddb requires a database name")
            extra_vars.extend(["-e", f"database={psql_args['database']}"])
            if 'owner' in psql_args:
                extra_vars.extend(["-e", f"owner={psql_args['owner']}"])
                
        elif operation == 'delete-db':
            if 'database' not in psql_args:
                error("--delete-db requires a database name")
            extra_vars.extend(["-e", f"database={psql_args['database']}"])
            
        elif operation == 'dump-database':
            if 'database' not in psql_args:
                error("--dump-database requires a database name")
            extra_vars.extend(["-e", f"database={psql_args['database']}"])
            
        elif operation == 'change-password':
            if 'username' not in psql_args or 'password' not in psql_args:
                error("--change-password requires both username and --password")
            extra_vars.extend(["-e", f"username={psql_args['username']}"])
            extra_vars.extend(["-e", f"password={psql_args['password']}"])
            
        elif operation == 'grant-privileges':
            if 'username' not in psql_args:
                error("--grant-privileges requires a username")
            extra_vars.extend(["-e", f"username={psql_args['username']}"])
            if 'database' in psql_args:
                extra_vars.extend(["-e", f"database={psql_args['database']}"])
            if 'privileges' in psql_args:
                extra_vars.extend(["-e", f"privileges={psql_args['privileges']}"])
            else:
                extra_vars.extend(["-e", "privileges=ALL"])  # Default privileges
                
        elif operation == 'configure-port':
            if 'port' in psql_args:
                extra_vars.extend(["-e", f"pg_port={psql_args['port']}"])
            else:
                extra_vars.extend(["-e", "pg_port=5432"])  # Default port
                
        elif operation == 'create-cluster':
            if 'cluster_name' not in psql_args:
                error("--create-cluster requires a cluster name")
            extra_vars.extend(["-e", f"cluster_name={psql_args['cluster_name']}"])
            
        elif operation == 'remove-cluster':
            if 'cluster_name' not in psql_args:
                error("--remove-cluster requires a cluster name")
            extra_vars.extend(["-e", f"cluster_name={psql_args['cluster_name']}"])
            
        # Operations that don't require additional parameters
        elif operation in ['list-users', 'list-databases', 'install-postgis', 'get-installed-version',
                           'get-latest-version', 'install-client', 'install-repo']:
            pass  # No additional parameters needed
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            extra_vars.insert(0, "-v")
        
        # Execute task
        environment = self.inventory_manager.get_environment_from_args(args)
        inventory_path = self.inventory_manager.get_inventory_path(
            environment=environment,
            custom_path=getattr(args, 'inventory_path', None)
        )
        
        return self.runner.run_task(
            task_path=str(task_path),
            inventory_path=inventory_path,
            extra_args=extra_vars,
            dry_run=args.check,
            target_host=getattr(args, 'target_host', None),
            extra_vars_file=getattr(args, 'extra_vars_file', None),
        )