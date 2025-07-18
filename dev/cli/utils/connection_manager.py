"""
Smart Connection Manager
Handles automatic detection and switching between fresh and secured server connections
"""

import subprocess
import socket
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .colors import Colors, warn, info
from .config import CliConfig


class ConnectionManager:
    """Manages intelligent connection switching between fresh and secured servers"""
    
    def __init__(self, config: CliConfig):
        self.config = config
        
    def detect_server_state(self, host: str, ansible_port: int) -> Dict[str, Any]:
        """Detect if server is fresh (password) or secured (SSH key) using configured port"""
        
        # Simple: test if SSH key works on configured port
        if self._test_ssh_key_auth(host, ansible_port):
            info(f"🔐 Secured server detected (SSH key authentication on port {ansible_port})")
            return {
                'connection_type': 'secured',
                'auth_method': 'ssh_key'
            }
        else:
            info(f"🆕 Fresh server detected (password authentication required on port {ansible_port})")
            return {
                'connection_type': 'fresh', 
                'auth_method': 'password'
            }
    
    def _test_ssh_key_auth(self, host: str, port: int) -> bool:
        """Test if SSH key authentication works for root user on specified port"""
        key_path = Path.home() / '.ssh' / 'id_rsa'
        
        if not key_path.exists():
            return False
            
        ssh_cmd = [
            'ssh',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'BatchMode=yes',  # No interactive prompts
            '-o', 'PasswordAuthentication=no',  # Force key-only auth
            '-i', str(key_path),
            '-p', str(port),
            f"root@{host}",
            'echo "connection_test"'
        ]
        
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
    
    def get_connection_info(self, host: str, ansible_port: int) -> str:
        """Get simple connection information for logging"""
        server_state = self.detect_server_state(host, ansible_port)
        
        if server_state['connection_type'] == 'secured':
            return f"Secured server (root@{ansible_port} with SSH keys)"
        else:
            return f"Fresh server (root@{ansible_port} with password required)"
