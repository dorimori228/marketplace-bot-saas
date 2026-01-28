#!/usr/bin/env python3
"""
Test script for image metadata modification functionality.
"""

import os
import sys
from image_metadata import ImageMetadataModifier

def test_metadata_modification():
    """Test the metadata modification functionality."""
    print("🧪 Testing Image Metadata Modification")
    print("=" * 50)
    
    # Initialize modifier
    modifier = ImageMetadataModifier()
    
    # Find test images
    test_images = []
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(root, file))
                if len(test_images) >= 3:  # Test with up to 3 images
                    break
        if len(test_images) >= 3:
            break
    
    if not test_images:
        print("❌ No test images found in accounts directory")
        print("💡 Add some images to test the metadata modification")
        return False
    
    print(f"📸 Found {len(test_images)} test images")
    print()
    
    # Test individual image modification
    print("🔧 Testing individual image modification...")
    test_image = test_images[0]
    print(f"📁 Test image: {os.path.basename(test_image)}")
    
    # Create output directory for test
    test_output_dir = "test_metadata_output"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Get original image info
    print("\n📊 Original image info:")
    original_info = modifier.get_image_info(test_image)
    if original_info['has_exif']:
        print("✅ Has EXIF data")
        if 'Make' in original_info['exif_data']:
            print(f"   Camera: {original_info['exif_data'].get('Make', 'Unknown')} {original_info['exif_data'].get('Model', 'Unknown')}")
        if 'DateTime' in original_info['exif_data']:
            print(f"   Date: {original_info['exif_data'].get('DateTime', 'Unknown')}")
    else:
        print("❌ No EXIF data found")
    
    # Modify the image
    output_path = os.path.join(test_output_dir, f"modified_{os.path.basename(test_image)}")
    result = modifier.modify_image_metadata(test_image, output_path)
    
    if result['success']:
        print(f"\n✅ Image modified successfully!")
        print(f"📁 Output: {output_path}")
        print(f"📍 Location: {result['location']['name']} ({result['location']['lat']:.4f}, {result['location']['lon']:.4f})")
        print(f"📅 Date: {result['timestamp']}")
        print(f"📱 Camera: {result['camera']}")
        
        # Check modified image info
        print("\n📊 Modified image info:")
        modified_info = modifier.get_image_info(output_path)
        if modified_info['has_exif']:
            print("✅ Has EXIF data")
            if 'Make' in modified_info['exif_data']:
                print(f"   Camera: {modified_info['exif_data'].get('Make', 'Unknown')} {modified_info['exif_data'].get('Model', 'Unknown')}")
            if 'DateTime' in modified_info['exif_data']:
                print(f"   Date: {modified_info['exif_data'].get('DateTime', 'Unknown')}")
            if 'GPS' in modified_info['exif_data']:
                print("   GPS: ✅ Location data present")
        else:
            print("❌ No EXIF data found")
    else:
        print(f"❌ Failed to modify image: {result['error']}")
        return False
    
    # Test multiple image modification
    print(f"\n🔧 Testing multiple image modification...")
    multiple_results = modifier.modify_multiple_images(test_images[:2], test_output_dir)
    
    successful = sum(1 for r in multiple_results if r['success'])
    print(f"\n📊 Multiple image test: {successful}/{len(multiple_results)} successful")
    
    # Show UK locations
    print(f"\n🇬🇧 Available UK locations:")
    for i, location in enumerate(modifier.uk_locations[:10], 1):
        print(f"   {i:2d}. {location['name']} ({location['lat']:.4f}, {location['lon']:.4f})")
    if len(modifier.uk_locations) > 10:
        print(f"   ... and {len(modifier.uk_locations) - 10} more")
    
    print(f"\n🎉 Metadata modification test completed!")
    print(f"📁 Test output directory: {test_output_dir}")
    print("💡 Check the modified images to see the new metadata")
    
    return True

def show_metadata_info():
    """Show information about the metadata modification system."""
    print("\n📋 METADATA MODIFICATION INFO")
    print("=" * 40)
    print()
    print("🔧 What gets modified:")
    print("   • Camera make/model → Apple iPhone 12")
    print("   • GPS coordinates → Random UK location")
    print("   • Date/time → Random date within last 30 days")
    print("   • Camera settings → iPhone 12 specifications")
    print()
    print("🇬🇧 UK Locations included:")
    modifier = ImageMetadataModifier()
    for location in modifier.uk_locations:
        print(f"   • {location['name']}")
    print()
    print("📱 iPhone 12 Camera Specs:")
    specs = modifier.iphone_12_specs
    print(f"   • Make: {specs['make']}")
    print(f"   • Model: {specs['model']}")
    print(f"   • Focal Length: {specs['focal_length'][0]}mm")
    print(f"   • Lens: {specs['lens_model']}")

def main():
    """Main test function."""
    print("🧪 Image Metadata Modification Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--info':
        show_metadata_info()
        return
    
    try:
        success = test_metadata_modification()
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
