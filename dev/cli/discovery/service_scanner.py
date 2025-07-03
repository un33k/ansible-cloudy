"""
Service Discovery Engine for CLI
Auto-discovers services and operations from recipes and tasks
"""

import glob
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.colors import Colors, error


class ServiceScanner:
    """Automatically discover services and operations from filesystem"""

    def __init__(self, config):
        self.config = config
        self._service_cache = None

    def discover_services(self) -> Dict[str, Any]:
        """Discover all services from recipes and tasks"""
        if self._service_cache is None:
            self._service_cache = self._scan_services()
        return self._service_cache

    def _scan_services(self) -> Dict[str, Any]:
        """Scan filesystem for services and operations"""
        services = {}

        # Scan recipes directory for service definitions
        recipes = self._scan_recipes()
        
        # Scan tasks directory for operations
        operations = self._scan_task_operations()

        # Combine recipes and operations
        for service_name in set(list(recipes.keys()) + list(operations.keys())):
            services[service_name] = {
                'recipe': recipes.get(service_name),
                'operations': operations.get(service_name, {}),
                'description': self._get_service_description(service_name, recipes.get(service_name))
            }

        return services

    def _scan_recipes(self) -> Dict[str, str]:
        """Scan recipes directory for service recipes"""
        recipes = {}
        
        pattern = str(self.config.recipes_dir / "**" / "*.yml")
        for recipe_path in glob.glob(pattern, recursive=True):
            rel_path = Path(recipe_path).relative_to(self.config.recipes_dir)
            
            if len(rel_path.parts) == 2:  # category/service.yml
                category, filename = rel_path.parts
                service_name = filename[:-4]  # Remove .yml extension
                
                # Normalize special cases
                if service_name == "all-in-one" and category == "standalone":
                    service_name = "standalone"
                elif service_name.endswith("-production"):
                    # Keep production recipes with their full name
                    pass
                    
                recipes[service_name] = str(rel_path)

        return recipes

    def _scan_task_operations(self) -> Dict[str, Dict[str, str]]:
        """Scan tasks directory for service operations"""
        operations = {}
        
        tasks_dir = self.config.base_dir / "cloudy" / "tasks"
        
        # Look for service directories (e.g., db/postgresql/, services/redis/)
        for category_dir in tasks_dir.iterdir():
            if category_dir.is_dir():
                for service_dir in category_dir.iterdir():
                    if service_dir.is_dir():
                        service_name = self._normalize_service_name(category_dir.name, service_dir.name)
                        operations[service_name] = self._scan_service_operations(service_dir)

        return operations

    def _normalize_service_name(self, category: str, service: str) -> str:
        """Normalize service names for consistency"""
        # Map database services
        if category == "db" and service == "postgresql":
            return "psql"
        elif category == "db" and service == "pgvector":
            return "pgvector"
        elif category == "services" and service == "redis":
            return "redis"
        elif category == "web" and service == "nginx":
            return "nginx"
        elif category == "www" and service == "nodejs":
            return "nodejs"
        elif category == "standalone" and service == "all-in-one":
            return "standalone"
        else:
            return service

    def _scan_service_operations(self, service_dir: Path) -> Dict[str, str]:
        """Scan a service directory for available operations"""
        operations = {}
        
        for task_file in service_dir.glob("*.yml"):
            operation_name = self._extract_operation_name(task_file)
            if operation_name:
                operations[operation_name] = str(task_file)

        return operations

    def _extract_operation_name(self, task_file: Path) -> Optional[str]:
        """Extract operation name from task file"""
        try:
            with open(task_file, 'r') as f:
                content = f.read()
                
            # Look for CLI-Operation header
            for line in content.split('\n'):
                if line.startswith('# CLI-Operation:'):
                    return line.split(':', 1)[1].strip()
            
            # Fall back to filename-based operation name
            filename = task_file.stem
            return self._filename_to_operation(filename)
            
        except Exception:
            return None

    def _filename_to_operation(self, filename: str) -> str:
        """Convert filename to operation name"""
        # Convert create-user.yml -> adduser
        # Convert delete-user.yml -> delete-user
        # Convert list-users.yml -> list-users
        
        operation_map = {
            'create-user': 'adduser',
            'create-database': 'adddb',
            'delete-database': 'delete-db',
            'change-user-password': 'change-password',
        }
        
        return operation_map.get(filename, filename)

    def _get_service_description(self, service_name: str, recipe_path: Optional[str]) -> str:
        """Extract service description from recipe file"""
        if not recipe_path:
            return f"{service_name.capitalize()} operations"
            
        try:
            full_path = self.config.recipes_dir / recipe_path
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Look for Purpose comment in recipe
            for line in content.split('\n'):
                if line.startswith('# Purpose:'):
                    return line.split(':', 1)[1].strip()
                    
        except Exception:
            pass
            
        return f"{service_name.capitalize()} database operations" if service_name == "psql" else f"{service_name.capitalize()} operations"

    def list_all_services(self):
        """Display all discovered services and operations"""
        services = self.discover_services()
        
        print(f"{Colors.CYAN}CLI{Colors.NC} (Infrastructure Management Tool)")
        print(f"{Colors.YELLOW}Intelligent Infrastructure Management Made Intuitive{Colors.NC}\n")
        
        print(f"{Colors.BLUE}Available Services:{Colors.NC}")
        
        for service_name, service_info in sorted(services.items()):
            recipe_status = "✅" if service_info['recipe'] else "⚪"
            ops_count = len(service_info['operations'])
            
            print(f"  {Colors.GREEN}{service_name:<12}{Colors.NC} {recipe_status} {service_info['description']}")
            
            if ops_count > 0:
                operations = list(service_info['operations'].keys())[:3]  # Show first 3 operations
                ops_display = ", ".join(operations)
                if ops_count > 3:
                    ops_display += f", +{ops_count-3} more"
                print(f"    {Colors.CYAN}Operations:{Colors.NC} {ops_display}")
            
        print(f"\n{Colors.YELLOW}Usage:{Colors.NC}")
        print(f"  {Colors.GREEN}cli <service> --help{Colors.NC}     Show service operations")
        print(f"  {Colors.GREEN}cli <service> --install{Colors.NC}  Install/setup service")
        print(f"  {Colors.GREEN}cli psql --adduser foo{Colors.NC}   Create PostgreSQL user")

    def get_service_operations(self, service_name: str) -> Dict[str, str]:
        """Get operations for a specific service"""
        services = self.discover_services()
        return services.get(service_name, {}).get('operations', {})
