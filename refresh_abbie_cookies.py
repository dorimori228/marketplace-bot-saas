#!/usr/bin/env python3
"""
Script to help refresh cookies for the abbie account.
This will open a browser, let you log in manually, and save fresh cookies.
"""

import os
import sys
from bot import MarketplaceBot

def refresh_abbie_cookies():
    """Refresh cookies for the abbie account."""
    print("🔄 Refreshing Cookies for Abbie Account")
    print("=" * 50)
    
    cookies_path = "accounts/abbie/cookies.pkl"
    
    # Ensure the accounts/abbie directory exists
    os.makedirs("accounts/abbie", exist_ok=True)
    
    try:
        print("🤖 Opening browser for manual login...")
        print("📝 Instructions:")
        print("   1. Log into Facebook with the abbie account")
        print("   2. Navigate to Facebook Marketplace")
        print("   3. Wait for the script to automatically save cookies")
        print("   4. The browser will close automatically")
        print()
        
        # Initialize bot without cookies (will prompt for manual login)
        bot = MarketplaceBot(cookies_path, delay_factor=2.0)
        
        print("✅ Cookies refreshed successfully!")
        print(f"📁 Saved to: {cookies_path}")
        
        # Close bot
        bot.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    refresh_abbie_cookies()
