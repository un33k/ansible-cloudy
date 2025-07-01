#!/bin/bash

# Ansible Cloudy Bootstrap Script
# Sets up Python via pyenv (if needed) and creates virtual environment with Ansible tools

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_VERSION="3.11.9"
VENV_DIR="./.venv"
AUTO_YES=false
CI_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            AUTO_YES=true
            shift
            ;;
        --ci)
            CI_MODE=true
            AUTO_YES=true
            shift
            ;;
        *)
            echo "Usage: $0 [-y|--yes] [--ci]"
            echo "  -y, --yes    Auto-confirm all prompts"
            echo "  --ci         CI mode (skip pyenv, use system Python)"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

ask() {
    if [[ "$AUTO_YES" == true ]]; then
        return 0
    fi
    
    local prompt="$1"
    local default="${2:-y}"
    
    echo -e "${BLUE}?${NC} $prompt (${default}/n): "
    read -r response
    response=${response:-$default}
    
    [[ "$response" =~ ^[Yy] ]]
}

# Detect Linux distribution
detect_linux_distribution() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "debian"
    elif command -v yum >/dev/null 2>&1; then
        echo "rhel"
    elif command -v dnf >/dev/null 2>&1; then
        echo "fedora"
    else
        echo "unknown"
    fi
}

# Check and install Homebrew on macOS
check_brew() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            log "Homebrew found: $(brew --version | head -n1)"
            return 0
        else
            warn "Homebrew not found"
            if ask "Install Homebrew?"; then
                echo -e "${BLUE}Installing Homebrew...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                log "Homebrew installed successfully"
            else
                warn "Homebrew is required for macOS installations"
                return 1
            fi
        fi
    fi
    return 0
}

# Check if Python 3 is available (fallback option)
check_system_python() {
    if command -v python3 >/dev/null 2>&1; then
        local version=$(python3 --version 2>&1 | cut -d' ' -f2)
        log "System Python 3 found: $version"
        return 0
    else
        return 1
    fi
}

# Check if pyenv is installed
check_pyenv() {
    if command -v pyenv >/dev/null 2>&1; then
        log "pyenv found: $(pyenv --version)"
        return 0
    else
        warn "pyenv not found"
        return 1
    fi
}

# Install pyenv
install_pyenv() {
    echo -e "${BLUE}Installing pyenv...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            brew install pyenv
            log "pyenv installed via Homebrew"
        else
            error "Homebrew required for pyenv installation on macOS"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - install dependencies first
        local distribution=$(detect_linux_distribution)
        case $distribution in
            "debian")
                sudo apt-get update
                sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
                    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
                    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
                    libffi-dev liblzma-dev
                ;;
            "rhel")
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel \
                    zlib-devel readline-devel sqlite-devel
                ;;
            "fedora")
                sudo dnf groupinstall -y "Development Tools"
                sudo dnf install -y gcc openssl-devel bzip2-devel libffi-devel \
                    zlib-devel readline-devel sqlite-devel
                ;;
        esac
        
        # Install pyenv
        curl https://pyenv.run | bash
        
        # Add to shell profile
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
        
        warn "Please restart your shell or run: source ~/.bashrc"
        warn "Then run this script again"
        exit 0
    else
        error "Unsupported OS. Please install pyenv manually: https://github.com/pyenv/pyenv"
    fi
}

# Install Python version via pyenv
install_python_pyenv() {
    log "Installing Python $PYTHON_VERSION via pyenv..."
    
    if pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
        log "Python $PYTHON_VERSION already installed"
    else
        pyenv install "$PYTHON_VERSION"
        log "Python $PYTHON_VERSION installed"
    fi
    
    # Set local version
    pyenv local "$PYTHON_VERSION"
    log "Set local Python version to $PYTHON_VERSION"
}

# Setup Python (pyenv or system)
setup_python() {
    if [[ "$CI_MODE" == true ]]; then
        # In CI, use whatever Python is available
        if command -v python >/dev/null 2>&1; then
            log "Using CI Python: $(python --version)"
        elif command -v python3 >/dev/null 2>&1; then
            log "Using CI Python 3: $(python3 --version)"
            # Create a python symlink if needed
            if ! command -v python >/dev/null 2>&1; then
                warn "Creating python symlink to python3"
            fi
        else
            error "No Python found in CI environment"
        fi
    elif command -v pyenv >/dev/null 2>&1; then
        install_python_pyenv
    elif check_system_python; then
        warn "Using system Python 3 (pyenv not available)"
    else
        error "No suitable Python 3 installation found. Please install Python 3.8+ or pyenv"
    fi
}

# Create virtual environment
create_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        if [[ "$CI_MODE" == true ]]; then
            log "Removing existing virtual environment in CI mode"
            rm -rf "$VENV_DIR"
        elif ask "Virtual environment already exists. Recreate?"; then
            rm -rf "$VENV_DIR"
        else
            log "Using existing virtual environment"
            return 0
        fi
    fi
    
    log "Creating virtual environment in $VENV_DIR..."
    
    # Try different approaches for CI compatibility
    if command -v python >/dev/null 2>&1; then
        python -m venv "$VENV_DIR" || python -m virtualenv "$VENV_DIR" || {
            error "Failed to create virtual environment with python"
            return 1
        }
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m venv "$VENV_DIR" || python3 -m virtualenv "$VENV_DIR" || {
            error "Failed to create virtual environment with python3"
            return 1
        }
    else
        error "No Python executable found"
        return 1
    fi
    
    # Verify venv was created
    if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
        error "Virtual environment creation failed - no activate script found"
        return 1
    fi
    
    log "Virtual environment created"
}

# Install Ansible dependencies
install_deps() {
    log "Activating virtual environment and installing Ansible tools..."
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    
    # Install Ansible and development tools from pyproject.toml
    pip install -e ".[dev]"
    
    # Install cli wrapper into venv
    log "Installing cli command..."
    cp "$SCRIPT_DIR/dev/bin/claudia-venv" "$VENV_DIR/bin/claudia"
    chmod +x "$VENV_DIR/bin/claudia"
    
    # Create cli alias for claudia
    log "Creating 'cli' alias for claudia..."
    cd "$VENV_DIR/bin"
    ln -sf claudia cli
    cd "$SCRIPT_DIR"
    
    log "Ansible dependencies installed successfully"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Ansible Cloudy Bootstrap${NC}"
    
    if [[ "$CI_MODE" == true ]]; then
        echo "Running in CI mode - using system Python"
    else
        echo "Setting up Python development environment for Ansible automation..."
    fi
    echo
    
    # Skip Homebrew and pyenv in CI mode
    if [[ "$CI_MODE" != true ]]; then
        # Check/install Homebrew (macOS only)
        check_brew
        
        # Check/install pyenv (optional)
        if ! check_pyenv; then
            if ask "Install pyenv for better Python version management?"; then
                install_pyenv
            else
                warn "Continuing with system Python (pyenv recommended but not required)"
            fi
        fi
    fi
    
    # Setup Python
    setup_python
    
    # Create virtual environment
    create_venv
    
    # Install Ansible dependencies
    install_deps
    
    echo
    log "Bootstrap complete!"
    echo -e "${GREEN}To activate the environment:${NC} source $VENV_DIR/bin/activate"
    echo -e "${GREEN}To test the setup:${NC}"
    echo "  cli dev syntax    # Quick syntax check"
    echo "  cli dev yaml      # YAML syntax validation"
    echo "  cli dev lint      # Complete linting (YAML + Ansible)"
    echo "  cli dev validate  # Full validation"
    echo
    echo -e "${GREEN}To run recipes:${NC}"
    echo "  cli security --install      # Security hardening"
    echo "  cli django --install        # Django web server"
    echo "  cli psql --install          # PostgreSQL database"
    echo
    echo -e "${YELLOW}Remember to activate the environment first: source .venv/bin/activate${NC}"
}

main "$@"