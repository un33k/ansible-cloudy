"""
Container Module Operations
Routes container commands to specific runtime handlers (Docker, Podman, etc.)
"""

from typing import Dict, Any, List
from pathlib import Path
from utils.colors import Colors, error, info
from operations.docker import DockerOperations


class ContainerOperations:
    """Main container operations router"""
    
    def __init__(self, config):
        self.config = config
        self.container_dir = config.base_dir / "container"
        
    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Route container operations to appropriate handler"""
        
        # For now, we only support Docker
        # In the future, this could route to Podman, containerd, etc.
        if args.service == "docker":
            docker_ops = DockerOperations(self.config)
            return docker_ops.handle_operation(args, ansible_args)
        else:
            error(f"Unknown container runtime: {args.service}")
            return 1
            
    def list_available_templates(self):
        """List available container templates"""
        templates_dir = self.container_dir / "templates"
        
        if not templates_dir.exists():
            info("No templates directory found")
            return
            
        print(f"{Colors.CYAN}Available Container Templates:{Colors.NC}")
        print()
        
        # List docker-compose templates
        compose_files = list(templates_dir.glob("*.yml")) + list(templates_dir.glob("*.yaml"))
        
        if compose_files:
            print(f"{Colors.BLUE}Docker Compose Stacks:{Colors.NC}")
            for template in compose_files:
                # Read first few lines to get description
                with open(template, 'r') as f:
                    lines = f.readlines()
                    description = ""
                    for line in lines[:5]:
                        if line.strip().startswith("#") and not line.startswith("#!"):
                            description = line.strip("# \n")
                            break
                
                rel_path = template.relative_to(self.config.base_dir)
                print(f"  {Colors.GREEN}{template.stem}{Colors.NC}")
                print(f"    Path: {rel_path}")
                if description:
                    print(f"    Description: {description}")
                print()
        else:
            print("  No templates found")
            
    def prepare_deployment(self, template_name: str) -> Path:
        """Prepare a deployment from template"""
        templates_dir = self.container_dir / "templates"
        deployments_dir = self.container_dir / "deployments"
        
        # Find template
        template_path = None
        for ext in ['.yml', '.yaml']:
            candidate = templates_dir / f"{template_name}{ext}"
            if candidate.exists():
                template_path = candidate
                break
                
        if not template_path:
            error(f"Template not found: {template_name}")
            return None
            
        # Create deployment directory
        deployment_dir = deployments_dir / template_name
        deployment_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy template and related files
        import shutil
        shutil.copy2(template_path, deployment_dir / "docker-compose.yml")
        
        # Copy any related files (like init scripts)
        related_files = {
            'n8n-portainer-stack': ['init-pgvector.sql', '.env.example'],
            'portainer-standalone': []
        }
        
        if template_name in related_files:
            for file in related_files[template_name]:
                src = templates_dir / file
                if src.exists():
                    shutil.copy2(src, deployment_dir / file)
                    
        info(f"Deployment prepared at: {deployment_dir}")
        return deployment_dir / "docker-compose.yml"