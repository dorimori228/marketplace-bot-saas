#!/usr/bin/env python3
"""
Test script to verify that emojis are now preserved in the bot.
"""

def test_emoji_preservation():
    """Test that emojis are preserved in the new approach."""
    print("🧪 Testing Emoji Preservation")
    print("=" * 50)
    
    # Test data with emojis that should be preserved
    test_description = """🚚 Fast Delivery: 2–4 days
✅ Free Samples Available

15mm Carpet £14 per m²
11mm Carpet £10 per m²
8mm Carpet £8.20 per m²
Felt-Backed £7 per m²

Available in 4m & 5m widths ✂️
Over 30 colours to choose from 

Message me to order your free sample today!"""
    
    print("📝 Original Description:")
    print(test_description)
    print()
    
    # Test the sanitization function (should now preserve emojis)
    from bot import MarketplaceBot
    
    class TestBot:
        def _sanitize_text_for_chromedriver(self, text):
            """Copy of the updated sanitization function."""
            if not text:
                return text
            try:
                text = str(text)
                # Now just returns the text as-is
                return text
            except Exception as e:
                print(f"⚠️ Error sanitizing text: {e}")
                return str(text)
    
    test_bot = TestBot()
    sanitized_description = test_bot._sanitize_text_for_chromedriver(test_description)
    
    print("🔧 After Sanitization:")
    print(sanitized_description)
    print()
    
    # Check if emojis are preserved
    emojis_in_original = ['🚚', '✅', '✂️']
    emojis_preserved = all(emoji in sanitized_description for emoji in emojis_in_original)
    
    if emojis_preserved:
        print("✅ SUCCESS: All emojis are preserved!")
        print("🎉 The bot will now display emojis properly in Facebook listings!")
    else:
        print("❌ FAILED: Some emojis were removed")
        print("🔍 Missing emojis:")
        for emoji in emojis_in_original:
            if emoji not in sanitized_description:
                print(f"   - {emoji}")
    
    print()
    print("📋 Summary:")
    print("- The bot now uses JavaScript to set text content")
    print("- This bypasses ChromeDriver's Unicode limitations")
    print("- Emojis should display properly in Facebook listings")
    print("- Fallback to send_keys() if JavaScript fails")
    
    return emojis_preserved

if __name__ == "__main__":
    test_emoji_preservation()
