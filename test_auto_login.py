#!/usr/bin/env python3
"""
Test script to verify auto-login functionality for existing accounts.
"""

import os
import sys
from bot import MarketplaceBot

def test_auto_login(account_name):
    """Test auto-login for a specific account."""
    print(f"🧪 Testing Auto-Login for Account: {account_name}")
    print("=" * 50)
    
    # Check if account exists
    account_dir = os.path.join("accounts", account_name)
    if not os.path.exists(account_dir):
        print(f"❌ Account directory not found: {account_dir}")
        return False
    
    # Find cookies file
    cookies_json = os.path.join(account_dir, "cookies.json")
    cookies_pkl = os.path.join(account_dir, "cookies.pkl")
    
    cookies_path = None
    if os.path.exists(cookies_json):
        cookies_path = cookies_json
        print(f"📁 Found cookies file: {cookies_json}")
    elif os.path.exists(cookies_pkl):
        cookies_path = cookies_pkl
        print(f"📁 Found cookies file: {cookies_pkl}")
    else:
        print(f"❌ No cookies file found for account '{account_name}'")
        print("💡 Run setup_new_user.py or setup_yumi.py first")
        return False
    
    # Test auto-login
    bot = None
    try:
        print("🤖 Initializing bot with auto-login...")
        bot = MarketplaceBot(cookies_path, delay_factor=2.0)
        
        print("🔍 Checking login status...")
        if bot._is_logged_in():
            print("✅ Auto-login test PASSED!")
            print("🚀 Account is ready for normal bot usage")
            return True
        else:
            print("❌ Auto-login test FAILED")
            print("💡 Cookies may be expired or invalid")
            print("🔄 Try running setup again to refresh cookies")
            return False
            
    except Exception as e:
        print(f"❌ Error during auto-login test: {e}")
        return False
        
    finally:
        if bot:
            print("🔒 Closing browser...")
            bot.close()

def test_all_accounts():
    """Test auto-login for all available accounts."""
    print("🧪 Testing Auto-Login for All Accounts")
    print("=" * 50)
    
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("❌ No accounts directory found")
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
    
    print(f"📋 Found {len(accounts)} account(s)")
    print()
    
    results = []
    for account, has_cookies in accounts:
        print(f"Testing {account}...")
        if has_cookies:
            success = test_auto_login(account)
            results.append((account, success))
        else:
            print(f"⚠️ {account}: No cookies found - skipping")
            results.append((account, False))
        print()
    
    # Summary
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    for account, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{account}: {status}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        account_name = sys.argv[1]
        test_auto_login(account_name)
    else:
        print("Auto-Login Test Tool")
        print("=" * 30)
        print("1. Test specific account")
        print("2. Test all accounts")
        print()
        
        choice = input("Choose option (1-2): ").strip()
        
        if choice == "1":
            account_name = input("Enter account name: ").strip()
            if account_name:
                test_auto_login(account_name)
        elif choice == "2":
            test_all_accounts()
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
