"""
Recipe discovery, management, and help generation for Ali CLI
"""

import glob
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from config import AliConfig
from colors import Colors, error, warn


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
            f"  ali {recipe_name}                    # Show this help (default action)"
        )
        print(f"  ali {recipe_name} --install          # Execute recipe on test environment")
        print(f"  ali {recipe_name} --install --prod   # Execute recipe on production")
        print(f"  ali {recipe_name} --install --check  # Dry run (no changes)")
        print(f"  ali {recipe_name} --install --verbose # Verbose output")
        
        # Add security-specific options
        if recipe_name == "security":
            print(f"  ali {recipe_name} --verify           # Run security verification/check")

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
            f'  ali {recipe_name} --install -- -e "admin_user=myuser"  # Override variables'
        )
        print(
            f"  ali {recipe_name} --install -- --tags ssh              # Run only SSH tasks"
        )
        print(
            f"  ali {recipe_name} --install -- --skip-tags firewall    # Skip firewall tasks"
        )
        print(
            f"  ali {recipe_name} --install -- --limit test-server     # Run on specific host"
        )
        
        # Add security-specific advanced examples
        if recipe_name == "security":
            print(
                f"  ali {recipe_name} --verify --prod                      # Verify production security"
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
    print("  ali security                # Show security recipe help")
    print("  ali security --install      # Execute core/security.yml on test")
    print("  ali django --install --prod # Execute www/django.yml on production")
    print("  ali redis --install --check # Dry run cache/redis.yml")
    print("  ali nginx --install -- --tags ssl # Execute nginx with --tags ssl")
    print(
        f"\n{Colors.CYAN}💡 Tip:{Colors.NC} Use 'ali RECIPE' to see detailed help and available options"
    )
