"""
Application Runner
------------------
Entry point for the expense tracker application.

Usage:
    python run.py                  # Run on localhost:5000
    python run.py --host 0.0.0.0   # Run accessible on local network
    python run.py --port 8080      # Run on custom port
"""
import argparse
import sys
from pathlib import Path
from app import create_app

# Check if configuration exists, run setup if needed
try:
    from setup_config import check_and_setup
    if not check_and_setup():
        print("\n❌ Configuration required to run the application.")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Setup check failed: {e}")
    print("Please ensure config_private.py exists or run: python setup_config.py")
    sys.exit(1)


def main():
    """Parse arguments and run the Flask application."""
    parser = argparse.ArgumentParser(description='Expenses Tracker Application')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host to bind to (use 0.0.0.0 for network access)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run on (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    app = create_app()
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║           💰 Expenses Tracker                             ║
╠═══════════════════════════════════════════════════════════╣
║  Running on: http://{args.host}:{args.port}                       
║  Debug mode: {args.debug}                                      
║                                                           ║
║  Press Ctrl+C to stop                                     ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True  # Enable threading for concurrent requests
    )


if __name__ == '__main__':
    main()
