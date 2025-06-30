"""
Ansible execution and smart security runners for Ali CLI
"""

import os
import subprocess
from typing import List
from utils.config import AliConfig, InventoryManager
from utils.colors import info, warn, error


class AnsibleRunner:
    """Execute ansible-playbook commands"""

    def __init__(self, config: AliConfig):
        self.config = config
    
    def _auto_load_vault_file(self, extra_args: List[str], recipe_path: str = "") -> List[str]:
        """Automatically load vault file if it exists and not already specified"""
        # Skip vault loading for dev commands (except dev test which handles its own vault loading)
        if recipe_path and ("dev/" in recipe_path or recipe_path.startswith("dev")):
            return extra_args
        
        # Check if vault file is already being loaded via -e @path
        for i, arg in enumerate(extra_args):
            if arg == "-e" and i + 1 < len(extra_args):
                next_arg = extra_args[i + 1]
                if next_arg.startswith("@") and "vault" in next_arg.lower():
                    # Vault file already specified, don't add another
                    return extra_args
        
        # Look for vault files in .vault directory
        vault_dir = self.config.project_root / ".vault"
        if vault_dir.exists():
            # Try dev.yml first, then other files
            for vault_file in ["dev.yml", "prod.yml", "ci.yml"]:
                vault_path = vault_dir / vault_file
                if vault_path.exists():
                    # Show relative path instead of full path
                    relative_path = f".vault/{vault_file}"
                    info(f"🔐 Auto-loading vault credentials from: {relative_path}")
                    return extra_args + ["-e", f"@{vault_path}"]
        
        return extra_args

    def run_recipe(
        self,
        recipe_path: str,
        inventory_path: str,
        extra_args: List[str],
        dry_run: bool = False,
    ) -> int:
        """Run ansible-playbook with the specified recipe"""

        # Auto-load vault file if available (skip for dev commands)
        extra_args = self._auto_load_vault_file(extra_args, recipe_path)

        # Build the command
        cmd = [
            "ansible-playbook",
            "-i",
            inventory_path,
            str(self.config.recipes_dir / recipe_path),
        ]

        # Add dry run flag if requested
        if dry_run:
            cmd.append("--check")

        # Add any extra arguments
        cmd.extend(extra_args)

        # Show what we're running
        info(f"Running: {' '.join(cmd)}")

        # Change to cloudy directory for execution
        os.chdir(self.config.cloudy_dir)

        # Execute the command
        try:
            return subprocess.run(cmd).returncode
        except KeyboardInterrupt:
            warn("Operation cancelled by user")
            return 1
        except Exception as e:
            error(f"Failed to execute recipe: {e}")

    def run_task(
        self,
        task_path: str,
        inventory_path: str,
        extra_args: List[str],
        dry_run: bool = False,
    ) -> int:
        """Run ansible-playbook with a single task file"""

        # Auto-load vault file if available (for granular operations, always load vault)
        extra_args = self._auto_load_vault_file(extra_args, "")

        # Build the command
        cmd = [
            "ansible-playbook",
            "-i",
            inventory_path,
            task_path,
        ]

        # Add dry run flag if requested
        if dry_run:
            cmd.append("--check")

        # Add any extra arguments
        cmd.extend(extra_args)

        # Show what we're running
        info(f"Running: {' '.join(cmd)}")

        # Change to cloudy directory for execution
        os.chdir(self.config.cloudy_dir)

        # Execute the command
        try:
            return subprocess.run(cmd).returncode
        except KeyboardInterrupt:
            warn("Interrupted by user")
            return 130
        except FileNotFoundError:
            error(
                "ansible-playbook not found. Please install Ansible or activate your virtual environment."
            )


class SmartSecurityRunner:
    """Handle smart security detection and execution"""

    def __init__(
        self,
        config: AliConfig,
        inventory_manager: InventoryManager,
        ansible_runner: AnsibleRunner,
    ):
        self.config = config
        self.inventory_manager = inventory_manager
        self.ansible_runner = ansible_runner

    def run_smart_security(
        self,
        production: bool = False,
        extra_args: List[str] = None,
        dry_run: bool = False,
    ) -> int:
        """Run security with smart detection (try root first, fallback to admin verification)"""
        if extra_args is None:
            extra_args = []

        info("🔍 Detecting server security status...")

        # Try connecting as root first (fresh server scenario)
        if self._test_root_connection(production):
            info(
                "✅ Found unsecured server (root@22) - running initial hardening"
            )
            return self._run_initial_hardening(production, extra_args, dry_run)

        # Try connecting as admin user (already secured scenario)
        if self._test_admin_connection(production):
            info("✅ Found secured server - running security verification")
            return self._run_security_verification(
                production, extra_args, dry_run
            )

        # Both connections failed
        error(
            "❌ Cannot connect as root@22 or admin@ssh_port.\n"
            "Ensure server is accessible and check your SSH keys/credentials."
        )

    def _test_root_connection(self, production: bool) -> bool:
        """Test if we can connect as root on port 22"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Auto-load vault file for connection tests
        vault_args = self.ansible_runner._auto_load_vault_file([])

        # Use ansible ad-hoc command to test root connection on port 22
        cmd = [
            "ansible",
            "all",
            "-i",
            inventory_path,
            "-m",
            "setup",
            "-u",
            "root",
            "-e",
            "ansible_port=22",
            "--timeout=10",
            "-f",
            "1",
        ] + vault_args

        try:
            os.chdir(self.config.cloudy_dir)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _test_admin_connection(self, production: bool) -> bool:
        """Test if we can connect as admin user on the configured SSH port"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Auto-load vault file for connection tests
        vault_args = self.ansible_runner._auto_load_vault_file([])

        # Use ansible ad-hoc command to test admin connection
        cmd = [
            "ansible",
            "all",
            "-i",
            inventory_path,
            "-m",
            "setup",
            "--timeout=10",
            "-f",
            "1",
        ] + vault_args

        try:
            os.chdir(self.config.cloudy_dir)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _run_initial_hardening(
        self, production: bool, extra_args: List[str], dry_run: bool
    ) -> int:
        """Run the initial security hardening recipe"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Temporarily override connection settings for root access
        temp_args = [
            "-u",
            "root",
            "-e",
            "ansible_port=22",
            "-e",
            "ansible_user=root",
        ] + extra_args

        return self.ansible_runner.run_recipe(
            recipe_path="core/security.yml",
            inventory_path=inventory_path,
            extra_args=temp_args,
            dry_run=dry_run,
        )

    def _run_security_verification(
        self, production: bool, extra_args: List[str], dry_run: bool
    ) -> int:
        """Run the security verification recipe"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        return self.ansible_runner.run_recipe(
            recipe_path="core/security-verify.yml",
            inventory_path=inventory_path,
            extra_args=extra_args,
            dry_run=dry_run,
        )
