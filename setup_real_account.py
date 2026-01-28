#!/usr/bin/env python3
"""
Script to help you set up your real Facebook account with cookies.
"""

import os
import json
import pickle

def setup_real_account():
    """Help set up a real account with cookies."""
    print("🔧 Facebook Account Setup")
    print("=" * 50)
    print()
    print("This script will help you set up your real Facebook account.")
    print()
    
    # Get account name
    account_name = input("Enter your account name (e.g., 'jay'): ").strip()
    if not account_name:
        print("❌ Account name is required!")
        return
    
    # Create account directory
    account_dir = os.path.join("accounts", account_name)
    os.makedirs(account_dir, exist_ok=True)
    print(f"📁 Created account directory: {account_dir}")
    
    # Check if cookies file already exists
    cookies_json = os.path.join(account_dir, "cookies.json")
    cookies_pkl = os.path.join(account_dir, "cookies.pkl")
    
    if os.path.exists(cookies_json) or os.path.exists(cookies_pkl):
        print(f"⚠️  Cookies file already exists for account '{account_name}'")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 INSTRUCTIONS TO GET YOUR FACEBOOK COOKIES:")
    print("1. Open your web browser and log into Facebook")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the 'Application' or 'Storage' tab")
    print("4. Find 'Cookies' in the left sidebar")
    print("5. Click on 'https://www.facebook.com'")
    print("6. Copy the important cookies (c_user, xs, datr, sb, fr)")
    print()
    
    print("🔧 COOKIE SETUP OPTIONS:")
    print("1. Enter cookies manually")
    print("2. Load from existing file")
    print("3. Skip cookies setup (you can add them later)")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        # Manual entry
        cookies = []
        print("\n📝 Enter your Facebook cookies (press Enter with empty name to finish):")
        
        while True:
            name = input("Cookie name (e.g., c_user): ").strip()
            if not name:
                break
            
            value = input(f"Cookie value for {name}: ").strip()
            if not value:
                print("❌ Cookie value is required!")
                continue
            
            cookie = {
                "name": name,
                "value": value,
                "domain": ".facebook.com",
                "path": "/",
                "expires": -1,
                "httpOnly": name in ["xs", "datr", "sb", "fr"],
                "secure": True,
                "sameSite": "None"
            }
            cookies.append(cookie)
            print(f"✅ Added cookie: {name}")
        
        if cookies:
            # Save as JSON
            with open(cookies_json, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"✅ Cookies saved to: {cookies_json}")
        else:
            print("❌ No cookies entered!")
            
    elif choice == "2":
        # Load from existing file
        file_path = input("Enter path to your existing cookies file: ").strip()
        if os.path.exists(file_path):
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        cookies = json.load(f)
                elif file_path.endswith('.pkl'):
                    with open(file_path, 'rb') as f:
                        cookies = pickle.load(f)
                else:
                    print("❌ Unsupported file format!")
                    return
                
                # Save to account directory
                with open(cookies_json, 'w') as f:
                    json.dump(cookies, f, indent=2)
                
                print(f"✅ Cookies loaded and saved for account: {account_name}")
                
            except Exception as e:
                print(f"❌ Error loading cookies file: {e}")
        else:
            print("❌ File not found!")
    elif choice == "3":
        print("⏭️  Skipping cookies setup. You can add them later by running this script again.")
    else:
        print("❌ Invalid choice!")
        return
    
    print(f"\n✅ Account '{account_name}' setup complete!")
    print("You can now:")
    print("1. Test the bot with: python test_login.py")
    print("2. Start the web interface and select your account")
    print("3. Create listings using the web form")

if __name__ == "__main__":
    setup_real_account()
