#!/usr/bin/env python3
"""
Simple debug script for image upload issues.
"""

import os
import sys

def check_accounts_directory():
    """Check accounts directory and images."""
    print("Checking accounts directory...")
    
    if not os.path.exists('accounts'):
        print("ERROR: accounts directory not found")
        return False
    
    print("SUCCESS: accounts directory exists")
    
    # List all accounts
    accounts = []
    for item in os.listdir('accounts'):
        item_path = os.path.join('accounts', item)
        if os.path.isdir(item_path):
            accounts.append(item)
    
    print(f"Found {len(accounts)} accounts: {accounts}")
    
    # Check for images in each account
    for account in accounts:
        account_path = os.path.join('accounts', account)
        print(f"\nChecking account: {account}")
        
        image_count = 0
        for root, dirs, files in os.walk(account_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        print(f"  Image: {file} ({file_size:,} bytes)")
                        image_count += 1
        
        print(f"  Total images: {image_count}")
    
    return True

def test_image_processing():
    """Test image processing modules."""
    print("\nTesting image processing...")
    
    # Test imports
    try:
        from image_cropper import ImageCropper
        print("SUCCESS: ImageCropper imported")
    except Exception as e:
        print(f"ERROR: ImageCropper import failed: {e}")
        return False
    
    try:
        from image_metadata import ImageMetadataModifier
        print("SUCCESS: ImageMetadataModifier imported")
    except Exception as e:
        print(f"ERROR: ImageMetadataModifier import failed: {e}")
        return False
    
    # Find a test image
    test_image = None
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break
    
    if not test_image:
        print("ERROR: No test image found")
        return False
    
    print(f"Testing with: {os.path.basename(test_image)}")
    
    # Test cropping
    try:
        cropper = ImageCropper()
        result = cropper.get_best_crop(test_image)
        
        if result['success']:
            print(f"SUCCESS: Crop created - {result['cropped_size']}")
            print(f"Output: {result['output_path']}")
            
            if os.path.exists(result['output_path']):
                size = os.path.getsize(result['output_path'])
                print(f"SUCCESS: Cropped file exists ({size:,} bytes)")
            else:
                print("ERROR: Cropped file missing")
                return False
        else:
            print(f"ERROR: Crop failed - {result['error']}")
            return False
            
    except Exception as e:
        print(f"ERROR: Cropping failed - {e}")
        return False
    
    # Test metadata
    try:
        modifier = ImageMetadataModifier()
        output_path = result['output_path'].replace('.', '_processed.')
        metadata_result = modifier.modify_image_metadata(result['output_path'], output_path)
        
        if metadata_result['success']:
            print(f"SUCCESS: Metadata applied - {output_path}")
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"SUCCESS: Final file exists ({size:,} bytes)")
                return True
            else:
                print("ERROR: Final file missing")
                return False
        else:
            print(f"ERROR: Metadata failed - {metadata_result['error']}")
            return False
            
    except Exception as e:
        print(f"ERROR: Metadata processing failed - {e}")
        return False

def main():
    """Run debug analysis."""
    print("IMAGE UPLOAD DEBUG")
    print("=" * 30)
    
    # Check directory structure
    if not check_accounts_directory():
        print("\nFAILURE: Directory structure issues")
        return
    
    # Test image processing
    if test_image_processing():
        print("\nSUCCESS: Image processing is working")
        print("\nThe issue may be in the Facebook upload process")
        print("Check the bot logs for specific upload errors")
    else:
        print("\nFAILURE: Image processing has issues")
        print("Fix the image processing before testing upload")

if __name__ == "__main__":
    main()
