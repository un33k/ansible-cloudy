"""
Development tools for Claudia CLI
Integrates with existing validation scripts and linting configurations
"""

import subprocess
import sys
from pathlib import Path
from .colors import Colors, error, info


class DevTools:
    """Development and validation tools for Claudia"""
    
    def __init__(self, config):
        self.config = config
        self.dev_dir = config.project_root / "dev"
        self.claudia_dir = self.dev_dir / "claudia"
    
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
