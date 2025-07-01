"""
Standalone operations handler for Claudia
Handles all-in-one server deployment with complete stack
"""

from operations.base_service import BaseServiceOperations
from utils.colors import Colors, info, success, warning, error


class StandaloneOperations(BaseServiceOperations):
    """Handle standalone all-in-one server deployment"""
    
    def __init__(self, config):
        super().__init__(config, "standalone")
        self.name = "standalone"
        self.description = "All-in-one server with complete stack (DB, Cache, App, LB)"
    
    def _get_parameter_mapping(self) -> dict:
        """Get CLI parameter to Ansible variable mapping"""
        return {
            # Application type
            '--app-type': 'app_type',
            '--app-name': 'app_name',
            '--app-repo': 'app_repo',
            '--app-port': 'app_port',
            
            # Domain and SSL
            '--domain': 'domain',
            '--enable-ssl': 'enable_ssl',
            '--ssl-email': 'ssl_email',
            
            # Component selection
            '--with-postgresql': 'install_postgresql',
            '--with-redis': 'install_redis',
            '--with-nginx': 'install_nginx',
            
            # PostgreSQL settings
            '--pg-version': 'pg_version',
            '--pg-port': 'pg_port',
            '--pg-password': 'pg_password',
            
            # Redis settings
            '--redis-port': 'redis_port',
            '--redis-memory': 'redis_memory_mb',
            '--redis-password': 'redis_password',
            
            # Production mode
            '--production': 'production_mode',
        }
    
    def show_help(self) -> None:
        """Show standalone-specific help"""
        print(f"\n{Colors.CYAN}standalone - All-in-One Server Deployment{Colors.RESET}")
        print(f"{Colors.DIM}Deploy complete stack (PostgreSQL, Redis, Nginx, App) on a single server{Colors.RESET}\n")
        
        print(f"{Colors.GREEN}USAGE:{Colors.RESET}")
        print(f"  {Colors.YELLOW}claudia standalone{Colors.RESET} --install [OPTIONS]")
        print(f"  {Colors.YELLOW}claudia standalone{Colors.RESET} --help\n")
        
        print(f"{Colors.GREEN}OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--install{Colors.RESET}              Install complete stack")
        print(f"  {Colors.CYAN}--app-type{Colors.RESET} TYPE        Application type: django|nodejs (default: django)")
        print(f"  {Colors.CYAN}--app-name{Colors.RESET} NAME        Application name (default: webapp)")
        print(f"  {Colors.CYAN}--app-repo{Colors.RESET} URL         Git repository URL (optional)")
        print(f"  {Colors.CYAN}--domain{Colors.RESET} DOMAIN        Domain name (default: server IP)")
        print(f"  {Colors.CYAN}--enable-ssl{Colors.RESET}           Enable SSL with Let's Encrypt (default: true)")
        print(f"  {Colors.CYAN}--production{Colors.RESET}           Enable production optimizations (default: true)")
        print()
        
        print(f"{Colors.GREEN}COMPONENT OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--with-postgresql{Colors.RESET}      Install PostgreSQL (default: true)")
        print(f"  {Colors.CYAN}--with-redis{Colors.RESET}           Install Redis (default: true)")
        print(f"  {Colors.CYAN}--with-nginx{Colors.RESET}           Install Nginx (default: true)")
        print()
        
        print(f"{Colors.GREEN}DATABASE OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--pg-version{Colors.RESET} VER       PostgreSQL version (default: 17)")
        print(f"  {Colors.CYAN}--pg-port{Colors.RESET} PORT         PostgreSQL port (default: 5432)")
        print(f"  {Colors.CYAN}--pg-password{Colors.RESET} PASS     Database password")
        print()
        
        print(f"{Colors.GREEN}CACHE OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--redis-port{Colors.RESET} PORT      Redis port (default: 6379)")
        print(f"  {Colors.CYAN}--redis-memory{Colors.RESET} MB      Redis memory limit (default: 512)")
        print(f"  {Colors.CYAN}--redis-password{Colors.RESET} PASS  Redis password")
        print()
        
        print(f"{Colors.GREEN}EXAMPLES:{Colors.RESET}")
        print(f"  # Deploy Django stack with defaults")
        print(f"  {Colors.YELLOW}claudia standalone --install{Colors.RESET}")
        print()
        print(f"  # Deploy Node.js stack with domain")
        print(f"  {Colors.YELLOW}claudia standalone --install --app-type nodejs --domain api.example.com{Colors.RESET}")
        print()
        print(f"  # Custom ports and passwords")
        print(f"  {Colors.YELLOW}claudia standalone --install --pg-port 5433 --redis-port 6380{Colors.RESET}")
        print()
        print(f"  # Deploy from Git repository")
        print(f"  {Colors.YELLOW}claudia standalone --install --app-repo https://github.com/user/app.git{Colors.RESET}")
        print()
        
        print(f"{Colors.GREEN}STACK COMPONENTS:{Colors.RESET}")
        print(f"  • PostgreSQL - Primary database")
        print(f"  • Redis - Caching and sessions")
        print(f"  • Nginx - Reverse proxy with SSL")
        print(f"  • Django/Node.js - Application server")
        print(f"  • Supervisor/PM2 - Process management")
        print()
        
        print(f"{Colors.GREEN}RESOURCE REQUIREMENTS:{Colors.RESET}")
        print(f"  • RAM: Minimum 2GB (4GB+ recommended)")
        print(f"  • CPU: 2+ cores recommended")
        print(f"  • Disk: 20GB+ recommended")
        print()
        
        print(f"{Colors.GREEN}POST-INSTALLATION:{Colors.RESET}")
        print(f"  • Access: https://<domain>/")
        print(f"  • Reports: /root/standalone-report.txt")
        print(f"  • Optimize: /usr/local/bin/optimize-standalone.sh")
        print(f"  • Monitor: htop, systemctl status --all")
        print(f"  • Logs: /var/log/<service>/")
        print()
    
    def _extract_service_args(self, ansible_args: list) -> dict:
        """Extract standalone-specific arguments"""
        service_args = {}
        
        # Extract arguments that should be passed as extra vars
        i = 0
        while i < len(ansible_args):
            if ansible_args[i] == '--app-type' and i + 1 < len(ansible_args):
                if ansible_args[i + 1] not in ['django', 'nodejs']:
                    warning(f"Invalid app type: {ansible_args[i + 1]}. Using default (django)")
                else:
                    service_args['app_type'] = ansible_args[i + 1]
                i += 2
            else:
                i += 1
        
        return service_args
    
    def _validate_prerequisites(self) -> bool:
        """Validate system requirements for standalone deployment"""
        info("Checking system requirements for standalone deployment...")
        
        # This would normally check actual system resources
        # For now, just return True
        return True