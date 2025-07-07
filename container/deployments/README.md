# Deployments Directory

This directory is used for active container deployments. Files in this directory are gitignored to prevent accidental commits of sensitive configuration.

## Usage

1. Copy templates from `../templates/` to this directory
2. Create `.env` files with your configuration
3. Deploy using the CLI:

```bash
cli docker --deploy-compose container/deployments/your-stack.yml
```

## Important

- Never commit `.env` files or files with passwords
- Keep backups of your configurations separately
- Use strong, unique passwords for all services