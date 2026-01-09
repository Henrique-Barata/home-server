# Pre-Commit Checklist

Before committing to git, verify:

## ✅ Configuration Files
- [ ] `config_private.py` is NOT staged (should be in .gitignore)
- [ ] Personal passwords/keys are NOT in any committed files
- [ ] `config_private.py.template` has placeholder values only

## ✅ Data Files
- [ ] No `*.db` files in `data/` are staged
- [ ] No `*.xlsx` or `*.csv` files in `exports/` are staged
- [ ] Only `.gitkeep` or `README.md` files in data/exports directories

## ✅ Environment Files
- [ ] `.env` file is NOT staged (if you use it)
- [ ] `.env.example` contains only placeholder values

## ✅ Personal Information
- [ ] No personal names in code comments
- [ ] No hardcoded passwords anywhere
- [ ] No personal URLs or paths in committed code

## ✅ Documentation
- [ ] README.md updated if you changed features
- [ ] Setup instructions are accurate
- [ ] No personal data in example configurations

## Quick Check Command

Run this to see what's about to be committed:
```bash
git status
git diff --cached
```

Look for:
- Personal names (Henrique, Carlota, etc.)
- Passwords or API keys
- Database files
- Export files

## If You Accidentally Committed Private Data

```bash
# Remove file from git but keep locally
git rm --cached config_private.py

# Or to remove from history (use carefully!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config_private.py" \
  --prune-empty --tag-name-filter cat -- --all
```

## Safe to Commit

- Python source code (without secrets)
- HTML templates (without personal data)
- CSS files
- Requirements.txt
- Migration scripts
- Documentation files
- .gitignore
- Template files
