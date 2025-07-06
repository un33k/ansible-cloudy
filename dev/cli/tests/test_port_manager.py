"""
Tests for SSH Port Manager

Tests for SSH port detection and management functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess

from execution.ansible.port_manager import SSHPortManager


class TestSSHPortManager:
    """Test the SSHPortManager class"""
    
    def test_test_port_connection_success(self, mock_config):
        """Test successful port connection test"""
        manager = SSHPortManager(mock_config)
        
        # Mock successful subprocess run
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = manager.test_port_connection("/path/to/inventory.yml", 22)
            
            assert result is True
            mock_run.assert_called_once()
            
            # Check the command structure
            call_args = mock_run.call_args[0][0]
            assert "ansible" in call_args
            assert "-m" in call_args
            assert "setup" in call_args
            assert "-e" in call_args
            assert "ansible_port=22" in call_args
    
    def test_test_port_connection_failure(self, mock_config):
        """Test failed port connection test"""
        manager = SSHPortManager(mock_config)
        
        # Mock failed subprocess run
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result
            
            result = manager.test_port_connection("/path/to/inventory.yml", 22)
            
            assert result is False
    
    def test_test_port_connection_timeout(self, mock_config):
        """Test port connection timeout"""
        manager = SSHPortManager(mock_config)
        
        # Mock timeout exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=15)
            
            result = manager.test_port_connection("/path/to/inventory.yml", 22)
            
            assert result is False
    
    def test_test_port_connection_with_target_host(self, mock_config):
        """Test port connection with target host override"""
        manager = SSHPortManager(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = manager.test_port_connection(
                "/path/to/inventory.yml", 
                22,
                target_host="192.168.1.100"
            )
            
            assert result is True
            
            # Check that target host was added to command
            call_args = mock_run.call_args[0][0]
            assert "-e" in call_args
            assert "ansible_host=192.168.1.100" in call_args
    
    def test_smart_port_detection_configured_port_first(self, mock_config):
        """Test that configured port is tried before default port 22"""
        manager = SSHPortManager(mock_config)
        
        # Mock vault loader that returns custom port
        mock_vault_loader = Mock()
        mock_vault_loader.auto_load_vault_file.return_value = []
        mock_vault_loader.extract_vault_ssh_port.return_value = 2222
        
        # Mock successful connection on configured port
        with patch.object(manager, 'test_port_connection') as mock_test:
            mock_test.return_value = True
            
            result = manager.smart_port_detection(
                production=False,
                target_host=None,
                inventory_path="/path/to/inventory.yml",
                vault_loader=mock_vault_loader
            )
            
            assert result['success'] is True
            assert result['port'] == 2222
            assert result['user'] == 'root'
            
            # Verify it was called with configured port first
            mock_test.assert_called_once_with(
                "/path/to/inventory.yml",
                2222,
                False,
                None,
                []
            )
    
    def test_smart_port_detection_fallback_to_22(self, mock_config):
        """Test fallback to port 22 when configured port fails"""
        manager = SSHPortManager(mock_config)
        
        # Mock vault loader that returns custom port
        mock_vault_loader = Mock()
        mock_vault_loader.auto_load_vault_file.return_value = []
        mock_vault_loader.extract_vault_ssh_port.return_value = 2222
        
        # Mock connection: fail on 2222, succeed on 22
        with patch.object(manager, 'test_port_connection') as mock_test:
            mock_test.side_effect = [False, True]  # Fail on 2222, succeed on 22
            
            result = manager.smart_port_detection(
                production=False,
                target_host=None,
                inventory_path="/path/to/inventory.yml",
                vault_loader=mock_vault_loader
            )
            
            assert result['success'] is True
            assert result['port'] == 22
            assert result['user'] == 'root'
            assert result['auth_method'] == 'password'
            
            # Verify both ports were tried
            assert mock_test.call_count == 2
    
    def test_smart_port_detection_all_fail(self, mock_config):
        """Test when all port connection attempts fail"""
        manager = SSHPortManager(mock_config)
        
        # Mock vault loader
        mock_vault_loader = Mock()
        mock_vault_loader.auto_load_vault_file.return_value = []
        mock_vault_loader.extract_vault_ssh_port.return_value = 2222
        
        # Mock all connections fail
        with patch.object(manager, 'test_port_connection') as mock_test:
            mock_test.return_value = False
            
            result = manager.smart_port_detection(
                production=False,
                target_host=None,
                inventory_path="/path/to/inventory.yml",
                vault_loader=mock_vault_loader
            )
            
            assert result['success'] is False
            assert result['port'] is None
            assert result['user'] is None
            assert result['auth_method'] is None
