# Docker/Container CLI Implementation Plan

## Overview
This document outlines the implementation plan for Docker container management through the CLI, based on the vault variables and existing codebase patterns.

## Vault Variables
The following variables are defined in `.vault/dev.yml`:
- `vault_portainer_domain_name` = "portainer.example.com" (required)
- `vault_portainer_docker_name` = "portainer" (defaults to "portainer") 
- `vault_portainer_internal_port` = 9000 (defaults to 9000)

## CLI Command Structure

### Simple Commands
```bash
cli docker --install                    # Install Docker + create networks
cli portainer --install                 # Deploy Portainer with nginx proxy
cli nginx --install --docker            # Deploy nginx container (opens 80/443)
```

### Combined Command
```bash
cli docker --compose portainer          # Install docker, nginx, and portainer
```

## Implementation Steps

### 1. Create Docker Service Operations
**File**: `dev/cli/operations/docker.py`
- Extends BaseServiceOperations
- Handles `--compose` flag for deploying containers
- Auto-installs nginx when deploying edge services

### 2. Create Container Recipes

#### a. Docker Installation
**File**: `/cloudy/playbooks/recipes/container/docker.yml`
- Install Docker CE
- Install Docker Compose
- Configure Docker daemon
- Create Docker networks (proxy_network, internal_network)
- Setup docker group permissions

#### b. Portainer Deployment
**File**: `/cloudy/playbooks/recipes/container/portainer.yml`
- Deploy Portainer using docker-compose
- Configure nginx reverse proxy
- Use vault variables for configuration
- No external port exposure (internal network only)

#### c. Nginx Container Deployment
**File**: `/cloudy/playbooks/recipes/container/nginx.yml`
- Deploy nginx as Docker container
- Open UFW ports 80/443
- Mount configuration volumes
- Setup as edge service on proxy network

### 3. Template Management

#### Template Locations
- Move from: `/container/docker/templates/`
- Move to: `/cloudy/templates/container/`

#### Hydration Flow
1. Copy templates to `/tmp/docker-compose/[service]/`
2. Hydrate with vault variables
3. Deploy using docker-compose
4. Configure nginx proxy if needed

### 4. UFW/Firewall Handling
- **Edge Services** (nginx): Opens ports 80/443
- **Internal Services** (portainer): No UFW rules needed
- Only nginx container has external port exposure
- All other containers communicate via Docker networks

### 5. Network Architecture
```
Internet → UFW (80/443) → Nginx Container → Internal Network → Portainer
                              ↓
                         Proxy Network
```

## Workflow Example

### Deploy Portainer with Nginx Proxy
```bash
cli docker --compose portainer
```

This command will:
1. Check if Docker is installed (install if not)
2. Create Docker networks:
   - `proxy_network` (external-facing)
   - `internal_network` (internal-only)
3. Deploy nginx container:
   - Opens UFW ports 80/443
   - Connects to both networks
4. Deploy Portainer container:
   - Internal network only
   - No external ports
5. Configure nginx proxy:
   - Route `portainer.example.com` → `portainer:9000`
   - Generate SSL certificates

## Key Design Principles

### 1. LEVER Compliance
- **Locate**: Reuse existing Docker tasks
- **Extend**: Build on BaseServiceOperations
- **Validate**: Follow existing patterns
- **Enhance**: Add container-specific features
- **Reduce**: Minimal new code

### 2. Security First
- Internal services never expose ports directly
- All external access through nginx proxy
- Proper network isolation
- UFW rules only for edge services

### 3. Simplicity
- Simple CLI commands
- Automatic dependency handling
- Smart defaults with override capability
- Consistent with existing services

## File Structure

```
ansible-cloudy/
├── dev/cli/operations/
│   └── docker.py                    # Docker CLI operations
├── cloudy/
│   ├── playbooks/recipes/container/
│   │   ├── docker.yml              # Docker installation
│   │   ├── portainer.yml           # Portainer deployment
│   │   └── nginx.yml               # Nginx container
│   ├── templates/container/
│   │   ├── nginx/
│   │   │   └── docker-compose.yml.j2
│   │   └── portainer/
│   │       └── docker-compose.yml.j2
│   └── defaults/
│       └── container.yml           # Container defaults
```

## Next Steps

1. Create the Docker operations handler
2. Create container recipe playbooks
3. Move and update templates
4. Add container defaults file
5. Test with portainer deployment
6. Document usage in CLAUDE.md

## Notes

- Templates already exist and have been optimized
- Nginx template uses `{{docker_container_name}}` for proxy targets
- Portainer template has no port exposure (internal only)
- Both templates use fixed data directory: `/data/docker/*`