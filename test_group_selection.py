#!/usr/bin/env python3
"""
Test script for the group selection functionality.
This script tests the _handle_group_selection method without actually creating a listing.
"""

import os
import sys
from bot import MarketplaceBot

def test_group_selection():
    """Test the group selection functionality."""
    print("🧪 Testing Group Selection Functionality")
    print("=" * 50)
    
    # Check if we have any account with cookies
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("❌ No accounts directory found")
        return False
    
    accounts = [d for d in os.listdir(accounts_dir) if os.path.isdir(os.path.join(accounts_dir, d))]
    if not accounts:
        print("❌ No accounts found")
        return False
    
    # Use the first available account
    account_name = accounts[0]
    account_dir = os.path.join(accounts_dir, account_name)
    
    # Find cookies file
    cookies_path = None
    for ext in ['.pkl', '.json']:
        potential_path = os.path.join(account_dir, f'cookies{ext}')
        if os.path.exists(potential_path):
            cookies_path = potential_path
            break
    
    if not cookies_path:
        print(f"❌ No cookies file found for account: {account_name}")
        return False
    
    print(f"✅ Using account: {account_name}")
    print(f"✅ Cookies file: {cookies_path}")
    
    try:
        # Initialize the bot
        print("\n🤖 Initializing bot...")
        bot = MarketplaceBot(cookies_path, delay_factor=1.0)
        
        # Navigate to the create listing page
        print("\n🌐 Navigating to create listing page...")
        bot.driver.get("https://www.facebook.com/marketplace/create/")
        bot._sleep(3, 5)
        
        # Handle mobile redirect
        current_url = bot.driver.current_url
        if "m.facebook.com" in current_url:
            print("📱 Detected mobile redirect, forcing desktop...")
            bot.driver.get("https://www.facebook.com/marketplace/create/")
            bot._sleep(3, 5)
        
        # Click "Item for sale"
        print("\n🔍 Looking for 'Item for sale' button...")
        item_for_sale_selectors = [
            "//span[text()='Item for sale']/ancestor::div[@role='button']",
            "//span[text()='Item for sale']",
            "//div[contains(@aria-label, 'Item for sale')]"
        ]
        
        item_clicked = False
        for selector in item_for_sale_selectors:
            try:
                if selector.startswith("//"):
                    element = bot.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    element = bot.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                bot._safe_click(element)
                print("✅ Clicked 'Item for sale' button")
                item_clicked = True
                break
            except:
                continue
        
        if not item_clicked:
            print("❌ Could not find 'Item for sale' button")
            return False
        
        bot._sleep(2, 3)
        
        # Fill minimal required fields to get to the group selection screen
        print("\n📝 Filling minimal required fields...")
        
        # Fill title
        title_selectors = [
            "//span[text()='Title']/following-sibling::input",
            "//span[text()='Title']/following::input[1]",
            'input[aria-label="Title"]'
        ]
        
        title_filled = False
        for selector in title_selectors:
            try:
                if selector.startswith("//"):
                    title_input = bot.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    title_input = bot.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                bot._safe_click(title_input)
                title_input.clear()
                title_input.send_keys("Test Listing for Group Selection")
                print("✅ Title filled")
                title_filled = True
                break
            except:
                continue
        
        if not title_filled:
            print("❌ Could not fill title")
            return False
        
        bot._sleep(1, 2)
        
        # Fill price
        price_selectors = [
            "//span[text()='Price']/following-sibling::input",
            "//span[text()='Price']/following::input[1]",
            'input[aria-label="Price"]'
        ]
        
        price_filled = False
        for selector in price_selectors:
            try:
                if selector.startswith("//"):
                    price_input = bot.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    price_input = bot.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                bot._safe_click(price_input)
                price_input.clear()
                price_input.send_keys("£10")
                print("✅ Price filled")
                price_filled = True
                break
            except:
                continue
        
        if not price_filled:
            print("❌ Could not fill price")
            return False
        
        bot._sleep(1, 2)
        
        # Click Next to get to the group selection screen
        print("\n➡️ Clicking Next button to reach group selection screen...")
        next_selectors = [
            'div[aria-label="Next"]',
            '//div[@aria-label="Next"]',
            'button[aria-label="Next"]'
        ]
        
        next_clicked = False
        for selector in next_selectors:
            try:
                if selector.startswith("//"):
                    next_button = bot.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    next_button = bot.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                bot._safe_click(next_button)
                print("✅ Next button clicked")
                next_clicked = True
                break
            except:
                continue
        
        if not next_clicked:
            print("❌ Could not click Next button")
            return False
        
        bot._sleep(2, 3)
        
        # Test the group selection functionality
        print("\n🧪 Testing group selection functionality...")
        bot._handle_group_selection()
        
        print("\n✅ Group selection test completed successfully!")
        print("🔍 Check the browser window to see if groups were selected")
        
        # Keep browser open for manual inspection
        print("\n⏳ Keeping browser open for 30 seconds for manual inspection...")
        bot._sleep(30, 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            if 'bot' in locals():
                bot.close()
        except:
            pass

if __name__ == "__main__":
    # Import required modules
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    
    success = test_group_selection()
    if success:
        print("\n🎉 Group selection test completed successfully!")
    else:
        print("\n❌ Group selection test failed!")
        sys.exit(1)
