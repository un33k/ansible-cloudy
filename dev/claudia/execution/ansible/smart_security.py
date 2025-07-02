"""
Smart Security Runner

Handles intelligent security detection and multi-phase security setup.
"""

from typing import List, Optional
from utils.config import ClaudiaConfig, InventoryManager
from utils.colors import info, warn, error
from .runner import AnsibleRunner
from .vault_loader import VaultAutoLoader
from .port_manager import SSHPortManager


class SmartSecurityRunner:
    """Handle smart security detection and execution"""

    def __init__(
        self,
        config: ClaudiaConfig,
        inventory_manager: InventoryManager,
        ansible_runner: AnsibleRunner,
    ):
        self.config = config
        self.inventory_manager = inventory_manager
        self.ansible_runner = ansible_runner
        self.vault_loader = VaultAutoLoader(config.project_root)
        self.port_manager = SSHPortManager(config)

    def run_smart_security(
        self,
        production: bool = False,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        target_host: Optional[str] = None,
    ) -> int:
        """Run security with smart detection and port fallback logic"""
        if extra_args is None:
            extra_args = []

        info("🔍 Detecting server security status...")

        # Get inventory path
        inventory_path = self.inventory_manager.get_inventory_path(
            environment='prod' if production else 'dev'
        )

        # Try smart port detection first
        connection_info = self.port_manager.smart_port_detection(
            production, target_host, inventory_path, self.vault_loader
        )
        
        if connection_info['success']:
            if connection_info['port'] == 22 and connection_info['user'] == 'root':
                info("✅ Found fresh server (root@22) - running initial hardening")
                return self._run_initial_hardening(production, extra_args, dry_run, target_host)
            else:
                info(f"✅ Found secured server (root@{connection_info['port']}) - running verification")
                return self._run_security_verification(production, extra_args, dry_run, target_host)

        # All connection attempts failed
        error(
            "❌ Cannot connect to server on any port.\n"
            "Check server accessibility, credentials, and network connectivity."
        )
        return 1

    def _run_initial_hardening(
        self, production: bool, extra_args: List[str], dry_run: bool, target_host: Optional[str] = None
    ) -> int:
        """Run the initial security hardening recipe with SSH port management"""
        inventory_path = self.inventory_manager.get_inventory_path(
            environment='prod' if production else 'dev'
        )

        # Get configured SSH port from vault
        vault_args = self.vault_loader.auto_load_vault_file([])
        configured_port = self.vault_loader.extract_vault_ssh_port(vault_args)

        # If configured port is different from 22, we need special handling
        if configured_port != 22:
            info(f"🔄 Detected custom SSH port configuration: {configured_port}")
            return self._run_security_with_port_change(
                inventory_path, extra_args, dry_run, target_host, configured_port
            )
        else:
            # Standard security setup on port 22
            temp_args = [
                "-u",
                "root",
                "-e",
                "ansible_port=22",
                "-e",
                "ansible_user=root",
            ] + extra_args

            # Check if production hardening is requested
            recipe_path = "core/security.yml"
            for i, arg in enumerate(extra_args):
                if arg == '-e' and i + 1 < len(extra_args):
                    if 'use_production_hardening=true' in extra_args[i + 1]:
                        recipe_path = "core/security-production.yml"
                        info("🔒 Using production security hardening")
                        break
            
            return self.ansible_runner.run_recipe(
                recipe_path=recipe_path,
                inventory_path=inventory_path,
                extra_args=temp_args,
                dry_run=dry_run,
                target_host=target_host,
            )

    def _run_security_with_port_change(
        self, inventory_path: str, extra_args: List[str], dry_run: bool, 
        target_host: Optional[str], new_port: int
    ) -> int:
        """Run security setup with SSH port change and reconnection logic"""
        
        if dry_run:
            info("🔍 Dry run: Would perform SSH port change security setup")
            return 0

        info(f"🔐 Running security setup with SSH port change to {new_port}")
        
        # Phase 1: Install SSH keys and create grunt user (on port 22)
        info("📋 Phase 1: Installing SSH keys and creating users...")
        temp_args = [
            "-u", "root",
            "-e", "ansible_port=22",
            "-e", "ansible_user=root",
            "-e", "skip_ssh_port_change=true",  # Skip port change in first phase
        ] + extra_args

        # Check if production hardening is requested
        recipe_path = "core/security.yml"
        for i, arg in enumerate(extra_args):
            if arg == '-e' and i + 1 < len(extra_args):
                if 'use_production_hardening=true' in extra_args[i + 1]:
                    recipe_path = "core/security-production.yml"
                    break

        result = self.ansible_runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=temp_args,
            dry_run=False,
            target_host=target_host,
        )
        
        if result != 0:
            error("❌ Phase 1 security setup failed")
            return result

        # Phase 2: Change SSH port and disable root password
        info(f"📋 Phase 2: Changing SSH port to {new_port} and securing server...")
        temp_args = [
            "-u", "root",
            "-e", "ansible_port=22",  # Still connect on 22 for port change
            "-e", "ansible_user=root",
            "-e", f"new_ssh_port={new_port}",
            "-e", "ssh_port_change_only=true",  # Only do port change tasks
        ] + extra_args

        # Check if production hardening is requested (for phase 2 as well)
        recipe_path = "core/security.yml"
        for i, arg in enumerate(extra_args):
            if arg == '-e' and i + 1 < len(extra_args):
                if 'use_production_hardening=true' in extra_args[i + 1]:
                    recipe_path = "core/security-production.yml"
                    break

        result = self.ansible_runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=temp_args,
            dry_run=False,
            target_host=target_host,
        )
        
        if result != 0:
            error("❌ Phase 2 SSH port change failed")
            return result

        # Phase 3: Verify connection on new port
        info(f"📋 Phase 3: Verifying connection on port {new_port}...")
        if self.port_manager.test_port_connection(inventory_path, new_port, False, target_host):
            info(f"✅ Successfully connected on new port {new_port}")
            info("🎉 Security setup with port change completed successfully!")
            return 0
        else:
            error(f"❌ Cannot connect on new port {new_port} - security setup may have failed")
            return 1

    def _run_security_verification(
        self, production: bool, extra_args: List[str], dry_run: bool, target_host: Optional[str] = None
    ) -> int:
        """Run the security verification recipe"""
        inventory_path = self.inventory_manager.get_inventory_path(
            environment='prod' if production else 'dev'
        )

        return self.ansible_runner.run_recipe(
            recipe_path="core/security-verify.yml",
            inventory_path=inventory_path,
            extra_args=extra_args,
            dry_run=dry_run,
            target_host=target_host,
        )
