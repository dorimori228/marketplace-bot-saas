#!/usr/bin/env python3
"""
Test script to verify the new login functionality.
"""

import os
import sys
from bot import MarketplaceBot

def test_login():
    """Test the new login functionality."""
    print("🔐 Testing Facebook Login Functionality")
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
    print(f"\n🧪 Testing login with account: {test_account}")
    
    try:
        # Initialize bot with new login logic
        bot = MarketplaceBot(test_cookies, delay_factor=2.0)
        
        # Test marketplace access
        print("🧪 Testing marketplace access...")
        bot.driver.get("https://www.facebook.com/marketplace")
        bot._sleep(3, 5)
        
        # Check if we can access marketplace
        try:
            marketplace_indicators = [
                "//span[contains(text(), 'Marketplace')]",
                "//div[contains(text(), 'Marketplace')]",
                "//a[contains(@href, '/marketplace')]"
            ]
            
            marketplace_accessible = False
            for indicator in marketplace_indicators:
                try:
                    element = bot.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        print("✅ Marketplace access confirmed!")
                        marketplace_accessible = True
                        break
                except:
                    continue
            
            if not marketplace_accessible:
                print("⚠️  Marketplace access unclear - may need manual login")
                
        except Exception as e:
            print(f"⚠️  Error testing marketplace: {e}")
        
        # Close bot
        bot.close()
        print("✅ Bot closed successfully!")
        
        print("\n🎉 Login test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
