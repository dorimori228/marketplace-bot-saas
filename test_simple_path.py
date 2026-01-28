#!/usr/bin/env python3
"""
Simple test for path conversion.
"""

import os

def test_path_conversion():
    """Test converting relative paths to absolute paths."""
    print("Testing Path Conversion")
    print("=" * 30)
    
    # Test with a real path that exists
    test_path = "accounts/unknown/originals/main_photos/20251022_115738_11e90c07-e161-46c7-bba4-18b2ba4957dd/original_01_processed.jpg"
    
    print(f"Original path: {test_path}")
    print(f"Is absolute: {os.path.isabs(test_path)}")
    print(f"Exists: {os.path.exists(test_path)}")
    
    # Convert to absolute
    abs_path = os.path.abspath(test_path)
    print(f"Absolute path: {abs_path}")
    print(f"Is absolute: {os.path.isabs(abs_path)}")
    print(f"Exists: {os.path.exists(abs_path)}")
    
    return abs_path

def main():
    """Run path conversion test."""
    print("PATH CONVERSION TEST")
    print("=" * 40)
    
    abs_path = test_path_conversion()
    
    if abs_path and os.path.exists(abs_path):
        print("\nSUCCESS: Path conversion working")
        print("The bot should now be able to upload images with absolute paths")
    else:
        print("\nFAILURE: Path conversion not working")

if __name__ == "__main__":
    main()
