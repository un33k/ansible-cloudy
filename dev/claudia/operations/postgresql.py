"""
PostgreSQL Operations for Claudia
Handles both recipe installation and granular database operations
"""

import sys
from typing import Dict, Any, List
from pathlib import Path

from utils.colors import Colors, error
from utils.config import AliConfig, InventoryManager
from execution.ansible import AnsibleRunner
from discovery.service_scanner import ServiceScanner
from operations.recipes import RecipeFinder, RecipeHelpParser


class PostgreSQLOperations:
    """Handle PostgreSQL operations - both recipes and granular tasks"""

    def __init__(self, config: AliConfig):
        self.config = config
        self.inventory_manager = InventoryManager(config)
        self.runner = AnsibleRunner(config)
        self.scanner = ServiceScanner(config)

    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route PostgreSQL operation to appropriate handler"""
        
        # Show connection info if performing actual operations
        if args.install or self._detect_operation(ansible_args):
            from utils.connection_manager import ConnectionManager
            conn_manager = ConnectionManager(self.config)
            # Get host and port from inventory for connection info
            inventory_path = self.inventory_manager.get_inventory_path(args.prod)
            host, ansible_port = self._extract_host_and_port_from_inventory(inventory_path)
            if host and ansible_port:
                conn_info = conn_manager.get_connection_info(host, ansible_port)
                print(f"🔍 {conn_info}")
        
        # Extract PostgreSQL-specific arguments
        psql_args = self._extract_psql_args(ansible_args)
        
        # Handle recipe installation
        if args.install:
            return self._handle_recipe_install(args, ansible_args, psql_args)
        
        # Handle granular operations
        operation = self._detect_operation(ansible_args)
        if operation:
            return self._handle_granular_operation(operation, args, ansible_args, psql_args)
        
        # Default: show help
        return self._show_psql_help()

    def _extract_psql_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract PostgreSQL-specific arguments from command line"""
        psql_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            # PostgreSQL recipe arguments
            if arg == "--port":
                if i + 1 < len(ansible_args):
                    psql_args['database_port'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--port requires a value")
            elif arg == "--pgis":
                psql_args['setup_postgis'] = True
                i += 1
            
            # Granular operation arguments
            elif arg == "--adduser":
                psql_args['operation'] = 'adduser'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--adduser requires a username")
            elif arg == "--password":
                if i + 1 < len(ansible_args):
                    psql_args['password'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--password requires a value")
            elif arg == "--database":
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--database requires a value")
            elif arg == "--delete-user":
                psql_args['operation'] = 'delete-user'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--delete-user requires a username")
            elif arg == "--list-users":
                psql_args['operation'] = 'list-users'
                i += 1
            elif arg == "--list-databases":
                psql_args['operation'] = 'list-databases'
                i += 1
            elif arg == "--adddb":
                psql_args['operation'] = 'adddb'
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--adddb requires a database name")
            elif arg == "--owner":
                if i + 1 < len(ansible_args):
                    psql_args['owner'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--owner requires a username")
            
            # Additional PostgreSQL operations
            elif arg == "--delete-db":
                psql_args['operation'] = 'delete-db'
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--delete-db requires a database name")
            elif arg == "--dump-database":
                psql_args['operation'] = 'dump-database'
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--dump-database requires a database name")
            elif arg == "--change-password":
                psql_args['operation'] = 'change-password'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--change-password requires a username")
            elif arg == "--grant-privileges":
                psql_args['operation'] = 'grant-privileges'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--grant-privileges requires a username")
            elif arg == "--privileges":
                if i + 1 < len(ansible_args):
                    psql_args['privileges'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--privileges requires a value")
            elif arg == "--install-postgis":
                psql_args['operation'] = 'install-postgis'
                i += 1
            elif arg == "--get-version":
                psql_args['operation'] = 'get-installed-version'
                i += 1
            elif arg == "--get-latest-version":
                psql_args['operation'] = 'get-latest-version'
                i += 1
            elif arg == "--install-client":
                psql_args['operation'] = 'install-client'
                i += 1
            elif arg == "--configure-port":
                psql_args['operation'] = 'configure-port'
                if i + 1 < len(ansible_args):
                    psql_args['port'] = ansible_args[i + 1]
                    i += 2
                else:
                    psql_args['port'] = '5432'  # Default port
                    i += 1
            elif arg == "--create-cluster":
                psql_args['operation'] = 'create-cluster'
                if i + 1 < len(ansible_args):
                    psql_args['cluster_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--create-cluster requires a cluster name")
            elif arg == "--remove-cluster":
                psql_args['operation'] = 'remove-cluster'
                if i + 1 < len(ansible_args):
                    psql_args['cluster_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--remove-cluster requires a cluster name")
            elif arg == "--install-repo":
                psql_args['operation'] = 'install-repo'
                i += 1
            else:
                i += 1
        
        return psql_args

    def _detect_operation(self, ansible_args: List[str]) -> str:
        """Detect which granular operation is requested"""
        operations = [
            '--adduser', '--delete-user', '--list-users', '--list-databases', '--adddb',
            '--delete-db', '--dump-database', '--change-password', '--grant-privileges',
            '--install-postgis', '--get-version', '--get-latest-version', '--install-client',
            '--configure-port', '--create-cluster', '--remove-cluster', '--install-repo'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                # Handle special mapping for get-version
                if arg == '--get-version':
                    return 'get-installed-version'
                return arg[2:]  # Remove -- prefix
        
        return None

    def _handle_recipe_install(self, args, ansible_args: List[str], psql_args: Dict[str, Any]) -> int:
        """Handle PostgreSQL recipe installation"""
        
        # Find PostgreSQL recipe
        finder = RecipeFinder(self.config)
        recipe_path = finder.find_recipe("psql")
        
        if not recipe_path:
            error("PostgreSQL recipe not found")
        
        # Build Ansible extra vars from psql_args
        extra_vars = []
        if 'database_port' in psql_args:
            extra_vars.extend(["-e", f"database_port={psql_args['database_port']}"])
        if psql_args.get('setup_postgis'):
            extra_vars.extend(["-e", "setup_postgis=true"])
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            extra_vars.insert(0, "-v")
        
        # Execute recipe
        inventory_path = self.inventory_manager.get_inventory_path(args.prod)
        return self.runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=extra_vars + [arg for arg in ansible_args if arg not in ['--port', '--pgis'] and not arg.isdigit()],
            dry_run=args.check,
        )

    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], psql_args: Dict[str, Any]) -> int:
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
        inventory_path = self.inventory_manager.get_inventory_path(args.prod)
        return self.runner.run_task(
            task_path=str(task_path),
            inventory_path=inventory_path,
            extra_args=extra_vars,
            dry_run=args.check,
        )

    def _show_psql_help(self) -> int:
        """Show PostgreSQL help with available operations"""
        
        print(f"{Colors.CYAN}📖 Help: PostgreSQL Operations{Colors.NC}")
        print("=" * 50)
        print()
        
        print(f"{Colors.BLUE}Description:{Colors.NC}")
        print("  PostgreSQL Database Server with PostGIS Support")
        print()
        
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia psql --install{Colors.NC}                    Install PostgreSQL server")
        print(f"  {Colors.GREEN}claudia psql --install --port 5544{Colors.NC}       Install on custom port")
        print(f"  {Colors.GREEN}claudia psql --install --pgis{Colors.NC}            Install with PostGIS extension")
        print(f"  {Colors.GREEN}claudia psql --install --port 5544 --pgis{Colors.NC} Install with custom port and PostGIS")
        print()
        
        print(f"{Colors.BLUE}User Management:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia psql --adduser foo --password 1234{Colors.NC}         Create user")
        print(f"  {Colors.GREEN}claudia psql --delete-user foo{Colors.NC}                    Delete user")
        print(f"  {Colors.GREEN}claudia psql --list-users{Colors.NC}                         List all users")
        print()
        
        print(f"{Colors.BLUE}Database Management:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia psql --adddb myapp{Colors.NC}                        Create database")
        print(f"  {Colors.GREEN}claudia psql --adddb myapp --owner myuser{Colors.NC}         Create database with owner")
        print(f"  {Colors.GREEN}claudia psql --delete-db oldapp{Colors.NC}                   Delete database")
        print(f"  {Colors.GREEN}claudia psql --list-databases{Colors.NC}                     List all databases")
        print(f"  {Colors.GREEN}claudia psql --dump-database myapp{Colors.NC}               Dump database to file")
        print()
        
        print(f"{Colors.BLUE}Advanced Operations:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia psql --change-password foo --password newpass{Colors.NC}  Change user password")
        print(f"  {Colors.GREEN}claudia psql --grant-privileges foo --database myapp{Colors.NC}   Grant user privileges")
        print(f"  {Colors.GREEN}claudia psql --install-postgis{Colors.NC}                    Install PostGIS extension")
        print(f"  {Colors.GREEN}claudia psql --configure-port 5433{Colors.NC}               Configure PostgreSQL port")
        print(f"  {Colors.GREEN}claudia psql --get-version{Colors.NC}                        Get installed PostgreSQL version")
        print(f"  {Colors.GREEN}claudia psql --create-cluster mycluster{Colors.NC}          Create PostgreSQL cluster")
        print(f"  {Colors.GREEN}claudia psql --install-client{Colors.NC}                    Install PostgreSQL client tools")
        print()
        
        print(f"{Colors.BLUE}Options:{Colors.NC}")
        print(f"  {Colors.CYAN}--prod{Colors.NC}                 Use production inventory")
        print(f"  {Colors.CYAN}--check{Colors.NC}                Dry run (no changes)")
        print(f"  {Colors.CYAN}--verbose{Colors.NC}              Verbose output")
        print()
        
        # Show discovered operations
        operations = self.scanner.get_service_operations('psql')
        if operations:
            print(f"{Colors.BLUE}Auto-discovered Operations:{Colors.NC}")
            for op_name, task_path in operations.items():
                print(f"  {Colors.YELLOW}{op_name}{Colors.NC}")
        
        return 0
    
    def _extract_host_and_port_from_inventory(self, inventory_path: str) -> tuple:
        """Extract the primary host IP and ansible_port from inventory file"""
        try:
            import yaml
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
