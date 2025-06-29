"""
Development tools for Claudia CLI
Integrates with existing validation scripts and linting configurations
"""

import subprocess
import sys
import os
from pathlib import Path
from .colors import Colors, error, info


class DevTools:
    """Development and validation tools for Claudia"""
    
    def __init__(self, config):
        self.config = config
        self.dev_dir = config.project_root / "dev"
        self.claudia_dir = self.dev_dir / "claudia"
        self._check_obsolete_vault_env()
    
    def validate_precommit(self) -> int:
        """Run essential pre-commit validation suite"""
        print(f"\n{Colors.CYAN}🚀 Pre-Commit Validation Suite{Colors.NC}")
        print(f"{Colors.YELLOW}Running essential checks before commit...{Colors.NC}\n")
        
        checks = [
            ("Syntax Check", self.syntax),
            ("Ansible Linting", self.lint),
            ("YAML Formatting", self.yamlint),
            ("Python Code Quality", self.flake8),
            ("Spell Check", self.spell)
        ]
        
        failed_checks = []
        total_checks = len(checks)
        
        for i, (check_name, check_func) in enumerate(checks, 1):
            print(f"{Colors.BLUE}[{i}/{total_checks}] {check_name}...{Colors.NC}")
            
            try:
                result = check_func()
                if result == 0:
                    print(f"{Colors.GREEN}✅ {check_name} PASSED{Colors.NC}\n")
                else:
                    print(f"{Colors.RED}❌ {check_name} FAILED{Colors.NC}\n")
                    failed_checks.append(check_name)
            except Exception as e:
                print(f"{Colors.RED}❌ {check_name} ERROR: {e}{Colors.NC}\n")
                failed_checks.append(check_name)
        
        # Summary
        print("=" * 50)
        print(f"{Colors.CYAN}📊 Pre-Commit Check Summary:{Colors.NC}")
        
        if not failed_checks:
            print(f"   {Colors.GREEN}✅ All checks passed! Ready to commit.{Colors.NC}")
            print(f"   Total: {total_checks}/{total_checks} passed")
            return 0
        else:
            print(f"   {Colors.RED}❌ {len(failed_checks)} check(s) failed:{Colors.NC}")
            for check in failed_checks:
                print(f"     - {check}")
            print(f"   Total: {total_checks - len(failed_checks)}/{total_checks} passed")
            print(f"\n{Colors.YELLOW}💡 Fix the issues above before committing.{Colors.NC}")
            return 1
    
    def validate(self) -> int:
        """Run comprehensive validation using the existing validate.py script"""
        info("Running comprehensive validation...")
        
        validate_script = self.dev_dir / "validate.py"
        if not validate_script.exists():
            error(f"Validation script not found: {validate_script}")
            return 1
        
        try:
            result = subprocess.run(
                [sys.executable, str(validate_script)],
                cwd=self.config.project_root,
                capture_output=False
            )
            return result.returncode
        except Exception as e:
            error(f"Failed to run validation: {e}")
            return 1
    
    def syntax(self) -> int:
        """Run syntax checking using the existing syntax-check.sh script"""
        info("Running syntax check...")
        
        syntax_script = self.dev_dir / "syntax-check.sh"
        if not syntax_script.exists():
            error(f"Syntax check script not found: {syntax_script}")
            return 1
        
        try:
            result = subprocess.run(
                ["bash", str(syntax_script)],
                cwd=self.config.project_root,
                capture_output=False
            )
            return result.returncode
        except Exception as e:
            error(f"Failed to run syntax check: {e}")
            return 1
    
    def test(self, ansible_args=None) -> int:
        """Run authentication flow test"""
        info("Running authentication test...")
        
        if ansible_args is None:
            ansible_args = []
        
        test_playbook = self.dev_dir / "test-auth.yml"
        if not test_playbook.exists():
            error(f"Test playbook not found: {test_playbook}")
            return 1
        
        # Use ansible-playbook directly for the auth test
        inventory_path = self.config.inventory_dir / "dev.yml"
        
        cmd = [
            "ansible-playbook",
            "-i", str(inventory_path),
            str(test_playbook)
        ]
        cmd.extend(ansible_args)
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            return result.returncode
        except Exception as e:
            error(f"Failed to run authentication test: {e}")
            return 1
    
    def lint(self) -> int:
        """Run ansible linting with dev configuration"""
        info("Running Ansible linting...")
        
        try:
            # Check if ansible-lint is available
            result = subprocess.run(
                ["ansible-lint", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error("ansible-lint not available. Install with: pip install ansible-lint")
                return 1
            
            # Run ansible-lint on the cloudy directory with dev config
            config_file = self.dev_dir / ".ansible-lint.yml"
            if config_file.exists():
                result = subprocess.run(
                    ["ansible-lint", "-c", str(config_file), "cloudy/"],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    ["ansible-lint", "cloudy/"],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            return result.returncode
            
        except Exception as e:
            error(f"Failed to run ansible-lint: {e}")
            return 1
    
    def spell(self) -> int:
        """Run spell checking with dev configuration"""
        info("Running spell check...")
        
        try:
            # Check if cspell is available
            result = subprocess.run(
                ["cspell", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error("cspell not available. Install with: npm install -g cspell")
                return 1
            
            # Run cspell with dev configuration
            cspell_config = self.dev_dir / ".cspell.json"
            if cspell_config.exists():
                result = subprocess.run(
                    ["cspell", "--config", str(cspell_config), "**/*.{md,yml,yaml,py}"],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    ["cspell", "**/*.{md,yml,yaml,py}"],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            return result.returncode
            
        except Exception as e:
            error(f"Failed to run spell check: {e}")
            return 1
    
    def flake8(self) -> int:
        """Run Python code linting with flake8"""
        info("Running Python linting (flake8)...")
        
        try:
            # Check if flake8 is available
            result = subprocess.run(
                ["flake8", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error("flake8 not available. Install with: pip install flake8")
                return 1
            
            # Run flake8 on the claudia directory with dev config
            flake8_config = self.dev_dir / ".flake8"
            if flake8_config.exists():
                result = subprocess.run(
                    ["flake8", "--config", str(flake8_config), str(self.claudia_dir)],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    ["flake8", str(self.claudia_dir)],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            return result.returncode
            
        except Exception as e:
            error(f"Failed to run flake8: {e}")
            return 1
    
    def yamlint(self) -> int:
        """Run YAML linting with dev configuration"""
        info("Running YAML linting...")
        
        try:
            # Check if yamllint is available
            result = subprocess.run(
                ["yamllint", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error("yamllint not available. Install with: pip install yamllint")
                return 1
            
            # Run yamllint on the cloudy directory with dev config
            yamllint_config = self.dev_dir / ".yamlint.yml"
            if yamllint_config.exists():
                result = subprocess.run(
                    ["yamllint", "-c", str(yamllint_config), "cloudy/"],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    ["yamllint", "cloudy/"],
                    cwd=self.config.project_root,
                    capture_output=False
                )
            return result.returncode
            
        except Exception as e:
            error(f"Failed to run yamllint: {e}")
            return 1
    
    def _check_obsolete_vault_env(self):
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
            print(f"  3. Use simple vault files: {Colors.GREEN}./claudia psql --install -- -e @.vault/my-dev.yml{Colors.NC}\n")
            
            print(f"{Colors.YELLOW}For now, temporarily unsetting these variables...{Colors.NC}")
            for var in found_vars:
                os.environ.pop(var, None)
            print(f"{Colors.GREEN}✅ Variables unset for this session.{Colors.NC}\n")
