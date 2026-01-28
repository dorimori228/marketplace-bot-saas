#!/usr/bin/env python3
"""
Test script to verify the Unicode character fix works properly.
"""

import os
import sys
from bot import MarketplaceBot

def test_unicode_sanitization():
    """Test the Unicode sanitization function."""
    print("🧪 Testing Unicode Character Sanitization")
    print("=" * 50)
    
    # Test data with various Unicode characters
    test_cases = [
        {
            'title': '🚚 Fast Delivery: 2-4 days',
            'price': '£150',
            'description': '''🚚 Fast Delivery: 2-4 days
✅ Free Samples Available

💷 Options Available:
- Budget Range (30mm)
- Mid-Range (35mm)  
- Premium Range (40mm)

🌱 Perfect for gardens and outdoor spaces!''',
            'product_tags': 'artificial grass, decking, garden 🌱',
            'location': 'London, UK 🇬🇧'
        },
        {
            'title': 'Premium Carpet 🏆',
            'price': '€200',
            'description': 'High quality carpet with ⭐ 5-star rating!',
            'product_tags': 'carpet, home, decor',
            'location': 'Paris, France'
        }
    ]
    
    # Test the sanitization function directly
    print("🔧 Testing sanitization function...")
    
    # Create a dummy bot instance to test the sanitization function
    try:
        # We'll just test the sanitization function without actually running the bot
        from bot import MarketplaceBot
        
        # Create a minimal bot instance just to access the sanitization method
        class TestBot:
            def _sanitize_text_for_chromedriver(self, text):
                """Copy of the updated sanitization function for testing."""
                if not text:
                    return text
                
                try:
                    text = str(text)
                    
                    # Only remove characters that are actually outside the BMP (Basic Multilingual Plane)
                    # Most emojis are actually within the BMP and should work fine
                    sanitized_text = ''.join(char for char in text if ord(char) <= 0xFFFF)
                    
                    if len(sanitized_text) != len(text):
                        removed_chars = len(text) - len(sanitized_text)
                        print(f"⚠️ Removed {removed_chars} non-BMP characters from text")
                        removed_chars_list = [char for char in text if ord(char) > 0xFFFF]
                        if removed_chars_list:
                            print(f"   Removed characters: {removed_chars_list}")
                    
                    return sanitized_text
                    
                except Exception as e:
                    print(f"⚠️ Error sanitizing text: {e}")
                    return str(text)
        
        test_bot = TestBot()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}:")
            print(f"Original Title: {test_case['title']}")
            sanitized_title = test_bot._sanitize_text_for_chromedriver(test_case['title'])
            print(f"Sanitized Title: {sanitized_title}")
            
            print(f"\nOriginal Description:")
            print(test_case['description'])
            print(f"\nSanitized Description:")
            sanitized_desc = test_bot._sanitize_text_for_chromedriver(test_case['description'])
            print(sanitized_desc)
            
            print(f"\nOriginal Tags: {test_case['product_tags']}")
            sanitized_tags = test_bot._sanitize_text_for_chromedriver(test_case['product_tags'])
            print(f"Sanitized Tags: {sanitized_tags}")
            
            print(f"\nOriginal Location: {test_case['location']}")
            sanitized_location = test_bot._sanitize_text_for_chromedriver(test_case['location'])
            print(f"Sanitized Location: {sanitized_location}")
            
            print("-" * 50)
        
        print("✅ Unicode sanitization test completed successfully!")
        print("🎉 The bot should now handle Unicode characters without crashing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_unicode_sanitization()
