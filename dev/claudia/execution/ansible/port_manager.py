"""
SSH Port Detection and Management

Handles smart SSH port detection with fallback logic.
"""

import os
import subprocess
from typing import Dict, Optional
from pathlib import Path
from utils.colors import info
from utils.config import ClaudiaConfig


class SSHPortManager:
    """Manage SSH port detection and testing"""
    
    def __init__(self, config: ClaudiaConfig):
        self.config = config
    
    def test_port_connection(
        self, 
        inventory_path: str,
        port: int, 
        production: bool = False,
        target_host: Optional[str] = None,
        vault_args: list = None
    ) -> bool:
        """Test connection on specific port"""
        if vault_args is None:
            vault_args = []
            
        cmd = [
            "ansible",
            "security_targets" if port == 22 else "service_targets",
            "-i",
            inventory_path,
            "-m",
            "setup",
            "-u",
            "root",
            "-e",
            f"ansible_port={port}",
            "--timeout=10",
            "-f",
            "1",
        ] + vault_args

        # Add target host override if specified
        if target_host:
            cmd.extend(["-e", f"ansible_host={target_host}"])

        try:
            os.chdir(self.config.cloudy_dir)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def smart_port_detection(
        self,
        production: bool,
        target_host: Optional[str],
        inventory_path: str,
        vault_loader
    ) -> Dict:
        """Smart SSH port detection with fallback logic"""
        info("🔍 Testing SSH connectivity with smart port detection...")
        
        # Get configured SSH port from vault (if any)
        vault_args = vault_loader.auto_load_vault_file([])
        configured_port = vault_loader.extract_vault_ssh_port(vault_args)
        
        # Define port test order: configured port first, then 22
        ports_to_try = []
        if configured_port and configured_port != 22:
            ports_to_try.append(configured_port)
        ports_to_try.append(22)
        
        # Test each port
        for port in ports_to_try:
            info(f"🔌 Testing root connection on port {port}...")
            
            if self.test_port_connection(inventory_path, port, production, target_host, vault_args):
                info(f"✅ Successfully connected on port {port}")
                return {
                    'success': True,
                    'port': port,
                    'user': 'root',
                    'auth_method': 'password' if port == 22 else 'ssh_key'
                }
            else:
                info(f"❌ Connection failed on port {port}")
        
        return {'success': False, 'port': None, 'user': None, 'auth_method': None}
