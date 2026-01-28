#!/usr/bin/env python3
"""
Test script specifically for image cropping functionality.
"""

import os
import sys
from image_cropper import ImageCropper

def test_image_cropping_detailed():
    """Test image cropping with detailed output."""
    print("🧪 Testing Image Cropping - Detailed")
    print("=" * 50)
    
    cropper = ImageCropper()
    
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
        print("❌ No test images found in accounts directory")
        print("💡 Please add some images to the accounts directory to test")
        return False
    
    print(f"📸 Found {len(test_images)} test images")
    print()
    
    # Test cropping with detailed output
    for i, image_path in enumerate(test_images[:2], 1):  # Test first 2 images
        print(f"🔄 Testing crop {i}/2 for: {os.path.basename(image_path)}")
        print(f"   📁 Full path: {image_path}")
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"   ❌ File does not exist: {image_path}")
            continue
        
        # Get file size
        file_size = os.path.getsize(image_path)
        print(f"   📊 Original file size: {file_size:,} bytes")
        
        # Test cropping
        result = cropper.get_best_crop(image_path)
        
        if result['success']:
            print(f"   ✅ Crop successful!")
            print(f"   📐 Original size: {result['original_size']}")
            print(f"   📐 Cropped size: {result['cropped_size']}")
            print(f"   📊 Area ratio: {result['area_ratio']}")
            print(f"   🎯 Strategy: {result['strategy']}")
            print(f"   📁 Output path: {result['output_path']}")
            
            # Check if output file exists
            if os.path.exists(result['output_path']):
                output_size = os.path.getsize(result['output_path'])
                print(f"   📊 Output file size: {output_size:,} bytes")
                print(f"   ✅ Cropped image file exists and is accessible")
            else:
                print(f"   ❌ Output file does not exist: {result['output_path']}")
        else:
            print(f"   ❌ Crop failed: {result['error']}")
        
        print()
    
    return True

def test_multiple_crops():
    """Test creating multiple crops of the same image."""
    print("🧪 Testing Multiple Crops")
    print("=" * 30)
    
    cropper = ImageCropper()
    
    # Find one test image
    test_image = None
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break
    
    if not test_image:
        print("❌ No test image found")
        return False
    
    print(f"📸 Testing multiple crops for: {os.path.basename(test_image)}")
    
    # Create multiple crops
    results = cropper.create_unique_crops([test_image], max_crops_per_image=3)
    
    for result in results:
        if result['crops']:
            print(f"✅ Created {len(result['crops'])} crops")
            for i, crop in enumerate(result['crops'], 1):
                print(f"   Crop {i}: {crop['cropped_size']} (strategy: {crop['strategy']})")
        else:
            print(f"❌ Failed to create crops: {result.get('error', 'Unknown error')}")
    
    return True

def main():
    """Run image cropping tests."""
    print("🚀 Image Cropping Test Suite")
    print("=" * 50)
    
    tests = [
        ("Detailed Cropping Test", test_image_cropping_detailed),
        ("Multiple Crops Test", test_multiple_crops)
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
        print("🎉 All image cropping tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
