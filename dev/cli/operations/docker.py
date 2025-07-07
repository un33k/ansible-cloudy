"""
Docker Operations for CLI
Handles Docker container runtime installation and management
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from utils.colors import Colors, error
from operations.base_service import BaseServiceOperations


class DockerOperations(BaseServiceOperations):
    """Handle Docker operations - installation, configuration, and container management"""

    def __init__(self, config):
        super().__init__(config, "docker")

    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract Docker-specific arguments from command line"""
        docker_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            # Docker installation arguments
            if arg == "--add-user":
                if i + 1 < len(ansible_args):
                    docker_args['add_user'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--add-user requires a username")
            elif arg == "--configure":
                docker_args['configure'] = True
                i += 1
            elif arg == "--deploy-compose":
                if i + 1 < len(ansible_args):
                    docker_args['deploy_compose'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--deploy-compose requires a file path")
            elif arg == "--compose-name":
                if i + 1 < len(ansible_args):
                    docker_args['compose_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--compose-name requires a stack name")
            else:
                i += 1
        
        return docker_args

    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        return {
            '--add-user': 'docker_user',
            '--configure': 'docker_configure_daemon=true',
            '--deploy-compose': 'docker_compose_file',
            '--compose-name': 'docker_compose_project_name'
        }

    def _get_operation_flags(self) -> List[str]:
        """Get list of operation flags for Docker"""
        return [
            '--add-user', '--configure', '--deploy-compose'
        ]

    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which Docker operation is requested"""
        operations = [
            '--add-user', '--configure', '--deploy-compose'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                return arg[2:]  # Remove -- prefix
        
        return None

    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], docker_args: Dict[str, Any]) -> int:
        """Handle granular Docker operations"""
        
        # Map operations to task files
        operation_map = {
            'add-user': 'add-user.yml',
            'configure': 'configure.yml',
            'deploy-compose': 'deploy-compose.yml'
        }
        
        task_file = operation_map.get(operation)
        if not task_file:
            error(f"Unknown Docker operation: {operation}")
        
        # Build task path (Docker tasks are in sys/docker/)
        task_path = self.config.base_dir / "cloudy" / "tasks" / "sys" / "docker" / task_file
        
        # For deploy-compose, check if it's a template name
        if operation == 'deploy-compose':
            compose_path = docker_args.get('deploy_compose', '')
            
            # Check if it's a template name (no path separators)
            if compose_path and '/' not in compose_path and '\\' not in compose_path:
                # Try to prepare deployment from template
                from operations.container.operations import ContainerOperations
                container_ops = ContainerOperations(self.config)
                deployment_path = container_ops.prepare_deployment(compose_path)
                if deployment_path:
                    docker_args['deploy_compose'] = str(deployment_path)
                    print(f"{Colors.GREEN}Using template: {compose_path}{Colors.NC}")
            
            task_path = self._create_compose_task(docker_args)
        
        if not task_path.exists():
            error(f"Task file not found: {task_path}")
        
        # Build extra vars
        extra_vars = []
        
        if operation == 'add-user':
            if 'add_user' not in docker_args:
                error("--add-user requires a username")
            extra_vars.extend(["-e", f"docker_user={docker_args['add_user']}"])
            
        elif operation == 'deploy-compose':
            if 'deploy_compose' not in docker_args:
                error("--deploy-compose requires a file path")
            extra_vars.extend(["-e", f"docker_compose_file={docker_args['deploy_compose']}"])
            if 'compose_name' in docker_args:
                extra_vars.extend(["-e", f"docker_compose_project_name={docker_args['compose_name']}"])
        
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

    def _create_compose_task(self, docker_args: Dict[str, Any]) -> Path:
        """Create a temporary task file for docker-compose deployment"""
        # For now, we'll assume the task exists. In a full implementation,
        # this would create a dynamic task file for docker-compose deployment
        return self.config.base_dir / "cloudy" / "tasks" / "sys" / "docker" / "deploy-compose.yml"

    def _show_installation_help(self):
        """Show Docker installation parameters"""
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --install{Colors.NC}                    Install Docker CE")
        print(f"  {Colors.GREEN}cli docker --install --configure{Colors.NC}        Install and configure daemon")
        print()

    def _show_granular_operations_help(self):
        """Show Docker granular operations help"""
        print(f"{Colors.BLUE}User Management:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --add-user username{Colors.NC}         Add user to docker group")
        print()
        print(f"{Colors.BLUE}Configuration:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --configure{Colors.NC}                 Configure Docker daemon")
        print()
        print(f"{Colors.BLUE}Container Deployment:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --deploy-compose /path/file{Colors.NC} Deploy docker-compose stack")
        print(f"  {Colors.GREEN}cli docker --deploy-compose /path/file --compose-name mystack{Colors.NC}")
        print()
        print(f"{Colors.BLUE}Template Deployment:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --deploy-compose n8n-portainer-stack{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --deploy-compose portainer-standalone{Colors.NC}")
        print()
        print(f"{Colors.BLUE}Available Templates:{Colors.NC}")
        print(f"  • n8n-portainer-stack - Complete n8n workflow automation with Portainer")
        print(f"  • portainer-standalone - Docker management UI")
        print()
        print(f"{Colors.BLUE}Note:{Colors.NC} For container management, use Portainer after installation")
        print()