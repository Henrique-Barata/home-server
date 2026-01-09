# 🏠 Home Server

A self-hosted application suite designed for Raspberry Pi and low-resource systems. Manage multiple home applications from a centralized hub with minimal overhead and maximum simplicity.

## 📦 What's Inside

This repository contains:

### 1. **Hub** - Central Management Dashboard
A lightweight Flask application that provides a web interface to manage, monitor, and control all your home server apps from one place.

**Features:**
- 🎛️ Start, stop, and restart apps via web UI
- 📊 Real-time status monitoring
- 🔗 Quick links to running applications
- 🎨 Clean, responsive interface
- 🐳 Container-ready (future)

### 2. **Expenses App** - Household Expense Tracker
A simple, privacy-focused expense tracking application optimized for shared household budgets.

**Features:**
- 💰 Track fixed expenses (rent, subscriptions)
- 💡 Monitor utilities (electricity, gas, water, internet)
- 🍕 Log food and miscellaneous purchases
- 📦 Categorize stuff/items with custom types
- 📈 Monthly spending summaries per person
- 📊 Excel exports for analysis
- 🔐 Simple password-based auth

### Future Apps
The modular architecture makes it easy to add more apps. Just drop them into the project and configure them in the hub.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Raspberry Pi OS includes Python 3.9+)
- **Git** (optional, for cloning)
- **4GB+ storage** (for apps and data)

### Installation

#### Option A: Clone from Git (Recommended)

```bash
# Clone the repository
git clone <your-repository-url> home-server
cd home-server
```

#### Option B: Download and Extract

Download the repository as a ZIP and extract it to your desired location.

### Setup & Run

You can run each app independently or use the hub to manage them all:

#### 1. Set up the Hub (Management Dashboard)

```bash
cd hub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the hub
python run.py
```

Access the hub at **`http://localhost:8000`** (or `http://<your-pi-ip>:8000` from other devices).

#### 2. Set up the Expenses App

```bash
cd expensesApp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the interactive setup wizard
python setup_config.py

# Initialize the database
python init_db.py

# Run the app
python run.py
```

Access the expenses app at **`http://localhost:5000`**.

Or, once the hub is running, you can start the Expenses App from the hub dashboard with one click!

---

## 🛠️ Configuration

### Hub Configuration

Edit `hub/config.yaml` to register your applications:

```yaml
hub:
  name: "Home Server Hub"
  description: "Central management for home server applications"
  version: "1.0.0"

apps:
  expenses:
    name: "Expenses Tracker"
    description: "Track household expenses and settlements"
    icon: "💰"
    color: "#4CAF50"
    path: "../expensesApp"
    entry: "run.py"
    port: 5000
    host: "127.0.0.1"
```

### Expenses App Configuration

The Expenses App uses `config_private.py` for sensitive settings. Run the setup wizard to create it interactively:

```bash
cd expensesApp
python setup_config.py
```

Or manually copy and edit the template:

```bash
cp config_private.py.template config_private.py
# Edit config_private.py with your SECRET_KEY, APP_PASSWORD, and USERS
```

**⚠️ Important:** `config_private.py` contains sensitive data and is excluded from version control (`.gitignore`).

---

## 🌐 Network Access

To access the hub and apps from other devices on your local network:

```bash
# Hub
cd hub
python run.py --host 0.0.0.0 --port 8000

# Expenses App
cd expensesApp
python run.py --host 0.0.0.0 --port 5000
```

Then access from any device on your network:
- Hub: `http://<raspberry-pi-ip>:8000`
- Expenses: `http://<raspberry-pi-ip>:5000`

---

##  Raspberry Pi Deployment

### Recommended Setup

1. **Transfer the project to your Pi:**
   ```bash
   # From your Mac/PC:
   rsync -avP ~/path/to/home-server pi@raspberrypi.local:/home/pi/
   
   # Or clone directly on the Pi:
   ssh pi@raspberrypi.local
   git clone <your-repo-url> ~/home-server
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip git
   ```

3. **Set up and run the hub** (follow Quick Start instructions above).

4. **Create systemd services** for auto-start on boot:

   **Hub Service** (`/etc/systemd/system/home-server-hub.service`):
   ```ini
   [Unit]
   Description=Home Server Hub
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/home-server/hub
   Environment="HUB_SECRET_KEY=your-secure-secret-key-here"
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

   **Expenses App Service** (optional, or manage via hub):
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

---

## 📁 Project Structure

```
home-server/
├── README.md                    # This file
├── hub/                         # Central management dashboard
│   ├── app/                     # Flask application
│   │   ├── routes/             # API and UI routes
│   │   ├── services/           # App management logic
│   │   ├── templates/          # HTML templates
│   │   └── static/             # CSS assets
│   ├── config.yaml             # App registry configuration
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                  # Entry point
│   └── README.md               # Hub documentation
├── expensesApp/                # Expense tracking application
│   ├── app/                    # Flask application
│   │   ├── models/            # Database models
│   │   ├── routes/            # URL handlers
│   │   ├── templates/         # HTML templates
│   │   └── static/            # CSS files
│   ├── data/                   # SQLite database (gitignored)
│   ├── exports/                # Excel exports (gitignored)
│   ├── docs/                   # Detailed documentation
│   ├── scripts/                # Utilities & migrations
│   ├── ai/                     # AI context docs
│   ├── config_private.py       # Your config (gitignored)
│   ├── config_private.py.template
│   ├── requirements.txt
│   ├── setup_config.py         # Interactive setup wizard
│   ├── init_db.py              # Database initialization
│   ├── run.py                  # Entry point
│   └── README.md               # Expenses app documentation
└── [future apps]/              # Add more apps here
```

---

## 🔒 Security & Privacy

This is a **local-network, self-hosted** system designed for private use:

### Security Considerations

- **Private data:** All databases and exports are excluded from git (`.gitignore`).
- **Credentials:** Sensitive settings live in `config_private.py` (not tracked).
- **Network exposure:** By default, apps bind to `127.0.0.1` (localhost only).
- **Password protection:** The Expenses App uses simple password authentication.

### Best Practices for Production Use

1. **Strong passwords:** Use long, random passwords in your configs.
2. **HTTPS:** Use a reverse proxy (nginx, Caddy) with Let's Encrypt for SSL.
3. **Firewall:** Restrict access to your Pi using `ufw` or router settings.
4. **Backups:** Regularly back up `expensesApp/data/` and other critical files.
5. **Updates:** Keep the Pi OS and Python packages updated.
6. **VPN:** For remote access, use a VPN (Tailscale, WireGuard) instead of exposing ports.

---

## 📖 Documentation

Each application has its own detailed documentation:

- **Hub:** [hub/README.md](hub/README.md)
- **Expenses App:** [expensesApp/README.md](expensesApp/README.md)
- **Expenses Setup Guide:** [expensesApp/docs/SETUP.md](expensesApp/docs/SETUP.md)
- **Expenses Quick Reference:** [expensesApp/docs/QUICK_REFERENCE.md](expensesApp/docs/QUICK_REFERENCE.md)
- **Contributing:** [expensesApp/docs/CONTRIBUTING.md](expensesApp/docs/CONTRIBUTING.md)

---

## 🎯 Use Cases

- **Raspberry Pi home server:** Run on a Pi 3/4/5 with minimal resources.
- **Shared household:** Track expenses for roommates or partners.
- **Local-first apps:** Keep your data on your network, not in the cloud.
- **Learning project:** Simple, well-documented Flask apps for learning.
- **Modular platform:** Add more apps as you need them.

---

## 🛣️ Roadmap

### Hub
- [ ] Docker container support
- [ ] App health checks and auto-restart
- [ ] Resource monitoring (CPU, memory)
- [ ] Log viewer in the UI
- [ ] User authentication
- [ ] API tokens for automation

### Expenses App
- [ ] Multi-currency support
- [ ] Recurring expense templates
- [ ] Budget goals and alerts
- [ ] Charts and visualizations
- [ ] Mobile-friendly UI improvements
- [ ] API for integrations

### Platform
- [ ] Photo gallery app
- [ ] Media server integration
- [ ] IoT device dashboard
- [ ] Backup/restore utilities

---

## 🤝 Contributing

Contributions are welcome! This is a personal project, but if you find it useful:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [expensesApp/docs/CONTRIBUTING.md](expensesApp/docs/CONTRIBUTING.md) for guidelines.

---

## 📝 License

MIT License - see individual app LICENSE files for details.

---

## 💡 Tips & Troubleshooting

### Common Issues

**Hub can't find the Expenses App:**
- Check that `hub/config.yaml` has the correct `path` (should be `../expensesApp`).
- Ensure the `expensesApp/run.py` file exists.

**Expenses App won't start (400 error in hub):**
- The app needs `config_private.py` to exist. Run `python setup_config.py` first.
- Ensure the venv exists and has dependencies: `pip install -r requirements.txt`.

**Can't access from other devices:**
- Make sure you're running with `--host 0.0.0.0`.
- Check firewall rules on the Pi: `sudo ufw status`.
- Verify the Pi's IP address: `hostname -I`.

**Database errors:**
- Run `python init_db.py` to initialize/reset the database.
- Check file permissions in `expensesApp/data/`.

### Getting Help

Check the individual app READMEs and documentation folders for detailed guides. For issues, open a GitHub issue (once public).

---

## 🙏 Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [SQLite](https://www.sqlite.org/) - Embedded database
- [psutil](https://github.com/giampaolo/psutil) - Process monitoring
- [PyYAML](https://pyyaml.org/) - Configuration parsing

Optimized for [Raspberry Pi OS](https://www.raspberrypi.com/software/).

---

**Happy self-hosting! 🏡**