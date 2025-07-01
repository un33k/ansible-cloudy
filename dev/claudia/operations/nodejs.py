"""
Node.js operations handler for Claudia
Handles Node.js application deployment with PM2
"""

from operations.base_service import BaseServiceOperations
from utils.colors import Colors, info, success, warning


class NodeJSOperations(BaseServiceOperations):
    """Handle Node.js application deployment operations"""
    
    def __init__(self, config):
        super().__init__(config, "nodejs")
        self.name = "nodejs"
        self.description = "Node.js web application with PM2 process manager"
    
    def _get_parameter_mapping(self) -> dict:
        """Get CLI parameter to Ansible variable mapping"""
        return {
            # Node.js configuration
            '--node-version': 'node_version',
            '--npm-registry': 'npm_registry',
            
            # Application configuration
            '--app-name': 'app_name',
            '--app-repo': 'app_repo',
            '--app-branch': 'app_branch',
            '--app-path': 'app_path',
            '--app-port': 'app_port',
            '--app-env': 'app_env',
            
            # PM2 configuration
            '--pm2-instances': 'pm2_instances',
            '--pm2-mode': 'pm2_exec_mode',
            '--pm2-memory': 'pm2_memory_limit',
            
            # Nginx configuration
            '--with-nginx': 'setup_nginx',
            '--domain': 'nginx_domain',
            '--ssl': 'nginx_ssl_enabled',
            
            # Environment variables
            '--env-vars': 'app_env_vars',
        }
    
    def show_help(self) -> None:
        """Show Node.js-specific help"""
        print(f"\n{Colors.CYAN}nodejs - Node.js Web Application Server{Colors.RESET}")
        print(f"{Colors.DIM}Deploy Node.js applications with PM2 process manager and optional Nginx{Colors.RESET}\n")
        
        print(f"{Colors.GREEN}USAGE:{Colors.RESET}")
        print(f"  {Colors.YELLOW}claudia nodejs{Colors.RESET} --install [OPTIONS]")
        print(f"  {Colors.YELLOW}claudia nodejs{Colors.RESET} --help\n")
        
        print(f"{Colors.GREEN}OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--install{Colors.RESET}              Install Node.js and deploy application")
        print(f"  {Colors.CYAN}--node-version{Colors.RESET} VER     Node.js version (default: 18)")
        print(f"  {Colors.CYAN}--app-name{Colors.RESET} NAME        Application name (default: nodejs-app)")
        print(f"  {Colors.CYAN}--app-repo{Colors.RESET} URL         Git repository URL")
        print(f"  {Colors.CYAN}--app-branch{Colors.RESET} BRANCH    Git branch (default: main)")
        print(f"  {Colors.CYAN}--app-port{Colors.RESET} PORT        Application port (default: 3000)")
        print(f"  {Colors.CYAN}--app-env{Colors.RESET} ENV          Environment: development|production (default: production)")
        print()
        
        print(f"{Colors.GREEN}PM2 OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--pm2-instances{Colors.RESET} NUM    Number of instances or 'max' (default: max)")
        print(f"  {Colors.CYAN}--pm2-mode{Colors.RESET} MODE        Execution mode: cluster|fork (default: cluster)")
        print(f"  {Colors.CYAN}--pm2-memory{Colors.RESET} SIZE      Memory limit per instance (default: 2G)")
        print()
        
        print(f"{Colors.GREEN}NGINX OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--with-nginx{Colors.RESET}           Setup Nginx reverse proxy (default: true)")
        print(f"  {Colors.CYAN}--domain{Colors.RESET} DOMAIN        Domain name for Nginx")
        print(f"  {Colors.CYAN}--ssl{Colors.RESET}                  Enable SSL/HTTPS")
        print()
        
        print(f"{Colors.GREEN}ENVIRONMENT OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--dev{Colors.RESET}                  Use development environment")
        print(f"  {Colors.CYAN}--prod{Colors.RESET}                 Use production environment (default)")
        print(f"  {Colors.CYAN}--env-vars{Colors.RESET} JSON        Additional environment variables as JSON")
        print()
        
        print(f"{Colors.GREEN}EXAMPLES:{Colors.RESET}")
        print(f"  # Install with sample application")
        print(f"  {Colors.YELLOW}claudia nodejs --install{Colors.RESET}")
        print()
        print(f"  # Deploy from Git repository")
        print(f"  {Colors.YELLOW}claudia nodejs --install --app-repo https://github.com/user/app.git{Colors.RESET}")
        print()
        print(f"  # Production deploy with domain and SSL")
        print(f"  {Colors.YELLOW}claudia nodejs --install --prod --domain api.example.com --ssl{Colors.RESET}")
        print()
        print(f"  # Custom configuration")
        print(f"  {Colors.YELLOW}claudia nodejs --install --node-version 20 --pm2-instances 4 --app-port 8080{Colors.RESET}")
        print()
        
        print(f"{Colors.GREEN}PM2 FEATURES:{Colors.RESET}")
        print(f"  • Cluster mode with load balancing")
        print(f"  • Auto-restart on crashes")
        print(f"  • Zero-downtime reloads")
        print(f"  • Built-in log rotation")
        print(f"  • Memory limit monitoring")
        print()
        
        print(f"{Colors.GREEN}POST-INSTALLATION:{Colors.RESET}")
        print(f"  • View status: pm2 list")
        print(f"  • View logs: pm2 logs <app-name>")
        print(f"  • Monitor: pm2 monit")
        print(f"  • Restart: pm2 restart <app-name>")
        print(f"  • Reload: pm2 reload <app-name>")
        print()
    
    def _extract_service_args(self, ansible_args: list) -> dict:
        """Extract Node.js-specific arguments"""
        service_args = {}
        
        # Extract arguments that should be passed as extra vars
        i = 0
        while i < len(ansible_args):
            if ansible_args[i] == '--env-vars' and i + 1 < len(ansible_args):
                # Parse JSON environment variables
                try:
                    import json
                    env_vars = json.loads(ansible_args[i + 1])
                    service_args['app_env_vars'] = env_vars
                except:
                    warning(f"Invalid JSON for --env-vars: {ansible_args[i + 1]}")
                i += 2
            elif ansible_args[i] == '--pm2-mode' and i + 1 < len(ansible_args):
                if ansible_args[i + 1] not in ['cluster', 'fork']:
                    warning(f"Invalid PM2 mode: {ansible_args[i + 1]}. Using default (cluster)")
                else:
                    service_args['pm2_exec_mode'] = ansible_args[i + 1]
                i += 2
            else:
                i += 1
        
        return service_args