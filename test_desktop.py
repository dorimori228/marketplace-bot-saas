#!/usr/bin/env python3
"""
Test script to verify desktop version access and mobile redirect handling.
"""

import os
import sys
from bot import MarketplaceBot

def test_desktop_access():
    """Test if the bot can access Facebook desktop version."""
    print("🖥️  Testing Desktop Facebook Access")
    print("=" * 50)
    
    # Find accounts with cookies
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("❌ Accounts directory not found!")
        return False
    
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
        print("Please add your cookies.pkl or cookies.json files to account folders.")
        return False
    
    print(f"📁 Found {len(accounts)} account(s):")
    for account, cookies_file in accounts:
        print(f"   - {account}: {cookies_file}")
    
    # Test with first account
    test_account, test_cookies = accounts[0]
    print(f"\n🧪 Testing desktop access with account: {test_account}")
    
    try:
        # Initialize bot
        bot = MarketplaceBot(test_cookies, delay_factor=2.0)
        
        # Check current URL
        current_url = bot.driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        if "m.facebook.com" in current_url:
            print("❌ Still on mobile version!")
            return False
        elif "www.facebook.com" in current_url:
            print("✅ Successfully on desktop version!")
        else:
            print("⚠️  Unknown URL format")
        
        # Test marketplace access
        print("\n🧪 Testing marketplace access...")
        bot.driver.get("https://www.facebook.com/marketplace?_rdr")
        bot._sleep(3, 5)
        
        current_url = bot.driver.current_url
        print(f"📍 Marketplace URL: {current_url}")
        
        if "m.facebook.com" in current_url:
            print("❌ Marketplace redirected to mobile!")
            return False
        else:
            print("✅ Marketplace accessible on desktop!")
        
        # Close bot
        bot.close()
        print("✅ Bot closed successfully!")
        
        print("\n🎉 Desktop access test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Desktop access test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_desktop_access()
    sys.exit(0 if success else 1)
