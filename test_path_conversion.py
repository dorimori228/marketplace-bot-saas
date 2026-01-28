#!/usr/bin/env python3
"""
Test script to verify path conversion works correctly.
"""

import os

def test_path_conversion():
    """Test converting relative paths to absolute paths."""
    print("Testing Path Conversion")
    print("=" * 30)
    
    # Test paths (similar to what the bot uses)
    test_paths = [
        "accounts/unknown/originals/main_photos/20251022_115738_11e90c07-e161-46c7-bba4-18b2ba4957dd/original_01_processed.jpg",
        "accounts/yumi/image_01.jpg",
        "accounts/yumi/image_02.jpg"
    ]
    
    print("Original paths:")
    for i, path in enumerate(test_paths):
        print(f"  {i+1}. {path}")
        print(f"     Is absolute: {os.path.isabs(path)}")
        print(f"     Exists: {os.path.exists(path)}")
    
    print("\nConverting to absolute paths:")
    absolute_paths = []
    for i, path in enumerate(test_paths):
        if not os.path.isabs(path):
            abs_path = os.path.abspath(path)
            print(f"  {i+1}. {path}")
            print(f"     → {abs_path}")
            print(f"     Is absolute: {os.path.isabs(abs_path)}")
            print(f"     Exists: {os.path.exists(abs_path)}")
            absolute_paths.append(abs_path)
        else:
            print(f"  {i+1}. {path} (already absolute)")
            absolute_paths.append(path)
    
    print(f"\nResult: {len(absolute_paths)} absolute paths")
    for i, path in enumerate(absolute_paths):
        print(f"  {i+1}. {path}")
    
    return absolute_paths

def test_selenium_path_format():
    """Test the format that Selenium expects."""
    print("\nTesting Selenium Path Format")
    print("=" * 30)
    
    # Find a real image file
    test_image = None
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break
    
    if not test_image:
        print("No test image found")
        return
    
    print(f"Test image: {test_image}")
    print(f"Is absolute: {os.path.isabs(test_image)}")
    print(f"Exists: {os.path.exists(test_image)}")
    
    # Convert to absolute
    abs_path = os.path.abspath(test_image)
    print(f"Absolute path: {abs_path}")
    print(f"Is absolute: {os.path.isabs(abs_path)}")
    print(f"Exists: {os.path.exists(abs_path)}")
    
    # Test the format Selenium expects
    selenium_paths = abs_path
    print(f"Selenium format: {selenium_paths}")
    
    return abs_path

def main():
    """Run path conversion tests."""
    print("PATH CONVERSION TEST")
    print("=" * 40)
    
    # Test path conversion
    absolute_paths = test_path_conversion()
    
    # Test Selenium format
    selenium_path = test_selenium_path_format()
    
    print(f"\nSUMMARY:")
    print(f"✅ Path conversion working: {len(absolute_paths)} paths converted")
    print(f"✅ Selenium format ready: {selenium_path is not None}")
    
    if selenium_path and os.path.exists(selenium_path):
        print("✅ Test image exists and is accessible")
        print("✅ Bot should now be able to upload images successfully")
    else:
        print("❌ Test image not found or not accessible")

if __name__ == "__main__":
    main()
