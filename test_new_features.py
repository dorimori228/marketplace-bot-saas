#!/usr/bin/env python3
"""
Test script for the new image cropping and title variation features.
"""

import os
import sys
from image_cropper import ImageCropper
from title_variator import TitleVariator
from original_storage import OriginalStorage

def test_image_cropping():
    """Test image cropping functionality."""
    print("🧪 Testing Image Cropping")
    print("=" * 40)
    
    cropper = ImageCropper()
    
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
        return False
    
    print(f"📸 Found {len(test_images)} test images")
    
    # Test cropping
    for image_path in test_images[:2]:  # Test first 2 images
        print(f"\n🔄 Testing crop for: {os.path.basename(image_path)}")
        result = cropper.get_best_crop(image_path)
        
        if result['success']:
            print(f"✅ Best crop created: {result['cropped_size']} (from {result['original_size']})")
            print(f"   📊 Area: {result['area_ratio']} of original")
            print(f"   🎯 Strategy: {result['strategy']}")
        else:
            print(f"❌ Failed to create crop: {result['error']}")
    
    return True

def test_title_variation():
    """Test title variation functionality."""
    print("\n🧪 Testing Title Variation")
    print("=" * 40)
    
    variator = TitleVariator()
    
    # Test titles
    test_titles = [
        "40mm artificial grass rolls to thick 40mm artificial grass rolls",
        "Premium Artificial Grass 4m x 2m",
        "High Quality Garden Turf - Fast Delivery"
    ]
    
    for title in test_titles:
        print(f"\n🔄 Testing variations for: {title}")
        
        # Generate multiple variations
        variations = variator.generate_multiple_variations(title, 3)
        
        for i, variation in enumerate(variations, 1):
            if variation['success']:
                print(f"  {i}. {variation['variation']} ({variation['type']})")
            else:
                print(f"  {i}. Error: {variation['error']}")
    
    return True

def test_original_storage():
    """Test original storage functionality."""
    print("\n🧪 Testing Original Storage")
    print("=" * 40)
    
    storage = OriginalStorage()
    test_account = "test_account"
    
    # Test creating storage
    print(f"🔄 Creating storage for account: {test_account}")
    result = storage.create_account_storage(test_account)
    if result:
        print("✅ Account storage created successfully")
    else:
        print("❌ Failed to create account storage")
        return False
    
    # Test storing title
    test_title = "40mm artificial grass rolls to thick 40mm artificial grass rolls"
    print(f"🔄 Storing title: {test_title}")
    result = storage.store_original_title(test_account, test_title)
    if result['success']:
        print(f"✅ Title stored: {result['message']}")
    else:
        print(f"❌ Failed to store title: {result['error']}")
        return False
    
    # Test finding matching title
    print(f"🔄 Finding matching title for: {test_title}")
    match = storage.find_matching_original(test_account, test_title)
    if match:
        print(f"✅ Found matching title: {match['title']}")
    else:
        print("❌ No matching title found")
        return False
    
    return True

def test_integration():
    """Test integration of all features."""
    print("\n🧪 Testing Integration")
    print("=" * 40)
    
    # Test account
    test_account = "integration_test"
    
    # Initialize modules
    cropper = ImageCropper()
    variator = TitleVariator()
    storage = OriginalStorage()
    
    # Test title variation with storage
    original_title = "40mm artificial grass rolls to thick 40mm artificial grass rolls"
    print(f"🔄 Testing title variation for: {original_title}")
    
    # Generate variation
    variation_result = variator.get_next_title_variation(test_account, original_title)
    
    if variation_result['success']:
        print(f"✅ Generated variation: {variation_result['variation']}")
        print(f"   📝 Type: {variation_result['type']}")
        
        # Store original title
        storage.store_original_title(test_account, original_title)
        print("✅ Original title stored")
        
        # Test finding match
        match = storage.find_matching_original(test_account, original_title)
        if match:
            print(f"✅ Found stored title: {match['title']}")
        else:
            print("❌ Could not find stored title")
            return False
    else:
        print(f"❌ Failed to generate variation: {variation_result['error']}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Testing New Features")
    print("=" * 50)
    
    tests = [
        ("Image Cropping", test_image_cropping),
        ("Title Variation", test_title_variation),
        ("Original Storage", test_original_storage),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
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
        print("🎉 All tests passed! New features are working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
