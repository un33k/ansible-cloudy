"""
Tests for Vault Auto-Loading

Tests for the VaultAutoLoader class functionality.
"""

import pytest
from pathlib import Path

from execution.ansible.vault_loader import VaultAutoLoader


class TestVaultAutoLoader:
    """Test the VaultAutoLoader class"""
    
    def test_auto_load_vault_dev_file(self, temp_project_dir, sample_vault_file):
        """Test automatic loading of dev vault file"""
        loader = VaultAutoLoader(temp_project_dir)
        
        extra_args = []
        result = loader.auto_load_vault_file(extra_args)
        
        assert len(result) == 2
        assert result[0] == "-e"
        assert result[1].startswith("@")
        assert "dev.yml" in result[1]
    
    def test_auto_load_vault_skip_if_already_loaded(self, temp_project_dir, sample_vault_file):
        """Test that vault loading is skipped if already in args"""
        loader = VaultAutoLoader(temp_project_dir)
        
        # Already has vault file
        extra_args = ["-e", "@.vault/custom.yml"]
        result = loader.auto_load_vault_file(extra_args)
        
        # Should return unchanged
        assert result == extra_args
    
    def test_auto_load_vault_skip_for_dev_commands(self, temp_project_dir, sample_vault_file):
        """Test that vault loading is skipped for dev commands"""
        loader = VaultAutoLoader(temp_project_dir)
        
        extra_args = []
        result = loader.auto_load_vault_file(extra_args, recipe_path="dev/test.yml")
        
        # Should return unchanged
        assert result == extra_args
    
    def test_extract_vault_ssh_port(self, temp_project_dir, sample_vault_file):
        """Test extraction of SSH port from vault file"""
        loader = VaultAutoLoader(temp_project_dir)
        
        vault_args = ["-e", f"@{sample_vault_file}"]
        port = loader.extract_vault_ssh_port(vault_args)
        
        assert port == 22022
    
    def test_extract_vault_ssh_port_default(self, temp_project_dir):
        """Test default SSH port when not in vault"""
        loader = VaultAutoLoader(temp_project_dir)
        
        vault_args = []
        port = loader.extract_vault_ssh_port(vault_args)
        
        assert port == 22
    
    def test_no_vault_directory(self, temp_project_dir):
        """Test behavior when no vault directory exists"""
        # Remove the .vault directory
        vault_dir = temp_project_dir / ".vault"
        if vault_dir.exists():
            import shutil
            shutil.rmtree(vault_dir)
        
        loader = VaultAutoLoader(temp_project_dir)
        
        extra_args = []
        result = loader.auto_load_vault_file(extra_args)
        
        # Should return unchanged
        assert result == extra_args
