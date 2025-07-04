#!/usr/bin/env python3
"""
Ansible Cloudy Validation Script
Comprehensive validation for simplified Ansible infrastructure automation
"""

import os
import sys
import yaml
import glob
import subprocess
from typing import Tuple

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class CloudyValidator:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a test function and track results"""
        print(f"\n{Colors.YELLOW}Running: {test_name}{Colors.NC}")
        self.tests_run += 1
        
        try:
            result = test_func()
            if result:
                print(f"{Colors.GREEN}✅ PASSED: {test_name}{Colors.NC}")
                self.tests_passed += 1
                return True
            else:
                print(f"{Colors.RED}❌ FAILED: {test_name}{Colors.NC}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ ERROR: {test_name} - {str(e)}{Colors.NC}")
            self.errors.append(f"{test_name}: {str(e)}")
            self.tests_failed += 1
            return False
    
    def validate_yaml_file(self, filepath: str) -> Tuple[bool, str]:
        """Validate YAML syntax"""
        try:
            with open(filepath, 'r') as f:
                yaml.safe_load(f)
            return True, "Valid YAML"
        except yaml.YAMLError as e:
            return False, f"YAML Error: {str(e)}"
        except Exception as e:
            return False, f"File Error: {str(e)}"
    
    def validate_task_file(self, filepath: str) -> Tuple[bool, str]:
        """Validate task file structure"""
        try:
            with open(filepath, 'r') as f:
                content = yaml.safe_load(f)
            
            if not isinstance(content, list):
                return False, "Task file must be a YAML list"
            
            for i, task in enumerate(content):
                if not isinstance(task, dict):
                    return False, f"Task {i+1} must be a dictionary"
                if 'name' not in task:
                    return False, f"Task {i+1} missing 'name' field"
            
            return True, f"Valid task file with {len(content)} tasks"
        except Exception as e:
            return False, str(e)
    
    def validate_playbook_file(self, filepath: str) -> Tuple[bool, str]:
        """Validate playbook structure"""
        try:
            with open(filepath, 'r') as f:
                content = yaml.safe_load(f)
            
            if not isinstance(content, list):
                return False, "Playbook must be a YAML list"
            
            for play in content:
                if not isinstance(play, dict):
                    return False, "Each play must be a dictionary"
                if 'hosts' not in play:
                    return False, "Play missing 'hosts' field"
                if 'name' not in play:
                    return False, "Play missing 'name' field"
            
            return True, f"Valid playbook with {len(content)} plays"
        except Exception as e:
            return False, str(e)
    
    def test_task_files(self) -> bool:
        """Test all task files"""
        task_files = glob.glob("cloudy/tasks/**/*.yml", recursive=True)
        if not task_files:
            return False
        
        valid_count = 0
        for task_file in task_files:
            is_valid, message = self.validate_task_file(task_file)
            if is_valid:
                valid_count += 1
            else:
                print(f"  {Colors.RED}❌ {task_file}: {message}{Colors.NC}")
        
        print(f"  {Colors.BLUE}Task files: {valid_count}/{len(task_files)} valid{Colors.NC}")
        return valid_count == len(task_files)
    
    def test_recipe_files(self) -> bool:
        """Test all recipe files in new structure"""
        recipe_files = glob.glob("cloudy/playbooks/recipes/**/*.yml", recursive=True)
        
        if not recipe_files:
            return False
        
        valid_count = 0
        for recipe_file in recipe_files:
            is_valid, message = self.validate_playbook_file(recipe_file)
            if is_valid:
                valid_count += 1
            else:
                print(f"  {Colors.RED}❌ {recipe_file}: {message}{Colors.NC}")
        
        print(f"  {Colors.BLUE}Recipe files: {valid_count}/{len(recipe_files)} valid{Colors.NC}")
        return valid_count == len(recipe_files)
    
    def test_inventory_files(self) -> bool:
        """Test inventory files"""
        inventory_files = glob.glob("cloudy/inventory/*.yml")
        if not inventory_files:
            return False
        
        valid_count = 0
        for inv_file in inventory_files:
            try:
                result = subprocess.run(
                    ["ansible-inventory", "-i", inv_file, "--list"],
                    capture_output=True, text=True, check=True
                )
                valid_count += 1
            except subprocess.CalledProcessError as e:
                print(f"  {Colors.RED}❌ {inv_file}: {e.stderr.strip()}{Colors.NC}")
        
        print(f"  {Colors.BLUE}Inventory files: {valid_count}/{len(inventory_files)} valid{Colors.NC}")
        return valid_count == len(inventory_files)
    
    def test_template_files(self) -> bool:
        """Test template files"""
        template_files = glob.glob("cloudy/templates/*.j2")
        if not template_files:
            return True  # No templates is OK
        
        valid_count = 0
        for template_file in template_files:
            try:
                # Basic check - file exists and is readable
                with open(template_file, 'r') as f:
                    content = f.read()
                if content.strip():
                    valid_count += 1
                else:
                    print(f"  {Colors.RED}❌ {template_file}: Empty template{Colors.NC}")
            except Exception as e:
                print(f"  {Colors.RED}❌ {template_file}: {str(e)}{Colors.NC}")
        
        print(f"  {Colors.BLUE}Templates: {valid_count}/{len(template_files)} valid{Colors.NC}")
        return valid_count == len(template_files)
    
    def test_recipe_dependencies(self) -> bool:
        """Test that recipe dependencies exist"""
        recipe_files = glob.glob("cloudy/playbooks/recipes/**/*.yml", recursive=True)
        if not recipe_files:
            return False
        
        all_valid = True
        for recipe_file in recipe_files:
            try:
                with open(recipe_file, 'r') as f:
                    content = f.read()
                
                # Find include_tasks references
                import re
                includes = re.findall(r'include_tasks:\s*([^\s\n]+)', content)
                
                for include_path in includes:
                    # Convert relative path to absolute
                    if include_path.startswith('../../'):
                        # Recipe files are in cloudy/playbooks/recipes/*, so ../../ points to cloudy/
                        full_path = 'cloudy/' + include_path.replace('../../', '')
                    else:
                        full_path = include_path
                    
                    if not os.path.exists(full_path):
                        print(f"  {Colors.RED}❌ {recipe_file}: Missing dependency {full_path}{Colors.NC}")
                        all_valid = False
                        
            except Exception as e:
                print(f"  {Colors.RED}❌ {recipe_file}: {str(e)}{Colors.NC}")
                all_valid = False
        
        return all_valid
    
    def test_ansible_syntax(self) -> bool:
        """Test Ansible syntax for recipes"""
        try:
            # Test main recipes
            recipe_files = glob.glob("cloudy/playbooks/recipes/**/*.yml", recursive=True)
            dev_files = glob.glob("dev/*.yml")
            
            all_files = recipe_files + dev_files
            
            for playbook in all_files:
                if os.path.exists(playbook):
                    result = subprocess.run(
                        ["ansible-playbook", "--syntax-check", playbook],
                        capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        print(f"  {Colors.RED}❌ Syntax error in {playbook}{Colors.NC}")
                        print(f"  {result.stderr}")
                        return False
            
            return True
        except Exception as e:
            print(f"  {Colors.RED}❌ Ansible syntax check failed: {str(e)}{Colors.NC}")
            return False
    
    def test_simplified_structure(self) -> bool:
        """Test that the simplified structure is correct"""
        try:
            # Check required directories
            required_dirs = [
                "cloudy/playbooks/recipes/core",
                "cloudy/playbooks/recipes/cache", 
                "cloudy/playbooks/recipes/db",
                "cloudy/playbooks/recipes/www",
                "cloudy/playbooks/recipes/lb",
                "cloudy/playbooks/recipes/vpn",
                "cloudy/inventory",
                "cloudy/tasks",
                "cloudy/templates"
            ]
            
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    print(f"  {Colors.RED}❌ Missing required directory: {dir_path}{Colors.NC}")
                    return False
            
            # Check core recipes exist
            core_recipes = [
                "cloudy/playbooks/recipes/core/security.yml",
                "cloudy/playbooks/recipes/core/base.yml"
            ]
            
            for recipe in core_recipes:
                if not os.path.exists(recipe):
                    print(f"  {Colors.RED}❌ Missing core recipe: {recipe}{Colors.NC}")
                    return False
            
            # Check inventory files
            inventory_files = ["cloudy/inventory/dev.yml", "cloudy/inventory/prod.yml"]
            for inv_file in inventory_files:
                if not os.path.exists(inv_file):
                    print(f"  {Colors.RED}❌ Missing inventory file: {inv_file}{Colors.NC}")
                    return False
            
            print(f"  {Colors.BLUE}Simplified structure: All required components present{Colors.NC}")
            return True
            
        except Exception as e:
            print(f"  {Colors.RED}❌ Structure check failed: {str(e)}{Colors.NC}")
            return False
    
    def run_all_tests(self):
        """Run all validation tests"""
        print(f"{Colors.BLUE}🧪 Running Ansible Cloudy Validation Suite (Simplified)...{Colors.NC}")
        print("=" * 60)
        
        # Run all tests
        self.run_test("Simplified Structure", self.test_simplified_structure)
        self.run_test("Task File Structure", self.test_task_files)
        self.run_test("Recipe Files", self.test_recipe_files)
        self.run_test("Inventory Files", self.test_inventory_files)
        self.run_test("Template Files", self.test_template_files)
        self.run_test("Recipe Dependencies", self.test_recipe_dependencies)
        self.run_test("Ansible Syntax", self.test_ansible_syntax)
        
        # Summary
        print("\n" + "=" * 60)
        print(f"{Colors.BLUE}🧪 Validation Summary:{Colors.NC}")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   {Colors.GREEN}Passed: {self.tests_passed}{Colors.NC}")
        print(f"   {Colors.RED}Failed: {self.tests_failed}{Colors.NC}")
        
        if self.errors:
            print(f"\n{Colors.RED}Errors encountered:{Colors.NC}")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.tests_failed == 0:
            print(f"\n{Colors.GREEN}🎉 All validations passed!{Colors.NC}")
            print(f"{Colors.GREEN}✅ Ansible Cloudy is ready for deployment{Colors.NC}")
            return True
        else:
            print(f"\n{Colors.RED}❌ Some validations failed.{Colors.NC}")
            return False

def main():
    """Main entry point"""
    if not os.path.exists("cloudy/ansible.cfg"):
        print(f"{Colors.RED}❌ Must be run from the project root directory (ansible-cloudy/){Colors.NC}")
        sys.exit(1)
    
    validator = CloudyValidator()
    success = validator.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()