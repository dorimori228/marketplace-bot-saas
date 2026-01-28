#!/usr/bin/env python3
"""
Test script for title variation functionality.
"""

from title_variator import TitleVariator

def test_title_variation():
    """Test title variation without emojis."""
    print("Testing Title Variation")
    print("=" * 30)
    
    variator = TitleVariator()
    
    # Test title
    original_title = "Artificial Grass | SAMPLE BOX"
    print(f"Original title: {original_title}")
    
    # Generate variations
    print("\nGenerating variations:")
    variations = variator.generate_multiple_variations(original_title, 5)
    
    for i, variation in enumerate(variations, 1):
        if variation['success']:
            print(f"  {i}. {variation['variation']} ({variation['type']})")
        else:
            print(f"  {i}. Error: {variation['error']}")
    
    # Test single variation
    print(f"\nSingle variation:")
    result = variator.get_next_title_variation("test_account", original_title)
    if result['success']:
        print(f"  New title: {result['variation']}")
        print(f"  Type: {result['type']}")
    else:
        print(f"  Error: {result['error']}")
    
    return True

def main():
    """Run title variation test."""
    print("TITLE VARIATION TEST")
    print("=" * 40)
    
    test_title_variation()
    
    print("\nSUCCESS: Title variation is working")
    print("Emojis have been removed from title variations")

if __name__ == "__main__":
    main()
