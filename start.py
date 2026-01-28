#!/usr/bin/env python3
"""
Startup script for the Facebook Marketplace Bot.
This script provides a simple way to start the application with proper setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import selenium
        import undetected_chromedriver
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_accounts():
    """Check if any accounts are configured."""
    accounts_dir = Path("accounts")
    if not accounts_dir.exists():
        print("📁 Creating accounts directory...")
        accounts_dir.mkdir()
    
    accounts = [d for d in accounts_dir.iterdir() if d.is_dir()]
    
    if not accounts:
        print("⚠️  No accounts configured yet!")
        print("Please create account folders in the 'accounts' directory")
        print("Each account folder should contain a 'cookies.json' file")
        return False
    
    print(f"✅ Found {len(accounts)} account(s):")
    for account in accounts:
        cookies_file = account / "cookies.json"
        if cookies_file.exists():
            print(f"   - {account.name} (cookies configured)")
        else:
            print(f"   - {account.name} (⚠️  cookies.json missing)")
    
    return True

def main():
    """Main startup function."""
    print("🤖 Facebook Marketplace Bot")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check accounts
    check_accounts()
    
    print("\n🚀 Starting the application...")
    print("The web interface will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
