"""
Vault Environment Checker

Checks for obsolete vault environment variables and provides migration guidance.
"""

import os
from ..colors import Colors


class VaultChecker:
    """Checks for obsolete vault configuration"""
    
    @staticmethod
    def check_obsolete_vault_env():
        """Check for obsolete vault environment variables and warn user"""
        vault_env_vars = [
            'ANSIBLE_VAULT_PASSWORD_FILE',
            'ANSIBLE_VAULT_PASSWORD_FILE_DEV',
            'ANSIBLE_VAULT_PASSWORD_FILE_CI', 
            'ANSIBLE_VAULT_PASSWORD_FILE_PROD'
        ]
        
        found_vars = []
        for var in vault_env_vars:
            if var in os.environ:
                found_vars.append(var)
        
        if found_vars:
            print(f"\n{Colors.YELLOW}⚠️  OBSOLETE VAULT ENVIRONMENT VARIABLES DETECTED{Colors.NC}")
            print(f"{Colors.YELLOW}Ansible Cloudy now uses simple .vault/ files instead of encrypted vaults.{Colors.NC}")
            print(f"{Colors.YELLOW}The following environment variables are no longer needed:{Colors.NC}\n")
            
            for var in found_vars:
                value = os.environ[var]
                print(f"  {Colors.RED}${var}{Colors.NC} = {value}")
            
            print(f"\n{Colors.CYAN}To fix this:{Colors.NC}")
            print(f"  1. Remove these lines from your shell profile (~/.bashrc, ~/.zshrc):")
            for var in found_vars:
                print(f"     {Colors.RED}export {var}=...{Colors.NC}")
            print(f"  2. Restart your terminal or run: {Colors.GREEN}unset {' '.join(found_vars)}{Colors.NC}")
            print(f"  3. Use simple vault files: {Colors.GREEN}./cli psql --install -- -e @.vault/my-dev.yml{Colors.NC}\n")
            
            print(f"{Colors.YELLOW}For now, temporarily unsetting these variables...{Colors.NC}")
            for var in found_vars:
                os.environ.pop(var, None)
            print(f"{Colors.GREEN}✅ Variables unset for this session.{Colors.NC}\n")
