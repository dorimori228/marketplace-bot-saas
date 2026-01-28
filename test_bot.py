#!/usr/bin/env python3
"""
Test script for the Facebook Marketplace Bot.
This script tests the bot initialization without running the full automation.
"""

import os
import sys
from bot import MarketplaceBot

def test_bot_initialization():
    """Test if the bot can initialize properly."""
    print("🤖 Testing Facebook Marketplace Bot...")
    print("=" * 50)
    
    # Check if accounts directory exists
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("❌ Accounts directory not found!")
        return False
    
    # Find available accounts
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
        print("Please add cookies.pkl or cookies.json files to account folders.")
        return False
    
    print(f"✅ Found {len(accounts)} account(s) with cookies:")
    for account, cookies_file in accounts:
        print(f"   - {account}: {cookies_file}")
    
    # Test bot initialization with first account
    test_account, test_cookies = accounts[0]
    print(f"\n🧪 Testing bot initialization with account: {test_account}")
    
    try:
        # Initialize bot (this will test Chrome driver setup)
        bot = MarketplaceBot(test_cookies, delay_factor=2.0)
        print("✅ Bot initialized successfully!")
        
        # Test basic functionality
        print("🧪 Testing basic browser functionality...")
        bot.driver.get("https://www.google.com")
        print("✅ Browser navigation test passed!")
        
        # Close the bot
        bot.close()
        print("✅ Bot closed successfully!")
        
        print("\n🎉 All tests passed! The bot is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Bot test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_bot_initialization()
    sys.exit(0 if success else 1)
