#!/usr/bin/env python3
# type: ignore
# pylint: disable-all
# flake8: noqa
# mypy: ignore-errors
"""
Ali (Ansible Line Interpreter) - Simplified Ansible CLI for Cloudy

Makes Ansible commands shorter and more intuitive:
  ali security       → ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/security.yml
  ali django --prod  → ansible-playbook -i cloudy/inventory/production.yml cloudy/playbooks/recipes/www/django.yml
"""

import os
import sys
import glob
import argparse
import subprocess
import yaml
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any


# Colors for terminal output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def log(message: str, color: str = Colors.GREEN) -> None:
    """Print colored log message"""
    print(f"{color}✓{Colors.NC} {message}")


def warn(message: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def error(message: str) -> None:
    """Print error message and exit"""
    print(f"{Colors.RED}✗{Colors.NC} {message}")
    sys.exit(1)


def info(message: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")


class AliConfig:
    """Configuration and paths for Ali CLI"""

    def __init__(self):
        # Find project root (directory containing cloudy/)
        self.project_root = self._find_project_root()
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


class RecipeFinder:
    """Find and manage recipe files"""

    def __init__(self, config: AliConfig):
        self.config = config
        self._recipe_cache = None

    def get_all_recipes(self) -> dict:
        """Get all available recipes organized by category"""
        if self._recipe_cache is None:
            self._recipe_cache = self._scan_recipes()
        return self._recipe_cache

    def _scan_recipes(self) -> dict:
        """Scan recipes directory and organize by category"""
        recipes = {}

        # Scan all yml files in recipes directory
        pattern = str(self.config.recipes_dir / "**" / "*.yml")
        for recipe_path in glob.glob(pattern, recursive=True):
            rel_path = Path(recipe_path).relative_to(self.config.recipes_dir)

            # Extract category and name
            if len(rel_path.parts) == 2:  # category/name.yml
                category, filename = rel_path.parts
                name = filename[:-4]  # Remove .yml extension

                if category not in recipes:
                    recipes[category] = {}
                recipes[category][name] = str(rel_path)

        return recipes

    def find_recipe(self, name: str) -> Optional[str]:
        """Find a recipe by name, searching all categories"""
        recipes = self.get_all_recipes()

        # First try exact match in any category
        for category, category_recipes in recipes.items():
            if name in category_recipes:
                return category_recipes[name]

        # Try partial matches
        matches = []
        for category, category_recipes in recipes.items():
            for recipe_name, recipe_path in category_recipes.items():
                if name in recipe_name:
                    matches.append((recipe_name, recipe_path))

        if len(matches) == 1:
            return matches[0][1]
        elif len(matches) > 1:
            error(
                f"Ambiguous recipe name '{name}'. Found multiple matches: {[m[0] for m in matches]}"
            )

        return None


class InventoryManager:
    """Manage inventory files"""

    def __init__(self, config: AliConfig):
        self.config = config

    def get_inventory_path(self, production: bool = False) -> str:
        """Get the appropriate inventory file path"""
        if production:
            inventory_file = self.config.inventory_dir / "production.yml"
        else:
            inventory_file = self.config.inventory_dir / "test.yml"

        if not inventory_file.exists():
            error(f"Inventory file not found: {inventory_file}")

        return str(inventory_file)


class AnsibleRunner:
    """Execute ansible-playbook commands"""

    def __init__(self, config: AliConfig):
        self.config = config

    def run_recipe(
        self,
        recipe_path: str,
        inventory_path: str,
        extra_args: List[str],
        dry_run: bool = False,
    ) -> int:
        """Run ansible-playbook with the specified recipe"""

        # Build the command
        cmd = [
            "ansible-playbook",
            "-i",
            inventory_path,
            str(self.config.recipes_dir / recipe_path),
        ]

        # Add dry run flag if requested
        if dry_run:
            cmd.append("--check")

        # Add any extra arguments
        cmd.extend(extra_args)

        # Show what we're running
        info(f"Running: {' '.join(cmd)}")

        # Change to cloudy directory for execution
        os.chdir(self.config.cloudy_dir)

        # Execute the command
        try:
            return subprocess.run(cmd).returncode
        except KeyboardInterrupt:
            warn("Interrupted by user")
            return 130
        except FileNotFoundError:
            error(
                "ansible-playbook not found. Please install Ansible or activate your virtual environment."
            )


class SmartSecurityRunner:
    """Handle smart security detection and execution"""

    def __init__(
        self,
        config: AliConfig,
        inventory_manager: InventoryManager,
        ansible_runner: AnsibleRunner,
    ):
        self.config = config
        self.inventory_manager = inventory_manager
        self.ansible_runner = ansible_runner

    def run_smart_security(
        self,
        production: bool = False,
        extra_args: List[str] = None,
        dry_run: bool = False,
    ) -> int:
        """Run security with smart detection (try root first, fallback to admin verification)"""
        if extra_args is None:
            extra_args = []

        info("🔍 Detecting server security status...")

        # Try connecting as root first (fresh server scenario)
        if self._test_root_connection(production):
            info(
                "✅ Found unsecured server (root@22) - running initial hardening"
            )
            return self._run_initial_hardening(production, extra_args, dry_run)

        # Try connecting as admin user (already secured scenario)
        if self._test_admin_connection(production):
            info("✅ Found secured server - running security verification")
            return self._run_security_verification(
                production, extra_args, dry_run
            )

        # Both connections failed
        error(
            "❌ Cannot connect as root@22 or admin@ssh_port.\n"
            "Ensure server is accessible and check your SSH keys/credentials."
        )

    def _test_root_connection(self, production: bool) -> bool:
        """Test if we can connect as root on port 22"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Use ansible ad-hoc command to test root connection on port 22
        cmd = [
            "ansible",
            "all",
            "-i",
            inventory_path,
            "-m",
            "setup",
            "-u",
            "root",
            "-e",
            "ansible_port=22",
            "--timeout=10",
            "-f",
            "1",
        ]

        try:
            os.chdir(self.config.cloudy_dir)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _test_admin_connection(self, production: bool) -> bool:
        """Test if we can connect as admin user on the configured SSH port"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Use ansible ad-hoc command to test admin connection
        cmd = [
            "ansible",
            "all",
            "-i",
            inventory_path,
            "-m",
            "setup",
            "--timeout=10",
            "-f",
            "1",
        ]

        try:
            os.chdir(self.config.cloudy_dir)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _run_initial_hardening(
        self, production: bool, extra_args: List[str], dry_run: bool
    ) -> int:
        """Run the initial security hardening recipe"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        # Temporarily override connection settings for root access
        temp_args = [
            "-u",
            "root",
            "-e",
            "ansible_port=22",
            "-e",
            "ansible_user=root",
        ] + extra_args

        return self.ansible_runner.run_recipe(
            recipe_path="core/security.yml",
            inventory_path=inventory_path,
            extra_args=temp_args,
            dry_run=dry_run,
        )

    def _run_security_verification(
        self, production: bool, extra_args: List[str], dry_run: bool
    ) -> int:
        """Run the security verification recipe"""
        inventory_path = self.inventory_manager.get_inventory_path(production)

        return self.ansible_runner.run_recipe(
            recipe_path="core/security-verify.yml",
            inventory_path=inventory_path,
            extra_args=extra_args,
            dry_run=dry_run,
        )


class DevTools:
    """Development tools and commands"""

    def __init__(self, config: AliConfig):
        self.config = config

    def validate(self) -> int:
        """Run comprehensive validation"""
        validate_script = self.config.dev_dir / "validate.py"
        if not validate_script.exists():
            error(f"Validation script not found: {validate_script}")

        info(f"Running comprehensive validation...")
        os.chdir(self.config.project_root)

        result = subprocess.run(
            [str(validate_script)], capture_output=True, text=True
        )

        if result.returncode != 0:
            # Check if it's a missing dependency issue
            if (
                "ModuleNotFoundError" in result.stderr
                or "No module named" in result.stderr
            ):
                warn("Validation script requires additional Python packages")
                warn("Install with: pip install pyyaml")
                warn("Falling back to syntax check only...")
                return self.syntax()
            else:
                # Print the actual error output
                if result.stderr:
                    print(result.stderr)
                if result.stdout:
                    print(result.stdout)
        else:
            # Print successful output
            if result.stdout:
                print(result.stdout)

        return result.returncode

    def syntax(self) -> int:
        """Run syntax checking"""
        syntax_script = self.config.dev_dir / "syntax-check.sh"
        if not syntax_script.exists():
            error(f"Syntax check script not found: {syntax_script}")

        info(f"Running syntax checks...")
        os.chdir(self.config.project_root)
        return subprocess.run([str(syntax_script)]).returncode

    def lint(self) -> int:
        """Run both YAML syntax validation and ansible-lint"""
        info("Running comprehensive linting (YAML + Ansible)...")

        # First run YAML validation
        info("Step 1/2: Running yamllint...")
        yaml_exit_code = self.yaml()

        # Then run ansible-lint
        info("Step 2/2: Running ansible-lint...")
        lint_config = self.config.dev_dir / ".ansible-lint.yml"
        if not lint_config.exists():
            warn("Ansible-lint config not found, using defaults")
            config_args = []
        else:
            config_args = ["-c", str(lint_config)]

        os.chdir(self.config.project_root)

        try:
            cmd = (
                ["ansible-lint"] + config_args + [str(self.config.recipes_dir)]
            )
            ansible_exit_code = subprocess.run(cmd).returncode
        except FileNotFoundError:
            error(
                "ansible-lint not found. Install with: pip install ansible-lint"
            )

        # Return failure if either linter failed
        if yaml_exit_code != 0 or ansible_exit_code != 0:
            warn(
                f"Linting completed with issues (YAML: {yaml_exit_code}, Ansible: {ansible_exit_code})"
            )
            return 1
        else:
            log("All linting checks passed!")
            return 0

    def yaml(self) -> int:
        """Run YAML syntax validation with yamllint"""
        yaml_config = self.config.dev_dir / ".yamlint.yml"
        if not yaml_config.exists():
            warn("yamllint config not found, using defaults")
            config_args = []
        else:
            config_args = ["-c", str(yaml_config)]

        info(f"Running yamllint on YAML files...")
        os.chdir(self.config.project_root)

        try:
            # Check all YAML files in key directories
            yaml_paths = [
                str(self.config.recipes_dir),
                str(self.config.cloudy_dir / "inventory"),
                str(self.config.cloudy_dir / "tasks"),
                str(self.config.dev_dir / "test-auth.yml"),
            ]
            cmd = ["yamllint"] + config_args + yaml_paths
            return subprocess.run(cmd).returncode
        except FileNotFoundError:
            error("yamllint not found. Install with: pip install yamllint")

    def test(self, extra_args: List[str] = None) -> int:
        """Run authentication tests"""
        test_playbook = self.config.dev_dir / "test-auth.yml"
        if not test_playbook.exists():
            error(f"Test playbook not found: {test_playbook}")

        inventory_path = self.config.inventory_dir / "test.yml"
        if not inventory_path.exists():
            error(f"Test inventory not found: {inventory_path}")

        info(f"Running authentication tests...")
        os.chdir(self.config.cloudy_dir)

        cmd = [
            "ansible-playbook",
            "-i",
            str(inventory_path),
            str(test_playbook),
            "--check",
        ]

        # Add extra arguments if provided
        if extra_args:
            cmd.extend(extra_args)

        return subprocess.run(cmd).returncode

    def spell(self) -> int:
        """Run spell checking"""
        spell_config = self.config.dev_dir / ".cspell.json"
        if not spell_config.exists():
            error(f"Spell check config not found: {spell_config}")

        info(f"Running spell check...")
        os.chdir(self.config.project_root)

        try:
            cmd = [
                "npx",
                "cspell",
                "**/*.md",
                "**/*.yml",
                "--config",
                str(spell_config),
            ]
            return subprocess.run(cmd).returncode
        except FileNotFoundError:
            error("cspell not found. Install with: npm install -g cspell")


def list_dev_commands() -> None:
    """List available development commands"""
    print(f"\n{Colors.CYAN}🛠️  Development Commands:{Colors.NC}")
    print("=" * 50)

    commands = [
        ("validate", "Comprehensive validation of all components"),
        ("syntax", "Quick syntax checking for all recipes"),
        ("yaml", "YAML syntax validation with yamllint"),
        ("lint", "Complete linting (YAML + Ansible)"),
        ("test", "Authentication flow testing"),
        ("spell", "Spell check all documentation and configs"),
    ]

    for cmd, desc in commands:
        print(f"  • {Colors.GREEN}ali dev {cmd:<8}{Colors.NC} - {desc}")

    print(f"\n{Colors.YELLOW}Usage examples:{Colors.NC}")
    print("  ali dev validate       # Full validation suite")
    print("  ali dev syntax         # Quick syntax check")
    print("  ali dev yaml           # YAML syntax validation")
    print("  ali dev lint           # Complete linting (YAML + Ansible)")
    print("  ali dev test           # Test authentication")


class RecipeHelpParser:
    """Parse recipe files to extract help information automatically"""

    def __init__(self, config: AliConfig):
        self.config = config

    def parse_recipe_help(self, recipe_path: Path) -> Dict[str, Any]:
        """Extract help information from a recipe file"""
        help_info = {
            "name": recipe_path.stem,
            "description": "",
            "purpose": "",
            "usage": "",
            "variables": {},
            "tags": set(),
            "prerequisites": "",
        }

        try:
            with open(recipe_path, "r") as f:
                content = f.read()

            # Extract header comments
            lines = content.split("\n")
            for line in lines[:20]:  # Check first 20 lines for comments
                line = line.strip()
                if line.startswith("# Purpose:"):
                    help_info["purpose"] = line.replace(
                        "# Purpose:", ""
                    ).strip()
                elif line.startswith("# Usage:"):
                    help_info["usage"] = line.replace("# Usage:", "").strip()
                elif line.startswith("# Prerequisites:"):
                    help_info["prerequisites"] = line.replace(
                        "# Prerequisites:", ""
                    ).strip()
                elif line.startswith("# Recipe:"):
                    help_info["description"] = line.replace(
                        "# Recipe:", ""
                    ).strip()

            # Parse YAML to extract variables and tags
            try:
                yaml_content = yaml.safe_load(content)
                if isinstance(yaml_content, list) and yaml_content:
                    playbook = yaml_content[0]

                    # Extract variables from vars section
                    if "vars" in playbook:
                        for var_name, var_value in playbook["vars"].items():
                            # Skip internal variables
                            if not var_name.startswith("task_"):
                                help_info["variables"][var_name] = var_value

                    # Extract tags from tasks
                    if "tasks" in playbook:
                        for task in playbook["tasks"]:
                            if isinstance(task, dict) and "tags" in task:
                                if isinstance(task["tags"], list):
                                    help_info["tags"].update(task["tags"])
                                else:
                                    help_info["tags"].add(task["tags"])

            except yaml.YAMLError:
                pass  # Skip YAML parsing errors

            # Get inventory variables for this recipe
            help_info["inventory_vars"] = self._get_inventory_variables()

        except Exception:
            pass  # Skip file reading errors

        return help_info

    def _get_inventory_variables(self) -> Dict[str, Any]:
        """Extract variables from inventory files"""
        variables = {}

        # Check test inventory
        test_inventory = self.config.cloudy_dir / "inventory" / "test.yml"
        if test_inventory.exists():
            try:
                with open(test_inventory, "r") as f:
                    inventory = yaml.safe_load(f)
                    if "all" in inventory and "vars" in inventory["all"]:
                        # Filter out variables that don't apply to all recipes
                        all_vars = inventory["all"]["vars"]
                        for var_name, var_value in all_vars.items():
                            # Skip context-specific variables that shouldn't appear in all recipes
                            if not self._is_context_specific_variable(
                                var_name
                            ):
                                variables[var_name] = var_value
            except:
                pass

        return variables

    def _is_context_specific_variable(self, var_name: str) -> bool:
        """Check if a variable is context-specific and shouldn't appear in all recipe help"""
        context_specific_vars = {
            # Service-specific variables
            "postgresql_version",
            "postgis_version",
            "database_port",
            "redis_memory_mb",
            "redis_port",
            "webserver",
            "webserver_port",
            "domain_name",
            # Other service-specific vars that might be added
        }
        return var_name in context_specific_vars

    def display_recipe_help(self, recipe_name: str, recipe_path) -> None:
        """Display comprehensive help for a recipe"""
        # Convert to Path object if it's a string
        if isinstance(recipe_path, str):
            recipe_path = self.config.recipes_dir / recipe_path
        help_info = self.parse_recipe_help(recipe_path)

        print(f"\n{Colors.CYAN}📖 Help: {recipe_name}{Colors.NC}")
        print("=" * 50)

        if help_info["description"]:
            print(f"\n{Colors.BLUE}Description:{Colors.NC}")
            print(f"  {help_info['description']}")

        if help_info["purpose"]:
            print(f"\n{Colors.BLUE}Purpose:{Colors.NC}")
            print(f"  {help_info['purpose']}")

        if help_info["prerequisites"]:
            print(f"\n{Colors.BLUE}Prerequisites:{Colors.NC}")
            print(f"  {help_info['prerequisites']}")

        # Usage examples
        print(f"\n{Colors.BLUE}Usage:{Colors.NC}")
        if help_info["usage"]:
            print(f"  {help_info['usage']}")
        print(
            f"  ali {recipe_name}                    # Run on test environment"
        )
        print(f"  ali {recipe_name} --prod             # Run on production")
        print(f"  ali {recipe_name} --check            # Dry run (no changes)")
        print(f"  ali {recipe_name} --verbose          # Verbose output")

        # Display key variables (combine inventory and recipe variables)
        all_variables = {}
        all_variables.update(help_info.get("inventory_vars", {}))
        all_variables.update(help_info.get("variables", {}))

        if all_variables:
            print(
                f"\n{Colors.BLUE}Available Variables (override with -e):{Colors.NC}"
            )
            for var_name, var_value in sorted(all_variables.items()):
                if not var_name.startswith(
                    "ansible_"
                ):  # Skip ansible internal vars
                    print(
                        f"  {Colors.GREEN}{var_name:<20}{Colors.NC} = {var_value}"
                    )

        # Display tags
        if help_info["tags"]:
            print(
                f"\n{Colors.BLUE}Available Tags (use with --tags):{Colors.NC}"
            )
            sorted_tags = sorted(help_info["tags"])
            # Group tags in lines of 5
            for i in range(0, len(sorted_tags), 5):
                tag_group = sorted_tags[i : i + 5]
                print(f"  {', '.join(tag_group)}")

        # Usage examples with variables and tags
        print(f"\n{Colors.YELLOW}Advanced Examples:{Colors.NC}")
        print(
            f'  ali {recipe_name} -- -e "admin_user=myuser"        # Override variables'
        )
        print(
            f"  ali {recipe_name} -- --tags ssh                    # Run only SSH tasks"
        )
        print(
            f"  ali {recipe_name} -- --skip-tags firewall         # Skip firewall tasks"
        )
        print(
            f"  ali {recipe_name} -- --limit test-server           # Run on specific host"
        )


def list_recipes(config: AliConfig) -> None:
    """List all available recipes"""
    finder = RecipeFinder(config)
    recipes = finder.get_all_recipes()

    if not recipes:
        warn("No recipes found")
        return

    print(f"\n{Colors.CYAN}📋 Available Recipes:{Colors.NC}")
    print("=" * 50)

    for category in sorted(recipes.keys()):
        print(f"\n{Colors.BLUE}{category.upper()}:{Colors.NC}")
        for recipe_name in sorted(recipes[category].keys()):
            print(f"  • {recipe_name}")

    print(f"\n{Colors.YELLOW}Usage examples:{Colors.NC}")
    print("  ali security           # Run core/security.yml on test")
    print("  ali django --prod      # Run www/django.yml on production")
    print("  ali redis --check      # Dry run cache/redis.yml")
    print("  ali nginx -- --tags ssl # Pass --tags ssl to ansible-playbook")
    print(
        f"\n{Colors.CYAN}💡 Tip:{Colors.NC} Use 'ali RECIPE --help' for detailed recipe help"
    )


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter with colors"""

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = f"{Colors.CYAN}usage:{Colors.NC} "
        return super()._format_usage(usage, actions, groups, prefix)

    def format_help(self):
        help_text = super().format_help()
        # Add colors to section headers
        help_text = help_text.replace(
            "positional arguments:",
            f"{Colors.BLUE}positional arguments:{Colors.NC}",
        )
        help_text = help_text.replace(
            "options:", f"{Colors.BLUE}options:{Colors.NC}"
        )

        # Color individual arguments and options
        import re

        # Color positional arguments (like "command", "subcommand")
        help_text = re.sub(
            r"^  (command|subcommand)(\s+)",
            f"  {Colors.GREEN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        # Color option flags (handle both "-h, --help" and "--list, -l" patterns)
        help_text = re.sub(
            r"^  ((?:-[a-zA-Z-]+(?:, --[a-zA-Z-]+)?|--[a-zA-Z-]+(?:, -[a-zA-Z])?))(\s+)",
            f"  {Colors.CYAN}\\1{Colors.NC}\\2",
            help_text,
            flags=re.MULTILINE,
        )

        return help_text


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}Ali (Ansible Line Interpreter) - Simplified Ansible CLI{Colors.NC}",
        formatter_class=ColoredHelpFormatter,
        epilog=f"""
{Colors.YELLOW}Examples:{Colors.NC}
  {Colors.GREEN}ali security{Colors.NC}                    Run security recipe on test environment
  {Colors.GREEN}ali django --prod{Colors.NC}              Run django recipe on production
  {Colors.GREEN}ali redis --check{Colors.NC}              Dry run redis recipe
  {Colors.GREEN}ali nginx -- --tags ssl{Colors.NC}        Pass --tags ssl to ansible-playbook
  {Colors.GREEN}ali --list{Colors.NC}                      Show all available recipes
  
  {Colors.GREEN}ali dev validate{Colors.NC}                Run comprehensive validation
  {Colors.GREEN}ali dev syntax{Colors.NC}                 Quick syntax checking  
  {Colors.GREEN}ali dev yaml{Colors.NC}                   YAML syntax validation
  {Colors.GREEN}ali dev lint{Colors.NC}                   Complete linting (YAML + Ansible)
  {Colors.GREEN}ali dev test{Colors.NC}                   Authentication testing
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        help="Recipe name or 'dev' for development commands",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        help="Development subcommand (when using 'dev')",
    )
    parser.add_argument(
        "--prod",
        "--production",
        action="store_true",
        help="Use production inventory instead of test",
    )
    parser.add_argument(
        "--check",
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (--check)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all available recipes or dev commands",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    return parser


def main() -> None:
    """Main entry point for Ali CLI"""

    # Parse arguments, splitting on -- for ansible args
    if "--" in sys.argv:
        split_idx = sys.argv.index("--")
        ali_args = sys.argv[1:split_idx]
        ansible_args = sys.argv[split_idx + 1 :]
    else:
        ali_args = sys.argv[1:]
        ansible_args = []

    # Check for recipe-specific help before parsing
    if len(ali_args) >= 2 and ali_args[1] in ["--help", "-h"]:
        recipe_name = ali_args[0]
        # Initialize config to find recipe
        try:
            config = AliConfig()
            finder = RecipeFinder(config)
            recipe_path = finder.find_recipe(recipe_name)
            if recipe_path:
                help_parser = RecipeHelpParser(config)
                help_parser.display_recipe_help(recipe_name, recipe_path)
                return
            else:
                # Recipe not found, show error then general help
                print(
                    f"{Colors.RED}(✗){Colors.NC} {Colors.YELLOW}{recipe_name}{Colors.NC} {Colors.RED}not found{Colors.NC}:\n"
                )
                parser = create_parser()
                parser.print_help()
                return
        except:
            pass  # Fall back to normal help

    # Parse ali arguments
    parser = create_parser()
    args, remaining_args = parser.parse_known_args(ali_args)

    # Combine remaining args with original ansible args
    ansible_args.extend(remaining_args)

    # Initialize configuration
    try:
        config = AliConfig()
    except Exception as e:
        error(f"Configuration error: {e}")

    # Handle list command
    if args.list:
        if args.command == "dev":
            list_dev_commands()
        else:
            list_recipes(config)
        return

    # Handle dev commands
    if args.command == "dev":
        if not args.subcommand:
            list_dev_commands()
            return

        dev_tools = DevTools(config)

        # Route to appropriate dev command
        if args.subcommand == "validate":
            exit_code = dev_tools.validate()
        elif args.subcommand == "syntax":
            exit_code = dev_tools.syntax()
        elif args.subcommand == "yaml":
            exit_code = dev_tools.yaml()
        elif args.subcommand == "lint":
            exit_code = dev_tools.lint()
        elif args.subcommand == "test":
            exit_code = dev_tools.test(ansible_args)
        elif args.subcommand == "spell":
            exit_code = dev_tools.spell()
        else:
            error(
                f"Unknown dev command '{args.subcommand}'. Use 'ali dev --list' to see available commands."
            )

        sys.exit(exit_code)

    # Require recipe name if not listing or dev command
    if not args.command:
        parser.print_help()
        return

    # Find the recipe
    finder = RecipeFinder(config)
    recipe_path = finder.find_recipe(args.command)

    # Check if help is requested for this recipe
    if "--help" in ansible_args or "-h" in ansible_args:
        if recipe_path:
            help_parser = RecipeHelpParser(config)
            help_parser.display_recipe_help(args.command, recipe_path)
            return
        else:
            # Show "not found" error then general help
            print(f"{Colors.RED}✗{Colors.NC} {args.command} not found:")
            parser.print_help()
            return

    if not recipe_path:
        error(
            f"Recipe '{args.command}' not found. Use 'ali --list' to see available recipes."
        )

    # Get inventory and runner
    inventory_manager = InventoryManager(config)
    runner = AnsibleRunner(config)

    # Add verbose flag if requested
    if args.verbose:
        ansible_args.insert(0, "-v")

    # Handle smart security execution
    if args.command == "security":
        smart_security = SmartSecurityRunner(config, inventory_manager, runner)
        exit_code = smart_security.run_smart_security(
            production=args.prod, extra_args=ansible_args, dry_run=args.check
        )
    else:
        # Run regular recipe
        inventory_path = inventory_manager.get_inventory_path(args.prod)
        exit_code = runner.run_recipe(
            recipe_path=recipe_path,
            inventory_path=inventory_path,
            extra_args=ansible_args,
            dry_run=args.check,
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
