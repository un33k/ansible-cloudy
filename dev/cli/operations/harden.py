"""
Harden Operation Handler
Manages atomic SSH hardening
"""

from typing import List, Dict, Any
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
        return {}  # No special args for harden
    
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
    
    def _show_connection_info(self, args):
        """Override to skip connection info for harden - it's misleading"""
        # Skip showing connection info for harden since it shows template variables
        pass
    
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

{Colors.YELLOW}CONNECTION:{Colors.NC}
    • Initial: root@vault_ssh_port_initial (password)
    • Final: root@vault_ssh_port_final (SSH keys)

{Colors.YELLOW}NOTES:{Colors.NC}
    • Idempotent - safe to run multiple times
    • Gracefully handles already-hardened servers
    • Run this before 'cli security --install'
""")