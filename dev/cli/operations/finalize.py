"""Finalize operation for completing server setup with upgrades and optional port change."""

from typing import Dict, Any, List
from .base_service import BaseServiceOperations
from operations.recipes import RecipeFinder
from utils.colors import error


class FinalizeService(BaseServiceOperations):
    """Handle server finalization - upgrades, port changes, and reboot."""
    
    def get_help_description(self) -> str:
        """Get service description for help display."""
        return "Finalize server with upgrades and optional reboot"
    
    def get_recipe_description(self) -> str:
        """Get the recipe description."""
        return "Complete server configuration with system updates and optional reboot"
    
    def get_recipe_path(self) -> str:
        """Get the path to the finalize recipe."""
        return "playbooks/recipes/core/finalize.yml"
    
    def _handle_recipe_install(self, args, ansible_args: List[str], service_args: Dict[str, Any]) -> int:
        """Handle the finalize installation."""
        # Build extra vars from properly parsed arguments
        extra_vars = []
        
        # Handle upgrades
        if hasattr(args, 'skip_upgrade') and args.skip_upgrade:
            extra_vars.append("perform_system_upgrade=false")
        
        # Handle reboot logic
        if hasattr(args, 'reboot') and args.reboot:
            extra_vars.append("reboot=true")
            if hasattr(args, 'force') and args.force:
                extra_vars.append("force=true")
        # Default: reboot=false (no reboot)
        
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
            "cli finalize --install                      # Run upgrades (no reboot)",
            "cli finalize --install --reboot             # Run upgrades and reboot if needed",
            "cli finalize --install --reboot --force     # Force reboot after upgrades",
            "cli finalize --install --skip-upgrade       # Skip system updates",
        ]
    
    def validate_operation(self, args) -> tuple[bool, str]:
        """Validate the operation arguments."""
        # Force requires reboot flag
        if hasattr(args, 'force') and args.force and (not hasattr(args, 'reboot') or not args.reboot):
            return False, "--force requires --reboot flag"
        
        return True, ""
    
    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract service-specific arguments from ansible args."""
        # Finalize doesn't have service-specific args in ansible_args
        return {}
    
    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get parameter mapping for service."""
        # Finalize parameters are handled in handle_install
        return {}
