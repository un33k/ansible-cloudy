"""
Tests for Argument Parser

Tests for the CliArgumentParser class.
"""

import pytest
from unittest.mock import patch

from cmd.argument_parser import CliArgumentParser


class TestCliArgumentParser:
    """Test the CliArgumentParser class"""
    
    def test_parse_help_flag(self):
        """Test that help flag is parsed correctly"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                parser.parse_args()
            assert exc_info.value.code == 0
    
    def test_parse_service_name(self):
        """Test parsing service name"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql']):
            args = parser.parse_args()
            assert args.service == 'psql'
            assert args.install is False
    
    def test_parse_install_flag(self):
        """Test parsing install flag"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install']):
            args = parser.parse_args()
            assert args.service == 'psql'
            assert args.install is True
    
    def test_parse_environment_flags(self):
        """Test parsing environment selection flags"""
        parser = CliArgumentParser()
        
        # Test --dev flag
        with patch('sys.argv', ['cli', 'psql', '--install', '--dev']):
            args = parser.parse_args()
            assert args.dev is True
            assert args.prod is False
            assert args.ci is False
        
        # Test --prod flag
        with patch('sys.argv', ['cli', 'psql', '--install', '--prod']):
            args = parser.parse_args()
            assert args.prod is True
            assert args.dev is False
            assert args.ci is False
        
        # Test --ci flag
        with patch('sys.argv', ['cli', 'psql', '--install', '--ci']):
            args = parser.parse_args()
            assert args.ci is True
            assert args.dev is False
            assert args.prod is False
    
    def test_parse_custom_inventory(self):
        """Test parsing custom inventory path"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install', '-i', '/path/to/inventory.yml']):
            args = parser.parse_args()
            assert args.inventory_path == '/path/to/inventory.yml'
    
    def test_parse_extra_vars_file(self):
        """Test parsing extra vars file path"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install', '-e', '/path/to/vars.yml']):
            args = parser.parse_args()
            assert args.extra_vars_file == '/path/to/vars.yml'
    
    def test_parse_check_flag(self):
        """Test parsing check (dry run) flag"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install', '--check']):
            args = parser.parse_args()
            assert args.check is True
    
    def test_parse_host_flag(self):
        """Test parsing host override flag"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install', '--host', '192.168.1.100']):
            args = parser.parse_args()
            assert args.host == '192.168.1.100'
    
    def test_parse_verbose_flag(self):
        """Test parsing verbose flag"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install', '-v']):
            args = parser.parse_args()
            assert args.verbose is True
    
    def test_parse_ansible_args(self):
        """Test parsing additional Ansible arguments"""
        parser = CliArgumentParser()
        
        with patch('sys.argv', ['cli', 'psql', '--install', '--', '-e', 'foo=bar', '--tags', 'test']):
            args = parser.parse_args()
            assert args.ansible_args == ['-e', 'foo=bar', '--tags', 'test']
    
    def test_mutually_exclusive_environments(self):
        """Test that environment flags are mutually exclusive"""
        parser = CliArgumentParser()
        
        # This should work (only one environment)
        with patch('sys.argv', ['cli', 'psql', '--install', '--prod']):
            args = parser.parse_args()
            assert args.prod is True
        
        # Multiple environments should fail
        with patch('sys.argv', ['cli', 'psql', '--install', '--prod', '--dev']):
            with pytest.raises(SystemExit):
                parser.parse_args()
