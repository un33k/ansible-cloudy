"""
Dependency Manager for CLI
Handles automatic dependency chain execution: security → base → service
"""

import subprocess
from typing import List, Dict, Any
from pathlib import Path

from utils.colors import info, warn, error
from utils.config import CliConfig, InventoryManager
from execution.ansible import AnsibleRunner, SmartSecurityRunner


class DependencyManager:
    """Manages service dependencies and automatic prerequisite execution"""

    def __init__(self, config: CliConfig):
        self.config = config
        self.inventory_manager = InventoryManager(config)
        self.ansible_runner = AnsibleRunner(config)
        self.smart_security = SmartSecurityRunner(
            config, self.inventory_manager, self.ansible_runner
        )

    def execute_with_dependencies(
        self,
        service_name: str,
        environment: str = 'dev',
        custom_inventory: str = None,
        extra_vars_file: str = None,
        extra_args: List[str] = None,
        dry_run: bool = False,
        target_host: str = None,
        skip_dependencies: bool = False,
    ) -> int:
        """Execute service with automatic dependency resolution"""
        if extra_args is None:
            extra_args = []

        # If skip_dependencies is True, execute service directly
        if skip_dependencies:
            info(f"🚀 Executing service: {service_name} (dependencies skipped)")
            return self._execute_service_directly(
                service_name, environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )

        info(f"🔍 Checking dependencies for service: {service_name}")

        # Get dependency chain
        dependencies = self._get_dependency_chain(service_name)
        
        if not dependencies:
            info(f"✨ No dependencies required for {service_name}")
            # Execute the main service directly
            info(f"🚀 Executing service: {service_name}")
            return self._execute_service_directly(
                service_name, environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )

        info(f"📋 Dependency chain: {' → '.join(dependencies)}")

        # Execute dependency chain
        for dep in dependencies:
            result = self._execute_dependency(
                dep, environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )
            if result != 0:
                error(f"❌ Dependency '{dep}' failed - stopping execution")
                return result
            info(f"✅ Dependency '{dep}' completed successfully")

        # Execute the main service
        info(f"🚀 Executing main service: {service_name}")
        
        # For -server variants, use the base service name
        if service_name.endswith('-server'):
            base_service_name = service_name[:-7]  # Remove '-server'
        else:
            base_service_name = service_name
            
        result = self._execute_service_directly(
            base_service_name, environment, custom_inventory, extra_vars_file,
            extra_args, dry_run, target_host
        )
        
        if result != 0:
            return result
            
        # Special handling: django-server and nodejs-server also install pgbouncer
        if service_name in ['django-server', 'nodejs-server']:
            info(f"🔧 Installing pgbouncer for {service_name}")
            return self._execute_service_directly(
                'pgbouncer', environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )
            
        return result

    def _get_dependency_chain(self, service_name: str) -> List[str]:
        """Get the dependency chain for a service"""
        # Define dependency mappings
        # Note: Regular services now have NO dependencies by default
        # Only -server variants will have dependencies
        dependencies = {
            # Core services
            "harden": [],  # No dependencies - port change tool
            "security": [],  # No dependencies - handles initial setup
            "base": [],  # No dependencies for direct base install
            
            # Database services (no dependencies for service-only install)
            "psql": [],
            "postgis": [],
            "mongodb": [],
            
            # Cache services
            "redis": [],
            
            # Connection pooling
            "pgbouncer": [],  # No dependencies - installed on existing web servers
            
            # Web services
            "nginx": [],
            "apache": [],
            "django": [],
            "nodejs": [],
            
            # VPN services
            "openvpn": [],
            "wireguard": [],
            
            # Finalization
            "finalize": [],
            
            # Full server installations (-server variants)
            # These will be handled by the command router
            "psql-server": ["security", "base"],
            "postgis-server": ["security", "base"],
            "mongodb-server": ["security", "base"],
            "redis-server": ["security", "base"],
            "nginx-server": ["security", "base"],
            "apache-server": ["security", "base"],
            "django-server": ["security", "base"],
            "nodejs-server": ["security", "base"],
            "openvpn-server": ["security", "base"],
            "wireguard-server": ["security", "base"],
        }
        
        return dependencies.get(service_name, [])

    def _execute_dependency(
        self,
        dependency: str,
        environment: str,
        custom_inventory: str,
        extra_vars_file: str,
        extra_args: List[str],
        dry_run: bool,
        target_host: str = None,
    ) -> int:
        """Execute a single dependency"""
        
        # Skip if already deployed (basic check)
        if self._is_dependency_satisfied(dependency, environment, custom_inventory, target_host):
            info(f"✓ Dependency '{dependency}' already satisfied")
            return 0

        info(f"🔧 Installing dependency: {dependency}")
        
        if dependency == "security":
            return self._execute_security(
                environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )
        elif dependency == "base":
            return self._execute_base(
                environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )
        else:
            return self._execute_service_directly(
                dependency, environment, custom_inventory, extra_vars_file,
                extra_args, dry_run, target_host
            )

    def _execute_security(
        self,
        environment: str,
        custom_inventory: str,
        extra_vars_file: str,
        extra_args: List[str],
        dry_run: bool,
        target_host: str = None
    ) -> int:
        """Execute security setup using smart security runner"""
        # Need to convert environment to production bool for backward compatibility
        production = (environment == 'prod')
        
        return self.smart_security.run_smart_security(
            production=production,
            extra_args=extra_args,
            dry_run=dry_run,
            target_host=target_host,
        )

    def _execute_base(
        self,
        environment: str,
        custom_inventory: str,
        extra_vars_file: str,
        extra_args: List[str],
        dry_run: bool,
        target_host: str = None
    ) -> int:
        """Execute base configuration"""
        inventory_path = self.inventory_manager.get_inventory_path(
            environment=environment,
            custom_path=custom_inventory
        )
        
        return self.ansible_runner.run_recipe(
            recipe_path="core/base.yml",
            inventory_path=inventory_path,
            extra_args=extra_args,
            dry_run=dry_run,
            target_host=target_host,
            extra_vars_file=extra_vars_file,
        )

    def _execute_service_directly(
        self,
        service_name: str,
        environment: str,
        custom_inventory: str,
        extra_vars_file: str,
        extra_args: List[str],
        dry_run: bool,
        target_host: str = None,
    ) -> int:
        """Execute a service directly without dependency checking"""
        from operations.recipes import RecipeFinder
        
        finder = RecipeFinder(self.config)
        recipe_path = finder.find_recipe(service_name)
        
        if not recipe_path:
            error(f"Recipe not found for service: {service_name}")
            return 1
        
        inventory_path = self.inventory_manager.get_inventory_path(
            environment=environment,
            custom_path=custom_inventory
        )
        
        return self.ansible_runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=extra_args,
            dry_run=dry_run,
            target_host=target_host,
            extra_vars_file=extra_vars_file,
        )

    def _is_dependency_satisfied(
        self,
        dependency: str,
        environment: str,
        custom_inventory: str,
        target_host: str = None
    ) -> bool:
        """Check if a dependency is already satisfied"""
        
        # For now, always run dependencies to ensure proper setup
        # In the future, we could implement more sophisticated checking
        return False
