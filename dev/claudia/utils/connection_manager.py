"""
Smart Connection Manager for Claudia
Handles automatic detection and switching between fresh and secured server connections
"""

import subprocess
import socket
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .colors import Colors, warn, info
from .config import AliConfig


class ConnectionManager:
    """Manages intelligent connection switching between fresh and secured servers"""
    
    def __init__(self, config: AliConfig):
        self.config = config
        
    def detect_server_state(self, host: str) -> Dict[str, Any]:
        """Detect current server state and return appropriate connection settings"""
        
        # Test connection scenarios in order of preference
        connection_attempts = [
            {
                'name': 'secured_admin',
                'user': 'admino', 
                'port': 22022,
                'auth': 'key',
                'description': 'Admin user with SSH keys on secured port'
            },
            {
                'name': 'secured_root',
                'user': 'root',
                'port': 22022, 
                'auth': 'key',
                'description': 'Root user with SSH keys on secured port'
            },
            {
                'name': 'fresh_root',
                'user': 'root',
                'port': 22,
                'auth': 'key_fallback_password',
                'description': 'Fresh server - root with SSH key or password fallback'
            }
        ]
        
        for attempt in connection_attempts:
            if self._test_connection(host, attempt):
                info(f"✅ Connected via {attempt['description']}")
                return self._build_connection_config(attempt)
        
        # If all fail, return fresh server config as fallback
        warn("⚠️  All connection attempts failed, using fresh server fallback")
        return self._build_connection_config(connection_attempts[2])
    
    def _test_connection(self, host: str, attempt: Dict) -> bool:
        """Test if a specific connection configuration works"""
        
        # First check if port is open
        if not self._is_port_open(host, attempt['port']):
            return False
            
        # Test SSH connection
        ssh_cmd = [
            'ssh',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'BatchMode=yes',  # No interactive prompts
            '-p', str(attempt['port']),
        ]
        
        # Add key-based auth if available
        key_path = Path.home() / '.ssh' / 'id_rsa'
        if key_path.exists() and attempt['auth'] in ['key', 'key_fallback_password']:
            ssh_cmd.extend(['-i', str(key_path)])
            
        ssh_cmd.extend([f"{attempt['user']}@{host}", 'echo "connection_test"'])
        
        try:
            result = subprocess.run(
                ssh_cmd, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0 and 'connection_test' in result.stdout
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def _is_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open on the target host"""
        try:
            with socket.create_connection((host, port), timeout=3):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def _build_connection_config(self, attempt: Dict) -> Dict[str, Any]:
        """Build Ansible connection configuration from attempt details"""
        
        config = {
            'ansible_user': attempt['user'],
            'ansible_port': attempt['port'],
            'ansible_host_key_checking': False,
            'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
            'connection_type': attempt['name']
        }
        
        # Add SSH key if available and auth method supports it
        key_path = Path.home() / '.ssh' / 'id_rsa'
        if key_path.exists() and attempt['auth'] in ['key', 'key_fallback_password']:
            config['ansible_ssh_private_key_file'] = str(key_path)
        
        # For fresh server, we might need password fallback
        if attempt['name'] == 'fresh_root' and attempt['auth'] == 'key_fallback_password':
            # Password will be handled by ansible-playbook prompting or inventory
            pass
            
        return config
    
    def get_smart_inventory_vars(self, host: str) -> Dict[str, Any]:
        """Get smart inventory variables that auto-detect connection method"""
        
        detected_config = self.detect_server_state(host)
        
        # Base inventory vars (unchanged)
        base_vars = {
            'git_user_full_name': "Test User",
            'git_user_email': "test@example.com", 
            'timezone': "America/New_York",
            'admin_user': 'admino',
            'admin_password': 'secure123',
            'admin_groups': "admin,www-data",
            'admin_ssh_private_key_file': '~/.ssh/id_rsa',
            'ssh_port': 22022,
        }
        
        # Merge with detected connection settings
        base_vars.update(detected_config)
        
        return base_vars
    
    def create_dynamic_inventory(self, host: str, output_path: Optional[Path] = None) -> Path:
        """Create a dynamic inventory file with smart connection detection"""
        
        smart_vars = self.get_smart_inventory_vars(host)
        connection_type = smart_vars.get('connection_type', 'unknown')
        
        inventory_content = f"""# Dynamic Inventory - Auto-detected connection: {connection_type}
# Generated by Claudia Connection Manager

---
all:
  vars:
    # Global Settings
    git_user_full_name: "{smart_vars['git_user_full_name']}"
    git_user_email: "{smart_vars['git_user_email']}"
    timezone: "{smart_vars['timezone']}"
    
    # Smart Connection Settings (auto-detected)
    ansible_user: {smart_vars['ansible_user']}
    ansible_port: {smart_vars['ansible_port']}
    ansible_host_key_checking: {str(smart_vars['ansible_host_key_checking']).lower()}
    ansible_ssh_common_args: '{smart_vars['ansible_ssh_common_args']}'"""

        if 'ansible_ssh_private_key_file' in smart_vars:
            inventory_content += f"""
    ansible_ssh_private_key_file: {smart_vars['ansible_ssh_private_key_file']}"""

        inventory_content += f"""
    
    # Admin User Configuration
    admin_user: {smart_vars['admin_user']}
    admin_password: {smart_vars['admin_password']}
    admin_groups: "{smart_vars['admin_groups']}"
    admin_ssh_private_key_file: {smart_vars['admin_ssh_private_key_file']}
    ssh_port: {smart_vars['ssh_port']}
    
  hosts:
    test-server:
      ansible_host: {host}
      hostname: test-server.example.com
      
      # Service-specific configs
      domain_name: test-server.example.com
      postgresql_version: "15"
      postgis_version: "3.3"
      database_port: 5433
      redis_memory_mb: 512
      redis_port: 6379
      webserver: gunicorn
      webserver_port: 8181
"""
        
        if output_path is None:
            output_path = self.config.base_dir / "cloudy" / "inventory" / "dynamic.yml"
            
        output_path.write_text(inventory_content)
        info(f"📝 Created dynamic inventory: {output_path}")
        
        return output_path