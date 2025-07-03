"""
Tests for Configuration Module

Tests for ClaudiaConfig and InventoryManager classes.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from utils.config import CliConfig, InventoryManager


class TestCliConfig:
    """Test the CliConfig class"""
    
    def test_config_initialization(self, temp_project_dir):
        """Test that CliConfig initializes with correct paths"""
        with patch('utils.config.Path.cwd', return_value=temp_project_dir):
            config = CliConfig()
            
            assert config.project_root == temp_project_dir
            assert config.cloudy_dir == temp_project_dir / "cloudy"
            assert config.recipes_dir == temp_project_dir / "cloudy" / "playbooks" / "recipes"
            assert config.tasks_dir == temp_project_dir / "cloudy" / "tasks"
            assert config.inventory_dir == temp_project_dir / "cloudy" / "inventory"
    
    def test_config_find_project_root(self, temp_project_dir):
        """Test project root discovery logic"""
        # Create a subdirectory and test from there
        subdir = temp_project_dir / "cloudy" / "tasks" / "sys"
        subdir.mkdir(parents=True)
        
        with patch('utils.config.Path.cwd', return_value=subdir):
            config = CliConfig()
            assert config.project_root == temp_project_dir


class TestInventoryManager:
    """Test the InventoryManager class"""
    
    def test_get_inventory_path_default(self, mock_config):
        """Test default inventory path selection"""
        manager = InventoryManager(mock_config)
        
        # Create dev.yml file
        dev_file = mock_config.inventory_dir / "dev.yml"
        dev_file.parent.mkdir(parents=True, exist_ok=True)
        dev_file.touch()
        
        path = manager.get_inventory_path()
        assert str(path) == str(dev_file)
    
    def test_get_inventory_path_production(self, mock_config):
        """Test production inventory path selection"""
        manager = InventoryManager(mock_config)
        
        # Create prod.yml file
        prod_file = mock_config.inventory_dir / "prod.yml"
        prod_file.parent.mkdir(parents=True, exist_ok=True)
        prod_file.touch()
        
        path = manager.get_inventory_path(environment='prod')
        assert str(path) == str(prod_file)
    
    def test_get_inventory_path_ci(self, mock_config):
        """Test CI inventory path selection"""
        manager = InventoryManager(mock_config)
        
        # Create ci.yml file
        ci_file = mock_config.inventory_dir / "ci.yml"
        ci_file.parent.mkdir(parents=True, exist_ok=True)
        ci_file.touch()
        
        path = manager.get_inventory_path(environment='ci')
        assert str(path) == str(ci_file)
    
    def test_get_inventory_path_custom(self, mock_config, temp_project_dir):
        """Test custom inventory path"""
        manager = InventoryManager(mock_config)
        
        # Create custom inventory file
        custom_file = temp_project_dir / "custom-inventory.yml"
        custom_file.touch()
        
        path = manager.get_inventory_path(custom_path=str(custom_file))
        assert str(path) == str(custom_file)
    
    def test_get_inventory_path_custom_overrides_environment(self, mock_config, temp_project_dir):
        """Test that custom path overrides environment selection"""
        manager = InventoryManager(mock_config)
        
        # Create both files
        prod_file = mock_config.inventory_dir / "prod.yml"
        prod_file.parent.mkdir(parents=True, exist_ok=True)
        prod_file.touch()
        
        custom_file = temp_project_dir / "custom-inventory.yml"
        custom_file.touch()
        
        # Custom should override environment
        path = manager.get_inventory_path(environment='prod', custom_path=str(custom_file))
        assert str(path) == str(custom_file)
    
    def test_validate_inventory_exists(self, mock_config, sample_inventory_file):
        """Test inventory validation when file exists"""
        manager = InventoryManager(mock_config)
        
        # Should not raise exception
        manager.validate_inventory_exists(str(sample_inventory_file))
    
    def test_validate_inventory_missing(self, mock_config):
        """Test inventory validation when file is missing"""
        manager = InventoryManager(mock_config)
        
        with pytest.raises(SystemExit):
            manager.validate_inventory_exists("/nonexistent/inventory.yml")
