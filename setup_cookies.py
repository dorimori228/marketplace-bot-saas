#!/usr/bin/env python3
"""
Setup script to help you configure your Facebook cookies.
This script helps you set up your cookies.pkl files properly.
"""

import os
import pickle
import json

def create_sample_cookies():
    """Create a sample cookies structure for reference."""
    sample_cookies = [
        {
            "name": "c_user",
            "value": "YOUR_FACEBOOK_USER_ID_HERE",
            "domain": ".facebook.com",
            "path": "/",
            "expires": -1,
            "httpOnly": False,
            "secure": True,
            "sameSite": "None"
        },
        {
            "name": "xs",
            "value": "YOUR_XS_TOKEN_HERE",
            "domain": ".facebook.com",
            "path": "/",
            "expires": -1,
            "httpOnly": True,
            "secure": True,
            "sameSite": "None"
        },
        {
            "name": "datr",
            "value": "YOUR_DATR_TOKEN_HERE",
            "domain": ".facebook.com",
            "path": "/",
            "expires": -1,
            "httpOnly": True,
            "secure": True,
            "sameSite": "None"
        }
    ]
    
    return sample_cookies

def save_cookies_as_pkl(cookies, filepath):
    """Save cookies as a pickle file."""
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(cookies, f)
        print(f"✅ Cookies saved as pickle file: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving pickle file: {e}")
        return False

def save_cookies_as_json(cookies, filepath):
    """Save cookies as a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"✅ Cookies saved as JSON file: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False

def main():
    """Main setup function."""
    print("🍪 Facebook Cookies Setup Tool")
    print("=" * 50)
    print()
    print("This tool helps you set up your Facebook cookies for the bot.")
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Log into Facebook in your browser")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Application/Storage tab")
    print("4. Find Cookies for facebook.com")
    print("5. Copy the important cookies (c_user, xs, datr, etc.)")
    print("6. Use this tool to create your cookies file")
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
    
    # Show sample cookies
    print("\n📝 SAMPLE COOKIES STRUCTURE:")
    sample_cookies = create_sample_cookies()
    for cookie in sample_cookies:
        print(f"   {cookie['name']}: {cookie['value']}")
    
    print("\n🔧 COOKIE SETUP OPTIONS:")
    print("1. Create sample cookies file (you'll need to edit it)")
    print("2. Enter cookies manually")
    print("3. Load from existing file")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        # Create sample file
        sample_file = os.path.join(account_dir, "cookies.json")
        save_cookies_as_json(sample_cookies, sample_file)
        print(f"\n📝 Sample cookies file created: {sample_file}")
        print("Edit this file with your actual Facebook cookies!")
        
    elif choice == "2":
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
            # Save as both formats
            pkl_file = os.path.join(account_dir, "cookies.pkl")
            json_file = os.path.join(account_dir, "cookies.json")
            
            save_cookies_as_pkl(cookies, pkl_file)
            save_cookies_as_json(cookies, json_file)
            
            print(f"\n🎉 Cookies saved for account: {account_name}")
        else:
            print("❌ No cookies entered!")
            
    elif choice == "3":
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
                pkl_file = os.path.join(account_dir, "cookies.pkl")
                json_file = os.path.join(account_dir, "cookies.json")
                
                save_cookies_as_pkl(cookies, pkl_file)
                save_cookies_as_json(cookies, json_file)
                
                print(f"\n🎉 Cookies loaded and saved for account: {account_name}")
                
            except Exception as e:
                print(f"❌ Error loading cookies file: {e}")
        else:
            print("❌ File not found!")
    else:
        print("❌ Invalid choice!")
        return
    
    print(f"\n✅ Setup complete for account: {account_name}")
    print("You can now test the bot with: python debug_cookies.py")

if __name__ == "__main__":
    main()
