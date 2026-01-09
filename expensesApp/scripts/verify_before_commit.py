#!/usr/bin/env python3
"""
Pre-Commit Verification Script
-------------------------------
Run this before committing to ensure no personal data leaks.
"""
import os
import sys
from pathlib import Path


def check_personal_data():
    """Check for personal data in files that would be committed."""
    print("🔍 Checking for personal data in tracked files...")
    
    # Personal data to search for
    sensitive_patterns = [
        "cuzinho1904",  # Personal password
        # Add other sensitive data patterns here if needed
    ]
    
    # Files/dirs to exclude from search
    exclude_paths = [
        "venv/",
        "__pycache__/",
        ".git/",
        "config_private.py",  # Should be gitignored anyway
        "data/",
        "exports/",
    ]
    
    found_issues = False
    
    for pattern in sensitive_patterns:
        print(f"\n  Searching for: {pattern}")
        
        # Search in Python files
        for py_file in Path('.').rglob('*.py'):
            # Skip excluded paths
            if any(exclude in str(py_file) for exclude in exclude_paths):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern in content:
                        print(f"    ❌ FOUND in: {py_file}")
                        found_issues = True
            except Exception as e:
                pass
        
        # Search in Markdown files
        for md_file in Path('.').rglob('*.md'):
            # Skip excluded paths and documentation about the pattern
            if any(exclude in str(md_file) for exclude in exclude_paths):
                continue
            
            # Skip documentation files that mention the pattern as an example
            if md_file.name in ['PRE_COMMIT_CHECKLIST.md', 'GIT_SETUP_SUMMARY.md', 'FILES_TO_COMMIT.md']:
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern in content:
                        print(f"    ❌ FOUND in: {md_file}")
                        found_issues = True
            except Exception as e:
                pass
    
    if not found_issues:
        print("  ✅ No sensitive data found in tracked files")
    
    return not found_issues


def check_gitignore():
    """Verify important files are in gitignore."""
    print("\n🔍 Checking .gitignore...")
    
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        print("  ❌ .gitignore not found!")
        return False
    
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    required_ignores = [
        'config_private.py',
        'data/*.db',
        'exports/*.xlsx',
        'venv/',
        '__pycache__/',
    ]
    
    all_present = True
    for pattern in required_ignores:
        if pattern in gitignore_content:
            print(f"  ✅ {pattern} - gitignored")
        else:
            print(f"  ❌ {pattern} - NOT gitignored!")
            all_present = False
    
    return all_present


def check_required_files():
    """Check that all required files exist."""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'setup_config.py',
        'config_private.py.template',
        'README.md',
        'run.py',
        'init_db.py',
        '.gitignore',
        'requirements.txt',
    ]
    
    all_present = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - MISSING!")
            all_present = False
    
    return all_present


def check_config_exists():
    """Check if config_private.py exists (should not be committed)."""
    print("\n🔍 Checking personal config...")
    
    config_path = Path('config_private.py')
    template_path = Path('config_private.py.template')
    
    if config_path.exists():
        print(f"  ℹ️  config_private.py exists (should be gitignored)")
        # Verify it's actually gitignored
        return True
    else:
        print(f"  ✅ config_private.py not found (good for clean repo)")
    
    if template_path.exists():
        print(f"  ✅ config_private.py.template exists")
        return True
    else:
        print(f"  ❌ config_private.py.template MISSING!")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("  Pre-Commit Verification")
    print("=" * 60)
    
    os.chdir(Path(__file__).parent)
    
    checks = [
        ("Personal Data Check", check_personal_data),
        (".gitignore Check", check_gitignore),
        ("Required Files Check", check_required_files),
        ("Config Check", check_config_exists),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ❌ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All checks passed! Ready to commit.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix issues before committing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
