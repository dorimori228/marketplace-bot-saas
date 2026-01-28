#!/usr/bin/env python3
"""
Test script to create a listing with the abbie account to see what happens.
"""

import os
import sys
from bot import MarketplaceBot

def test_abbie_listing():
    """Test creating a listing with the abbie account."""
    print("🧪 Testing Abbie Account Listing Creation")
    print("=" * 50)
    
    # Test data
    cookies_path = "accounts/abbie/cookies.pkl"
    
    if not os.path.exists(cookies_path):
        print(f"❌ Cookies file not found: {cookies_path}")
        return False
    
    # Sample listing data
    listing_data = {
        'title': 'Test Listing for Abbie Account',
        'price': '£50',
        'description': 'This is a test listing to check if the abbie account works.',
        'category': 'Other Garden decor',
        'product_tags': 'test',
        'location': 'London, UK',
        'image_paths': [],  # No images for this test
        'speed': '1.0'
    }
    
    try:
        print("🤖 Initializing bot with abbie account...")
        bot = MarketplaceBot(cookies_path, delay_factor=2.0)
        
        print("🔍 Checking login status...")
        if bot._is_logged_in():
            print("✅ Successfully logged in!")
            
            print("🧪 Testing marketplace navigation...")
            bot.driver.get("https://www.facebook.com/marketplace")
            bot._sleep(3, 5)
            
            current_url = bot.driver.current_url
            print(f"📍 Current URL: {current_url}")
            
            if "marketplace" in current_url:
                print("✅ Successfully navigated to marketplace!")
                
                # Try to find the "Create new listing" button
                try:
                    create_button = bot.driver.find_element("xpath", "//span[contains(text(), 'Create new listing')]")
                    if create_button.is_displayed():
                        print("✅ Found 'Create new listing' button!")
                    else:
                        print("⚠️ 'Create new listing' button not visible")
                except:
                    print("❌ Could not find 'Create new listing' button")
                
            else:
                print("❌ Failed to navigate to marketplace")
                print(f"   Redirected to: {current_url}")
                
        else:
            print("❌ Login failed!")
            
        # Close bot
        bot.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_abbie_listing()
