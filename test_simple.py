#!/usr/bin/env python3
"""
Simple test for image processing.
"""

import os
import sys

def test_image_files():
    """Test if image files exist."""
    print("Testing Image Files")
    print("=" * 30)
    
    # Find test images
    test_images = []
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(root, file))
                if len(test_images) >= 3:
                    break
        if len(test_images) >= 3:
            break
    
    if not test_images:
        print("No test images found")
        print("Add some images to the accounts directory to test")
        return False
    
    print(f"Found {len(test_images)} test images")
    
    # Check each image
    valid_images = []
    for i, image_path in enumerate(test_images):
        print(f"Image {i+1}: {os.path.basename(image_path)}")
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"  - Exists: Yes")
            print(f"  - Size: {file_size:,} bytes")
            valid_images.append(image_path)
        else:
            print(f"  - Exists: No")
    
    if valid_images:
        print(f"\nSUCCESS: {len(valid_images)} valid images found")
        return True
    else:
        print(f"\nFAILURE: No valid images found")
        return False

def main():
    """Run test."""
    print("Simple Image Test")
    print("=" * 20)
    
    result = test_image_files()
    
    if result:
        print("\nPASS: Image files are available")
    else:
        print("\nFAIL: No image files found")
        print("\nTroubleshooting:")
        print("- Add some .jpg, .jpeg, or .png files to the accounts directory")
        print("- Check file permissions")

if __name__ == "__main__":
    main()
