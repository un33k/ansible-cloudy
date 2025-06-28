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
        """Detect if server is fresh (password) or secured (SSH key) - always port 22"""
        
        # Simple: test if SSH key works on port 22
        if self._test_ssh_key_auth(host, 22):
            info("🔐 Secured server detected (SSH key authentication)")
            return {
                'connection_type': 'secured',
                'auth_method': 'ssh_key'
            }
        else:
            info("🆕 Fresh server detected (password authentication required)")
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
    
    def get_connection_info(self, host: str) -> str:
        """Get simple connection information for logging"""
        server_state = self.detect_server_state(host)
        
        if server_state['connection_type'] == 'secured':
            return "Secured server (root@22 with SSH keys)"
        else:
            return "Fresh server (root@22 with password required)"