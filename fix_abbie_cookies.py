#!/usr/bin/env python3
"""
Script to fix the abbie account cookies by analyzing the working jay account.
"""

import os
import pickle
import json

def analyze_and_fix_cookies():
    """Analyze jay cookies and suggest fixes for abbie."""
    print("🔍 Analyzing Cookie Differences")
    print("=" * 50)
    
    # Load jay cookies (working)
    jay_cookies_path = "accounts/jay/cookies.pkl"
    abbie_cookies_path = "accounts/abbie/cookies.pkl"
    
    if not os.path.exists(jay_cookies_path):
        print(f"❌ Jay cookies not found: {jay_cookies_path}")
        return False
    
    if not os.path.exists(abbie_cookies_path):
        print(f"❌ Abbie cookies not found: {abbie_cookies_path}")
        return False
    
    try:
        # Load both cookie sets
        with open(jay_cookies_path, 'rb') as f:
            jay_cookies = pickle.load(f)
        
        with open(abbie_cookies_path, 'rb') as f:
            abbie_cookies = pickle.load(f)
        
        print(f"📊 Jay cookies: {len(jay_cookies)}")
        print(f"📊 Abbie cookies: {len(abbie_cookies)}")
        
        # Analyze cookie names
        jay_names = {cookie.get('name') for cookie in jay_cookies}
        abbie_names = {cookie.get('name') for cookie in abbie_cookies}
        
        print(f"\n🍪 Jay cookie names: {sorted(jay_names)}")
        print(f"🍪 Abbie cookie names: {sorted(abbie_names)}")
        
        missing_in_abbie = jay_names - abbie_names
        extra_in_abbie = abbie_names - jay_names
        
        print(f"\n❌ Missing in abbie: {missing_in_abbie}")
        print(f"➕ Extra in abbie: {extra_in_abbie}")
        
        # Check for the critical 'fr' cookie
        if 'fr' in missing_in_abbie:
            print("\n🚨 CRITICAL: Abbie is missing the 'fr' cookie!")
            print("   The 'fr' cookie is essential for Facebook authentication.")
            print("   This is likely why abbie account login fails.")
            
            # Find the fr cookie in jay
            fr_cookie = None
            for cookie in jay_cookies:
                if cookie.get('name') == 'fr':
                    fr_cookie = cookie.copy()
                    break
            
            if fr_cookie:
                print(f"   Found fr cookie in jay: {fr_cookie}")
                print("\n💡 Solution: You need to get fresh cookies for abbie account.")
                print("   The fr cookie is account-specific and cannot be copied.")
                print("   Run the refresh_abbie_cookies.py script to get fresh cookies.")
        
        # Check cookie domains
        print(f"\n🌐 Domain analysis:")
        for cookie in jay_cookies:
            print(f"   Jay - {cookie.get('name')}: {cookie.get('domain')}")
        
        for cookie in abbie_cookies:
            print(f"   Abbie - {cookie.get('name')}: {cookie.get('domain')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_and_fix_cookies()
