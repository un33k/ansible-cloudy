"""
Harden Operation Handler
Manages SSH port changes
"""

from typing import List, Dict, Any
from operations.base_service import BaseServiceOperations
from utils.colors import Colors, info, log, error, warn


class HardenOperations(BaseServiceOperations):
    """Handle SSH port change operations"""
    
    def __init__(self, config):
        super().__init__(config, "harden")
        self.name = "harden"
        self.description = "SSH port change utility"
    
    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract port change arguments from command line"""
        harden_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            if arg == "--from-port":
                if i + 1 < len(ansible_args):
                    harden_args['from-port'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--from-port requires a value")
            elif arg == "--to-port":
                if i + 1 < len(ansible_args):
                    harden_args['to-port'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--to-port requires a value")
            else:
                i += 1
        
        return harden_args
    
    def _handle_recipe_install(self, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle port change operation"""
        # Check if port parameters are provided
        if 'from-port' not in service_args or 'to-port' not in service_args:
            error("Port parameters required!")
            print(f"""
{Colors.YELLOW}Usage:{Colors.NC}
    cli harden --install --from-port [current] --to-port [new]

{Colors.YELLOW}Example:{Colors.NC}
    cli harden --install --from-port 22 --to-port 2222

{Colors.YELLOW}Note:{Colors.NC}
    SSH authentication hardening is now part of security setup.
    This command only changes the SSH port.
""")
            return 1
        
        # Use base implementation with port parameters
        return super()._handle_recipe_install(args, ansible_args, service_args)
    
    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        return {
            '--from-port': 'from_port',
            '--to-port': 'to_port'
        }
    
    def _show_connection_info(self, args):
        """Override to skip connection info for harden"""
        # Skip showing connection info
        pass
    
    def show_help(self) -> None:
        """Show harden-specific help"""
        print(f"""
{Colors.CYAN}cli harden{Colors.NC} - SSH Port Change Utility

{Colors.YELLOW}DESCRIPTION:{Colors.NC}
    Changes SSH port from one port to another.
    SSH authentication hardening is handled by 'cli security --install'.

{Colors.YELLOW}USAGE:{Colors.NC}
    cli harden --install --from-port [current] --to-port [new]

{Colors.YELLOW}EXAMPLES:{Colors.NC}
    cli harden --install --from-port 22 --to-port 2222
    cli harden --install --from-port 22 --to-port 2222 --check

{Colors.YELLOW}OPTIONS:{Colors.NC}
    --from-port    Current SSH port (required)
    --to-port      New SSH port (required)
    --check        Dry run (show what would change)

{Colors.YELLOW}WORKFLOW:{Colors.NC}
    1. Run 'cli security --install' first (handles SSH keys & auth)
    2. Run 'cli harden --install' to change port (optional)
    3. Update inventory with new port after change

{Colors.YELLOW}NOTES:{Colors.NC}
    • Connection will timeout after port change (expected)
    • Update your inventory file after successful change
    • Firewall rules may need adjustment
""")
