#!/usr/bin/env python3
"""
Simple setup script for the abbie account.
This will guide you through getting fresh cookies.
"""

import os
import pickle
import json

def setup_abbie_account():
    """Setup the abbie account with fresh cookies."""
    print("🔧 Setting up Abbie Account")
    print("=" * 50)
    
    # Ensure directory exists
    os.makedirs("accounts/abbie", exist_ok=True)
    
    print("📋 To fix the abbie account login issue:")
    print()
    print("1. 🌐 Open your browser and go to: https://www.facebook.com")
    print("2. 🔐 Log in with the abbie account")
    print("3. 🏪 Navigate to: https://www.facebook.com/marketplace")
    print("4. 🍪 Export cookies using one of these methods:")
    print()
    print("   Method A - Browser Extension:")
    print("   - Install 'Cookie Editor' extension")
    print("   - Click the extension icon")
    print("   - Click 'Export' and save as JSON")
    print("   - Rename the file to 'cookies.json'")
    print()
    print("   Method B - Manual Export:")
    print("   - Press F12 to open Developer Tools")
    print("   - Go to Application/Storage tab")
    print("   - Click on Cookies > https://www.facebook.com")
    print("   - Copy all cookie values")
    print()
    print("5. 📁 Save the cookies file as:")
    print("   accounts/abbie/cookies.json (for JSON format)")
    print("   OR")
    print("   accounts/abbie/cookies.pkl (for pickle format)")
    print()
    print("6. 🧪 Test the account by running:")
    print("   python test_login.py")
    print()
    
    # Check if cookies file exists
    cookies_paths = [
        "accounts/abbie/cookies.pkl",
        "accounts/abbie/cookies.json"
    ]
    
    for path in cookies_paths:
        if os.path.exists(path):
            print(f"✅ Found cookies file: {path}")
            
            # Validate cookies
            try:
                if path.endswith('.pkl'):
                    with open(path, 'rb') as f:
                        cookies = pickle.load(f)
                else:
                    with open(path, 'r') as f:
                        cookies = json.load(f)
                
                print(f"📊 Loaded {len(cookies)} cookies")
                
                # Check for important cookies
                cookie_names = {cookie.get('name') for cookie in cookies}
                important_cookies = ['c_user', 'xs', 'fr', 'sb', 'datr']
                found_important = cookie_names.intersection(important_cookies)
                missing_important = set(important_cookies) - found_important
                
                print(f"✅ Found important cookies: {sorted(found_important)}")
                if missing_important:
                    print(f"❌ Missing important cookies: {sorted(missing_important)}")
                    if 'fr' in missing_important:
                        print("🚨 CRITICAL: Missing 'fr' cookie - this will cause login failures!")
                else:
                    print("🎉 All important cookies present!")
                    
            except Exception as e:
                print(f"❌ Error reading cookies: {e}")
            
            return True
    
    print("❌ No cookies file found. Please follow the steps above to get fresh cookies.")
    return False

if __name__ == "__main__":
    setup_abbie_account()
