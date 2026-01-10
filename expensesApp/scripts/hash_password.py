#!/usr/bin/env python3
"""
Password Hashing Utility
------------------------
Generate secure password hashes for config_private.py.

Usage:
    python -m scripts.hash_password
    python scripts/hash_password.py

This script will prompt for a password and output a secure hash
that can be used as APP_PASSWORD in config_private.py.
"""
import getpass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from werkzeug.security import generate_password_hash, check_password_hash


def generate_hash(password: str) -> str:
    """Generate a secure hash for the given password."""
    # Use PBKDF2 with SHA-256 and 600,000 iterations (OWASP recommendation)
    return generate_password_hash(password, method='pbkdf2:sha256:600000')


def main():
    """Main entry point for password hashing utility."""
    print("=" * 60)
    print("Expenses App - Password Hashing Utility")
    print("=" * 60)
    print()
    print("This utility generates a secure password hash for your app.")
    print("The hash should be used as APP_PASSWORD in config_private.py")
    print()
    
    # Get password with confirmation
    while True:
        password = getpass.getpass("Enter password: ")
        if not password:
            print("Error: Password cannot be empty.")
            continue
            
        if len(password) < 8:
            print("Warning: Password is short. Consider using at least 8 characters.")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                continue
        
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("Error: Passwords do not match. Try again.")
            continue
        
        break
    
    # Generate hash
    password_hash = generate_hash(password)
    
    # Verify the hash works
    if not check_password_hash(password_hash, password):
        print("Error: Hash verification failed. This should not happen.")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("SUCCESS! Your secure password hash:")
    print("=" * 60)
    print()
    print(f'APP_PASSWORD = "{password_hash}"')
    print()
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. Open config_private.py")
    print("2. Replace the APP_PASSWORD line with the line above")
    print("3. Save the file")
    print("4. Restart the application")
    print()
    print("Note: The hash is different each time you run this script,")
    print("even for the same password. This is expected and secure.")
    print()


if __name__ == "__main__":
    main()
