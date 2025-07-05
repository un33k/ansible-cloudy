"""
Harden Operation Handler
Manages atomic SSH hardening
"""

from typing import List, Dict, Any, Optional
from operations.base_service import BaseServiceOperations
from utils.colors import Colors, info, log, error, warn


class HardenOperations(BaseServiceOperations):
    """Handle harden-specific operations"""
    
    def __init__(self, config):
        super().__init__(config, "harden")
        self.name = "harden"
        self.description = "Atomic SSH hardening for fresh servers"
    
    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract service-specific arguments from command line"""
        harden_args = {}
        
        # Check for --status flag
        if '--status' in ansible_args:
            harden_args['operation'] = 'status'
        
        return harden_args
    
    def _handle_recipe_install(self, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle harden recipe installation - use base implementation with limit"""
        # Add --limit to ensure we only run on harden_targets
        if "--limit" not in ansible_args:
            ansible_args = ["--limit", "harden_targets"] + ansible_args
        
        # Use base implementation
        return super()._handle_recipe_install(args, ansible_args, service_args)
    
    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        return {}  # No parameter mapping needed for harden
    
    def _get_operation_flags(self) -> List[str]:
        """Get list of operation flags for harden"""
        return ['--status']
    
    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which operation is requested"""
        if '--status' in ansible_args:
            return 'status'
        return None
    
    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle granular harden operations"""
        if operation == 'status':
            # Run the status check playbook
            from operations.recipes import RecipeFinder
            
            # Use the harden-status playbook
            recipe_path = "core/harden-status.yml"
            inventory_path = self.inventory_manager.get_inventory_path(args.prod)
            
            # Filter out --status from ansible args
            filtered_args = [arg for arg in ansible_args if arg != '--status']
            
            return self.runner.run_recipe(
                recipe_path=recipe_path,
                inventory_path=inventory_path,
                extra_args=filtered_args,
                dry_run=False,  # Status check is always read-only
            )
        
        error(f"Unknown operation: {operation}")
        return 1
    
    def _show_connection_info(self, args):
        """Override to skip connection info for harden - it's misleading"""
        # Skip showing connection info for harden since it shows template variables
        pass
    
    def _show_granular_operations_help(self):
        """Show granular operations help"""
        print(f"{Colors.BLUE}Status Check:{Colors.NC}")
        print(f"  {Colors.GREEN}cli harden --status{Colors.NC}              Check SSH hardening status")
        print()
    
    def show_help(self) -> None:
        """Show harden-specific help"""
        print(f"""
{Colors.CYAN}cli harden{Colors.NC} - Atomic SSH Hardening

{Colors.YELLOW}DESCRIPTION:{Colors.NC}
    Performs atomic SSH hardening on fresh servers.
    Installs SSH keys, disables passwords, changes port.

{Colors.YELLOW}USAGE:{Colors.NC}
    cli harden --install          # Harden server SSH
    cli harden --install --check  # Dry run
    cli harden --status           # Check hardening status

{Colors.YELLOW}CONNECTION:{Colors.NC}
    • Initial: root@vault_ssh_port_initial (password)
    • Final: root@vault_ssh_port_final (SSH keys)

{Colors.YELLOW}NOTES:{Colors.NC}
    • Idempotent - safe to run multiple times
    • Gracefully handles already-hardened servers
    • Run this before 'cli security --install'
""")