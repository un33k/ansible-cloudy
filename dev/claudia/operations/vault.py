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
            elif arg == "--all":
                vault_args['all'] = True
                i += 1
            else:
                i += 1
        
        return vault_args

    def _handle_vault_operation(self, operation: str, args, vault_args: dict) -> int:
        """Handle specific vault operations"""
        
        # Check if --all flag is used
        if vault_args.get('all', False):
            return self._handle_all_vaults(operation, vault_args)
        
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

    def _handle_all_vaults(self, operation: str, vault_args: dict) -> int:
        """Handle vault operations on all vault files in current directory and .secrets/"""
        
        # Find all .yml files in current directory and .secrets/ (excluding templates and examples)
        vault_files = []
        
        # Check current directory for vault files
        for file_path in self.config.base_dir.glob("*.vault.yml"):
            vault_files.append(file_path)
        for file_path in self.config.base_dir.glob("*-vault.yml"):
            vault_files.append(file_path)
        
        # Check .secrets directory (if it exists)
        secrets_dir = self.config.base_dir / ".secrets"
        if secrets_dir.exists():
            for file_path in secrets_dir.glob("*.yml"):
                # Skip templates and examples
                if not (file_path.name.endswith('.template') or file_path.name.endswith('.example')):
                    vault_files.append(file_path)
        
        if not vault_files:
            error("No vault files found. Looking for *.vault.yml, *-vault.yml, and .secrets/*.yml files")
            return 1
        
        print(f"{Colors.BLUE}🔒 {operation.title()}ing all vault files:{Colors.NC}")
        for vault_file in vault_files:
            print(f"  • {vault_file.name}")
        print()
        
        # Perform operation on each vault file
        all_success = True
        for vault_file in vault_files:
            print(f"{Colors.YELLOW}Processing {vault_file.name}...{Colors.NC}")
            
            if operation == 'encrypt':
                result = self._encrypt_vault(vault_file)
            elif operation == 'decrypt':
                result = self._decrypt_vault(vault_file)
            elif operation == 'view':
                result = self._view_vault(vault_file)
            elif operation == 'rekey':
                result = self._rekey_vault(vault_file)
            else:
                error(f"Operation '{operation}' not supported with --all flag")
                return 1
            
            if result != 0:
                all_success = False
        
        if all_success:
            print(f"{Colors.GREEN}✅ All vault files processed successfully{Colors.NC}")
            return 0
        else:
            error("Some vault operations failed")
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
        
        print(f"{Colors.BLUE}Working with User Vault Files:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia vault --create --file my-dev.vault.yml{Colors.NC}     Create user vault")
        print(f"  {Colors.GREEN}claudia vault --edit --file my-prod.vault.yml{Colors.NC}      Edit user vault")
        print(f"  {Colors.GREEN}claudia vault --view --file staging-vault.yml{Colors.NC}      View user vault")
        print()
        
        print(f"{Colors.BLUE}Batch Operations:{Colors.NC}")
        print(f"  {Colors.GREEN}claudia vault --encrypt --all{Colors.NC}                      Encrypt all vault files (*.vault.yml, *-vault.yml, .secrets/*.yml)")
        print(f"  {Colors.GREEN}claudia vault --decrypt --all{Colors.NC}                      Decrypt all vault files")
        print(f"  {Colors.GREEN}claudia vault --view --all{Colors.NC}                         View all vault files")
        print(f"  {Colors.GREEN}claudia vault --rekey --all{Colors.NC}                        Change password for all vaults")
        print()
        
        print(f"{Colors.BLUE}Open Source Vault Structure:{Colors.NC}")
        print(f"  {Colors.YELLOW}Example files:{Colors.NC} .secrets/dev.yml.example, .secrets/ci.yml.example, .secrets/prod.yml.example")
        print(f"  {Colors.YELLOW}Template file:{Colors.NC} .secrets/vault.yml.template")
        print(f"  {Colors.YELLOW}User vault files:{Colors.NC} *.vault.yml, *-vault.yml (gitignored)")
        print(f"  {Colors.YELLOW}Workflow:{Colors.NC} Copy example → Edit → Encrypt → Use")
        print()
        
        print(f"{Colors.BLUE}Vault Security Features:{Colors.NC}")
        print(f"  🔒 {Colors.GREEN}AES256 Encryption{Colors.NC}           - Military-grade encryption")
        print(f"  🛡️  {Colors.GREEN}Git-Safe Storage{Colors.NC}            - Encrypted files can be committed")
        print(f"  🔑 {Colors.GREEN}Password Protection{Colors.NC}         - Vault password required for access")
        print(f"  📋 {Colors.GREEN}Ansible Integration{Colors.NC}         - Native support in playbooks")
        print()
        
        print(f"{Colors.BLUE}Open Source Usage Workflow:{Colors.NC}")
        print(f"  {Colors.GREEN}# 1. Copy example to your vault file{Colors.NC}")
        print(f"  {Colors.GREEN}cp .secrets/dev.yml.example my-dev.vault.yml{Colors.NC}")
        print(f"  {Colors.GREEN}# 2. Edit with your real credentials{Colors.NC}")
        print(f"  {Colors.GREEN}vim my-dev.vault.yml{Colors.NC}")
        print(f"  {Colors.GREEN}# 3. Encrypt it{Colors.NC}")
        print(f"  {Colors.GREEN}claudia vault --encrypt --file my-dev.vault.yml{Colors.NC}")
        print(f"  {Colors.GREEN}# 4. Use with playbooks{Colors.NC}")
        print(f"  {Colors.GREEN}ansible-playbook -i inventory/dev.yml --ask-vault-pass playbook.yml{Colors.NC}")
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
