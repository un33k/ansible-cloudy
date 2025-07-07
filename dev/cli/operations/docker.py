"""
Docker Operations for CLI
Handles Docker installation and container management
"""

from typing import Dict, Any, List, Optional
from utils.colors import Colors, error
from operations.base_service import BaseServiceOperations


class DockerOperations(BaseServiceOperations):
    """Handle Docker operations - installation and container deployment"""

    def __init__(self, config):
        super().__init__(config, "docker")

    def _extract_service_args(self, ansible_args: List[str]) -> Dict[str, Any]:
        """Extract Docker-specific arguments from command line"""
        docker_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            # Docker installation arguments
            if arg == "--compose":
                if i + 1 < len(ansible_args):
                    docker_args['compose'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--compose requires a service name (e.g., portainer)")
            elif arg == "--add-user":
                if i + 1 < len(ansible_args):
                    docker_args['add_user'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--add-user requires a username")
            elif arg == "--network":
                if i + 1 < len(ansible_args):
                    docker_args['network'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--network requires a network name")
            elif arg == "--docker-version":
                if i + 1 < len(ansible_args):
                    docker_args['docker_version'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--docker-version requires a version")
            elif arg == "--compose-version":
                if i + 1 < len(ansible_args):
                    docker_args['compose_version'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--compose-version requires a version")
            else:
                i += 1
        
        return docker_args

    def _get_parameter_mapping(self) -> Dict[str, str]:
        """Get mapping of CLI parameters to Ansible variables"""
        return {
            '--docker-version': 'docker_version',
            '--compose-version': 'docker_compose_version',
            '--network': 'docker_network_name'
        }

    def _get_operation_flags(self) -> List[str]:
        """Get list of operation flags for Docker"""
        return [
            '--add-user', '--compose'
        ]

    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which Docker operation is requested"""
        operations = [
            '--add-user', '--compose'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                return arg[2:]  # Remove -- prefix
        
        return None

    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route Docker operation to appropriate handler"""
        
        # Extract service-specific arguments
        service_args = self._extract_service_args(ansible_args)
        
        # Handle --compose flag specially
        if 'compose' in service_args:
            return self._handle_compose_deployment(args, ansible_args, service_args)
        
        # Otherwise use parent class logic
        return super().handle_operation(args, ansible_args)

    def _handle_compose_deployment(self, args, ansible_args: List[str], docker_args: Dict[str, Any]) -> int:
        """Handle container deployment via --compose flag"""
        
        service_to_deploy = docker_args.get('compose')
        
        # Validate service
        valid_services = ['portainer', 'nginx']
        if service_to_deploy not in valid_services:
            error(f"Unknown service '{service_to_deploy}'. Valid services: {', '.join(valid_services)}")
        
        # First ensure Docker is installed
        print(f"{Colors.CYAN}🐳 Ensuring Docker is installed...{Colors.NC}")
        
        # Get environment
        if hasattr(args, 'prod') and args.prod:
            environment = 'prod'
        elif hasattr(args, 'ci') and args.ci:
            environment = 'ci'
        else:
            environment = 'dev'
        
        # Execute Docker installation first
        docker_result = self.dependency_manager.execute_with_dependencies(
            service_name='docker',
            environment=environment,
            custom_inventory=getattr(args, 'inventory_path', None),
            extra_vars_file=getattr(args, 'extra_vars_file', None),
            extra_args=[],
            dry_run=args.check,
            target_host=getattr(args, 'target_host', None),
            skip_dependencies=True,
        )
        
        if docker_result != 0:
            error("Docker installation failed")
        
        # Deploy nginx if deploying an edge service
        if service_to_deploy == 'portainer':
            print(f"{Colors.CYAN}🔧 Deploying nginx container for edge access...{Colors.NC}")
            
            nginx_result = self.dependency_manager.execute_with_dependencies(
                service_name='nginx-docker',
                environment=environment,
                custom_inventory=getattr(args, 'inventory_path', None),
                extra_vars_file=getattr(args, 'extra_vars_file', None),
                extra_args=[],
                dry_run=args.check,
                target_host=getattr(args, 'target_host', None),
                skip_dependencies=True,
            )
            
            if nginx_result != 0:
                error("Nginx container deployment failed")
        
        # Deploy the requested service
        print(f"{Colors.CYAN}📦 Deploying {service_to_deploy} container...{Colors.NC}")
        
        service_result = self.dependency_manager.execute_with_dependencies(
            service_name=service_to_deploy,
            environment=environment,
            custom_inventory=getattr(args, 'inventory_path', None),
            extra_vars_file=getattr(args, 'extra_vars_file', None),
            extra_args=[],
            dry_run=args.check,
            target_host=getattr(args, 'target_host', None),
            skip_dependencies=True,
        )
        
        return service_result

    def _handle_granular_operation(self, operation: str, args, ansible_args: List[str], docker_args: Dict[str, Any]) -> int:
        """Handle granular Docker operations"""
        
        if operation == 'add-user':
            # Add user to docker group
            task_path = self.config.base_dir / "cloudy" / "tasks" / "sys" / "docker" / "add-user.yml"
            
            if not task_path.exists():
                error(f"Task file not found: {task_path}")
            
            # Build extra vars
            extra_vars = []
            
            if 'add_user' not in docker_args:
                error("--add-user requires a username")
            
            extra_vars.extend(["-e", f"username={docker_args['add_user']}"])
            
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
        
        else:
            error(f"Unknown Docker operation: {operation}")

    def _show_installation_help(self):
        """Show Docker installation parameters"""
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --install{Colors.NC}                    Install Docker + create networks")
        print(f"  {Colors.GREEN}cli docker --install --docker-version 24.0.7{Colors.NC} Install specific Docker version")
        print()

    def _show_granular_operations_help(self):
        """Show Docker granular operations help"""
        print(f"{Colors.BLUE}Container Deployment:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --compose portainer{Colors.NC}         Install docker, nginx, and portainer")
        print(f"  {Colors.GREEN}cli docker --compose nginx{Colors.NC}             Deploy nginx container (opens 80/443)")
        print()
        print(f"{Colors.BLUE}User Management:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --add-user username{Colors.NC}         Add user to docker group")
        print()