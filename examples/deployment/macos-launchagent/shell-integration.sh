#!/usr/bin/env bash
#
# Tokenash Proxy Shell Integration
#
# Automatically sets ANTHROPIC_BASE_URL if the tokenash proxy is running.
# Supports both bash and zsh.
#
# Usage:
#   Add to ~/.bashrc or ~/.zshrc:
#
#     export TOKENASH_PROXY_PORT=8787  # Optional: customize port (default: 8787)
#     source /path/to/shell-integration.sh
#
# This script will:
#   1. Check if the proxy is running on the configured port
#   2. If running, set ANTHROPIC_BASE_URL
#   3. If not running, try to start the LaunchAgent
#   4. Provide helpful status messages (only on first load)
#

# Configuration: Port can be customized via environment variable
TOKENASH_PROXY_PORT="${TOKENASH_PROXY_PORT:-8787}"
TOKENASH_PLIST_LABEL="com.tokenash.proxy"
USER_UID=$(id -u)

# Prevent duplicate loading (bash and zsh compatible)
if [[ -n "${TOKENASH_SHELL_INTEGRATION_LOADED:-}" ]]; then
  return 0
fi
export TOKENASH_SHELL_INTEGRATION_LOADED=1

# Check if proxy is running (fast path using lsof)
_tokenash_proxy_running() {
  lsof -iTCP:"${TOKENASH_PROXY_PORT}" -sTCP:LISTEN -t >/dev/null 2>&1
}

# Try to start the LaunchAgent if not running
_tokenash_start_proxy() {
  local plist_path="${HOME}/Library/LaunchAgents/${TOKENASH_PLIST_LABEL}.plist"

  # Check if LaunchAgent is installed
  if [[ ! -f "${plist_path}" ]]; then
    return 1
  fi

  # Try to bootstrap the LaunchAgent (idempotent - won't fail if already loaded)
  if launchctl bootstrap "gui/${USER_UID}" "${plist_path}" 2>/dev/null; then
    # Wait a moment for service to start
    sleep 1
    return 0
  fi

  return 1
}

# Main logic
if _tokenash_proxy_running; then
  # Proxy is running - set ANTHROPIC_BASE_URL
  export ANTHROPIC_BASE_URL="http://localhost:${TOKENASH_PROXY_PORT}"
else
  # Proxy not running - try to start it
  if _tokenash_start_proxy && _tokenash_proxy_running; then
    # Successfully started - set ANTHROPIC_BASE_URL
    export ANTHROPIC_BASE_URL="http://localhost:${TOKENASH_PROXY_PORT}"
    echo "✓ Tokenash proxy started on port ${TOKENASH_PROXY_PORT}"
  else
    # Could not start - provide helpful message
    echo "⚠ Tokenash proxy not running on port ${TOKENASH_PROXY_PORT}"
    echo "  Install with: cd /path/to/tokenash/examples/deployment/macos-launchagent && ./install.sh"
  fi
fi

# Cleanup helper functions (don't pollute shell namespace)
unset -f _tokenash_proxy_running _tokenash_start_proxy
