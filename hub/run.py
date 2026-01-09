#!/usr/bin/env python3
"""
Home Server Hub Runner
----------------------
Entry point for the home server hub application.

Usage:
    python run.py                  # Run on 0.0.0.0:8000 (network accessible)
    python run.py --port 8080      # Run on custom port
    python run.py --debug          # Enable debug mode
"""
import argparse
import os
import sys
from pathlib import Path

# Add hub to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app


def main():
    """Parse arguments and run the Hub application."""
    parser = argparse.ArgumentParser(description='Home Server Hub')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0 for network access)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to run on (default: 8000)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Load environment variables - require secret key in production
    secret_key = os.environ.get('HUB_SECRET_KEY')
    if not secret_key:
        if args.debug:
            # Allow development mode with auto-generated key
            import secrets
            secret_key = secrets.token_hex(32)
            print("⚠️  No HUB_SECRET_KEY set - using auto-generated key (dev mode only)")
        else:
            print("❌ HUB_SECRET_KEY environment variable is required!")
            print("   Set it with: export HUB_SECRET_KEY='your-secure-key'")
            print("   Or run with --debug flag for development mode")
            sys.exit(1)
    
    # Set the environment variable for the app factory
    os.environ['HUB_SECRET_KEY'] = secret_key
    
    app = create_app({
        'SECRET_KEY': secret_key,
        'DEBUG': args.debug
    })
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║           🏠 Home Server Hub                              ║
╠═══════════════════════════════════════════════════════════╣
║  Running on: http://{args.host}:{args.port}                       
║  Debug mode: {args.debug}                                      
║                                                           ║
║  Press Ctrl+C to stop                                     ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
