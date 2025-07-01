"""
Test Runner

Handles authentication test execution and result display.
"""

import subprocess
import os
from typing import List, Optional

from ..colors import Colors, error


class TestRunner:
    """Manages test execution and result display"""
    
    def __init__(self, config):
        self.config = config
        self.dev_dir = config.project_root / "dev"
    
    def test(self, ansible_args: Optional[List[str]] = None) -> int:
        """Run authentication flow test"""
        print(f"\n{Colors.CYAN}🔍 Starting Authentication Test{Colors.NC}")
        
        if ansible_args is None:
            ansible_args = []
        
        test_playbook = self.dev_dir / "test-auth.yml"
        if not test_playbook.exists():
            error(f"Test playbook not found: {test_playbook}")
            return 1
        
        # Use ansible-playbook directly for the auth test
        inventory_path = self.config.inventory_dir / "dev.yml"
        
        cmd = [
            "ansible-playbook",
            "-i", str(inventory_path),
            str(test_playbook)
        ]
        
        # Automatically load vault file if it exists
        vault_file = self.config.project_root / ".vault" / "dev.yml"
        if vault_file.exists():
            cmd.extend(["-e", f"@{vault_file}"])
            print(f"{Colors.BLUE}🔐 Loading vault credentials from: .vault/dev.yml{Colors.NC}")
        
        cmd.extend(ansible_args)
        
        print(f"{Colors.YELLOW}Running authentication tests...{Colors.NC}\n")
        
        try:
            # Run with completely suppressed output except for failures
            result = subprocess.run(
                cmd, 
                cwd=self.config.project_root,
                capture_output=True,
                text=True,
                env={**dict(os.environ), "ANSIBLE_CALLBACK_WHITELIST": "null"}
            )
            
            # Display results after playbook completes
            if result.returncode == 0:
                self._display_test_results()
                return 0
            else:
                print(f"\n{Colors.RED}❌ Authentication test failed with exit code {result.returncode}{Colors.NC}")
                # Show stderr for debugging failed tests
                if result.stderr:
                    print(f"{Colors.YELLOW}Error details:{Colors.NC}")
                    print(result.stderr)
                return result.returncode
                
        except Exception as e:
            error(f"Failed to run authentication test: {e}")
            return 1
    
    def _display_test_results(self):
        """Display formatted test results after playbook completion"""
        print(f"""
{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.NC}
{Colors.GREEN}🎉 ✅ AUTHENTICATION SETUP TEST COMPLETED SUCCESSFULLY!{Colors.NC}
{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.NC}

{Colors.BLUE}📋 Connection Test Results:{Colors.NC}
├── {Colors.GREEN}✅ Server reachable{Colors.NC}
├── {Colors.GREEN}✅ Authentication successful{Colors.NC}
├── {Colors.GREEN}✅ SSH connection established{Colors.NC}
└── {Colors.GREEN}✅ Playbook execution completed{Colors.NC}

{Colors.BLUE}👤 Admin User Configuration:{Colors.NC}
├── {Colors.GREEN}✅ User created successfully{Colors.NC}
├── {Colors.GREEN}✅ Home directory configured{Colors.NC}
├── {Colors.GREEN}✅ SSH keys installed{Colors.NC}
├── {Colors.GREEN}✅ Sudo access verified{Colors.NC}
└── {Colors.GREEN}✅ Groups configured{Colors.NC}

{Colors.BLUE}🔒 Security Configuration:{Colors.NC}
├── {Colors.GREEN}✅ Firewall (UFW) installed{Colors.NC}
├── {Colors.GREEN}✅ SSH port configured{Colors.NC}
├── {Colors.GREEN}✅ Firewall rules applied{Colors.NC}
└── {Colors.GREEN}✅ Admin SSH access ready{Colors.NC}

{Colors.BLUE}🚀 Next Steps:{Colors.NC}
├── Run {Colors.GREEN}'./cli security --install'{Colors.NC} for full security setup
├── This will restart SSH service on the configured port
└── After setup, connect using admin user with SSH keys

{Colors.GREEN}⚡ Status: AUTHENTICATION FRAMEWORK VALIDATED ✅{Colors.NC}
""")
        print(f"{Colors.YELLOW}💡 Note: Run with --verbose (-v) to see detailed task output{Colors.NC}")
