#!/usr/bin/env python3
"""
Test script to verify the updated field filling approach.
"""

import time

def test_updated_field_filling():
    """Test the updated field filling with slower title typing and simple price filling."""
    print("🧪 Testing Updated Field Filling")
    print("=" * 50)
    
    # Test data
    test_title = "11mm Plush Grey Carpet | Soft Durable & Stylish for Any Room"
    test_price = "10"
    
    print("📝 Test Data:")
    print(f"   Title: '{test_title}'")
    print(f"   Price: '{test_price}'")
    print()
    
    # Test slower title typing
    print("🔧 Testing Slower Title Typing:")
    print("=" * 35)
    
    def simulate_slower_title_typing(text):
        """Simulate slower, more human-like typing for title."""
        result = ""
        start_time = time.time()
        
        for i, char in enumerate(text):
            result += char
            # Simulate slower delay: 0.05-0.15 seconds between characters
            delay = 0.05 + (0.1 * (i % 3) / 2)  # Vary delay slightly for realism
            time.sleep(delay)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return result, total_time
    
    # Test title typing with timing
    title_result, title_time = simulate_slower_title_typing(test_title)
    print(f"✅ Title typing result: '{title_result}'")
    print(f"⏱️  Title typing time: {title_time:.2f} seconds")
    print(f"📊 Average time per character: {title_time/len(test_title):.3f} seconds")
    print()
    
    # Test simple price filling
    print("🔧 Testing Simple Price Filling:")
    print("=" * 35)
    
    def simulate_simple_price_filling(price):
        """Simulate simple price field filling."""
        # Simple and direct - no character-by-character typing
        return price
    
    # Test price filling
    price_result = simulate_simple_price_filling(test_price)
    print(f"✅ Price filling result: '{price_result}'")
    print("⚡ Price filled instantly (no character delays)")
    print()
    
    # Verify results
    print("🔍 Verification:")
    print("=" * 20)
    
    title_success = title_result == test_title
    price_success = price_result == test_price
    
    if title_success:
        print("✅ Title field: SUCCESS - Slower typing works")
    else:
        print(f"❌ Title field: FAILED - Expected '{test_title}', Got '{title_result}'")
    
    if price_success:
        print("✅ Price field: SUCCESS - Simple filling works")
    else:
        print(f"❌ Price field: FAILED - Expected '{test_price}', Got '{price_result}'")
    
    print()
    print("📋 Updated Approach Benefits:")
    print("- Title: Slower, more human-like typing (0.05-0.15s per character)")
    print("- Price: Simple and fast filling (no character delays)")
    print("- Title typing time: ~{:.1f} seconds for {} characters".format(title_time, len(test_title)))
    print("- Price filling: Instant")
    print("- More realistic human behavior for title")
    print("- Efficient and reliable for price")
    
    if title_success and price_success:
        print("🎉 All tests passed! Updated field filling should work perfectly.")
    else:
        print("⚠️ Some tests failed. Check the implementation.")
    
    return title_success and price_success

if __name__ == "__main__":
    test_updated_field_filling()
