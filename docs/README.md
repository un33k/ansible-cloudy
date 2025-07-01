# Ansible Cloudy Documentation

## Quick Links

### Getting Started
- [Quick Start Guide](getting-started/quickstart.md) - Get up and running in 5 minutes
- [Installation](getting-started/installation.md) - Detailed installation instructions
- [First Deployment](getting-started/first-deployment.md) - Deploy your first server

### Architecture & Design
- [System Architecture](architecture/overview.md) - How Ansible Cloudy works
- [Authentication Flow](architecture/authentication-flow.md) - Two-phase security model
- [Directory Structure](architecture/directory-structure.md) - Project organization

### Development
- [Development Guide](development/guide.md) - Contributing to Ansible Cloudy
- [Testing](development/testing.md) - Running tests and validation
- [Claudia CLI Development](development/claudia-cli.md) - Extending the CLI

### Operations
- [Command Reference](operations/commands.md) - All available commands
- [Deployment Recipes](operations/recipes.md) - Available deployment flavors
- [Configuration](operations/configuration.md) - Vault and inventory setup

### Reference
- [Variable Reference](reference/variables.md) - All configurable variables
- [Changelog](reference/changelog.md) - Version history
- [Troubleshooting](reference/troubleshooting.md) - Common issues and solutions

## Overview

Ansible Cloudy is a production-ready infrastructure automation framework that simplifies server deployment and management. Built on top of Ansible, it provides:

- **Claudia CLI**: Intelligent command-line interface for infrastructure management
- **Two-Phase Security**: Secure authentication flow from initial setup to production
- **Production-Ready Recipes**: Pre-configured deployments for common architectures
- **Modular Design**: Reusable components for custom configurations

## Key Features

- 🔒 **Secure by Default**: Two-phase authentication, firewall configuration, SSH hardening
- 🚀 **Quick Deployment**: From bare server to production in minutes
- 📦 **Pre-Built Recipes**: PostgreSQL, Redis, Nginx, Django, Node.js, and more
- 🎯 **Intelligent CLI**: Auto-discovery of services and operations
- 🔧 **Highly Configurable**: Vault-based configuration management
- ✅ **Well Tested**: Comprehensive test suite with Docker-based E2E tests

## Documentation Structure

This documentation is organized to help you find information quickly:

- **Getting Started**: New users start here
- **Architecture**: Understanding how things work
- **Development**: Contributing and extending
- **Operations**: Day-to-day usage and management
- **Reference**: Detailed technical information