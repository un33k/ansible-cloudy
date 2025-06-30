"""
Development Tools Main Class

Coordinates all development tool functionality.
"""

from .validators import ValidationTools
from .test_runner import TestRunner
from .vault_checker import VaultChecker


class DevTools:
    """Development and validation tools for Claudia"""
    
    def __init__(self, config):
        self.config = config
        self.validators = ValidationTools(config)
        self.test_runner = TestRunner(config)
        VaultChecker.check_obsolete_vault_env()
    
    # Delegate to validators
    def validate_precommit(self) -> int:
        """Run essential pre-commit validation suite"""
        return self.validators.validate_precommit()
    
    def validate(self) -> int:
        """Run comprehensive validation using the existing validate.py script"""
        return self.validators.validate()
    
    def syntax(self) -> int:
        """Run syntax checking using the existing syntax-check.sh script"""
        return self.validators.syntax()
    
    def lint(self) -> int:
        """Run ansible linting with dev configuration"""
        return self.validators.lint()
    
    def spell(self) -> int:
        """Run spell checking with dev configuration"""
        return self.validators.spell()
    
    def flake8(self) -> int:
        """Run Python code linting with flake8"""
        return self.validators.flake8()
    
    def yamlint(self) -> int:
        """Run YAML linting with dev configuration"""
        return self.validators.yamlint()
    
    # Delegate to test runner
    def test(self, ansible_args=None) -> int:
        """Run authentication flow test"""
        return self.test_runner.test(ansible_args)