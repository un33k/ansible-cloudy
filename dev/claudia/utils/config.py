"""
Configuration management for Ali CLI
"""

import os
from pathlib import Path
from .colors import error, warn, Colors


class AliConfig:
    """Configuration and paths for Ali CLI"""

    def __init__(self):
        # Find project root (directory containing cloudy/)
        self.project_root = self._find_project_root()
        self.base_dir = self.project_root  # Add base_dir for compatibility
        self.cloudy_dir = self.project_root / "cloudy"
        self.recipes_dir = self.cloudy_dir / "playbooks" / "recipes"
        self.inventory_dir = self.cloudy_dir / "inventory"
        self.dev_dir = self.project_root / "dev"

        # Validate project structure
        self._validate_structure()

        # Check virtual environment
        self._check_virtual_environment()

    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for cloudy/ folder"""
        current = Path.cwd()

        # Check current directory and parents
        for path in [current] + list(current.parents):
            if (path / "cloudy" / "ansible.cfg").exists():
                return path

        error(
            "Could not find project root. Run ali from the ansible-cloudy project directory."
        )

    def _validate_structure(self) -> None:
        """Validate that required directories exist"""
        required_paths = [
            self.cloudy_dir,
            self.recipes_dir,
            self.inventory_dir,
        ]

        for path in required_paths:
            if not path.exists():
                error(f"Required directory not found: {path}")

    def _check_virtual_environment(self) -> None:
        """Check if virtual environment is properly activated"""
        venv_path = self.project_root / ".venv"

        # Check if .venv exists and if we're in a virtual environment
        if not venv_path.exists():
            error(
                "Virtual environment not found!\n"
                f"{Colors.YELLOW}Run:{Colors.NC} ./bootstrap.sh && source .venv/bin/activate"
            )
        elif not os.environ.get("VIRTUAL_ENV"):
            error(
                "Virtual environment not activated!\n"
                f"{Colors.YELLOW}Run:{Colors.NC} deactivate >/dev/null 2>&1 || source .venv/bin/activate"
            )

        # Check if ansible is available in the venv
        try:
            import importlib.util

            ansible_spec = importlib.util.find_spec("ansible")
            if ansible_spec is None:
                error(
                    "Ansible not found in virtual environment!\n"
                    f"{Colors.YELLOW}Run:{Colors.NC} ./bootstrap.sh && source .venv/bin/activate"
                )
        except ImportError:
            error(
                "Python import system error - virtual environment may be corrupted"
            )


class InventoryManager:
    """Manage inventory files with smart connection detection"""

    def __init__(self, config: AliConfig):
        self.config = config

    def get_inventory_path(self, production: bool = False, smart_connection: bool = True) -> str:
        """Get the appropriate inventory file path with optional smart connection detection"""
        
        if production:
            inventory_file = self.config.inventory_dir / "production.yml"
        else:
            inventory_file = self.config.inventory_dir / "test.yml"

        if not inventory_file.exists():
            error(f"Inventory file not found: {inventory_file}")

        # For smart connection, create dynamic inventory if enabled
        if smart_connection and not production:
            return self._get_smart_inventory_path()
        
        return str(inventory_file)
    
    def _get_smart_inventory_path(self) -> str:
        """Create and return path to smart inventory with connection detection"""
        try:
            from .connection_manager import ConnectionManager
            
            # Get target host from static inventory
            static_inventory = self.config.inventory_dir / "test.yml"
            host = self._extract_host_from_inventory(static_inventory)
            
            if host:
                conn_manager = ConnectionManager(self.config)
                dynamic_inventory = conn_manager.create_dynamic_inventory(host)
                return str(dynamic_inventory)
            else:
                # Fallback to static inventory if we can't extract host
                return str(static_inventory)
                
        except Exception as e:
            # Fallback to static inventory on any error
            warn(f"Smart connection failed: {e}")
            return str(self.config.inventory_dir / "test.yml")
    
    def _extract_host_from_inventory(self, inventory_path: Path) -> str:
        """Extract the primary host IP from inventory file"""
        try:
            import yaml
            with open(inventory_path) as f:
                inventory = yaml.safe_load(f)
            
            # Look for ansible_host in the first host entry
            hosts = inventory.get('all', {}).get('hosts', {})
            for host_name, host_config in hosts.items():
                if 'ansible_host' in host_config:
                    return host_config['ansible_host']
            
            return None
        except Exception:
            return None
