"""
Base Service Operations for Claudia
Provides common functionality for all service operations
"""

import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from utils.colors import Colors, error, info
from utils.config import ClaudiaConfig, InventoryManager
from execution.ansible import AnsibleRunner
from discovery.service_scanner import ServiceScanner
from operations.recipes import RecipeFinder, RecipeHelpParser


class BaseServiceOperations(ABC):
    """Base class for all service operations"""

    def __init__(self, config: ClaudiaConfig, service_name: str):
        self.config = config
        self.service_name = service_name
        self.inventory_manager = InventoryManager(config)
        self.runner = AnsibleRunner(config)
        self.scanner = ServiceScanner(config)

    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route service operation to appropriate handler"""
        
        # Show connection info if performing actual operations
        if args.install or self._has_operation_args(ansible_args):
            self._show_connection_info(args)
        
        # Extract service-specific arguments
        service_args = self._extract_service_args(ansible_args)
        
        # Handle recipe installation
        if args.install:
            return self._handle_recipe_install(args, ansible_args, service_args)
        
        # Handle granular operations (if any)
        operation = self._detect_operation(ansible_args)
        if operation:
            return self._handle_granular_operation(operation, args, ansible_args, service_args)
        
        # Default: show help
        return self._show_service_help()

    def _show_connection_info(self, args):
        """Show connection information"""
        try:
            from utils.connection_manager import ConnectionManager
            conn_manager = ConnectionManager(self.config)
            inventory_path = self.inventory_manager.get_inventory_path(args.prod)
            host, ansible_port = self._extract_host_and_port_from_inventory(inventory_path)
            if host and ansible_port:
                conn_info = conn_manager.get_connection_info(host, ansible_port)
                print(f"🔍 {conn_info}")
        except Exception:
            pass  # Silently continue if connection info fails

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

    @abstractmethod
    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract service-specific arguments from command line"""
        pass

    @abstractmethod
    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        pass

    def _has_operation_args(self, ansible_args: List[str]) -> bool:
        """Check if ansible_args contains operation arguments"""
        operation_flags = self._get_operation_flags()
        return any(arg in operation_flags for arg in ansible_args)

    def _get_operation_flags(self) -> List[str]:
        """Get list of operation flags for this service (override in subclasses)"""
        return []

    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which granular operation is requested (override in subclasses)"""
        return None

    def _handle_recipe_install(self, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle service recipe installation"""
        
        # Find service recipe
        finder = RecipeFinder(self.config)
        recipe_path = finder.find_recipe(self.service_name)
        
        if not recipe_path:
            error(f"{self.service_name.title()} recipe not found")
        
        # Build Ansible extra vars from service_args
        extra_vars = []
        param_mapping = self._get_parameter_mapping()
        
        for cli_param, ansible_var in param_mapping.items():
            if cli_param.lstrip('-') in service_args:
                value = service_args[cli_param.lstrip('-')]
                extra_vars.extend(["-e", f"{ansible_var}={value}"])
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            extra_vars.insert(0, "-v")
        
        # Execute recipe
        inventory_path = self.inventory_manager.get_inventory_path(args.prod)
        return self.runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=extra_vars + [arg for arg in ansible_args if not self._is_service_arg(arg)],
            dry_run=args.check,
        )

    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle granular service operations (override in subclasses)"""
        error(f"Granular operations not implemented for {self.service_name}")

    def _is_service_arg(self, arg: str) -> bool:
        """Check if argument is a service-specific parameter"""
        param_mapping = self._get_parameter_mapping()
        return arg in param_mapping or arg.lstrip('-') in [p.lstrip('-') for p in param_mapping.keys()]

    def _show_service_help(self) -> int:
        """Show service help with parameters and operations"""
        print(f"{Colors.CYAN}📖 Help: {self.service_name.title()} Operations{Colors.NC}")
        print("=" * 50)
        print()
        
        # Get service description
        services = self.scanner.discover_services()
        service_info = services.get(self.service_name, {})
        description = service_info.get('description', f'{self.service_name.title()} service operations')
        
        print(f"{Colors.BLUE}Description:{Colors.NC}")
        print(f"  {description}")
        print()
        
        # Show installation help
        self._show_installation_help()
        
        # Show granular operations (if any)
        self._show_granular_operations_help()
        
        # Show options
        print(f"{Colors.BLUE}Options:{Colors.NC}")
        print(f"  {Colors.CYAN}--prod{Colors.NC}                 Use production inventory")
        print(f"  {Colors.CYAN}--check{Colors.NC}                Dry run (no changes)")
        print(f"  {Colors.CYAN}--verbose{Colors.NC}              Verbose output")
        print()
        
        # Show auto-discovered operations
        operations = service_info.get('operations', {})
        if operations:
            print(f"{Colors.BLUE}Auto-discovered Operations:{Colors.NC}")
            for op_name in sorted(operations.keys()):
                print(f"  {Colors.YELLOW}{op_name}{Colors.NC}")
        
        return 0

    def _show_installation_help(self):
        """Show installation parameters (override in subclasses for custom help)"""
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia {self.service_name} --install{Colors.NC}                    Install {self.service_name}")
        
        # Show parameter examples
        param_mapping = self._get_parameter_mapping()
        if param_mapping:
            print(f"  {Colors.GREEN}claudia {self.service_name} --install [options]{Colors.NC}       Install with custom parameters")
            print()
            print(f"{Colors.BLUE}Available Parameters:{Colors.NC}")
            for cli_param, ansible_var in param_mapping.items():
                print(f"  {Colors.CYAN}{cli_param}{Colors.NC}                 Configure {ansible_var}")
        print()

    def _show_granular_operations_help(self):
        """Show granular operations help (override in subclasses)"""
        pass
