"""
Dependency Manager for Claudia CLI
Handles automatic dependency chain execution: security → base → service
"""

import subprocess
from typing import List, Dict, Any
from pathlib import Path

from utils.colors import info, warn, error
from utils.config import ClaudiaConfig, InventoryManager
from execution.ansible import AnsibleRunner, SmartSecurityRunner


class DependencyManager:
    """Manages service dependencies and automatic prerequisite execution"""

    def __init__(self, config: ClaudiaConfig):
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
    ) -> int:
        """Execute service with automatic dependency resolution"""
        if extra_args is None:
            extra_args = []

        info(f"🔍 Checking dependencies for service: {service_name}")

        # Get dependency chain
        dependencies = self._get_dependency_chain(service_name)
        
        if not dependencies:
            warn(f"⚠️ No dependencies defined for {service_name}")
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
        return self._execute_service_directly(
            service_name, environment, custom_inventory, extra_vars_file,
            extra_args, dry_run, target_host
        )

    def _get_dependency_chain(self, service_name: str) -> List[str]:
        """Get the dependency chain for a service"""
        # Define dependency mappings
        dependencies = {
            # Core services (no dependencies)
            "security": [],
            "base": ["security"],
            
            # Database services
            "psql": ["security", "base"],
            "postgis": ["security", "base"],
            "mongodb": ["security", "base"],
            
            # Cache services
            "redis": ["security", "base"],
            
            # Connection pooling
            "pgbouncer": [],  # No dependencies - installed on existing web servers
            
            # Web services
            "nginx": ["security", "base"],
            "apache": ["security", "base"],
            "django": ["security", "base"],
            "nodejs": ["security", "base"],
            
            # VPN services
            "openvpn": ["security", "base"],
            "wireguard": ["security", "base"],
        }
        
        return dependencies.get(service_name, ["security", "base"])

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
        
        # For dry runs, always assume dependencies need to be checked
        if dependency == "security":
            return self._is_security_configured(environment, custom_inventory, target_host)
        elif dependency == "base":
            return self._is_base_configured(environment, custom_inventory, target_host)
        else:
            # For other services, we could add more sophisticated checking
            return False

    def _is_security_configured(
        self,
        environment: str,
        custom_inventory: str,
        target_host: str = None
    ) -> bool:
        """Check if security is already configured"""
        # Convert environment to production bool for backward compatibility
        production = (environment == 'prod')
        
        # Use smart security detection
        connection_info = self.smart_security._smart_port_detection(production, target_host)
        
        # If we can connect on a non-22 port with SSH keys, security is likely configured
        if connection_info['success'] and connection_info['port'] != 22:
            return True
        
        return False

    def _is_base_configured(
        self,
        environment: str,
        custom_inventory: str,
        target_host: str = None
    ) -> bool:
        """Check if base configuration is installed"""
        # Simple check: if security is configured and we can connect, base is likely done
        # In a more sophisticated implementation, we could check for specific markers
        return self._is_security_configured(environment, custom_inventory, target_host)
