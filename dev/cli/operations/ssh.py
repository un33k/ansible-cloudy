"""SSH port management operations."""

from typing import Dict, Any, List
from .base_service import BaseServiceOperations
from operations.recipes import RecipeFinder
from utils.colors import error, info


class SSHOperations(BaseServiceOperations):
    """Handle SSH port change operations."""
    
    def __init__(self, config):
        super().__init__(config, "ssh")
    
    def get_help_description(self) -> str:
        """Get service description for help display."""
        return "SSH port management - change SSH listening port"
    
    def get_recipe_description(self) -> str:
        """Get the recipe description."""
        return "Change SSH port with atomic UFW firewall update"
    
    def get_recipe_path(self) -> str:
        """Get the path to the SSH recipe."""
        return "playbooks/recipes/core/ssh-port.yml"
    
    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Handle SSH operations."""
        # Build extra vars
        extra_vars = []
        
        if hasattr(args, 'old_port') and args.old_port:
            extra_vars.append(f"old_port={args.old_port}")
        
        if hasattr(args, 'new_port') and args.new_port:
            extra_vars.append(f"new_port={args.new_port}")
        else:
            error("--new-port is required")
            return 1
        
        # Find recipe
        finder = RecipeFinder(self.config)
        recipe_path = finder.find_recipe("ssh-port")
        
        if not recipe_path:
            error("SSH port change recipe not found")
            return 1
        
        # Add extra vars to ansible args
        if extra_vars:
            ansible_args.extend(["-e", " ".join(extra_vars)])
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            ansible_args.insert(0, "-v")
        
        # Get environment
        environment = 'dev'
        if hasattr(args, 'prod') and args.prod:
            environment = 'prod'
        elif hasattr(args, 'ci') and args.ci:
            environment = 'ci'
        
        # Show warning
        info("⚠️  SSH port change will drop the connection - this is expected behavior")
        info("UFW will be automatically updated (old port removed, new port added)")
        info("Remember to update vault_ssh_port in your .vault/*.yml file after the change")
        
        # Execute recipe
        inventory_path = self.inventory_manager.get_inventory_path(environment == 'prod')
        return self.runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=ansible_args,
            dry_run=hasattr(args, 'check') and args.check,
        )
    
    def get_example_usage(self) -> list:
        """Get example usage commands."""
        return [
            "cli ssh --new-port 3333                    # Change to port 3333",
            "cli ssh --old-port 22 --new-port 3333     # Explicitly specify old port",
        ]
    
    def validate_operation(self, args) -> tuple[bool, str]:
        """Validate the operation arguments."""
        if not hasattr(args, 'new_port') or not args.new_port:
            return False, "--new-port is required"
        
        if args.new_port < 1 or args.new_port > 65535:
            return False, "Port must be between 1 and 65535"
        
        if hasattr(args, 'old_port') and args.old_port:
            if args.old_port == args.new_port:
                return False, "Old and new ports cannot be the same"
        
        return True, ""
    
    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract service-specific arguments from ansible args."""
        return {}
    
    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get parameter mapping for service."""
        return {}
