#!/bin/bash
# Prepare n8n deployment with Portainer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="${SCRIPT_DIR}/deployments/n8n-stack"

echo "🚀 Preparing n8n stack deployment..."

# Create deployment directory
mkdir -p "${DEPLOYMENT_DIR}"

# Copy template files
echo "📋 Copying template files..."
cp "${SCRIPT_DIR}/templates/n8n-portainer-stack.yml" "${DEPLOYMENT_DIR}/docker-compose.yml"
cp "${SCRIPT_DIR}/templates/init-pgvector.sql" "${DEPLOYMENT_DIR}/"

# Create .env file if it doesn't exist
if [ ! -f "${DEPLOYMENT_DIR}/.env" ]; then
    echo "🔐 Creating .env file..."
    cp "${SCRIPT_DIR}/templates/.env.example" "${DEPLOYMENT_DIR}/.env"
    
    # Generate random passwords
    POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    N8N_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    
    # Update .env with generated values
    sed -i.bak "s/changeme-strong-password/${POSTGRES_PASS}/g" "${DEPLOYMENT_DIR}/.env"
    sed -i.bak "s/changeme-strong-password/${N8N_PASS}/g" "${DEPLOYMENT_DIR}/.env"
    sed -i.bak "s/your-long-random-encryption-key-here/${ENCRYPTION_KEY}/g" "${DEPLOYMENT_DIR}/.env"
    
    echo "⚠️  Generated random passwords in .env file"
    echo "⚠️  Please update domain names and other settings!"
else
    echo "✅ .env file already exists, skipping..."
fi

# Create required directories on host
echo "📁 Creating data directories..."
sudo mkdir -p /data/{postgres,redis,n8n,npm/data,npm/letsencrypt,portainer/data,dump/psql}

# Set proper permissions
echo "🔒 Setting permissions..."
sudo chown -R 999:999 /data/postgres /data/redis /data/n8n
sudo chown -R 1000:1000 /data/npm/data /data/npm/letsencrypt /data/portainer/data

echo ""
echo "✅ Deployment prepared at: ${DEPLOYMENT_DIR}"
echo ""
echo "📝 Next steps:"
echo "1. Edit ${DEPLOYMENT_DIR}/.env to configure:"
echo "   - Domain names (N8N_HOST, WEBHOOK_URL)"
echo "   - Review generated passwords"
echo "   - Set admin email"
echo ""
echo "2. Deploy the stack:"
echo "   cli docker --deploy-compose ${DEPLOYMENT_DIR}/docker-compose.yml --compose-name n8n-stack"
echo ""
echo "3. Configure Nginx Proxy Manager:"
echo "   - Access at http://your-server:81"
echo "   - Default: admin@example.com / changeme"
echo "   - Add proxy hosts for your domains"
echo ""
echo "4. Scale workers if needed:"
echo "   cd /opt/docker-compose/n8n-stack"
echo "   docker-compose up -d --scale n8n-worker=3"