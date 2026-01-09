# Quick Setup Guide

The Expenses Tracker now includes an **automated setup wizard**! 🎉

## Automated Setup (Recommended)

Just run the app and it will guide you through the setup:

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run the setup wizard
python setup_config.py
```

### What the Setup Wizard Does

The wizard will interactively ask you for:

1. **👥 User Names**: Enter the people you want to track (comma-separated)
   - Example: `Alice, Bob` or `John, Jane`

2. **🔐 Password**: Set your app login password
   - You'll be asked to confirm it

3. **⚙️ Categories** (optional): Customize expense types
   - Or just press Enter to use sensible defaults

The wizard automatically:
- ✅ Generates a secure random SECRET_KEY (64 characters)
- ✅ Creates `config_private.py` with your settings
- ✅ Validates your inputs

### After Setup

Initialize the database and run the app:

```bash
python init_db.py  # Creates the database
python run.py      # Starts the app
```

## Manual Setup (If You Prefer)

If you want to configure manually:

```bash
cp config_private.py.template config_private.py
# Edit config_private.py with your values
```

## First Run

When you run `python run.py` for the first time:
- If `config_private.py` doesn't exist, you'll be prompted to run the setup wizard
- Just follow the interactive prompts!

## Example Setup Session

```
==================================================
  💰 Expenses Tracker - Initial Setup
==================================================

This wizard will help you configure the application.
Your settings will be saved to config_private.py

🔑 Generating secure secret key... ✅ Done

👥 User Configuration
==================================================
Enter the names of people to track expenses for.
Examples: Alice, Bob | John, Jane | You, Partner

Enter user names (comma-separated): Alice, Bob

✅ Users configured: Alice, Bob
Is this correct? (y/n): y

🔐 Password Configuration
==================================================
Set a password to access the application.
Choose something secure but memorable.

Enter app password: ********
Confirm password: ********

⚙️  Optional Settings
==================================================
Do you want to customize expense categories?
(Default categories will be used if you skip this)

Customize categories? (y/n, default: n): n

📝 Creating Configuration
==================================================
✅ Configuration saved to: /path/to/config_private.py

✨ Setup Complete!
==================================================
👥 Users: Alice, Bob
🔐 Password: ********
🔑 Secret Key: Generated securely

🚀 You can now run the application with: python run.py
```

## Generate a Random Secret Key (Manual Method)

**Option 1 - Python:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Option 2 - OpenSSL:**
```bash
openssl rand -hex 32
```

---

## Database Initialization

After configuration (automated or manual):

```bash
python init_db.py
```

This creates the SQLite database with all necessary tables.

## Running the App

Open your browser to `http://localhost:5000` and log in with your configured password.

## Troubleshooting

**"config_private.py not found" warning:**
- Make sure you copied `config_private.py.template` to `config_private.py`
- The file must be in the root directory (same level as `run.py`)

**Can't log in:**
- Check that `APP_PASSWORD` in `config_private.py` matches what you're entering
- The file is loaded when the app starts, so restart after changes

**Network access:**
```bash
python run.py --host 0.0.0.0
```
Then use your local IP (e.g., `192.168.1.100:5000`)

## Security Reminders

✅ **DO:**
- Keep `config_private.py` secure and private
- Use a strong `APP_PASSWORD`
- Backup your `data/` folder regularly

❌ **DON'T:**
- Commit `config_private.py` to git
- Share your database file publicly
- Use default/weak passwords
