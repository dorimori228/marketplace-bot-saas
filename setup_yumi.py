#!/usr/bin/env python3
"""
Quick setup script for the yumi account.
This will help yumi set up auto-login functionality.
"""

import os
import sys
from setup_new_user import setup_new_user, test_auto_login

def setup_yumi():
    """Setup the yumi account specifically."""
    print("🌸 Setting up Yumi Account")
    print("=" * 40)
    print()
    
    # Check if yumi account already exists
    yumi_dir = "accounts/yumi"
    if os.path.exists(yumi_dir):
        print("📁 Yumi account directory already exists")
        
        # Check for existing cookies
        cookies_json = os.path.join(yumi_dir, "cookies.json")
        cookies_pkl = os.path.join(yumi_dir, "cookies.pkl")
        
        if os.path.exists(cookies_json) or os.path.exists(cookies_pkl):
            print("🍪 Cookies found for yumi account")
            test_choice = input("Do you want to test auto-login? (y/n): ").strip().lower()
            if test_choice == 'y':
                test_auto_login("yumi")
            return True
        else:
            print("⚠️ No cookies found - setup required")
    else:
        print("📁 Creating yumi account directory...")
        os.makedirs(yumi_dir, exist_ok=True)
    
    print("\n🔐 YUMI ACCOUNT SETUP")
    print("=" * 30)
    print("This will help you set up auto-login for your yumi account.")
    print("You'll need to log in manually once, then future runs will be automatic.")
    print()
    
    ready = input("Are you ready to start? (y/n): ").strip().lower()
    if ready != 'y':
        print("Setup cancelled.")
        return False
    
    # Use the new user setup with yumi specifically
    print("\n🚀 Starting setup process...")
    print("Note: When prompted for account name, enter 'yumi'")
    print()
    
    # Temporarily modify the input to auto-fill yumi
    import builtins
    original_input = builtins.input
    
    def mock_input(prompt):
        if "account name" in prompt.lower():
            print("yumi")  # Auto-fill the account name
            return "yumi"
        return original_input(prompt)
    
    builtins.input = mock_input
    
    try:
        success = setup_new_user()
        return success
    finally:
        builtins.input = original_input

def main():
    """Main function."""
    try:
        success = setup_yumi()
        if success:
            print("\n🎉 Yumi account setup completed!")
            print("✅ You can now use the bot normally")
            print("🚀 Future runs will auto-login automatically")
        else:
            print("\n❌ Setup failed. Please try again.")
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")

if __name__ == "__main__":
    main()
