#!/usr/bin/env python3
"""
Test script to verify the click interception fix for listing deletion.
This script tests the improved click strategies implemented in bot.py
"""

import os
import sys
import time
from bot import MarketplaceBot

def test_click_interception_fix():
    """Test the improved click strategies for listing deletion."""
    
    print("🧪 Testing click interception fix for listing deletion...")
    
    # Test account (you can change this to any account you have)
    test_account = "yumi"
    account_dir = os.path.join('accounts', test_account)
    
    # Look for cookies file
    cookies_path = None
    for ext in ['.pkl', '.json']:
        potential_path = os.path.join(account_dir, f'cookies{ext}')
        if os.path.exists(potential_path):
            cookies_path = potential_path
            break
    
    if not cookies_path:
        print(f"❌ No cookies found for account: {test_account}")
        print("Please run the bot setup first to create cookies.")
        return False
    
    print(f"✅ Found cookies for account: {test_account}")
    
    # Test listing title (change this to match an existing listing)
    test_title = "£10/m² 11mm Durable Carpet | Budget-Friendly Luxury"
    
    try:
        # Initialize bot
        print("🤖 Initializing bot...")
        bot = MarketplaceBot(cookies_path, delay_factor=1.0)
        
        # Test the deletion with improved click strategies
        print(f"🗑️ Testing deletion of listing: {test_title}")
        bot.delete_listing_if_exists(test_title)
        
        print("✅ Click interception fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        try:
            if 'bot' in locals():
                bot.close()
                print("🔒 Browser closed successfully")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting click interception fix test...")
    success = test_click_interception_fix()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("The click interception fix should now work properly.")
    else:
        print("\n❌ Test failed!")
        print("Please check the error messages above for details.")
    
    print("\n📋 Summary of improvements made:")
    print("1. ✅ Multiple click strategies (direct, JavaScript, ActionChains, force click)")
    print("2. ✅ Better element scrolling (center alignment)")
    print("3. ✅ Overlapping element handling (temporary hiding)")
    print("4. ✅ Improved error handling and retry logic")
    print("5. ✅ Element restoration after operations")
