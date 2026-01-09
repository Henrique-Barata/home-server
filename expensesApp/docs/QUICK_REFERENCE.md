# 🚀 Quick Reference

## First Time Setup (Automated - Recommended)
```bash
# 1. Install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Run setup wizard (or just run the app - it will prompt you)
python setup_config.py

# 3. Initialize database and run
python init_db.py
python run.py
```

The setup wizard will ask for:
- User names (e.g., Alice, Bob)
- App password
- Optional: custom categories

## First Time Setup (Manual - 3 steps)
```bash
# 1. Configure
cp config_private.py.template config_private.py
# Edit config_private.py with your settings

# 2. Install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python init_db.py

# 3. Run
python run.py
```

## Daily Use
```bash
# Start the app
source venv/bin/activate
python run.py

# Access: http://localhost:5000
```

## Common Tasks

### Update Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Backup Data
```bash
cp -r data/ ~/backups/expenses-$(date +%Y%m%d)
```

### Network Access
```bash
python run.py --host 0.0.0.0
# Access from other devices: http://YOUR_IP:5000
```

### Reset Database
```bash
rm data/expenses.db
python init_db.py
```

## Files You Should Modify
- ✅ `config_private.py` - Your personal settings
- ✅ `app/templates/` - Customize the UI
- ✅ `app/static/css/style.css` - Change styling

## Files You Should NOT Commit
- ❌ `config_private.py` - Contains passwords
- ❌ `data/*.db` - Your personal data
- ❌ `exports/*.xlsx` - Your financial exports
- ❌ `.env` - Environment variables
- ❌ `venv/` - Virtual environment

## Troubleshooting

**Can't start app:**
```bash
source venv/bin/activate
```

**Wrong password:**
- Check `config_private.py` → `APP_PASSWORD`
- Restart app after changes

**Database error:**
```bash
python init_db.py
```

**Port already in use:**
```bash
python run.py --port 8080
```

## Get Your Local IP
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Or simply
hostname -I
```

## Environment Variables (Alternative to config_private.py)
```bash
export SECRET_KEY="your-secret-key"
export APP_PASSWORD="your-password"
python run.py
```
