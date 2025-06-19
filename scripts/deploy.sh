#!/bin/bash
set -euo pipefail

# Ansible Cloudy Deployment Script
PLAYBOOK=""
INVENTORY="inventory/development"
EXTRA_VARS=""
CHECK_MODE=false
VERBOSE=false

usage() {
    echo "Usage: $0 -p PLAYBOOK [-i INVENTORY] [-e EXTRA_VARS] [-c] [-v]"
    echo "  -p PLAYBOOK    Playbook to run (required)"
    echo "  -i INVENTORY   Inventory directory (default: inventory/development)"
    echo "  -e EXTRA_VARS  Extra variables (key=value format)"
    echo "  -c             Run in check mode (dry run)"
    echo "  -v             Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 -p playbooks/server-baseline.yml"
    echo "  $0 -p recipes/lamp-stack/site.yml -i inventory/production"
    echo "  $0 -p playbooks/web-server.yml -e 'web_domain=example.com' -v"
    exit 1
}

while getopts "p:i:e:cvh" opt; do
    case $opt in
        p) PLAYBOOK="$OPTARG" ;;
        i) INVENTORY="$OPTARG" ;;
        e) EXTRA_VARS="$OPTARG" ;;
        c) CHECK_MODE=true ;;
        v) VERBOSE=true ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [[ -z "$PLAYBOOK" ]]; then
    echo "❌ Playbook is required"
    usage
fi

if [[ ! -f "$PLAYBOOK" ]]; then
    echo "❌ Playbook not found: $PLAYBOOK"
    exit 1
fi

# Activate virtual environment if it exists
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

# Build ansible-playbook command
CMD="ansible-playbook"
CMD+=" -i $INVENTORY"
CMD+=" $PLAYBOOK"

if [[ "$CHECK_MODE" == true ]]; then
    CMD+=" --check"
fi

if [[ "$VERBOSE" == true ]]; then
    CMD+=" -vv"
fi

if [[ -n "$EXTRA_VARS" ]]; then
    CMD+=" -e '$EXTRA_VARS'"
fi

echo "🚀 Running deployment..."
echo "📋 Playbook: $PLAYBOOK"
echo "📦 Inventory: $INVENTORY"
if [[ "$CHECK_MODE" == true ]]; then
    echo "🔍 Mode: Check (dry run)"
fi

# Run the command
eval $CMD