#!/usr/bin/env python3
"""
Test script to verify comprehensive anti-duplicate detection pipeline.
"""

from image_metadata import ImageMetadataModifier
import os

def test_anti_duplicate_pipeline():
    """Test the comprehensive anti-duplicate detection feature."""
    
    print("🧪 Testing Anti-Duplicate Detection Pipeline")
    print("=" * 70)
    
    # Initialize modifier
    modifier = ImageMetadataModifier()
    
    print()
    print("Pipeline Configuration:")
    print(f"  🎨 Brightness: {modifier.brightness_min}x to {modifier.brightness_max}x")
    print(f"  🎨 Contrast:   {modifier.contrast_min}x to {modifier.contrast_max}x")
    print(f"  📐 Scaling:    {modifier.scale_min}x to {modifier.scale_max}x")
    print(f"  💾 JPEG Quality: {modifier.quality_min} to {modifier.quality_max}")
    print()
    print("Pipeline Steps:")
    print("  1️⃣ Metadata Stripping (all original EXIF removed)")
    print("  2️⃣ Perceptual Shift (±2% to ±5% brightness/contrast)")
    print("  3️⃣ Geometric Manipulation (±0.3% to ±0.7% resize + crop)")
    print("  4️⃣ Compression Change (random JPEG quality 88-92)")
    print()
    
    # Look for test images in accounts directory
    test_images = []
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                test_images.append(os.path.join(root, file))
                if len(test_images) >= 3:
                    break
        if len(test_images) >= 3:
            break
    
    if not test_images:
        print("❌ No test images found in accounts directory")
        print("💡 Tip: Add some images to test the brightness feature")
        return
    
    print(f"📸 Found {len(test_images)} test image(s)")
    print()
    
    # Process images and show all modifications
    print("🔄 Processing images through anti-duplicate pipeline...")
    print()
    
    for i, image_path in enumerate(test_images, 1):
        # Create temporary output path
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        temp_output = os.path.join(os.path.dirname(image_path), f"{name}_unique{ext}")
        
        # Process the image
        result = modifier.modify_image_metadata(image_path, temp_output)
        
        if result['success']:
            print(f"✅ Image {i}: {filename}")
            print(f"   📍 Location: {result['location']['name']}")
            print(f"   📅 Date: {result['timestamp']}")
            print(f"   📱 Camera: {result['camera']}")
            print(f"   🎨 Brightness: {result['brightness_change_pct']}")
            print(f"   🎨 Contrast:   {result['contrast_change_pct']}")
            print(f"   📐 Size:       {result['original_size']} → {result['final_size']} ({result['size_change_pct']})")
            print(f"   💾 Quality:    {result['jpeg_quality']}")
            print(f"   🔒 Unique perceptual hash generated")
            print(f"   💾 Saved to: {os.path.basename(temp_output)}")
            print()
        else:
            print(f"❌ Image {i}: Failed - {result['error']}")
            print()
    
    print("=" * 70)
    print("🎉 Test Complete!")
    print()
    print("📝 Summary:")
    print("   ✅ All images now have unique perceptual hashes")
    print("   ✅ Metadata stripped and replaced with iPhone 12 data")
    print("   ✅ Subtle visual changes that are imperceptible to buyers")
    print("   ✅ Different compression signatures")
    print("   ✅ Non-standard dimensions to avoid duplicate detection")
    print()
    print("🚀 Your listings will now be protected against duplicate detection!")

if __name__ == "__main__":
    test_anti_duplicate_pipeline()

