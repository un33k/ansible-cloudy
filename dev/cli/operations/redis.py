"""
Redis Operations for CLI
Handles Redis cache server installation and configuration
"""

from typing import Dict, Any, List, Optional
from utils.colors import Colors, error
from operations.base_service import BaseServiceOperations


class RedisOperations(BaseServiceOperations):
    """Handle Redis operations - installation and configuration"""

    def __init__(self, config):
        super().__init__(config, "redis")

    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract Redis-specific arguments from command line"""
        redis_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            # Redis installation arguments
            if arg == "--port":
                if i + 1 < len(ansible_args):
                    redis_args['port'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--port requires a value")
            elif arg == "--memory":
                if i + 1 < len(ansible_args):
                    redis_args['memory'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--memory requires a value")
            elif arg == "--password":
                if i + 1 < len(ansible_args):
                    redis_args['password'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--password requires a value")
            elif arg == "--interface":
                if i + 1 < len(ansible_args):
                    redis_args['interface'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--interface requires a value")
            elif arg == "--no-firewall":
                redis_args['no_firewall'] = True
                i += 1
            
            # Granular operation arguments
            elif arg == "--configure-port":
                redis_args['operation'] = 'configure-port'
                if i + 1 < len(ansible_args):
                    redis_args['port'] = ansible_args[i + 1]
                    i += 2
                else:
                    redis_args['port'] = '6379'  # Default port
                    i += 1
            elif arg == "--set-password":
                redis_args['operation'] = 'set-password'
                if i + 1 < len(ansible_args):
                    redis_args['password'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--set-password requires a password value")
            elif arg == "--configure-memory":
                redis_args['operation'] = 'configure-memory'
                if i + 1 < len(ansible_args):
                    redis_args['memory'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--configure-memory requires a memory value")
            elif arg == "--restart":
                redis_args['operation'] = 'restart'
                i += 1
            else:
                i += 1
        
        return redis_args

    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        return {
            '--port': 'redis_port',
            '--memory': 'redis_memory_mb',
            '--password': 'redis_password',
            '--interface': 'redis_interface',
            '--no-firewall': 'setup_firewall=false'
        }

    def _get_operation_flags(self) -> List[str]:
        """Get list of operation flags for Redis"""
        return [
            '--configure-port', '--set-password', '--configure-memory', '--restart'
        ]

    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which Redis operation is requested"""
        operations = [
            '--configure-port', '--set-password', '--configure-memory', '--restart'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                return arg[2:]  # Remove -- prefix
        
        return None

    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], redis_args: Dict[str, Any]) -> int:
        """Handle granular Redis operations"""
        
        # Map operations to task files
        operation_map = {
            'configure-port': 'configure-port.yml',
            'set-password': 'configure-password.yml', 
            'configure-memory': 'configure-memory.yml',
            'restart': 'install.yml'  # Restart is handled by install task
        }
        
        task_file = operation_map.get(operation)
        if not task_file:
            error(f"Unknown Redis operation: {operation}")
        
        # Build task path (Redis tasks are in sys/redis/)
        task_path = self.config.base_dir / "cloudy" / "tasks" / "sys" / "redis" / task_file
        
        if not task_path.exists():
            error(f"Task file not found: {task_path}")
        
        # Build extra vars
        extra_vars = []
        
        if operation == 'configure-port':
            port = redis_args.get('port', '6379')
            extra_vars.extend(["-e", f"redis_port={port}"])
            
        elif operation == 'set-password':
            if 'password' not in redis_args:
                error("--set-password requires a password")
            extra_vars.extend(["-e", f"redis_password={redis_args['password']}"])
            
        elif operation == 'configure-memory':
            if 'memory' not in redis_args:
                error("--configure-memory requires a memory value")
            extra_vars.extend(["-e", f"redis_memory_mb={redis_args['memory']}"])
            
        elif operation == 'restart':
            # Restart just runs the install task with current config
            pass
        
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
        """Show Redis installation parameters"""
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}cli redis --install{Colors.NC}                    Install Redis server")
        print(f"  {Colors.GREEN}cli redis --install --port 6380{Colors.NC}       Install on custom port")
        print(f"  {Colors.GREEN}cli redis --install --memory 512{Colors.NC}      Install with 512MB memory")
        print(f"  {Colors.GREEN}cli redis --install --password secret{Colors.NC} Install with password")
        print(f"  {Colors.GREEN}cli redis --install --interface 127.0.0.1{Colors.NC} Bind to specific interface")
        print()

    def _show_granular_operations_help(self):
        """Show Redis granular operations help"""
        print(f"{Colors.BLUE}Configuration Operations:{Colors.NC}")
        print(f"  {Colors.GREEN}cli redis --configure-port 6380{Colors.NC}       Change Redis port")
        print(f"  {Colors.GREEN}cli redis --set-password mypass{Colors.NC}       Set Redis password")
        print(f"  {Colors.GREEN}cli redis --configure-memory 1024{Colors.NC}     Set memory limit (MB)")
        print(f"  {Colors.GREEN}cli redis --restart{Colors.NC}                   Restart Redis service")
        print()
