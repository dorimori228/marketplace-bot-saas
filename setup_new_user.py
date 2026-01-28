#!/usr/bin/env python3
"""
New User Setup Script for Facebook Marketplace Bot
This script helps new users (like yumi) set up their account with auto-login functionality.
"""

import os
import sys
import json
import pickle
import time
from bot import MarketplaceBot

def setup_new_user():
    """Setup a new user account with auto-login functionality."""
    print("🚀 Facebook Marketplace Bot - New User Setup")
    print("=" * 60)
    print()
    
    # Get account name
    account_name = input("Enter your account name (e.g., 'yumi'): ").strip()
    if not account_name:
        print("❌ Account name is required!")
        return False
    
    # Create account directory
    account_dir = os.path.join("accounts", account_name)
    os.makedirs(account_dir, exist_ok=True)
    print(f"📁 Created account directory: {account_dir}")
    
    # Check if cookies already exist
    cookies_json = os.path.join(account_dir, "cookies.json")
    cookies_pkl = os.path.join(account_dir, "cookies.pkl")
    
    if os.path.exists(cookies_json) or os.path.exists(cookies_pkl):
        print(f"⚠️  Cookies already exist for account '{account_name}'")
        overwrite = input("Do you want to refresh/update them? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    print("\n🔐 SETUP INSTRUCTIONS:")
    print("1. A browser window will open to Facebook")
    print("2. Log in with your Facebook account credentials")
    print("3. Navigate to Facebook Marketplace if needed")
    print("4. The bot will automatically save your login cookies")
    print("5. Future runs will auto-login using these cookies")
    print()
    
    input("Press Enter when you're ready to start the setup process...")
    
    # Initialize bot with manual login
    cookies_path = cookies_json  # Use JSON format for better compatibility
    bot = None
    
    try:
        print("\n🤖 Initializing bot and opening browser...")
        print("⏳ Please wait while the browser loads...")
        
        # Initialize bot - this will trigger manual login if no cookies exist
        bot = MarketplaceBot(cookies_path, delay_factor=2.0)
        
        # Check if login was successful
        if bot._is_logged_in():
            print("✅ Login successful! Cookies have been saved.")
            print(f"📁 Cookies saved to: {cookies_path}")
            
            # Verify cookies were actually saved
            if os.path.exists(cookies_path):
                print("✅ Cookie file verification successful!")
                
                # Test the cookies by trying to load them
                try:
                    with open(cookies_path, 'r') as f:
                        saved_cookies = json.load(f)
                    print(f"✅ Cookie validation successful! ({len(saved_cookies)} cookies saved)")
                    
                    # Show some cookie info (without sensitive data)
                    important_cookies = ['c_user', 'xs', 'datr', 'sb', 'fr']
                    found_cookies = [cookie['name'] for cookie in saved_cookies if cookie['name'] in important_cookies]
                    print(f"🔑 Important cookies found: {', '.join(found_cookies)}")
                    
                except Exception as e:
                    print(f"⚠️ Cookie validation failed: {e}")
                    return False
            else:
                print("❌ Cookie file was not created!")
                return False
            
            print("\n🎉 Setup completed successfully!")
            print(f"✅ Account '{account_name}' is now ready for auto-login")
            print("🚀 You can now use the bot normally - it will auto-login next time!")
            
            return True
            
        else:
            print("❌ Login was not successful. Please try again.")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if bot:
            print("\n🔒 Closing browser...")
            bot.close()
            print("✅ Browser closed")

def test_auto_login(account_name):
    """Test auto-login functionality for an existing account."""
    print(f"\n🧪 Testing auto-login for account: {account_name}")
    print("=" * 50)
    
    account_dir = os.path.join("accounts", account_name)
    cookies_json = os.path.join(account_dir, "cookies.json")
    cookies_pkl = os.path.join(account_dir, "cookies.pkl")
    
    # Find existing cookies file
    cookies_path = None
    if os.path.exists(cookies_json):
        cookies_path = cookies_json
    elif os.path.exists(cookies_pkl):
        cookies_path = cookies_pkl
    else:
        print(f"❌ No cookies found for account '{account_name}'")
        return False
    
    bot = None
    try:
        print("🤖 Testing auto-login...")
        bot = MarketplaceBot(cookies_path, delay_factor=2.0)
        
        if bot._is_logged_in():
            print("✅ Auto-login test successful!")
            return True
        else:
            print("❌ Auto-login test failed - manual login may be required")
            return False
            
    except Exception as e:
        print(f"❌ Error during auto-login test: {e}")
        return False
        
    finally:
        if bot:
            bot.close()

def list_accounts():
    """List all available accounts."""
    print("\n📋 Available Accounts:")
    print("=" * 30)
    
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("No accounts directory found.")
        return
    
    accounts = []
    for item in os.listdir(accounts_dir):
        item_path = os.path.join(accounts_dir, item)
        if os.path.isdir(item_path):
            # Check for cookies
            has_cookies = False
            for ext in ['.json', '.pkl']:
                if os.path.exists(os.path.join(item_path, f'cookies{ext}')):
                    has_cookies = True
                    break
            
            accounts.append((item, has_cookies))
    
    if not accounts:
        print("No accounts found.")
        return
    
    for account, has_cookies in accounts:
        status = "✅ Ready" if has_cookies else "⚠️ Needs setup"
        print(f"  {account}: {status}")

def main():
    """Main function with menu options."""
    while True:
        print("\n" + "=" * 60)
        print("Facebook Marketplace Bot - User Management")
        print("=" * 60)
        print("1. Setup new user account")
        print("2. Test auto-login for existing account")
        print("3. List all accounts")
        print("4. Exit")
        print()
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            setup_new_user()
        elif choice == "2":
            account_name = input("Enter account name to test: ").strip()
            if account_name:
                test_auto_login(account_name)
        elif choice == "3":
            list_accounts()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
