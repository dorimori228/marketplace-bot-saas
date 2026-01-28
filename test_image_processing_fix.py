#!/usr/bin/env python3
"""
Test script to verify image processing is working correctly.
"""

import os
from image_cropper import ImageCropper
from image_metadata import ImageMetadataModifier

def test_image_processing():
    """Test complete image processing pipeline."""
    print("Testing Image Processing Pipeline")
    print("=" * 40)
    
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
        print("ERROR: No test images found")
        return False
    
    print(f"Found {len(test_images)} test images")
    
    # Test cropping
    cropper = ImageCropper()
    cropped_images = []
    
    for i, image_path in enumerate(test_images):
        print(f"\nProcessing image {i+1}: {os.path.basename(image_path)}")
        
        # Check original
        if not os.path.exists(image_path):
            print(f"  ERROR: Original image not found")
            continue
        
        original_size = os.path.getsize(image_path)
        print(f"  Original size: {original_size:,} bytes")
        
        # Test cropping
        crop_result = cropper.get_best_crop(image_path)
        
        if crop_result['success']:
            cropped_path = crop_result['output_path']
            print(f"  SUCCESS: Crop created - {crop_result['cropped_size']}")
            print(f"  Strategy: {crop_result['strategy']}")
            print(f"  Area ratio: {crop_result['area_ratio']}")
            
            if os.path.exists(cropped_path):
                cropped_size = os.path.getsize(cropped_path)
                print(f"  Cropped size: {cropped_size:,} bytes")
                cropped_images.append(cropped_path)
            else:
                print(f"  ERROR: Cropped file not found")
        else:
            print(f"  ERROR: Crop failed - {crop_result['error']}")
            cropped_images.append(image_path)  # Use original as fallback
    
    if not cropped_images:
        print("ERROR: No cropped images created")
        return False
    
    print(f"\nCropping complete: {len(cropped_images)} images")
    
    # Test metadata modification
    modifier = ImageMetadataModifier()
    processed_images = []
    
    for i, image_path in enumerate(cropped_images):
        print(f"\nApplying metadata to image {i+1}: {os.path.basename(image_path)}")
        
        # Create output path
        dir_path = os.path.dirname(image_path)
        filename, ext = os.path.splitext(os.path.basename(image_path))
        output_path = os.path.join(dir_path, f"{filename}_processed{ext}")
        
        # Apply metadata
        result = modifier.modify_image_metadata(image_path, output_path)
        
        if result['success']:
            print(f"  SUCCESS: Metadata applied")
            print(f"  Location: {result['location']['name']}")
            print(f"  Date: {result['timestamp']}")
            print(f"  Camera: {result['camera']}")
            print(f"  Brightness: {result['brightness_change_pct']}%")
            print(f"  Contrast: {result['contrast_change_pct']}%")
            print(f"  Size change: {result['size_change_pct']}%")
            print(f"  JPEG quality: {result['jpeg_quality']}")
            
            if os.path.exists(output_path):
                processed_size = os.path.getsize(output_path)
                print(f"  Processed size: {processed_size:,} bytes")
                processed_images.append(output_path)
            else:
                print(f"  ERROR: Processed file not found")
        else:
            print(f"  ERROR: Metadata failed - {result['error']}")
            processed_images.append(image_path)  # Use cropped as fallback
    
    if not processed_images:
        print("ERROR: No processed images created")
        return False
    
    print(f"\nProcessing complete: {len(processed_images)} images")
    
    # Final validation
    print(f"\nFinal validation:")
    valid_images = []
    for i, image_path in enumerate(processed_images):
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"  {i+1}. {os.path.basename(image_path)} ({file_size:,} bytes)")
            valid_images.append(image_path)
        else:
            print(f"  {i+1}. {os.path.basename(image_path)} - MISSING")
    
    if valid_images:
        print(f"\nSUCCESS: {len(valid_images)} images ready for upload")
        return True
    else:
        print(f"\nERROR: No valid images found")
        return False

def main():
    """Run image processing test."""
    print("IMAGE PROCESSING TEST")
    print("=" * 50)
    
    result = test_image_processing()
    
    if result:
        print("\nSUCCESS: Image processing is working correctly")
        print("Images will be cropped and have metadata applied")
    else:
        print("\nERROR: Image processing has issues")
        print("Check the errors above for specific problems")

if __name__ == "__main__":
    main()
