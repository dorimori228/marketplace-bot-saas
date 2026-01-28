#!/usr/bin/env python3
"""
Debug script to identify the exact image upload issue.
"""

import os
import sys

def debug_image_paths():
    """Debug image paths and processing."""
    print("DEBUG: Image Path Analysis")
    print("=" * 40)
    
    # Check accounts directory structure
    print("1. Checking accounts directory structure:")
    if os.path.exists('accounts'):
        print("   ✅ accounts directory exists")
        for account in os.listdir('accounts'):
            account_path = os.path.join('accounts', account)
            if os.path.isdir(account_path):
                print(f"   📁 Account: {account}")
                
                # Check for images in account directory
                image_count = 0
                for root, dirs, files in os.walk(account_path):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_path = os.path.join(root, file)
                            if os.path.exists(image_path):
                                file_size = os.path.getsize(image_path)
                                print(f"      📸 {file} ({file_size:,} bytes)")
                                image_count += 1
                
                print(f"      Total images: {image_count}")
    else:
        print("   ❌ accounts directory not found")
    
    print("\n2. Testing image processing modules:")
    
    # Test image cropper
    try:
        from image_cropper import ImageCropper
        print("   ✅ ImageCropper imported successfully")
        
        cropper = ImageCropper()
        print("   ✅ ImageCropper initialized")
        
        # Find a test image
        test_image = None
        for root, dirs, files in os.walk('accounts'):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image = os.path.join(root, file)
                    break
            if test_image:
                break
        
        if test_image:
            print(f"   📸 Testing with: {os.path.basename(test_image)}")
            result = cropper.get_best_crop(test_image)
            if result['success']:
                print(f"   ✅ Crop successful: {result['cropped_size']}")
                print(f"   📁 Output: {result['output_path']}")
                if os.path.exists(result['output_path']):
                    print(f"   ✅ Cropped file exists")
                else:
                    print(f"   ❌ Cropped file missing")
            else:
                print(f"   ❌ Crop failed: {result['error']}")
        else:
            print("   ⚠️ No test image found")
            
    except Exception as e:
        print(f"   ❌ ImageCropper error: {e}")
    
    # Test metadata modifier
    try:
        from image_metadata import ImageMetadataModifier
        print("   ✅ ImageMetadataModifier imported successfully")
        
        modifier = ImageMetadataModifier()
        print("   ✅ ImageMetadataModifier initialized")
        
    except Exception as e:
        print(f"   ❌ ImageMetadataModifier error: {e}")
    
    print("\n3. Testing file path handling:")
    
    # Test different path scenarios
    test_paths = [
        "accounts/yumi/image_01.jpg",
        "accounts/yumi/image_02.jpg", 
        "accounts/yumi/image_03.jpg"
    ]
    
    for path in test_paths:
        print(f"   Testing: {path}")
        print(f"      Exists: {os.path.exists(path)}")
        if os.path.exists(path):
            print(f"      Size: {os.path.getsize(path):,} bytes")
            print(f"      Absolute: {os.path.abspath(path)}")
        print()

def test_complete_processing():
    """Test complete image processing pipeline."""
    print("\nDEBUG: Complete Processing Test")
    print("=" * 40)
    
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
        print("❌ No test images found")
        return False
    
    print(f"📸 Found {len(test_images)} test images")
    
    # Test each step
    try:
        from image_cropper import ImageCropper
        from image_metadata import ImageMetadataModifier
        
        cropper = ImageCropper()
        modifier = ImageMetadataModifier()
        
        processed_images = []
        
        for i, image_path in enumerate(test_images):
            print(f"\n🔄 Processing image {i+1}: {os.path.basename(image_path)}")
            
            # Step 1: Crop
            crop_result = cropper.get_best_crop(image_path)
            if not crop_result['success']:
                print(f"   ❌ Crop failed: {crop_result['error']}")
                continue
            
            cropped_path = crop_result['output_path']
            print(f"   ✅ Cropped: {cropped_path}")
            
            if not os.path.exists(cropped_path):
                print(f"   ❌ Cropped file missing: {cropped_path}")
                continue
            
            # Step 2: Metadata
            output_path = cropped_path.replace('.', '_processed.')
            result = modifier.modify_image_metadata(cropped_path, output_path)
            
            if result['success']:
                print(f"   ✅ Metadata applied: {output_path}")
                if os.path.exists(output_path):
                    processed_images.append(output_path)
                    print(f"   ✅ Final file exists: {os.path.getsize(output_path):,} bytes")
                else:
                    print(f"   ❌ Final file missing: {output_path}")
            else:
                print(f"   ❌ Metadata failed: {result['error']}")
                # Use cropped image as fallback
                processed_images.append(cropped_path)
        
        print(f"\n📊 Processing Results:")
        print(f"   Input images: {len(test_images)}")
        print(f"   Processed images: {len(processed_images)}")
        
        if processed_images:
            print(f"   ✅ SUCCESS: {len(processed_images)} images ready for upload")
            for i, path in enumerate(processed_images):
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"      {i+1}. {os.path.basename(path)} ({size:,} bytes)")
                else:
                    print(f"      {i+1}. {os.path.basename(path)} - MISSING")
            return True
        else:
            print(f"   ❌ FAILURE: No processed images")
            return False
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return False

def main():
    """Run debug analysis."""
    print("IMAGE UPLOAD DEBUG ANALYSIS")
    print("=" * 50)
    
    debug_image_paths()
    result = test_complete_processing()
    
    print(f"\n{'='*50}")
    if result:
        print("✅ DIAGNOSIS: Image processing is working correctly")
        print("   The issue may be in the Facebook upload process")
    else:
        print("❌ DIAGNOSIS: Image processing has issues")
        print("   Check the errors above for specific problems")
    
    print("\nRECOMMENDATIONS:")
    print("1. Ensure images exist in accounts/yumi/ directory")
    print("2. Check file permissions")
    print("3. Verify image formats (jpg, jpeg, png)")
    print("4. Test with smaller images if needed")

if __name__ == "__main__":
    main()
