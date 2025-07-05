"""
Vault Auto-Loading Management

Handles automatic loading of vault files for Ansible operations.
"""

from typing import List
from pathlib import Path
from utils.colors import info


class VaultAutoLoader:
    """Manage automatic vault file loading"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def auto_load_vault_file(self, extra_args: List[str], recipe_path: str = "") -> List[str]:
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
        vault_dir = self.project_root / ".vault"
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
    
    def extract_vault_ssh_port(self, vault_args: List[str]) -> int:
        """Extract SSH port from vault args"""
        # Look for vault file and extract SSH port
        try:
            for i, arg in enumerate(vault_args):
                if arg == "-e" and i + 1 < len(vault_args) and vault_args[i + 1].startswith("@"):
                    vault_file = vault_args[i + 1][1:]  # Remove @ prefix
                    if Path(vault_file).exists():
                        import yaml
                        with open(vault_file, 'r') as f:
                            vault_data = yaml.safe_load(f)
                            # Get SSH port from vault
                            return vault_data.get('vault_ssh_port', 22)
        except Exception:
            pass
        return 22
