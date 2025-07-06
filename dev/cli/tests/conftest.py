"""
PyTest Configuration and Fixtures

Shared test fixtures and configuration for the CLI test suite.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import os
from unittest.mock import Mock

# Add the parent directory to the path so we can import cli modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import CliConfig  # noqa: E402


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # Create expected directory structure
        (project_dir / "cloudy").mkdir()
        (project_dir / "cloudy" / "playbooks" / "recipes").mkdir(parents=True)
        (project_dir / "cloudy" / "tasks").mkdir(parents=True)
        (project_dir / "cloudy" / "inventory").mkdir(parents=True)
        (project_dir / "dev" / "cli").mkdir(parents=True)
        (project_dir / ".vault").mkdir(parents=True)
        
        yield project_dir


@pytest.fixture
def mock_config(temp_project_dir):
    """Create a mock CliConfig instance"""
    config = Mock(spec=CliConfig)
    config.project_root = temp_project_dir
    config.cloudy_dir = temp_project_dir / "cloudy"
    config.recipes_dir = temp_project_dir / "cloudy" / "playbooks" / "recipes"
    config.tasks_dir = temp_project_dir / "cloudy" / "tasks"
    config.inventory_dir = temp_project_dir / "cloudy" / "inventory"
    config.cli_dir = temp_project_dir / "dev" / "cli"
    return config


@pytest.fixture
def sample_inventory_file(temp_project_dir):
    """Create a sample inventory file"""
    inventory_dir = temp_project_dir / "cloudy" / "inventory"
    inventory_file = inventory_dir / "dev.yml"
    
    inventory_content = """
all:
  vars:
    ansible_user: admin
    ansible_port: 2222
    
  children:
    generic_servers:
      hosts:
        test-server:
          ansible_host: 10.10.10.100
          admin_user: admin
          admin_password: secure123
"""
    
    inventory_file.write_text(inventory_content)
    return inventory_file


@pytest.fixture
def sample_vault_file(temp_project_dir):
    """Create a sample vault file"""
    vault_dir = temp_project_dir / ".vault"
    vault_file = vault_dir / "dev.yml"
    
    vault_content = """
---
vault_root_password: "test_root_pass"
vault_admin_password: "test_admin_pass"
vault_ssh_port: 2222
vault_postgres_password: "test_pg_pass"
"""
    
    vault_file.write_text(vault_content)
    return vault_file


@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment variables before each test"""
    # Remove any vault-related environment variables
    vault_vars = [
        'ANSIBLE_VAULT_PASSWORD_FILE',
        'ANSIBLE_VAULT_PASSWORD_FILE_DEV',
        'ANSIBLE_VAULT_PASSWORD_FILE_CI',
        'ANSIBLE_VAULT_PASSWORD_FILE_PROD'
    ]
    
    for var in vault_vars:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Clean up after test
    for var in vault_vars:
        if var in os.environ:
            del os.environ[var]
