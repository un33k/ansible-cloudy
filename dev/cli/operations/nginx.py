"""
Nginx Operations for CLI
Handles Nginx load balancer installation and configuration
"""

from typing import Dict, Any, List, Optional
from utils.colors import Colors, error
from operations.base_service import BaseServiceOperations


class NginxOperations(BaseServiceOperations):
    """Handle Nginx operations - installation and configuration"""

    def __init__(self, config):
        super().__init__(config, "nginx")

    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract Nginx-specific arguments from command line"""
        nginx_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            # Nginx installation arguments
            if arg == "--domain":
                if i + 1 < len(ansible_args):
                    nginx_args['domain'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--domain requires a value")
            elif arg == "--ssl":
                nginx_args['ssl'] = True
                i += 1
            elif arg == "--protocol":
                if i + 1 < len(ansible_args):
                    nginx_args['protocol'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--protocol requires a value (http/https)")
            elif arg == "--interface":
                if i + 1 < len(ansible_args):
                    nginx_args['interface'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--interface requires a value")
            elif arg == "--backends":
                if i + 1 < len(ansible_args):
                    nginx_args['backends'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--backends requires a value")
            elif arg == "--cert-dir":
                if i + 1 < len(ansible_args):
                    nginx_args['cert_dir'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--cert-dir requires a value")
            elif arg == "--no-firewall":
                nginx_args['no_firewall'] = True
                i += 1
            
            # Granular operation arguments
            elif arg == "--add-domain":
                nginx_args['operation'] = 'add-domain'
                if i + 1 < len(ansible_args):
                    nginx_args['domain'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--add-domain requires a domain name")
            elif arg == "--setup-ssl":
                nginx_args['operation'] = 'setup-ssl'
                if i + 1 < len(ansible_args):
                    nginx_args['domain'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--setup-ssl requires a domain name")
            elif arg == "--reload":
                nginx_args['operation'] = 'reload'
                i += 1
            elif arg == "--test-config":
                nginx_args['operation'] = 'test-config'
                i += 1
            else:
                i += 1
        
        return nginx_args

    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        return {
            '--domain': 'domain_name',
            '--ssl': 'setup_ssl=true',
            '--protocol': 'protocol',
            '--interface': 'interface',
            '--backends': 'upstream_servers',
            '--cert-dir': 'ssl_cert_dir',
            '--no-firewall': 'setup_firewall=false'
        }

    def _get_operation_flags(self) -> List[str]:
        """Get list of operation flags for Nginx"""
        return [
            '--add-domain', '--setup-ssl', '--reload', '--test-config'
        ]

    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which Nginx operation is requested"""
        operations = [
            '--add-domain', '--setup-ssl', '--reload', '--test-config'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                return arg[2:]  # Remove -- prefix
        
        return None

    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], nginx_args: Dict[str, Any]) -> int:
        """Handle granular Nginx operations"""
        
        # Map operations to task files
        operation_map = {
            'add-domain': 'setup-domain.yml',
            'setup-ssl': 'copy-ssl.yml',
            'reload': 'install.yml',  # Reload is handled by install task
            'test-config': 'install.yml'  # Test config runs nginx -t
        }
        
        task_file = operation_map.get(operation)
        if not task_file:
            error(f"Unknown Nginx operation: {operation}")
        
        # Build task path (Nginx tasks are in web/nginx/)
        task_path = self.config.base_dir / "cloudy" / "tasks" / "web" / "nginx" / task_file
        
        if not task_path.exists():
            error(f"Task file not found: {task_path}")
        
        # Build extra vars
        extra_vars = []
        
        if operation == 'add-domain':
            if 'domain' not in nginx_args:
                error("--add-domain requires a domain name")
            extra_vars.extend(["-e", f"domain_name={nginx_args['domain']}"])
            
        elif operation == 'setup-ssl':
            if 'domain' not in nginx_args:
                error("--setup-ssl requires a domain name")
            extra_vars.extend(["-e", f"domain_name={nginx_args['domain']}"])
            extra_vars.extend(["-e", "setup_ssl=true"])
            
        elif operation in ['reload', 'test-config']:
            # These operations just run the install task with current config
            if operation == 'test-config':
                extra_vars.extend(["-e", "nginx_test_only=true"])
        
        # Add verbose flag if requested
        if hasattr(args, 'verbose') and args.verbose:
            extra_vars.insert(0, "-v")
        
        # Execute task
        inventory_path = self.inventory_manager.get_inventory_path(args.prod)
        return self.runner.run_task(
            task_path=str(task_path),
            inventory_path=inventory_path,
            extra_args=extra_vars,
            dry_run=args.check,
        )

    def _show_installation_help(self):
        """Show Nginx installation parameters"""
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}cli nginx --install{Colors.NC}                    Install Nginx load balancer")
        print(f"  {Colors.GREEN}cli nginx --install --domain example.com{Colors.NC} Install with domain")
        print(f"  {Colors.GREEN}cli nginx --install --ssl{Colors.NC}             Install with SSL enabled")
        print(f"  {Colors.GREEN}cli nginx --install --protocol https{Colors.NC}  Install with HTTPS protocol")
        print(f"  {Colors.GREEN}cli nginx --install --backends '192.168.1.10:8080,192.168.1.11:8080'{Colors.NC} With backend servers")
        print()

    def _show_granular_operations_help(self):
        """Show Nginx granular operations help"""
        print(f"{Colors.BLUE}Configuration Operations:{Colors.NC}")
        print(f"  {Colors.GREEN}cli nginx --add-domain example.com{Colors.NC}    Add new domain configuration")
        print(f"  {Colors.GREEN}cli nginx --setup-ssl example.com{Colors.NC}     Setup SSL for domain")
        print(f"  {Colors.GREEN}cli nginx --reload{Colors.NC}                   Reload Nginx configuration")
        print(f"  {Colors.GREEN}cli nginx --test-config{Colors.NC}              Test Nginx configuration")
        print()
