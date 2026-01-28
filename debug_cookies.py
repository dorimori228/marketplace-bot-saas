#!/usr/bin/env python3
"""
Debug script to test cookie loading and login status.
This script helps troubleshoot cookie-related issues.
"""

import os
import sys
import pickle
import json
from bot import MarketplaceBot

def debug_cookies_file(cookies_path):
    """Debug a cookies file to see its contents."""
    print(f"🔍 Debugging cookies file: {cookies_path}")
    print("=" * 60)
    
    if not os.path.exists(cookies_path):
        print(f"❌ File not found: {cookies_path}")
        return False
    
    try:
        if cookies_path.endswith('.pkl'):
            print("📁 File type: Pickle (.pkl)")
            with open(cookies_path, 'rb') as f:
                cookies = pickle.load(f)
        else:
            print("📁 File type: JSON (.json)")
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
        
        print(f"📊 Total cookies: {len(cookies)}")
        print("\n🍪 Cookie details:")
        
        important_cookies = ['c_user', 'xs', 'datr', 'sb', 'fr', 'wd']
        found_important = []
        
        for i, cookie in enumerate(cookies):
            name = cookie.get('name', 'unknown')
            domain = cookie.get('domain', 'unknown')
            secure = cookie.get('secure', False)
            http_only = cookie.get('httpOnly', False)
            
            print(f"  {i+1:2d}. {name:15} | Domain: {domain:20} | Secure: {secure:5} | HttpOnly: {http_only}")
            
            if name in important_cookies:
                found_important.append(name)
        
        print(f"\n✅ Important cookies found: {found_important}")
        print(f"❌ Missing important cookies: {set(important_cookies) - set(found_important)}")
        
        # Check for Facebook domain cookies
        facebook_cookies = [c for c in cookies if '.facebook.com' in c.get('domain', '')]
        print(f"📘 Facebook domain cookies: {len(facebook_cookies)}")
        
        return len(found_important) >= 3  # Need at least 3 important cookies
        
    except Exception as e:
        print(f"❌ Error reading cookies file: {e}")
        return False

def test_bot_with_cookies(account_name, cookies_path):
    """Test the bot with a specific cookies file."""
    print(f"\n🤖 Testing bot with account: {account_name}")
    print("=" * 60)
    
    try:
        # Initialize bot
        bot = MarketplaceBot(cookies_path, delay_factor=2.0)
        
        # Check login status
        is_logged_in = bot._is_logged_in()
        
        if is_logged_in:
            print("🎉 SUCCESS: User is logged in!")
            
            # Try to navigate to marketplace
            print("🧪 Testing marketplace access...")
            bot.driver.get("https://www.facebook.com/marketplace")
            bot._sleep(3, 5)
            
            # Check if marketplace loaded
            try:
                marketplace_indicators = [
                    "//span[contains(text(), 'Marketplace')]",
                    "//div[contains(text(), 'Marketplace')]",
                    "//a[contains(@href, '/marketplace')]"
                ]
                
                for indicator in marketplace_indicators:
                    try:
                        element = bot.driver.find_element(By.XPATH, indicator)
                        if element.is_displayed():
                            print("✅ Marketplace access confirmed!")
                            break
                    except:
                        continue
                else:
                    print("⚠️  Marketplace access unclear")
                    
            except Exception as e:
                print(f"⚠️  Error testing marketplace: {e}")
        else:
            print("❌ FAILED: User is not logged in")
            print("💡 Suggestions:")
            print("   1. Check if your cookies are expired")
            print("   2. Make sure you exported cookies while logged in")
            print("   3. Try logging in manually and re-exporting cookies")
        
        # Close bot
        bot.close()
        return is_logged_in
        
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        return False

def main():
    """Main debug function."""
    print("🔧 Facebook Marketplace Bot - Cookie Debug Tool")
    print("=" * 60)
    
    # Find accounts
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("❌ Accounts directory not found!")
        return
    
    accounts = []
    for item in os.listdir(accounts_dir):
        item_path = os.path.join(accounts_dir, item)
        if os.path.isdir(item_path):
            # Check for cookies file
            for ext in ['.pkl', '.json']:
                cookies_file = os.path.join(item_path, f'cookies{ext}')
                if os.path.exists(cookies_file):
                    accounts.append((item, cookies_file))
                    break
    
    if not accounts:
        print("❌ No accounts with cookies found!")
        return
    
    print(f"📁 Found {len(accounts)} account(s):")
    for account, cookies_file in accounts:
        print(f"   - {account}: {cookies_file}")
    
    # Debug each account
    for account, cookies_file in accounts:
        print(f"\n{'='*60}")
        print(f"🔍 DEBUGGING ACCOUNT: {account}")
        print(f"{'='*60}")
        
        # Debug cookies file
        cookies_valid = debug_cookies_file(cookies_file)
        
        if cookies_valid:
            # Test bot
            test_bot_with_cookies(account, cookies_file)
        else:
            print("❌ Skipping bot test due to invalid cookies")
    
    print(f"\n{'='*60}")
    print("🏁 Debug complete!")

if __name__ == "__main__":
    main()
