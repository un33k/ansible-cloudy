"""
Configuration management for CLI
"""

import os
from pathlib import Path
from .colors import error, warn, Colors


class CliConfig:
    """Configuration and paths for CLI"""

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
            "Could not find project root. Run cli from the ansible-cloudy project directory."
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

    def __init__(self, config: CliConfig):
        self.config = config

    def get_inventory_path(self, environment: str = None, custom_path: str = None) -> str:
        """Get the appropriate inventory file path based on environment or custom path
        
        Args:
            environment: Environment name ('dev', 'prod', 'ci') or None for default
            custom_path: Custom inventory file path (overrides environment)
            
        Returns:
            Path to inventory file as string
        """
        # Use custom path if provided
        if custom_path:
            inventory_file = Path(custom_path)
            if not inventory_file.is_absolute():
                # Make relative paths relative to project root
                inventory_file = self.config.project_root / inventory_file
        else:
            # Determine environment-based inventory
            if environment == 'prod':
                inventory_file = self.config.inventory_dir / "prod.yml"
            elif environment == 'ci':
                inventory_file = self.config.inventory_dir / "ci.yml"
            else:  # Default to dev
                inventory_file = self.config.inventory_dir / "dev.yml"

        if not inventory_file.exists():
            error(f"Inventory file not found: {inventory_file}")

        return str(inventory_file)
    
    def get_environment_from_args(self, args) -> str:
        """Determine environment from parsed arguments
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Environment name ('dev', 'prod', 'ci')
        """
        if hasattr(args, 'prod') and args.prod:
            return 'prod'
        elif hasattr(args, 'ci') and args.ci:
            return 'ci'
        elif hasattr(args, 'dev') and args.dev:
            return 'dev'
        else:
            return 'dev'  # Default to dev
