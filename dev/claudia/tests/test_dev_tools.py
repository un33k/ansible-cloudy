"""
Tests for Development Tools

Tests for the DevTools functionality including validators and test runner.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import os

from utils.dev_tools import DevTools


class TestDevTools:
    """Test the DevTools class"""
    
    def test_dev_tools_initialization(self, mock_config):
        """Test DevTools initialization"""
        with patch('utils.dev_tools.vault_checker.VaultChecker.check_obsolete_vault_env'):
            dev_tools = DevTools(mock_config)
            
            assert dev_tools.config == mock_config
            assert dev_tools.validators is not None
            assert dev_tools.test_runner is not None
    
    def test_validate_precommit_all_pass(self, mock_config):
        """Test pre-commit validation when all checks pass"""
        with patch('utils.dev_tools.vault_checker.VaultChecker.check_obsolete_vault_env'):
            dev_tools = DevTools(mock_config)
            
            # Mock all validators to return success
            with patch.object(dev_tools.validators, 'syntax', return_value=0), \
                 patch.object(dev_tools.validators, 'lint', return_value=0), \
                 patch.object(dev_tools.validators, 'yamlint', return_value=0), \
                 patch.object(dev_tools.validators, 'flake8', return_value=0), \
                 patch.object(dev_tools.validators, 'spell', return_value=0):
                
                result = dev_tools.validate_precommit()
                assert result == 0
    
    def test_validate_precommit_some_fail(self, mock_config):
        """Test pre-commit validation when some checks fail"""
        with patch('utils.dev_tools.vault_checker.VaultChecker.check_obsolete_vault_env'):
            dev_tools = DevTools(mock_config)
            
            # Mock some validators to fail
            with patch.object(dev_tools.validators, 'syntax', return_value=0), \
                 patch.object(dev_tools.validators, 'lint', return_value=1), \
                 patch.object(dev_tools.validators, 'yamlint', return_value=0), \
                 patch.object(dev_tools.validators, 'flake8', return_value=1), \
                 patch.object(dev_tools.validators, 'spell', return_value=0):
                
                result = dev_tools.validate_precommit()
                assert result == 1
    
    def test_syntax_check(self, mock_config, temp_project_dir):
        """Test syntax check execution"""
        with patch('utils.dev_tools.vault_checker.VaultChecker.check_obsolete_vault_env'):
            dev_tools = DevTools(mock_config)
            
            # Create syntax check script
            syntax_script = temp_project_dir / "dev" / "syntax-check.sh"
            syntax_script.parent.mkdir(parents=True, exist_ok=True)
            syntax_script.write_text("#!/bin/bash\nexit 0")
            syntax_script.chmod(0o755)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                
                result = dev_tools.syntax()
                assert result == 0
                
                # Verify script was called
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert "bash" in call_args
                assert str(syntax_script) in call_args
    
    def test_lint_without_ansible_lint(self, mock_config):
        """Test lint when ansible-lint is not installed"""
        with patch('utils.dev_tools.vault_checker.VaultChecker.check_obsolete_vault_env'):
            dev_tools = DevTools(mock_config)
            
            with patch('subprocess.run') as mock_run:
                # Mock ansible-lint not found
                mock_run.return_value = Mock(returncode=1)
                
                result = dev_tools.lint()
                assert result == 1
    
    def test_test_runner(self, mock_config, temp_project_dir):
        """Test the test runner functionality"""
        with patch('utils.dev_tools.vault_checker.VaultChecker.check_obsolete_vault_env'):
            dev_tools = DevTools(mock_config)
            
            # Create test playbook
            test_playbook = temp_project_dir / "dev" / "test-auth.yml"
            test_playbook.parent.mkdir(parents=True, exist_ok=True)
            test_playbook.write_text("---\n- hosts: all\n  tasks: []")
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr="")
                
                result = dev_tools.test()
                assert result == 0
                
                # Verify ansible-playbook was called
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert "ansible-playbook" in call_args
                assert str(test_playbook) in call_args


class TestVaultChecker:
    """Test the VaultChecker functionality"""
    
    def test_check_obsolete_vault_env_found(self):
        """Test detection of obsolete vault environment variables"""
        # Set obsolete environment variables
        os.environ['ANSIBLE_VAULT_PASSWORD_FILE'] = '/path/to/vault'
        os.environ['ANSIBLE_VAULT_PASSWORD_FILE_DEV'] = '/path/to/dev/vault'
        
        from utils.dev_tools.vault_checker import VaultChecker
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            VaultChecker.check_obsolete_vault_env()
            
            # Verify warning was printed
            assert any('OBSOLETE VAULT ENVIRONMENT VARIABLES DETECTED' in str(call) 
                      for call in mock_print.call_args_list)
        
        # Verify environment variables were removed
        assert 'ANSIBLE_VAULT_PASSWORD_FILE' not in os.environ
        assert 'ANSIBLE_VAULT_PASSWORD_FILE_DEV' not in os.environ
    
    def test_check_obsolete_vault_env_none_found(self):
        """Test when no obsolete vault environment variables are found"""
        # Ensure no vault env vars are set
        for var in ['ANSIBLE_VAULT_PASSWORD_FILE', 'ANSIBLE_VAULT_PASSWORD_FILE_DEV']:
            if var in os.environ:
                del os.environ[var]
        
        from utils.dev_tools.vault_checker import VaultChecker
        
        # Should run without printing warnings
        with patch('builtins.print') as mock_print:
            VaultChecker.check_obsolete_vault_env()
            
            # Verify no warning was printed
            assert not any('OBSOLETE VAULT ENVIRONMENT VARIABLES DETECTED' in str(call) 
                          for call in mock_print.call_args_list)