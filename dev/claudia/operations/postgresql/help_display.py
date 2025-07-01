"""
PostgreSQL Help Display

Handles displaying help information for PostgreSQL operations.
"""

from utils.colors import Colors
from discovery.service_scanner import ServiceScanner


class PostgreSQLHelpDisplay:
    """Display help information for PostgreSQL operations"""
    
    def __init__(self, scanner: ServiceScanner):
        self.scanner = scanner
    
    def show_help(self) -> int:
        """Show PostgreSQL help with available operations"""
        
        print(f"{Colors.CYAN}📖 Help: PostgreSQL Operations{Colors.NC}")
        print("=" * 50)
        print()
        
        print(f"{Colors.BLUE}Description:{Colors.NC}")
        print("  PostgreSQL Database Server with PostGIS Support")
        print()
        
        print(f"{Colors.BLUE}Recipe Installation:{Colors.NC}")
        print(f"  {Colors.GREEN}cli psql --install{Colors.NC}                    Install PostgreSQL server")
        print(f"  {Colors.GREEN}cli psql --install --port 5544{Colors.NC}       Install on custom port")
        print(f"  {Colors.GREEN}cli psql --install --pgis{Colors.NC}            Install with PostGIS extension")
        print(f"  {Colors.GREEN}cli psql --install --port 5544 --pgis{Colors.NC} Install with custom port and PostGIS")
        print()
        
        print(f"{Colors.BLUE}User Management:{Colors.NC}")
        print(f"  {Colors.GREEN}cli psql --adduser foo --password 1234{Colors.NC}         Create user")
        print(f"  {Colors.GREEN}cli psql --delete-user foo{Colors.NC}                    Delete user")
        print(f"  {Colors.GREEN}cli psql --list-users{Colors.NC}                         List all users")
        print()
        
        print(f"{Colors.BLUE}Database Management:{Colors.NC}")
        print(f"  {Colors.GREEN}cli psql --adddb myapp{Colors.NC}                        Create database")
        print(f"  {Colors.GREEN}cli psql --adddb myapp --owner myuser{Colors.NC}         Create database with owner")
        print(f"  {Colors.GREEN}cli psql --delete-db oldapp{Colors.NC}                   Delete database")
        print(f"  {Colors.GREEN}cli psql --list-databases{Colors.NC}                     List all databases")
        print(f"  {Colors.GREEN}cli psql --dump-database myapp{Colors.NC}               Dump database to file")
        print()
        
        print(f"{Colors.BLUE}Advanced Operations:{Colors.NC}")
        print(f"  {Colors.GREEN}cli psql --change-password foo --password newpass{Colors.NC}  Change user password")
        print(f"  {Colors.GREEN}cli psql --grant-privileges foo --database myapp{Colors.NC}   Grant user privileges")
        print(f"  {Colors.GREEN}cli psql --install-postgis{Colors.NC}                    Install PostGIS extension")
        print(f"  {Colors.GREEN}cli psql --configure-port 5432{Colors.NC}               Configure PostgreSQL port")
        print(f"  {Colors.GREEN}cli psql --get-version{Colors.NC}                        Get installed PostgreSQL version")
        print(f"  {Colors.GREEN}cli psql --create-cluster mycluster{Colors.NC}          Create PostgreSQL cluster")
        print(f"  {Colors.GREEN}cli psql --install-client{Colors.NC}                    Install PostgreSQL client tools")
        print()
        
        print(f"{Colors.BLUE}Configuration Variables:{Colors.NC}")
        print(f"  {Colors.CYAN}postgresql_version{Colors.NC}     PostgreSQL version (default: 17)")
        print(f"  {Colors.CYAN}postgis_version{Colors.NC}        PostGIS version (default: 3)")
        print(f"  {Colors.CYAN}database_port{Colors.NC}          PostgreSQL port (default: 5432)")
        print(f"  {Colors.CYAN}setup_postgis{Colors.NC}          Enable PostGIS extension")
        print(f"  {Colors.CYAN}pg_databases{Colors.NC}           List of databases to create")
        print(f"  {Colors.CYAN}pg_users{Colors.NC}               List of users to create")
        print()
        
        print(f"{Colors.BLUE}Options:{Colors.NC}")
        print(f"  {Colors.CYAN}--prod{Colors.NC}                 Use production inventory")
        print(f"  {Colors.CYAN}--check{Colors.NC}                Dry run (no changes)")
        print(f"  {Colors.CYAN}--verbose{Colors.NC}              Verbose output")
        print()
        
        print(f"{Colors.BLUE}Example Inventory Configuration:{Colors.NC}")
        print(f"""  {Colors.GREEN}test-server:{Colors.NC}
    {Colors.CYAN}postgresql_version:{Colors.NC} "17"
    {Colors.CYAN}postgis_version:{Colors.NC} "3"
    {Colors.CYAN}database_port:{Colors.NC} 5432
    {Colors.CYAN}setup_postgis:{Colors.NC} true
    {Colors.CYAN}pg_databases:{Colors.NC}
      - name: myapp_db
        owner: myapp_user
        encoding: UTF8
      - name: gis_db
        owner: gis_user
        encoding: UTF8
    {Colors.CYAN}pg_users:{Colors.NC}
      - name: myapp_user
        password: "{{{{ vault_postgres_password }}}}"
        database: myapp_db
        privileges: ALL
      - name: gis_user
        password: "{{{{ vault_postgres_password }}}}"
        database: gis_db
        privileges: ALL""")
        print()
        
        # Show discovered operations
        operations = self.scanner.get_service_operations('psql')
        if operations:
            print(f"{Colors.BLUE}Auto-discovered Operations:{Colors.NC}")
            for op_name, task_path in operations.items():
                print(f"  {Colors.YELLOW}{op_name}{Colors.NC}")
        
        return 0
