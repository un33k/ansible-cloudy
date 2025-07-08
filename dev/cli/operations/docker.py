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
        docker_args: Dict[str, Any] = {}
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
            elif arg == "--restart":
                if i + 1 < len(ansible_args):
                    docker_args['restart'] = ansible_args[i + 1]
                    i += 2
                else:
                    docker_args['restart'] = 'all'
                    i += 1
            elif arg == "--stop":
                if i + 1 < len(ansible_args):
                    docker_args['stop'] = ansible_args[i + 1]
                    i += 2
                else:
                    docker_args['stop'] = 'all'
                    i += 1
            elif arg == "--pull":
                if i + 1 < len(ansible_args):
                    docker_args['pull'] = ansible_args[i + 1]
                    i += 2
                else:
                    docker_args['pull'] = 'all'
                    i += 1
            elif arg == "--logs":
                if i + 1 < len(ansible_args):
                    docker_args['logs'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--logs requires a container name")
            elif arg == "--status":
                docker_args['status'] = True
                i += 1
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
            '--compose', '--restart', '--stop', '--pull', '--logs', '--status'
        ]

    def _detect_operation(self, ansible_args: List[str]) -> Optional[str]:
        """Detect which Docker operation is requested"""
        operations = [
            '--compose', '--restart', '--stop', '--pull', '--logs', '--status'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                return arg[2:]  # Remove -- prefix
        
        return None

    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route Docker operation to appropriate handler"""
        
        # Check if --compose was provided
        if hasattr(args, 'compose') and args.compose:
            # Show connection info
            self._show_connection_info(args)
            # Extract service args and handle compose deployment
            service_args = self._extract_service_args(ansible_args)
            service_args['compose'] = args.compose
            return self._handle_compose_deployment(args, ansible_args, service_args)
        
        # Check for maintenance operations
        maintenance_ops = ['restart', 'stop', 'pull', 'logs', 'status']
        for op in maintenance_ops:
            if hasattr(args, op):
                value = getattr(args, op)
                if value is not None:
                    # Show connection info
                    self._show_connection_info(args)
                    # Build service args with the operation value
                    service_args = {op: value}
                    return self._handle_maintenance_operation(op, args, ansible_args, service_args)
        
        # Let parent class handle the standard flow
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
        
        if operation == 'compose':
            return self._handle_compose_deployment(args, ansible_args, docker_args)
        elif operation in ['restart', 'stop', 'pull', 'logs', 'status']:
            return self._handle_maintenance_operation(operation, args, ansible_args, docker_args)
        else:
            error(f"Unknown Docker operation: {operation}")
    
    def _handle_maintenance_operation(self, operation: str, args, ansible_args: List[str], docker_args: Dict[str, Any]) -> int:
        """Handle Docker maintenance operations"""
        import tempfile
        inventory_path = self.inventory_manager.get_inventory_path(args.prod)
        
        # Get target container/service
        target = docker_args.get(operation, 'all')
        
        # For status, use the pre-built task
        if operation == 'status':
            task_path = self.config.base_dir / "cloudy" / "tasks" / "container" / "docker-status.yml"
            extra_vars = []
            if hasattr(args, 'verbose') and args.verbose:
                extra_vars.append('-v')
            
            return self.runner.run_task(
                task_path=str(task_path),
                inventory_path=inventory_path,
                extra_args=extra_vars,
                dry_run=False
            )
        
        # Create a temporary playbook for other operations
        playbook_content = f"""---
- name: Docker {operation} operation
  hosts: all
  become: true
  gather_facts: false
  tasks:
"""
        
        if operation == 'logs':
            # Show container logs
            if target == 'all':
                error("--logs requires a specific container name")
            playbook_content += f"""    - name: Show container logs for {target}
      shell: |
        echo "=== Logs for {target} (last 50 lines) ==="
        docker logs --tail 50 {target} 2>&1
      changed_when: false
"""
        
        elif operation == 'restart':
            # Restart containers
            if target == 'all':
                cmd = 'docker restart $(docker ps -q)'
                desc = 'all containers'
            else:
                cmd = f'docker restart {target}'
                desc = f'container {target}'
            
            playbook_content += f"""    - name: Restart {desc}
      shell: {cmd}
      register: restart_result
      
    - name: Show restart status
      debug:
        msg: "Restarted: {{{{ restart_result.stdout }}}}"
"""
        
        elif operation == 'stop':
            # Stop containers
            if target == 'all':
                cmd = 'docker stop $(docker ps -q)'
                desc = 'all containers'
            else:
                cmd = f'docker stop {target}'
                desc = f'container {target}'
            
            playbook_content += f"""    - name: Stop {desc}
      shell: {cmd}
      register: stop_result
      
    - name: Show stop status
      debug:
        msg: "Stopped: {{{{ stop_result.stdout }}}}"
"""
        
        elif operation == 'pull':
            # Pull latest images
            if target == 'all':
                playbook_content += """    - name: Pull latest images for all containers
      shell: |
        for img in $(docker ps --format {% raw %}"{{.Image}}"{% endraw %}); do 
          echo "Pulling $img..."
          docker pull $img
        done
      register: pull_result
      
    - name: Show pull status
      debug:
        msg: "{{ pull_result.stdout_lines }}"
"""
            else:
                playbook_content += f"""    - name: Pull image {target}
      shell: docker pull {target}
      register: pull_result
      
    - name: Show pull status
      debug:
        msg: "{{{{ pull_result.stdout_lines }}}}"
"""
        
        # Write temporary playbook
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(playbook_content)
            temp_playbook = f.name
        
        try:
            # Run the playbook
            extra_vars = []
            if hasattr(args, 'verbose') and args.verbose:
                extra_vars.append('-v')
            
            result = self.runner.run_task(
                task_path=temp_playbook,
                inventory_path=inventory_path,
                extra_args=extra_vars,
                dry_run=args.check if hasattr(args, 'check') else False
            )
            
            return result
        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_playbook):
                os.unlink(temp_playbook)

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
        print(f"{Colors.BLUE}Container Maintenance:{Colors.NC}")
        print(f"  {Colors.GREEN}cli docker --status{Colors.NC}                    Show all container status")
        print(f"  {Colors.GREEN}cli docker --restart [container]{Colors.NC}       Restart container(s) (default: all)")
        print(f"  {Colors.GREEN}cli docker --stop [container]{Colors.NC}          Stop container(s) (default: all)")
        print(f"  {Colors.GREEN}cli docker --pull [image]{Colors.NC}              Pull latest image(s) (default: all)")
        print(f"  {Colors.GREEN}cli docker --logs <container>{Colors.NC}          Show container logs (last 50 lines)")
        print()