# Nginx + Portainer with Dual Docker Networks

This setup implements:
- External access via Nginx on all network interfaces (eth0, eth1, etc.)
- Portainer on an internal-only Docker network
- Clear documentation of each section

## 📦 File: `docker-compose.yml` for Portainer

```yaml
version: "3.8"

# Portainer container management UI
# - Direct access via ports 9000 (HTTP) and 9443 (HTTPS)
# - Can be accessed through Nginx reverse proxy or directly
# - Provides Docker container management interface

services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    
    # Configure with Docker socket
    command: -H unix:///var/run/docker.sock
    
    ports:
      - "9000:9000"
      - "9443:9443"
    
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # Docker API access
      - /data/docker/portainer:/data  # Persistent data
    
    networks:
      - proxy
      - internal
    
    labels:
      # Labels for service discovery and monitoring
      service.name: "portainer"
      service.type: "container-management"

networks:
  proxy:
    external: true
    name: proxy_network
  internal:
    external: true
    name: internal_network 
```

## 📦 File: `docker-compose.yml` for Nginx Proxy

```yaml
version: "3.8"

# Nginx container configuration for reverse proxy
# - Direct access via ports 80 (HTTP) and 443 (HTTPS)
# - Can be accessed through directly
# - Provides Docker proxy services to other dockers on the private interface

services:
  nginx:
    image: nginx:latest
    container_name: nginx
    restart: unless-stopped

    # These ports expose Nginx to the host on all interfaces (e.g., eth0, eth1, etc.)
    # You can later restrict binding to specific IPs via daemon-level rules if needed.
    ports:
      - "80:80"    # HTTP traffic from external clients
      - "443:443"  # HTTPS traffic from external clients

    volumes:
      # Main nginx configuration file (optional, uses default if not present)
      - /data/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      
      # Read-only mount for Nginx site configuration
      - /data/docker/nginx/conf.d:/etc/nginx/conf.d:ro

      # Read-only mount for TLS certificates (self-signed or Let's Encrypt)
      - /data/docker/nginx/certs:/etc/nginx/certs:ro
      
      # Logs for debugging and monitoring
      - /data/docker/nginx/logs:/var/log/nginx
      
      # Static content serving (optional)
      - /data/docker/nginx/assets:/usr/share/nginx/assets:ro

    networks:
      - proxy      # External-facing network, binds to host network stack
      - internal   # Internal-only network to reach backend services
    
    # Health check validates nginx configuration syntax
    # nginx -t tests config files without starting the server
    # Helps detect config errors, missing files, or cert issues
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    labels:
      # Labels for service discovery and monitoring
      service.name: "nginx"
      service.type: "network-proxy"

networks:
  proxy:
    external: true
    name: proxy_network
  internal:
    external: true
    name: internal_network 
```

## 🗂 Required Host Directory Structure

```bash
/data/docker
├── nginx/      # Nginx persistent state
│   ├── nginx.conf/ # Main nginx configuration file
│   └── conf.d/     # Nginx site configs (e.g. portainer.conf)
│   └── certs/      # SSL/TLS certs (self-signed or Let's Encrypt)
│   └── logs/       # Logs for debugging and monitoring
│   └── assets/     # Static content serving (optional)
└── portainer/  # Portainer persistent state
```

## 🛠 TLS Certificate Setup (Development)

```bash
mkdir -p /data/docker/nginx/certs

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /data/docker/nginx/certs/selfsigned.key \
  -out /data/docker/nginx/certs/selfsigned.crt \
  -subj "/CN=admin.example.com"
```

## 🔁 Start Services

```bash
docker-compose up -d
```

Visit: **https://admin.example.com** (browser will warn about self-signed cert)

## 🔐 Secure Routing (Nginx config in `/data/docker/nginx/conf.d/portainer.conf`)

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name {{domain_name}};

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS reverse proxy
server {
    listen 443 ssl http2;
    server_name {{domain_name}};

    # SSL configuration
    ssl_certificate     /etc/nginx/certs/{{domain_name}}_selfsigned.crt;
    ssl_certificate_key /etc/nginx/certs/{{domain_name}}_selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Logging
    access_log /var/log/nginx/{{domain_name}}_access.log;
    error_log /var/log/nginx/{{domain_name}}_error.log;
    
    # Client body size limit
    client_max_body_size 100M;

    location / {
        proxy_pass http://{{domain_name}}:{{remote_port}};
        
        # Pass all client headers
        proxy_pass_request_headers on;
        
        # Essential proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Pass original request headers
        proxy_set_header X-Original-URI $request_uri;
        proxy_set_header X-Original-Method $request_method;
        
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Prevent header modifications
        proxy_hide_header X-Powered-By;
        proxy_pass_header Server;
        
        # Increase buffer sizes for large headers
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Handle errors gracefully
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_next_upstream_tries 2;
        
        # Compression
        gzip on;
        gzip_vary on;
        gzip_proxied any;
        gzip_types text/plain text/css text/xml application/json application/javascript;
        
        # Rate limiting (optional - uncomment to enable)
        # limit_req zone=one burst=10 nodelay;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## ✅ Summary

- Nginx is exposed on **all external interfaces** by default (`0.0.0.0:80/443`)
- Portainer is **only accessible via Nginx** (internal network only)
- All persistent config/data stored under `/data/<service-name>`
- Self-signed certs can be swapped for Let's Encrypt later