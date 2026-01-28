#!/usr/bin/env python3
"""
Debug script for image upload issues.
"""

import os
import sys
from image_cropper import ImageCropper
from image_metadata import ImageMetadataModifier

def test_image_processing_pipeline():
    """Test the complete image processing pipeline."""
    print("Testing Image Processing Pipeline")
    print("=" * 50)
    
    # Find test images
    test_images = []
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(root, file))
                if len(test_images) >= 2:
                    break
        if len(test_images) >= 2:
            break
    
    if not test_images:
        print("❌ No test images found")
        print("💡 Add some images to the accounts directory to test")
        return False
    
    print(f"📸 Found {len(test_images)} test images")
    
    # Test cropping
    cropper = ImageCropper()
    cropped_images = []
    
    for i, image_path in enumerate(test_images):
        print(f"\n🔄 Processing image {i+1}: {os.path.basename(image_path)}")
        
        # Check if original exists
        if not os.path.exists(image_path):
            print(f"   ❌ Original image not found: {image_path}")
            continue
        
        original_size = os.path.getsize(image_path)
        print(f"   📊 Original size: {original_size:,} bytes")
        
        # Test cropping
        crop_result = cropper.get_best_crop(image_path)
        
        if crop_result['success']:
            cropped_path = crop_result['output_path']
            print(f"   ✅ Crop successful: {crop_result['cropped_size']}")
            print(f"   📁 Cropped file: {cropped_path}")
            
            # Check if cropped file exists
            if os.path.exists(cropped_path):
                cropped_size = os.path.getsize(cropped_path)
                print(f"   📊 Cropped size: {cropped_size:,} bytes")
                cropped_images.append(cropped_path)
            else:
                print(f"   ❌ Cropped file not found: {cropped_path}")
        else:
            print(f"   ❌ Crop failed: {crop_result['error']}")
            cropped_images.append(image_path)  # Use original as fallback
    
    if not cropped_images:
        print("❌ No valid images after cropping")
        return False
    
    print(f"\n✅ Cropping complete: {len(cropped_images)} images ready")
    
    # Test metadata modification
    metadata_modifier = ImageMetadataModifier()
    processed_images = []
    
    for i, image_path in enumerate(cropped_images):
        print(f"\n🔄 Applying metadata to image {i+1}: {os.path.basename(image_path)}")
        
        # Create output path
        dir_path = os.path.dirname(image_path)
        filename, ext = os.path.splitext(os.path.basename(image_path))
        output_path = os.path.join(dir_path, f"{filename}_processed{ext}")
        
        # Apply metadata
        result = metadata_modifier.modify_image_metadata(image_path, output_path)
        
        if result['success']:
            print(f"   ✅ Metadata applied successfully")
            print(f"   📍 Location: {result['location']['name']}")
            print(f"   📅 Date: {result['timestamp']}")
            print(f"   📱 Camera: {result['camera']}")
            
            # Check if processed file exists
            if os.path.exists(output_path):
                processed_size = os.path.getsize(output_path)
                print(f"   📊 Processed size: {processed_size:,} bytes")
                processed_images.append(output_path)
            else:
                print(f"   ❌ Processed file not found: {output_path}")
        else:
            print(f"   ❌ Metadata failed: {result['error']}")
            processed_images.append(image_path)  # Use cropped as fallback
    
    if not processed_images:
        print("❌ No valid images after metadata processing")
        return False
    
    print(f"\n✅ Metadata processing complete: {len(processed_images)} images ready")
    
    # Final validation
    print(f"\n🔍 Final validation:")
    valid_images = []
    for i, image_path in enumerate(processed_images):
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"   ✅ Image {i+1}: {os.path.basename(image_path)} ({file_size:,} bytes)")
            valid_images.append(image_path)
        else:
            print(f"   ❌ Image {i+1}: {os.path.basename(image_path)} - FILE NOT FOUND")
    
    if valid_images:
        print(f"\n🎉 SUCCESS: {len(valid_images)} images ready for upload")
        print("📤 Image paths for upload:")
        for i, path in enumerate(valid_images):
            print(f"   {i+1}. {path}")
        return True
    else:
        print(f"\n❌ FAILURE: No valid images found")
        return False

def test_file_paths():
    """Test file path handling."""
    print("\n🧪 Testing File Path Handling")
    print("=" * 40)
    
    # Test different path formats
    test_paths = [
        "accounts/test/image.jpg",
        "C:\\Users\\test\\image.jpg",
        "/home/user/image.jpg",
        "image.jpg"
    ]
    
    for path in test_paths:
        print(f"🔄 Testing path: {path}")
        print(f"   Exists: {os.path.exists(path)}")
        print(f"   Absolute: {os.path.abspath(path)}")
        print(f"   Dirname: {os.path.dirname(path)}")
        print(f"   Basename: {os.path.basename(path)}")
        print()

def main():
    """Run all tests."""
    print("Image Upload Debug Test")
    print("=" * 60)
    
    tests = [
        ("File Path Handling", test_file_paths),
        ("Image Processing Pipeline", test_image_processing_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Image processing should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("- Make sure you have images in the accounts directory")
        print("- Check file permissions")
        print("- Verify image formats are supported (jpg, jpeg, png)")

if __name__ == "__main__":
    main()
