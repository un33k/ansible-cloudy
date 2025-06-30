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
        target_host: str = None,
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

        # Add target host override if specified
        if target_host:
            cmd.extend(["-e", f"ansible_host={target_host}"])
            info(f"🎯 Target host override: {target_host}")

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
        target_host: str = None,
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

        # Add target host override if specified
        if target_host:
            cmd.extend(["-e", f"ansible_host={target_host}"])
            info(f"🎯 Target host override: {target_host}")

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
        target_host: str = None,
    ) -> int:
        """Run security with smart detection and port fallback logic"""
        if extra_args is None:
            extra_args = []

        info("🔍 Detecting server security status...")

        # Try smart port detection first
        connection_info = self._smart_port_detection(production, target_host)
        
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

    def _smart_port_detection(self, production: bool, target_host: str = None) -> dict:
        """Smart SSH port detection with fallback logic"""
        info("🔍 Testing SSH connectivity with smart port detection...")
        
        # Get configured SSH port from vault (if any)
        vault_args = self.ansible_runner._auto_load_vault_file([])
        configured_port = self._extract_vault_ssh_port(vault_args)
        
        # Define port test order: configured port first, then 22
        ports_to_try = []
        if configured_port and configured_port != 22:
            ports_to_try.append(configured_port)
        ports_to_try.append(22)
        
        # Test each port
        for port in ports_to_try:
            info(f"🔌 Testing root connection on port {port}...")
            
            if self._test_port_connection(production, port, target_host):
                info(f"✅ Successfully connected on port {port}")
                return {
                    'success': True,
                    'port': port,
                    'user': 'root',
                    'auth_method': 'password' if port == 22 else 'ssh_key'
                }
            else:
                info(f"❌ Connection failed on port {port}")
        
        return {'success': False, 'port': None, 'user': None, 'auth_method': None}

    def _extract_vault_ssh_port(self, vault_args: List[str]) -> int:
        """Extract SSH port from vault args"""
        # Look for vault file and extract SSH port
        try:
            from pathlib import Path
            for i, arg in enumerate(vault_args):
                if arg == "-e" and i + 1 < len(vault_args) and vault_args[i + 1].startswith("@"):
                    vault_file = vault_args[i + 1][1:]  # Remove @ prefix
                    if Path(vault_file).exists():
                        import yaml
                        with open(vault_file, 'r') as f:
                            vault_data = yaml.safe_load(f)
                            return vault_data.get('vault_ssh_port', 22)
        except Exception:
            pass
        return 22

    def _test_port_connection(self, production: bool, port: int, target_host: str = None) -> bool:
        """Test connection on specific port"""
        inventory_path = self.inventory_manager.get_inventory_path(production)
        vault_args = self.ansible_runner._auto_load_vault_file([])

        cmd = [
            "ansible",
            "security_targets" if port == 22 else "service_targets",
            "-i",
            inventory_path,
            "-m",
            "setup",
            "-u",
            "root",
            "-e",
            f"ansible_port={port}",
            "--timeout=10",
            "-f",
            "1",
        ] + vault_args

        # Add target host override if specified
        if target_host:
            cmd.extend(["-e", f"ansible_host={target_host}"])

        try:
            os.chdir(self.config.cloudy_dir)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

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
        self, production: bool, extra_args: List[str], dry_run: bool, target_host: str = None
    ) -> int:
        """Run the initial security hardening recipe with SSH port management"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Get configured SSH port from vault
        vault_args = self.ansible_runner._auto_load_vault_file([])
        configured_port = self._extract_vault_ssh_port(vault_args)

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

            return self.ansible_runner.run_recipe(
                recipe_path="core/security.yml",
                inventory_path=inventory_path,
                extra_args=temp_args,
                dry_run=dry_run,
                target_host=target_host,
            )

    def _run_security_with_port_change(
        self, inventory_path: str, extra_args: List[str], dry_run: bool, 
        target_host: str, new_port: int
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

        result = self.ansible_runner.run_recipe(
            recipe_path="core/security.yml",
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

        result = self.ansible_runner.run_recipe(
            recipe_path="core/security.yml",
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
        if self._test_port_connection(False, new_port, target_host):
            info(f"✅ Successfully connected on new port {new_port}")
            info("🎉 Security setup with port change completed successfully!")
            return 0
        else:
            error(f"❌ Cannot connect on new port {new_port} - security setup may have failed")
            return 1

    def _run_security_verification(
        self, production: bool, extra_args: List[str], dry_run: bool, target_host: str = None
    ) -> int:
        """Run the security verification recipe"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        return self.ansible_runner.run_recipe(
            recipe_path="core/security-verify.yml",
            inventory_path=inventory_path,
            extra_args=extra_args,
            dry_run=dry_run,
            target_host=target_host,
        )
