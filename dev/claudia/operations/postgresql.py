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
            else:
                i += 1
        
        return psql_args

    def _detect_operation(self, ansible_args: List[str]) -> str:
        """Detect which granular operation is requested"""
        operations = ['--adduser', '--delete-user', '--list-users', '--list-databases', '--adddb']
        
        for arg in ansible_args:
            if arg in operations:
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
        print(f"  {Colors.GREEN}claudia psql --list-databases{Colors.NC}                     List all databases")
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