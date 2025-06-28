"""
Development tools and commands for Ali CLI
"""

import os
import subprocess
from typing import List
from config import AliConfig
from colors import Colors, info, warn, error, log


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
