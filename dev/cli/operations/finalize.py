"""Finalize operation for completing server setup with upgrades and optional port change."""

from typing import Dict, Any, List
from .base_service import BaseServiceOperations
from operations.recipes import RecipeFinder
from utils.colors import error


class FinalizeService(BaseServiceOperations):
    """Handle server finalization - upgrades, port changes, and reboot."""
    
    def get_help_description(self) -> str:
        """Get service description for help display."""
        return "Finalize server setup with upgrades and optional SSH port change"
    
    def get_recipe_description(self) -> str:
        """Get the recipe description."""
        return "Complete server configuration with system updates, optional port change, and reboot if needed"
    
    def define_arguments(self, subparser):
        """Define finalize-specific arguments."""
        # SSH port change
        subparser.add_argument(
            '--change-port',
            action='store_true',
            help='Change SSH port to hardened port (2222)'
        )
        
        subparser.add_argument(
            '--to-port',
            type=int,
            help='Target SSH port (default: 2222)'
        )
        
        # Upgrade control
        subparser.add_argument(
            '--skip-upgrade',
            action='store_true',
            help='Skip system upgrades'
        )
        
        # Reboot control
        subparser.add_argument(
            '--force-reboot',
            action='store_true',
            help='Force reboot even if not required'
        )
        
        subparser.add_argument(
            '--no-reboot',
            action='store_true',
            help='Skip reboot even if required'
        )
    
    def get_recipe_path(self) -> str:
        """Get the path to the finalize recipe."""
        return "playbooks/recipes/core/finalize.yml"
    
    def _handle_recipe_install(self, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle the finalize installation."""
        # Parse finalize-specific arguments from remaining args
        extra_vars = []
        
        # Check for arguments in ansible_args
        i = 0
        while i < len(ansible_args):
            arg = ansible_args[i]
            if arg == '--change-port':
                extra_vars.append("change_ssh_port=true")
                ansible_args.pop(i)
            elif arg == '--to-port' and i + 1 < len(ansible_args):
                extra_vars.append("change_ssh_port=true")  # Automatically enable port change
                extra_vars.append(f"target_ssh_port={ansible_args[i+1]}")
                ansible_args.pop(i)  # Remove --to-port
                ansible_args.pop(i)  # Remove the port number
            elif arg == '--skip-upgrade':
                extra_vars.append("perform_system_upgrade=false")
                ansible_args.pop(i)
            elif arg == '--force-reboot':
                extra_vars.append("force_reboot=true")
                ansible_args.pop(i)
            elif arg == '--no-reboot':
                extra_vars.append("reboot_after_upgrade=false")
                ansible_args.pop(i)
            else:
                i += 1
        
        # Find recipe
        finder = RecipeFinder(self.config)
        recipe_path = finder.find_recipe(self.service_name)
        
        if not recipe_path:
            error(f"{self.service_name.title()} recipe not found")
            return 1
        
        # Add extra vars to ansible args
        if extra_vars:
            ansible_args.extend(["-e", " ".join(extra_vars)])
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            ansible_args.insert(0, "-v")
        
        # Execute recipe
        inventory_path = self.inventory_manager.get_inventory_path(args.prod)
        return self.runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=ansible_args,
            dry_run=args.check,
        )
    
    def get_example_usage(self) -> list:
        """Get example usage commands."""
        return [
            "cli finalize --install                    # Run upgrades and reboot if needed",
            "cli finalize --install --change-port      # Also change SSH port to 2222",
            "cli finalize --install --to-port 2222     # Change to custom port",
            "cli finalize --install --skip-upgrade     # Skip system updates",
            "cli finalize --install --force-reboot     # Force reboot",
            "cli finalize --install --no-reboot        # Never reboot",
        ]
    
    def validate_operation(self, args) -> tuple[bool, str]:
        """Validate the operation arguments."""
        # Validate port number if provided
        if args.to_port:
            if args.to_port < 1 or args.to_port > 65535:
                return False, "Port must be between 1 and 65535"
            if args.to_port == 22:
                return False, "Cannot change to port 22 (use default SSH setup instead)"
        
        # Can't force and skip reboot
        if args.force_reboot and args.no_reboot:
            return False, "Cannot use --force-reboot and --no-reboot together"
        
        return True, ""
    
    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract service-specific arguments from ansible args."""
        # Finalize doesn't have service-specific args in ansible_args
        return {}
    
    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get parameter mapping for service."""
        # Finalize parameters are handled in handle_install
        return {}