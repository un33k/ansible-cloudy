"""
Ansible Playbook Runner

Core functionality for executing ansible-playbook commands.
"""

import os
import subprocess
from typing import List, Optional
from pathlib import Path

from utils.config import ClaudiaConfig
from utils.colors import info, warn, error
from .vault_loader import VaultAutoLoader


class AnsibleRunner:
    """Execute ansible-playbook commands"""

    def __init__(self, config: ClaudiaConfig):
        self.config = config
        self.vault_loader = VaultAutoLoader(config.project_root)
    
    def run_recipe(
        self,
        recipe_path: str,
        inventory_path: str,
        extra_args: List[str],
        dry_run: bool = False,
        target_host: Optional[str] = None,
        extra_vars_file: Optional[str] = None,
    ) -> int:
        """Run ansible-playbook with the specified recipe"""

        # Auto-load vault file if available (skip for dev commands)
        extra_args = self.vault_loader.auto_load_vault_file(extra_args, recipe_path)

        # Build the command
        cmd = [
            "ansible-playbook",
            "-i",
            inventory_path,
            str(self.config.recipes_dir / recipe_path),
        ]

        # Add extra vars file if specified
        if extra_vars_file:
            extra_vars_path = Path(extra_vars_file)
            if not extra_vars_path.is_absolute():
                extra_vars_path = self.config.project_root / extra_vars_path
            if extra_vars_path.exists():
                cmd.extend(["-e", f"@{extra_vars_path}"])
                info(f"📋 Loading extra vars from: {extra_vars_file}")
            else:
                warn(f"Extra vars file not found: {extra_vars_file}")

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
            return 1

    def run_task(
        self,
        task_path: str,
        inventory_path: str,
        extra_args: List[str],
        dry_run: bool = False,
        target_host: Optional[str] = None,
        extra_vars_file: Optional[str] = None,
    ) -> int:
        """Run ansible-playbook with a single task file"""

        # Auto-load vault file if available (for granular operations, always load vault)
        extra_args = self.vault_loader.auto_load_vault_file(extra_args, "")

        # Build the command
        cmd = [
            "ansible-playbook",
            "-i",
            inventory_path,
            task_path,
        ]

        # Add extra vars file if specified
        if extra_vars_file:
            extra_vars_path = Path(extra_vars_file)
            if not extra_vars_path.is_absolute():
                extra_vars_path = self.config.project_root / extra_vars_path
            if extra_vars_path.exists():
                cmd.extend(["-e", f"@{extra_vars_path}"])
                info(f"📋 Loading extra vars from: {extra_vars_file}")
            else:
                warn(f"Extra vars file not found: {extra_vars_file}")

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
            return 1