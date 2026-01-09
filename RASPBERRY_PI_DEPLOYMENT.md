# Raspberry Pi Deployment Guide

This guide covers deploying the Home Server Hub on a Raspberry Pi.

## Quick Start

### 1. First-Time Setup

```bash
# Clone or copy the project to your Raspberry Pi
cd /home/pi
git clone <your-repo-url> home-server

# Or if copying manually:
scp -r home-server/ pi@raspberrypi:/home/pi/

# Run setup
cd home-server
./start_server.sh --setup
```

### 2. Start the Hub

```bash
./start_server.sh --start
```

The hub will be available at `http://raspberrypi:8000`

### 3. Install as Systemd Service (Auto-start on Boot)

```bash
sudo ./systemd/install_service.sh

# Start the service
sudo systemctl start home-server-hub
```

## Commands Reference

### Startup Script

```bash
# Run initial setup (create venvs, install dependencies)
./start_server.sh --setup

# Start the hub
./start_server.sh --start

# Stop all services
./start_server.sh --stop

# Restart all services
./start_server.sh --restart

# Check status
./start_server.sh --check
```

### Systemd Commands

```bash
# Start
sudo systemctl start home-server-hub

# Stop
sudo systemctl stop home-server-hub

# Restart
sudo systemctl restart home-server-hub

# Status
sudo systemctl status home-server-hub

# View logs
sudo journalctl -u home-server-hub -f

# Enable auto-start on boot
sudo systemctl enable home-server-hub

# Disable auto-start
sudo systemctl disable home-server-hub
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Raspberry Pi                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Home Server Hub (Port 8000)             │   │
│  │                                                      │   │
│  │  • Runs 24/7                                        │   │
│  │  • Manages app lifecycle                            │   │
│  │  • Auto-shutdown idle apps (15 min default)         │   │
│  │  • Web dashboard for control                        │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         │ Starts/Stops                      │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Managed Applications                        │   │
│  │                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐          │   │
│  │  │ Expenses App    │  │ Future App      │          │   │
│  │  │ Port 5000       │  │ Port 5001       │          │   │
│  │  │ ⏱️ Auto-shutdown │  │ ⏱️ Auto-shutdown │          │   │
│  │  └─────────────────┘  └─────────────────┘          │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Hub Settings (`hub/config.yaml`)

```yaml
hub:
  name: "Home Server Hub"
  scheduler:
    enabled: true
    default_idle_timeout_minutes: 15  # Apps auto-shutdown after 15 min
    check_interval_seconds: 60

apps:
  expenses:
    name: "Expenses Tracker"
    port: 5000
    idle_timeout_minutes: 15  # Per-app override
```

### Environment Variables (`.env`)

The setup script automatically generates a secret key, but you can set it manually:

```bash
HUB_SECRET_KEY=your-secure-secret-key
```

## Logs

Logs are stored in the `logs/` directory:

```
logs/
├── hub.log            # Hub application log
├── app_manager.log    # App manager logs
├── api.log            # API request logs
├── scheduler.log      # Auto-shutdown scheduler logs
├── hub_stdout.log     # Hub stdout
├── hub_stderr.log     # Hub stderr
├── expenses_stdout.log
└── expenses_stderr.log
```

## Troubleshooting

### Check if hub is running

```bash
./start_server.sh --check
```

### View hub logs

```bash
tail -f logs/hub.log
tail -f logs/hub_stderr.log
```

### Hub won't start

1. Check that Python 3 is installed: `python3 --version`
2. Check that the virtual environment exists: `ls hub/venv/bin/python`
3. Check the error logs: `cat logs/hub_stderr.log`
4. Run setup again: `./start_server.sh --setup`

### App won't start from hub

1. Check the app logs in the hub dashboard (Logs button)
2. Check the terminal: `cat logs/expenses_stderr.log`
3. Verify the app's virtual environment: `ls expensesApp/venv/bin/python`
4. Try running the app manually:
   ```bash
   cd expensesApp
   source venv/bin/activate
   python run.py
   ```

### Port already in use

Find and kill the process using the port:

```bash
# Find process using port 8000
lsof -i :8000

# Kill it (replace PID with actual PID)
kill PID
```

### Raspberry Pi-specific Issues

#### CPU Temperature

Monitor temperature to ensure it's not overheating:

```bash
vcgencmd measure_temp
```

If temperature is too high (>80°C), ensure proper ventilation or add a fan.

#### Memory Usage

Check memory with:

```bash
free -h
```

The hub itself uses minimal memory (~50MB). Apps use more during operation.

## Security Notes

1. **Firewall**: Consider enabling a firewall if the Pi is exposed to the internet:
   ```bash
   sudo apt install ufw
   sudo ufw allow 22    # SSH
   sudo ufw allow 8000  # Hub
   sudo ufw enable
   ```

2. **HTTPS**: For internet-facing deployments, use a reverse proxy (nginx) with Let's Encrypt certificates.

3. **Authentication**: The hub currently uses a simple password. For sensitive deployments, consider:
   - VPN access only
   - Additional authentication layers
   - IP whitelisting

## Adding New Apps

1. Create a new app directory at the same level as `expensesApp/`
2. Add it to `hub/config.yaml`:
   ```yaml
   apps:
     myapp:
       name: "My New App"
       description: "Description here"
       icon: "🎮"
       color: "#2196F3"
       path: "../myapp"
       entry: "run.py"
       port: 5001
       health_endpoint: "/"
   ```
3. Run setup: `./start_server.sh --setup`
4. Reload the hub dashboard

## Updates

To update the home server:

```bash
# Stop services
./start_server.sh --stop

# Pull updates
git pull

# Run setup to install any new dependencies
./start_server.sh --setup

# Start again
./start_server.sh --start
```

Or if using systemd:

```bash
sudo systemctl stop home-server-hub
git pull
./start_server.sh --setup
sudo systemctl start home-server-hub
```
