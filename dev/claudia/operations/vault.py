"""
Ansible Vault Operations for Claudia
Handles encrypted credential management and vault operations
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from utils.colors import Colors, error, info, log
from utils.config import ClaudiaConfig


class VaultOperations:
    """Handle Ansible Vault operations for secure credential management"""

    def __init__(self, config: ClaudiaConfig):
        self.config = config
        self.vault_file = config.base_dir / ".secrets" / "vault.yml"

    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route vault operation to appropriate handler"""
        
        # Extract vault-specific arguments
        vault_args = self._extract_vault_args(ansible_args)
        
        # Handle vault operations
        if vault_args.get('operation'):
            return self._handle_vault_operation(vault_args['operation'], args, vault_args)
        
        # Default: show help
        return self._show_vault_help()

    def _extract_vault_args(self, ansible_args: List[str]) -> dict:
        """Extract vault-specific arguments from command line"""
        vault_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            if arg == "--create":
                vault_args['operation'] = 'create'
                i += 1
            elif arg == "--edit":
                vault_args['operation'] = 'edit'
                i += 1
            elif arg == "--encrypt":
                vault_args['operation'] = 'encrypt'
                i += 1
            elif arg == "--decrypt":
                vault_args['operation'] = 'decrypt'
                i += 1
            elif arg == "--view":
                vault_args['operation'] = 'view'
                i += 1
            elif arg == "--rekey":
                vault_args['operation'] = 'rekey'
                i += 1
            elif arg == "--file":
                if i + 1 < len(ansible_args):
                    vault_args['file'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--file requires a file path")
            else:
                i += 1
        
        return vault_args

    def _handle_vault_operation(self, operation: str, args, vault_args: dict) -> int:
        """Handle specific vault operations"""
        
        # Determine vault file path
        vault_file = vault_args.get('file', str(self.vault_file))
        vault_path = Path(vault_file)
        
        # Ensure absolute path
        if not vault_path.is_absolute():
            vault_path = self.config.base_dir / vault_file
        
        if operation == 'create':
            return self._create_vault(vault_path)
        elif operation == 'edit':
            return self._edit_vault(vault_path)
        elif operation == 'encrypt':
            return self._encrypt_vault(vault_path)
        elif operation == 'decrypt':
            return self._decrypt_vault(vault_path)
        elif operation == 'view':
            return self._view_vault(vault_path)
        elif operation == 'rekey':
            return self._rekey_vault(vault_path)
        else:
            error(f"Unknown vault operation: {operation}")
            return 1

    def _create_vault(self, vault_path: Path) -> int:
        """Create a new encrypted vault file"""
        info(f"Creating new vault file: {vault_path}")
        
        if vault_path.exists():
            error(f"Vault file already exists: {vault_path}")
            return 1
        
        # Ensure parent directory exists
        vault_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ["ansible-vault", "create", str(vault_path)]
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            if result.returncode == 0:
                log(f"Created encrypted vault: {vault_path}")
            return result.returncode
        except Exception as e:
            error(f"Failed to create vault: {e}")
            return 1

    def _edit_vault(self, vault_path: Path) -> int:
        """Edit an encrypted vault file"""
        info(f"Editing vault file: {vault_path}")
        
        if not vault_path.exists():
            error(f"Vault file not found: {vault_path}")
            return 1
        
        cmd = ["ansible-vault", "edit", str(vault_path)]
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            if result.returncode == 0:
                log(f"Vault edited successfully: {vault_path}")
            return result.returncode
        except Exception as e:
            error(f"Failed to edit vault: {e}")
            return 1

    def _encrypt_vault(self, vault_path: Path) -> int:
        """Encrypt a plaintext vault file"""
        info(f"Encrypting vault file: {vault_path}")
        
        if not vault_path.exists():
            error(f"Vault file not found: {vault_path}")
            return 1
        
        cmd = ["ansible-vault", "encrypt", str(vault_path)]
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            if result.returncode == 0:
                log(f"Vault encrypted successfully: {vault_path}")
            return result.returncode
        except Exception as e:
            error(f"Failed to encrypt vault: {e}")
            return 1

    def _decrypt_vault(self, vault_path: Path) -> int:
        """Decrypt an encrypted vault file"""
        info(f"Decrypting vault file: {vault_path}")
        
        if not vault_path.exists():
            error(f"Vault file not found: {vault_path}")
            return 1
        
        cmd = ["ansible-vault", "decrypt", str(vault_path)]
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            if result.returncode == 0:
                log(f"Vault decrypted successfully: {vault_path}")
            return result.returncode
        except Exception as e:
            error(f"Failed to decrypt vault: {e}")
            return 1

    def _view_vault(self, vault_path: Path) -> int:
        """View contents of an encrypted vault file"""
        info(f"Viewing vault file: {vault_path}")
        
        if not vault_path.exists():
            error(f"Vault file not found: {vault_path}")
            return 1
        
        cmd = ["ansible-vault", "view", str(vault_path)]
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            return result.returncode
        except Exception as e:
            error(f"Failed to view vault: {e}")
            return 1

    def _rekey_vault(self, vault_path: Path) -> int:
        """Change the password of an encrypted vault file"""
        info(f"Changing vault password: {vault_path}")
        
        if not vault_path.exists():
            error(f"Vault file not found: {vault_path}")
            return 1
        
        cmd = ["ansible-vault", "rekey", str(vault_path)]
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            if result.returncode == 0:
                log(f"Vault password changed successfully: {vault_path}")
            return result.returncode
        except Exception as e:
            error(f"Failed to rekey vault: {e}")
            return 1

    def _show_vault_help(self) -> int:
        """Show vault operations help"""
        
        print(f"{Colors.CYAN}🔒 Help: Ansible Vault Operations{Colors.NC}")
        print("=" * 50)
        print()
        
        print(f"{Colors.BLUE}Description:{Colors.NC}")
        print("  Manage encrypted credential files with Ansible Vault")
        print("  Secure storage for passwords, API keys, and sensitive data")
        print()
        
        print(f"{Colors.BLUE}Vault Management:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia vault --create{Colors.NC}                     Create new encrypted vault")
        print(f"  {Colors.GREEN}claudia vault --edit{Colors.NC}                       Edit existing vault")
        print(f"  {Colors.GREEN}claudia vault --view{Colors.NC}                       View vault contents")
        print(f"  {Colors.GREEN}claudia vault --encrypt{Colors.NC}                    Encrypt plaintext file")
        print(f"  {Colors.GREEN}claudia vault --decrypt{Colors.NC}                    Decrypt vault file")
        print(f"  {Colors.GREEN}claudia vault --rekey{Colors.NC}                      Change vault password")
        print()
        
        print(f"{Colors.BLUE}Environment-Specific Vaults:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia vault --create --file .secrets/dev.yml{Colors.NC}     Create dev vault")
        print(f"  {Colors.GREEN}claudia vault --edit --file .secrets/prod.yml{Colors.NC}      Edit prod vault")
        print(f"  {Colors.GREEN}claudia vault --view --file .secrets/staging.yml{Colors.NC}   View staging vault")
        print()
        
        print(f"{Colors.BLUE}Default Vault Location:{Colors.NC}")
        print(f"  {Colors.YELLOW}{self.vault_file}{Colors.NC}")
        print()
        
        print(f"{Colors.BLUE}Vault Security Features:{Colors.NC}")
        print(f"  🔒 {Colors.GREEN}AES256 Encryption{Colors.NC}           - Military-grade encryption")
        print(f"  🛡️  {Colors.GREEN}Git-Safe Storage{Colors.NC}            - Encrypted files can be committed")
        print(f"  🔑 {Colors.GREEN}Password Protection{Colors.NC}         - Vault password required for access")
        print(f"  📋 {Colors.GREEN}Ansible Integration{Colors.NC}         - Native support in playbooks")
        print()
        
        print(f"{Colors.BLUE}Usage with Playbooks:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia psql --install --prod --ask-vault-pass{Colors.NC}")
        print(f"  {Colors.GREEN}export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass{Colors.NC}")
        print(f"  {Colors.GREEN}claudia redis --install --prod{Colors.NC}")
        print()
        
        # Show vault vs .env comparison
        self._show_vault_comparison()
        
        return 0

    def _show_vault_comparison(self):
        """Show vault vs .env.local comparison table"""
        print(f"{Colors.BLUE}🔧 Vault vs .env.local Comparison:{Colors.NC}")
        print()
        print("  | Feature             | Ansible Vault      | .env.local             |")
        print("  |---------------------|--------------------|------------------------|")
        print("  | Encryption          | ✅ AES256           | ❌ Plaintext            |")
        print("  | Git Safety          | ✅ Safe to commit   | ⚠️ Must be gitignored  |")
        print("  | Ansible Integration | ✅ Native           | ⚠️ Manual loading      |")
        print("  | Multi-environment   | ✅ Multiple vaults  | ⚠️ Multiple files      |")
        print("  | Security            | ✅ Enterprise-grade | ❌ Filesystem dependent |")
        print()
        print(f"  {Colors.GREEN}Recommendation:{Colors.NC} Use Ansible Vault for production deployments")
        print()
