"""
PostgreSQL Argument Parser

Handles parsing of PostgreSQL-specific command line arguments.
"""

from typing import Dict, Any, List
from utils.colors import error


class PostgreSQLArgumentParser:
    """Parse PostgreSQL-specific command line arguments"""
    
    @staticmethod
    def extract_psql_args(ansible_args: List[str]) -> Dict[str, Any]:
        """Extract PostgreSQL-specific arguments from command line"""
        psql_args = {}
        i = 0
        
        while i < len(ansible_args):
            arg = ansible_args[i]
            
            # PostgreSQL recipe arguments
            if arg == "--port":
                if i + 1 < len(ansible_args):
                    psql_args['database_port'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--port requires a value")
            elif arg == "--pgis":
                psql_args['setup_postgis'] = True
                i += 1
            elif arg == "--pgvector":
                psql_args['setup_pgvector'] = True
                i += 1
            
            # Granular operation arguments
            elif arg == "--adduser":
                psql_args['operation'] = 'adduser'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--adduser requires a username")
            elif arg == "--password":
                if i + 1 < len(ansible_args):
                    psql_args['password'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--password requires a value")
            elif arg == "--database":
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--database requires a value")
            elif arg == "--delete-user":
                psql_args['operation'] = 'delete-user'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--delete-user requires a username")
            elif arg == "--list-users":
                psql_args['operation'] = 'list-users'
                i += 1
            elif arg == "--list-databases":
                psql_args['operation'] = 'list-databases'
                i += 1
            elif arg == "--adddb":
                psql_args['operation'] = 'adddb'
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--adddb requires a database name")
            elif arg == "--owner":
                if i + 1 < len(ansible_args):
                    psql_args['owner'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--owner requires a username")
            
            # Additional PostgreSQL operations
            elif arg == "--delete-db":
                psql_args['operation'] = 'delete-db'
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--delete-db requires a database name")
            elif arg == "--dump-database":
                psql_args['operation'] = 'dump-database'
                if i + 1 < len(ansible_args):
                    psql_args['database'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--dump-database requires a database name")
            elif arg == "--change-password":
                psql_args['operation'] = 'change-password'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--change-password requires a username")
            elif arg == "--grant-privileges":
                psql_args['operation'] = 'grant-privileges'
                if i + 1 < len(ansible_args):
                    psql_args['username'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--grant-privileges requires a username")
            elif arg == "--privileges":
                if i + 1 < len(ansible_args):
                    psql_args['privileges'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--privileges requires a value")
            elif arg == "--install-postgis":
                psql_args['operation'] = 'install-postgis'
                i += 1
            elif arg == "--get-version":
                psql_args['operation'] = 'get-installed-version'
                i += 1
            elif arg == "--get-latest-version":
                psql_args['operation'] = 'get-latest-version'
                i += 1
            elif arg == "--install-client":
                psql_args['operation'] = 'install-client'
                i += 1
            elif arg == "--configure-port":
                psql_args['operation'] = 'configure-port'
                if i + 1 < len(ansible_args):
                    psql_args['port'] = ansible_args[i + 1]
                    i += 2
                else:
                    psql_args['port'] = '5432'  # Default port
                    i += 1
            elif arg == "--create-cluster":
                psql_args['operation'] = 'create-cluster'
                if i + 1 < len(ansible_args):
                    psql_args['cluster_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--create-cluster requires a cluster name")
            elif arg == "--remove-cluster":
                psql_args['operation'] = 'remove-cluster'
                if i + 1 < len(ansible_args):
                    psql_args['cluster_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--remove-cluster requires a cluster name")
            elif arg == "--install-repo":
                psql_args['operation'] = 'install-repo'
                i += 1
            
            # Extension management operations
            elif arg == "--enable-extension":
                psql_args['operation'] = 'enable-extension'
                if i + 1 < len(ansible_args):
                    psql_args['extension_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--enable-extension requires an extension name")
            elif arg == "--disable-extension":
                psql_args['operation'] = 'disable-extension'
                if i + 1 < len(ansible_args):
                    psql_args['extension_name'] = ansible_args[i + 1]
                    i += 2
                else:
                    error("--disable-extension requires an extension name")
            elif arg == "--list-extensions":
                psql_args['operation'] = 'list-extensions'
                i += 1
            elif arg == "--verify-extensions":
                psql_args['operation'] = 'verify-extensions'
                i += 1
            else:
                i += 1
        
        return psql_args

    @staticmethod
    def detect_operation(ansible_args: List[str]) -> str:
        """Detect which granular operation is requested"""
        operations = [
            '--adduser', '--delete-user', '--list-users', '--list-databases', '--adddb',
            '--delete-db', '--dump-database', '--change-password', '--grant-privileges',
            '--install-postgis', '--get-version', '--get-latest-version', '--install-client',
            '--configure-port', '--create-cluster', '--remove-cluster', '--install-repo',
            '--enable-extension', '--disable-extension', '--list-extensions', '--verify-extensions'
        ]
        
        for arg in ansible_args:
            if arg in operations:
                # Handle special mapping for get-version
                if arg == '--get-version':
                    return 'get-installed-version'
                return arg[2:]  # Remove -- prefix
        
        return None
