"""Finalize operation for completing server setup with upgrades and optional port change."""

from .base_service import BaseService


class FinalizeService(BaseService):
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
    
    def handle_install(self, args, extra_ansible_args):
        """Handle the finalize installation."""
        # Build extra vars
        extra_vars = []
        
        # Handle port change
        if args.change_port:
            extra_vars.append("change_ssh_port=true")
            if args.to_port:
                extra_vars.append(f"target_ssh_port={args.to_port}")
        
        # Handle upgrades
        if args.skip_upgrade:
            extra_vars.append("perform_system_upgrade=false")
        
        # Handle reboot
        if args.force_reboot:
            extra_vars.append("force_reboot=true")
        elif args.no_reboot:
            extra_vars.append("reboot_after_upgrade=false")
        
        # Add extra vars to ansible args
        if extra_vars:
            extra_ansible_args.extend(["-e", " ".join(extra_vars)])
        
        # Run the recipe
        self.run_recipe(extra_ansible_args)
    
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