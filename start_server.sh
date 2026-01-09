#!/bin/bash
# ==============================================================================
# Home Server Startup Script
# ==============================================================================
# This script initializes the Home Server Hub and all its dependencies.
# It can be run manually or via systemd service.
#
# Usage:
#   ./start_server.sh          # Normal start
#   ./start_server.sh --setup  # First-time setup (install dependencies)
#   ./start_server.sh --check  # Check status only
#   ./start_server.sh --stop   # Stop all services
#
# ==============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_DIR="${SCRIPT_DIR}/hub"
EXPENSES_DIR="${SCRIPT_DIR}/expensesApp"
LOG_DIR="${SCRIPT_DIR}/logs"
VENV_NAME="venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if running on Raspberry Pi
is_raspberry_pi() {
    if [ -f /proc/device-tree/model ]; then
        grep -q "raspberry" /proc/device-tree/model 2>/dev/null && return 0
    fi
    return 1
}

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    # Find Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check version (use sed for compatibility with BSD grep on macOS)
    PY_VERSION=$($PYTHON_CMD --version 2>&1 | sed -E 's/.*([0-9]+\.[0-9]+).*/\1/')
    log_info "Found Python $PY_VERSION"
    
    # Ensure pip is available
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        log_error "pip is not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    local app_dir=$1
    local app_name=$(basename "$app_dir")
    local venv_path="${app_dir}/${VENV_NAME}"
    
    if [ ! -d "$venv_path" ]; then
        log_info "Creating virtual environment for ${app_name}..."
        $PYTHON_CMD -m venv "$venv_path"
        log_success "Virtual environment created for ${app_name}"
    else
        log_info "Virtual environment exists for ${app_name}"
    fi
}

# Install dependencies
install_deps() {
    local app_dir=$1
    local app_name=$(basename "$app_dir")
    local venv_path="${app_dir}/${VENV_NAME}"
    local req_file="${app_dir}/requirements.txt"
    
    if [ ! -f "$req_file" ]; then
        log_warning "No requirements.txt found for ${app_name}"
        return
    fi
    
    log_info "Installing dependencies for ${app_name}..."
    
    # Activate venv and install
    source "${venv_path}/bin/activate"
    pip install --upgrade pip -q
    pip install -r "$req_file" -q
    deactivate
    
    log_success "Dependencies installed for ${app_name}"
}

# Setup a single app
setup_app() {
    local app_dir=$1
    local app_name=$(basename "$app_dir")
    
    log_info "Setting up ${app_name}..."
    
    if [ ! -d "$app_dir" ]; then
        log_error "App directory not found: ${app_dir}"
        return 1
    fi
    
    create_venv "$app_dir"
    install_deps "$app_dir"
    
    # Create logs directory if needed
    mkdir -p "${app_dir}/logs"
    
    log_success "${app_name} setup complete"
}

# Run initial setup
run_setup() {
    log_info "Running initial setup..."
    
    check_python
    
    # Create main logs directory
    mkdir -p "$LOG_DIR"
    
    # Setup Hub
    setup_app "$HUB_DIR"
    
    # Setup Expenses App
    setup_app "$EXPENSES_DIR"
    
    # Generate secret key if not exists
    ENV_FILE="${SCRIPT_DIR}/.env"
    if [ ! -f "$ENV_FILE" ]; then
        log_info "Generating secret key..."
        SECRET_KEY=$(openssl rand -hex 32)
        echo "HUB_SECRET_KEY=${SECRET_KEY}" > "$ENV_FILE"
        chmod 600 "$ENV_FILE"
        log_success "Secret key generated and saved to .env"
    fi
    
    log_success "Initial setup complete!"
}

# Start the Hub
start_hub() {
    log_info "Starting Home Server Hub..."
    
    # Source environment
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
    else
        log_error "No .env file found. Run with --setup first."
        exit 1
    fi
    
    cd "$HUB_DIR"
    
    # Check if already running
    if [ -f "hub.pid" ]; then
        PID=$(cat hub.pid)
        if ps -p $PID > /dev/null 2>&1; then
            log_warning "Hub is already running (PID: $PID)"
            return
        else
            rm -f hub.pid
        fi
    fi
    
    # Activate venv
    source "${VENV_NAME}/bin/activate"
    
    # Start hub in background
    log_info "Starting hub on port 8000..."
    nohup python run.py > "${LOG_DIR}/hub_stdout.log" 2> "${LOG_DIR}/hub_stderr.log" &
    HUB_PID=$!
    echo $HUB_PID > hub.pid
    
    # Wait for startup
    sleep 2
    
    if ps -p $HUB_PID > /dev/null 2>&1; then
        log_success "Hub started successfully (PID: $HUB_PID)"
        log_info "Hub available at: http://localhost:8000"
    else
        log_error "Hub failed to start. Check logs at ${LOG_DIR}/hub_stderr.log"
        exit 1
    fi
    
    deactivate
}

# Stop all services
stop_services() {
    log_info "Stopping all services..."
    
    # Stop Hub
    if [ -f "${HUB_DIR}/hub.pid" ]; then
        PID=$(cat "${HUB_DIR}/hub.pid")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "Stopping Hub (PID: $PID)..."
            kill $PID 2>/dev/null || true
            sleep 2
            if ps -p $PID > /dev/null 2>&1; then
                log_warning "Force killing Hub..."
                kill -9 $PID 2>/dev/null || true
            fi
        fi
        rm -f "${HUB_DIR}/hub.pid"
    fi
    
    # Stop Expenses App if running
    if [ -f "${EXPENSES_DIR}/app.pid" ]; then
        PID=$(cat "${EXPENSES_DIR}/app.pid")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "Stopping Expenses App (PID: $PID)..."
            kill $PID 2>/dev/null || true
            sleep 2
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null || true
            fi
        fi
        rm -f "${EXPENSES_DIR}/app.pid"
    fi
    
    log_success "All services stopped"
}

# Check status of services
check_status() {
    echo ""
    echo "====== Home Server Status ======"
    echo ""
    
    # Hub status
    echo -n "Hub: "
    if [ -f "${HUB_DIR}/hub.pid" ]; then
        PID=$(cat "${HUB_DIR}/hub.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}Running${NC} (PID: $PID)"
        else
            echo -e "${RED}Not running${NC} (stale PID file)"
        fi
    else
        echo -e "${YELLOW}Stopped${NC}"
    fi
    
    # Expenses App status
    echo -n "Expenses App: "
    if [ -f "${EXPENSES_DIR}/app.pid" ]; then
        PID=$(cat "${EXPENSES_DIR}/app.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}Running${NC} (PID: $PID)"
        else
            echo -e "${RED}Not running${NC} (stale PID file)"
        fi
    else
        echo -e "${YELLOW}Stopped${NC}"
    fi
    
    echo ""
    
    # System info
    if is_raspberry_pi; then
        echo "Running on: Raspberry Pi"
        if command -v vcgencmd &> /dev/null; then
            TEMP=$(vcgencmd measure_temp | sed -E "s/.*=([0-9.]+).*/\1/")
            echo "CPU Temperature: ${TEMP}°C"
        fi
    else
        echo "Running on: $(uname -s) $(uname -m)"
    fi
    
    echo ""
}

# Show help
show_help() {
    echo ""
    echo "Home Server Startup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --setup     Run first-time setup (create venvs, install deps)"
    echo "  --start     Start the Hub (default)"
    echo "  --stop      Stop all services"
    echo "  --restart   Restart all services"
    echo "  --check     Check status of all services"
    echo "  --help      Show this help message"
    echo ""
}

# Main
main() {
    echo ""
    echo "====== Home Server Startup Script ======"
    echo ""
    
    case "${1:-}" in
        --setup)
            run_setup
            ;;
        --start|"")
            check_python
            start_hub
            ;;
        --stop)
            stop_services
            ;;
        --restart)
            stop_services
            sleep 2
            start_hub
            ;;
        --check)
            check_status
            ;;
        --help|-h)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
