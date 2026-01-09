#!/bin/bash
# ==============================================================================
# Systemd Service Installation Script
# ==============================================================================
# Run this script on your Raspberry Pi to install the systemd service.
#
# Usage:
#   sudo ./install_service.sh
#
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (sudo)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="${SCRIPT_DIR}/home-server-hub.service"
INSTALL_DIR="/home/pi/home-server"

# Update paths in service file based on actual installation
if [ "$SCRIPT_DIR" != "/home/pi/home-server/systemd" ]; then
    log_info "Detected non-standard installation path: ${SCRIPT_DIR}"
    ACTUAL_DIR=$(dirname "$SCRIPT_DIR")
    log_info "Home server directory: ${ACTUAL_DIR}"
    
    # Create a modified service file
    sed "s|/home/pi/home-server|${ACTUAL_DIR}|g" "$SERVICE_FILE" > /tmp/home-server-hub.service
    SERVICE_FILE="/tmp/home-server-hub.service"
fi

# Get the actual user
ACTUAL_USER=$(stat -c '%U' "$SCRIPT_DIR")
if [ "$ACTUAL_USER" != "pi" ]; then
    log_info "Updating service to run as user: ${ACTUAL_USER}"
    sed -i "s|User=pi|User=${ACTUAL_USER}|g; s|Group=pi|Group=${ACTUAL_USER}|g" "$SERVICE_FILE"
fi

log_info "Installing systemd service..."

# Copy service file
cp "$SERVICE_FILE" /etc/systemd/system/home-server-hub.service
chmod 644 /etc/systemd/system/home-server-hub.service

# Create logs directory
mkdir -p "$(dirname "$SCRIPT_DIR")/logs"
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$(dirname "$SCRIPT_DIR")/logs"

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable home-server-hub.service

log_success "Service installed and enabled!"
echo ""
echo "Commands:"
echo "  sudo systemctl start home-server-hub    # Start the hub"
echo "  sudo systemctl stop home-server-hub     # Stop the hub"
echo "  sudo systemctl restart home-server-hub  # Restart the hub"
echo "  sudo systemctl status home-server-hub   # Check status"
echo "  sudo journalctl -u home-server-hub -f   # View logs"
echo ""
