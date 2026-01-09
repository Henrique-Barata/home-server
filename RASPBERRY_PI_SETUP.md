# Raspberry Pi Setup Guide

Quick reference for deploying home-server to your Raspberry Pi.

## Quick Start on Raspberry Pi

### 1. Transfer the Code

**Option A: Clone from Git (recommended if you have a repo)**
```bash
ssh pi@<raspberry-pi-ip>
cd ~
git clone <your-repo-url> home-server
cd home-server
```

**Option B: Copy from your Mac**
```bash
# From your Mac:
rsync -avP ~/CODE/home-server pi@<raspberry-pi-ip>:/home/pi/
```

### 2. Install System Dependencies

```bash
# On the Pi:
sudo apt update
sudo apt install -y python3-venv python3-pip git
```

### 3. Set Up the Hub

```bash
cd ~/home-server/hub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Generate a secret key
export HUB_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Run the hub
python run.py --host 0.0.0.0 --port 8000
```

Access the hub at: `http://<raspberry-pi-ip>:8000`

### 4. Set Up the Expenses App

```bash
cd ~/home-server/expensesApp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the setup wizard (creates config_private.py)
python setup_config.py

# Initialize the database
python init_db.py

# Test run the app
python run.py --host 0.0.0.0 --port 5000
```

Access the expenses app at: `http://<raspberry-pi-ip>:5000`

## Troubleshooting

### Hub Can't Start the Expenses App (400 Error)

**Problem**: When clicking "Start App" in the hub, you get a 400 error.

**Solution**: The expenses app needs `config_private.py` before it can start.

```bash
cd ~/home-server/expensesApp

# Quick non-interactive setup
python3 -c "
import secrets
config = f'''
SECRET_KEY = \"{secrets.token_hex(32)}\"
APP_PASSWORD = \"changeme\"
USERS = [\"User1\", \"User2\"]
'''
with open('config_private.py', 'w') as f:
    f.write(config)
"

# Or use the interactive wizard
python setup_config.py

# Ensure venv and dependencies exist
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python init_db.py
```

Now try starting from the hub again, or check logs in the hub UI.

### View Logs in the Hub

1. Open the hub UI at `http://<raspberry-pi-ip>:8000`
2. Click the **"Logs"** button on the expenses app card
3. Switch between `stdout` and `stderr` to see different output
4. Click **Refresh** to reload logs

Logs are also saved in `hub/logs/`:
```bash
cd ~/home-server/hub/logs
cat expenses_stderr.log
cat expenses_stdout.log
```

### Check if Apps are Running

```bash
# Check processes
ps aux | grep run.py

# Check ports
sudo netstat -tulpn | grep -E '8000|5000'

# Or use the hub API
curl http://localhost:8000/api/apps
```

### PID File Issues

If an app shows as running but isn't:

```bash
cd ~/home-server/expensesApp
rm -f app.pid

# Then restart from the hub or manually
```

## Systemd Services (Auto-start on Boot)

### Hub Service

Create `/etc/systemd/system/home-server-hub.service`:

```ini
[Unit]
Description=Home Server Hub
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/home-server/hub
Environment="HUB_SECRET_KEY=your-secret-key-here"
ExecStart=/home/pi/home-server/hub/venv/bin/python run.py --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now home-server-hub
sudo journalctl -u home-server-hub -f
```

### Expenses App Service (Optional)

Since the hub can manage the expenses app, you might not need a systemd service. But if you want one:

Create `/etc/systemd/system/home-server-expenses.service`:

```ini
[Unit]
Description=Expenses Tracker
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/home-server/expensesApp
ExecStart=/home/pi/home-server/expensesApp/venv/bin/python run.py --host 0.0.0.0 --port 5000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now home-server-expenses
```

## Common Commands

### Hub

```bash
# Start hub manually
cd ~/home-server/hub
source venv/bin/activate
python run.py --host 0.0.0.0 --port 8000

# View hub logs (if using systemd)
sudo journalctl -u home-server-hub -f

# Restart hub service
sudo systemctl restart home-server-hub
```

### Expenses App

```bash
# Start manually
cd ~/home-server/expensesApp
source venv/bin/activate
python run.py --host 0.0.0.0 --port 5000

# View logs
tail -f ~/home-server/hub/logs/expenses_stderr.log

# Reinitialize database (WARNING: deletes all data!)
python init_db.py
```

## Network Access

- **Local only**: Use `--host 127.0.0.1` (default for expenses app)
- **Local network**: Use `--host 0.0.0.0` (recommended for hub and Pi deployment)
- **Find Pi IP**: `hostname -I` on the Pi

## Security Checklist

- [ ] Changed default Pi password
- [ ] Set strong `APP_PASSWORD` in `expensesApp/config_private.py`
- [ ] Generated secure `HUB_SECRET_KEY`
- [ ] Firewall configured (`sudo ufw enable && sudo ufw allow 8000,5000/tcp`)
- [ ] Only expose on local network (don't port-forward to internet)
- [ ] Regular backups of `expensesApp/data/` directory
- [ ] Keep Pi OS updated: `sudo apt update && sudo apt upgrade`

## Backup & Restore

### Backup Expenses Data

```bash
# On the Pi
cd ~/home-server/expensesApp
tar -czf expenses-backup-$(date +%Y%m%d).tar.gz data/ exports/ config_private.py

# Copy to your Mac
scp pi@<raspberry-pi-ip>:~/home-server/expensesApp/expenses-backup-*.tar.gz ~/backups/
```

### Restore

```bash
cd ~/home-server/expensesApp
tar -xzf expenses-backup-YYYYMMDD.tar.gz
```

## Performance Tips

- **Pi 3/4/5**: Should handle both apps easily
- **Pi Zero/2**: Might struggle; run only the expenses app
- **SD Card**: Use a quality Class 10 or UHS-I card
- **Monitor resources**: `htop` or the planned hub resource monitor feature

## Getting Help

1. Check logs in the hub UI (click "Logs" button)
2. View systemd logs: `sudo journalctl -u home-server-hub -n 100`
3. Check app logs: `~/home-server/hub/logs/`
4. Verify config files exist and are valid
5. Test apps manually before using the hub

## Quick Health Check

```bash
# All-in-one status check
curl -s http://localhost:8000/api/apps | python3 -m json.tool
```

Should return JSON with app statuses. If the hub isn't running, you'll get a connection error.
