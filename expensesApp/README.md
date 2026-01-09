# Expenses Tracker

A lightweight, local-network expense tracking web application optimized for low-resource systems.

## 🚀 Quick Start

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python setup_config.py  # Interactive wizard
python init_db.py
python run.py
```

Access at `http://localhost:5000`

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed setup instructions
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Common commands
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute
- **[More Docs](docs/)** - All documentation

## Technology Choices

- **Flask**: Minimal overhead, proven, simple to deploy
- **SQLite**: File-based database, no separate server needed, perfect for 1-2 users
- **Flask-Login**: Simple authentication without complexity
- **Vanilla HTML/CSS**: No heavy frontend frameworks, fast loading

## Setup

### Quick Setup (Recommended)

The app includes an interactive setup wizard that will guide you through the configuration:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd expensesApp

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the setup wizard (or just run the app, it will prompt you)
python setup_config.py
```

The wizard will ask you for:
- **User names**: People to track (e.g., Alice, Bob)
- **Password**: Your login password
- **Categories** (optional): Customize expense types

That's it! The wizard will:
- ✅ Generate a secure secret key automatically
- ✅ Create your `config_private.py` file
- ✅ Set up everything you need

Then initialize the database and run:
```bash
python init_db.py
python run.py
```

### Manual Setup (Alternative)

If you prefer to configure manually:
### Manual Setup (Alternative)

If you prefer to configure manually:

```bash
# Copy the template file
cp config_private.py.template config_private.py
# Edit config_private.py with your settings
```

**Edit `config_private.py` and configure:**
- `SECRET_KEY`: A random, long string for Flask session security
- `APP_PASSWORD`: Your login password
- `USERS`: List of people to track (e.g., `["Alice", "Bob"]`)

**⚠️ IMPORTANT**: Never commit `config_private.py` to git! It's already in `.gitignore`.

### Running the App

After setup, initialize the database and start the application:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

## Login

Access the app and log in using the password you set in `config_private.py` (`APP_PASSWORD`).

## Project Structure
```
expensesApp/
├── app/                      # Application code
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration loader
│   ├── models/              # Database models
│   ├── routes/              # URL handlers
│   ├── templates/           # HTML templates
│   └── static/              # CSS files
├── docs/                    # Documentation
│   ├── SETUP.md            # Detailed setup guide
│   ├── QUICK_REFERENCE.md  # Quick commands
│   ├── AUTOMATED_SETUP.md  # Setup wizard docs
│   ├── CONTRIBUTING.md     # How to contribute
│   └── ...                 # More guides
├── scripts/                 # Utilities & migrations
│   ├── migrate_*.py        # Database migrations
│   └── verify_before_commit.py
├── data/                    # SQLite database (gitignored)
├── exports/                 # Excel exports (gitignored)
├── ai/                      # AI context documentation
├── run.py                   # Application entry point
├── setup_config.py          # Interactive setup wizard
├── init_db.py               # Database initialization
├── config_private.py        # Your config (gitignored)
├── config_private.py.template
├── requirements.txt
├── LICENSE
└── README.md
```

## Features
- Dashboard with monthly expense overview
- Fixed expenses management (rent, subscriptions)
- Utilities tracking (electricity, gas, water, internet)
- Food expenses
- Stuff/items with custom categories
- Other miscellaneous expenses
- Per-person spending summary
- Excel export compatible with Google Sheets

## Network Access
To access from other devices on your network:
```bash
python run.py --host 0.0.0.0
```
Then access via your machine's local IP address (e.g., `http://192.168.1.100:5000`).

## Security Notes

- The database and exports contain personal financial data and are excluded from git
- All sensitive configuration is in `config_private.py` (not tracked)
- For production use, consider:
  - Using HTTPS (set `SESSION_COOKIE_SECURE = True`)
  - Strong passwords
  - Network-level security (firewall, VPN)
  - Regular backups of the `data/` directory

## Customization

You can customize expense categories in your `config_private.py`:
```python
UTILITY_TYPES = ["Electricity", "Gas", "Water", "Internet", "Phone"]
FIXED_EXPENSE_TYPES = ["Rent", "Insurance", "Gym", "Streaming"]
```

## Alternative Configuration Methods

Instead of `config_private.py`, you can use environment variables:
```bash
export SECRET_KEY="your-secret-key"
export APP_PASSWORD="your-password"
python run.py
```

## Documentation

For detailed documentation, see the [`docs/`](docs/) folder:

- **Setup & Configuration**: [docs/SETUP.md](docs/SETUP.md)
- **Quick Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
- **Contributing**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **Git Setup**: [docs/GIT_SETUP_SUMMARY.md](docs/GIT_SETUP_SUMMARY.md)

## Database Migrations

Migration scripts are in the [`scripts/`](scripts/) folder. See [scripts/README.md](scripts/README.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.
