#!/usr/bin/env bash
# scripts/setup-hooks.sh
# Automates the configuration of local Git hooks

# Ensure we are in the root of the repository
ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$ROOT_DIR" ]; then
    echo "❌ Error: Not a git repository."
    exit 1
fi

# Define the central githooks directory
HOOKS_DIR="$ROOT_DIR/.githooks"

# Check if .githooks exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo "⚠️ .githooks directory not found! Ensure you are in the root directory running this script."
    exit 1
fi

# Set the execute bit unconditionally for safety
chmod -R +x "$HOOKS_DIR"

# Tell git to use this directory for hooks
git config core.hooksPath "$HOOKS_DIR"

echo "✅ Git hooks configured successfully!"
echo "Your core.hooksPath is now set to $HOOKS_DIR"
echo "Future commits will automatically run Python and Dart validations."
