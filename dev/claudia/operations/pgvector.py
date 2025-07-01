"""
pgvector operations handler for Claudia
Handles PostgreSQL with pgvector extension deployment
"""

from operations.base_service import BaseServiceOperations
from utils.colors import Colors, info, success, warning


class PgVectorOperations(BaseServiceOperations):
    """Handle pgvector operations with vector database capabilities"""
    
    def __init__(self, config):
        super().__init__(config, "pgvector")
        self.name = "pgvector"
        self.description = "PostgreSQL with pgvector extension for AI/ML embeddings"
    
    def _get_parameter_mapping(self) -> dict:
        """Get CLI parameter to Ansible variable mapping"""
        return {
            # Basic PostgreSQL parameters
            '--port': 'pg_port',
            '--version': 'pg_version',
            '--pgis': 'setup_postgis',
            
            # pgvector specific
            '--pgvector-version': 'pgvector_version',
            '--dimensions': 'pgvector_default_dimensions',
            '--index-type': 'pgvector_index_type',
            
            # Database configuration
            '--databases': 'pg_databases',
            '--users': 'pg_users',
            
            # Performance tuning for vector operations
            '--shared-buffers': 'pg_shared_buffers_mb',
            '--work-mem': 'pg_work_mem_mb',
            '--maintenance-work-mem': 'pg_maintenance_work_mem_mb',
            '--max-connections': 'pg_max_connections',
            
            # Example data
            '--create-examples': 'pg_create_example_schema',
        }
    
    def show_help(self) -> None:
        """Show pgvector-specific help"""
        print(f"\n{Colors.CYAN}pgvector - PostgreSQL with Vector Database Support{Colors.RESET}")
        print(f"{Colors.DIM}PostgreSQL with pgvector extension for AI/ML embedding storage and similarity search{Colors.RESET}\n")
        
        print(f"{Colors.GREEN}USAGE:{Colors.RESET}")
        print(f"  {Colors.YELLOW}claudia pgvector{Colors.RESET} --install [OPTIONS]")
        print(f"  {Colors.YELLOW}claudia pgvector{Colors.RESET} --help\n")
        
        print(f"{Colors.GREEN}OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--install{Colors.RESET}              Install PostgreSQL with pgvector extension")
        print(f"  {Colors.CYAN}--port{Colors.RESET} PORT            PostgreSQL port (default: 5432)")
        print(f"  {Colors.CYAN}--version{Colors.RESET} VERSION      PostgreSQL version (default: 17)")
        print(f"  {Colors.CYAN}--pgvector-version{Colors.RESET} VER pgvector version (default: v0.5.1)")
        print(f"  {Colors.CYAN}--dimensions{Colors.RESET} DIM       Default vector dimensions (default: 1536)")
        print(f"  {Colors.CYAN}--index-type{Colors.RESET} TYPE      Index type: ivfflat or hnsw (default: ivfflat)")
        print(f"  {Colors.CYAN}--pgis{Colors.RESET}                 Also install PostGIS extension")
        print(f"  {Colors.CYAN}--create-examples{Colors.RESET}      Create example schema with functions")
        print()
        
        print(f"{Colors.GREEN}PERFORMANCE OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--shared-buffers{Colors.RESET} MB    Shared buffers size (auto-calculated)")
        print(f"  {Colors.CYAN}--work-mem{Colors.RESET} MB          Work memory per operation (default: 16)")
        print(f"  {Colors.CYAN}--max-connections{Colors.RESET} NUM  Maximum connections (default: 200)")
        print()
        
        print(f"{Colors.GREEN}ENVIRONMENT OPTIONS:{Colors.RESET}")
        print(f"  {Colors.CYAN}--dev{Colors.RESET}                  Use development environment (default)")
        print(f"  {Colors.CYAN}--prod{Colors.RESET}                 Use production environment")
        print(f"  {Colors.CYAN}--ci{Colors.RESET}                   Use CI environment")
        print()
        
        print(f"{Colors.GREEN}EXAMPLES:{Colors.RESET}")
        print(f"  # Install pgvector with defaults")
        print(f"  {Colors.YELLOW}claudia pgvector --install{Colors.RESET}")
        print()
        print(f"  # Install with custom port and dimensions")
        print(f"  {Colors.YELLOW}claudia pgvector --install --port 5433 --dimensions 768{Colors.RESET}")
        print()
        print(f"  # Production install with PostGIS")
        print(f"  {Colors.YELLOW}claudia pgvector --install --prod --pgis --create-examples{Colors.RESET}")
        print()
        
        print(f"{Colors.GREEN}VECTOR DATABASE FEATURES:{Colors.RESET}")
        print(f"  • Embedding storage up to 16,000 dimensions")
        print(f"  • Distance functions: L2, Inner Product, Cosine")
        print(f"  • Index types: IVFFlat (fast build) and HNSW (better recall)")
        print(f"  • Perfect for: RAG, similarity search, recommendations")
        print()
        
        print(f"{Colors.GREEN}POST-INSTALLATION:{Colors.RESET}")
        print(f"  • Connection: psql -h <host> -p <port> -U postgres")
        print(f"  • Create vector column: CREATE TABLE items (embedding vector(1536));")
        print(f"  • Find similar: SELECT * FROM items ORDER BY embedding <-> '[1,2,3]' LIMIT 5;")
        print(f"  • Usage guide: /root/pgvector-guide.txt")
        print()
    
    def _extract_service_args(self, ansible_args: list) -> dict:
        """Extract pgvector-specific arguments"""
        service_args = {}
        
        # Extract arguments that should be passed as extra vars
        i = 0
        while i < len(ansible_args):
            if ansible_args[i] == '--dimensions' and i + 1 < len(ansible_args):
                service_args['pgvector_default_dimensions'] = ansible_args[i + 1]
                i += 2
            elif ansible_args[i] == '--index-type' and i + 1 < len(ansible_args):
                if ansible_args[i + 1] not in ['ivfflat', 'hnsw']:
                    warning(f"Invalid index type: {ansible_args[i + 1]}. Using default (ivfflat)")
                else:
                    service_args['pgvector_index_type'] = ansible_args[i + 1]
                i += 2
            else:
                i += 1
        
        return service_args