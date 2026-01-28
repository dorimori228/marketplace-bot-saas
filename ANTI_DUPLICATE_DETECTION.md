# Anti-Duplicate Detection Pipeline

## Overview

This Facebook Marketplace bot now includes a comprehensive **anti-duplicate detection pipeline** that processes every listing image to generate a unique perceptual hash. This prevents Facebook from flagging your listings as duplicates or reposts, while maintaining high visual quality for buyers.

## How It Works

Every image uploaded through the bot goes through a **4-step sequential pipeline**:

### Pipeline Steps

#### 1️⃣ **Metadata Stripping**
- **Action**: Removes all existing EXIF data (GPS, camera model, timestamps, etc.)
- **Replacement**: Adds new iPhone 12 metadata with random UK location and timestamp
- **Purpose**: Ensures metadata fingerprint is unique for each listing

#### 2️⃣ **Perceptual Shift**
- **Action**: Applies minimal random adjustments to image properties
- **Parameters**:
  - Brightness: ±3% to ±5% (0.97x to 1.05x)
  - Contrast: ±2% to ±5% (0.98x to 1.05x)
- **Purpose**: Creates subtle visual differences that are imperceptible to human eyes but change the perceptual hash

#### 3️⃣ **Geometric Manipulation**
- **Action**: Resizes image dimensions by a small, non-standard amount
- **Parameters**:
  - Scale factor: ±0.3% to ±0.7% (0.997x to 1.007x)
  - Additional pixel adjustments: ±1 to ±3 pixels per dimension
- **Example**: 1000x1000px → 997x997px or 1005x1003px
- **Purpose**: Changes pixel dimensions to create a unique image signature

#### 4️⃣ **Compression Change**
- **Action**: Re-saves image as JPEG with random quality setting
- **Parameters**: Quality level 88-92 (instead of typical 90 or 95)
- **Purpose**: Forces a new compression signature that differs from standard settings

## Technical Details

### Configuration Values

```python
# Perceptual Shift Ranges
brightness_min = 0.97    # -3% brightness
brightness_max = 1.05    # +5% brightness
contrast_min = 0.98      # -2% contrast
contrast_max = 1.05      # +5% contrast

# Geometric Manipulation
scale_min = 0.997        # -0.3% size
scale_max = 1.007        # +0.7% size

# JPEG Quality
quality_min = 88
quality_max = 92
```

### Image Quality Guarantee

All modifications are designed to be:
- ✅ **Imperceptible** to human viewers
- ✅ **High-quality** and clear for buyers
- ✅ **Unique** for duplicate detection algorithms
- ✅ **Professional** looking across all platforms

### Example Output

When processing an image, you'll see output like this:

```
✅ Image 1 processed successfully
   📍 Location: London (51.5234, -0.1456)
   📅 Date: 2025-01-05 14:32:18
   📱 Camera: Apple iPhone 12
   🎨 Perceptual Shift: Brightness +2.34%, Contrast -1.67%
   📐 Size Change: 1920x1080 → 1917x1078 (-0.34%)
   💾 JPEG Quality: 89
   🔒 Unique perceptual hash generated
```

## Why This Works

### Perceptual Hashing

Duplicate detection systems (like Facebook's) use **perceptual hashing** algorithms that:
1. Analyze image content (colors, edges, patterns)
2. Create a "fingerprint" of the image
3. Compare fingerprints to detect duplicates

Our pipeline changes:
- ✅ **Visual fingerprint** (brightness, contrast)
- ✅ **Geometric fingerprint** (dimensions, pixel count)
- ✅ **Compression fingerprint** (JPEG quality, artifacts)
- ✅ **Metadata fingerprint** (EXIF data)

By modifying all four aspects, we ensure each image generates a **completely unique perceptual hash**.

## Testing

### Test Script

Run the included test script to verify the pipeline:

```bash
python test_brightness.py
```

This will:
1. Find test images in your accounts directory
2. Process them through the pipeline
3. Show detailed modification statistics
4. Save test outputs for comparison

### Manual Verification

You can verify the pipeline is working by:

1. **Visual Inspection**: Processed images should look identical to originals
2. **Metadata Check**: Use an EXIF viewer to see new iPhone 12 metadata
3. **File Size**: Output files will have slightly different file sizes
4. **Hash Comparison**: Use image hashing tools to verify unique hashes

## Benefits

### For You
- 🛡️ **Protection** against duplicate detection
- ♻️ **Repost** the same items without being flagged
- 🤖 **Automated** - no manual work required
- 🎯 **Reliable** - works consistently

### For Buyers
- ✨ **High Quality** - images remain clear and professional
- 👁️ **No Visible Changes** - modifications are imperceptible
- 📱 **Authentic Looking** - appears as real iPhone photos
- 🌍 **Realistic** - includes UK location metadata

## Best Practices

### Multiple Listings of Same Item

If you want to relist the same item multiple times:

1. **Use Original Photos**: Start with your original, high-quality photos
2. **Let Bot Process**: The pipeline will automatically create unique versions
3. **Different Timings**: Space out listings by a few hours/days
4. **Vary Text**: Use slightly different titles and descriptions

### Image Quality Tips

For best results with the anti-duplicate pipeline:

- ✅ Use high-resolution source images (1000x1000px or larger)
- ✅ Start with clear, well-lit photos
- ✅ Avoid heavily compressed images
- ✅ Use JPEG or PNG formats
- ❌ Don't use images that are already heavily edited
- ❌ Avoid very small images (<500px)

## Technical Notes

### Image Formats

- **Input**: Accepts JPEG, PNG, WEBP, GIF
- **Output**: Always saves as JPEG for optimal compatibility
- **Conversion**: Automatically converts RGBA/transparency to RGB

### Processing Time

- **Per Image**: ~0.5-2 seconds (depending on size)
- **Multiple Images**: Processed sequentially
- **No Limit**: Can handle unlimited images per listing

### File Size Impact

- **Typical Change**: ±5-15% file size difference
- **Quality**: No visible quality loss
- **Optimization**: JPEG optimization enabled

## Maintenance

### Adjusting Ranges

If you want to adjust the modification ranges, edit `image_metadata.py`:

```python
# Make changes more subtle
self.brightness_min = 0.98  # Less brightness variation
self.brightness_max = 1.03

# Make changes more aggressive
self.contrast_min = 0.95    # More contrast variation
self.contrast_max = 1.08
```

### Disabling Steps

You can comment out specific steps in `modify_image_metadata()` if needed, but this will reduce anti-duplicate effectiveness.

## Troubleshooting

### Images Look Too Different

If processed images look noticeably different:
- Reduce the brightness/contrast ranges
- Check source image quality
- Ensure proper lighting in original photos

### Still Getting Duplicate Flags

If Facebook still flags duplicates:
- Verify all 4 pipeline steps are active
- Check that source images are different
- Space out your listings more
- Vary your listing text content

### Processing Errors

If images fail to process:
- Check image file format is supported
- Verify image isn't corrupted
- Ensure sufficient disk space
- Review console error messages

## Support

For issues or questions:
1. Check console output for error messages
2. Run test script to verify pipeline functionality
3. Review this documentation for configuration options
4. Check image source quality and format

## Version History

**v2.0** - Comprehensive Anti-Duplicate Pipeline
- Added perceptual shift (brightness + contrast)
- Added geometric manipulation (resize + crop)
- Added compression variation (random JPEG quality)
- Enhanced metadata replacement

**v1.0** - Basic Metadata Modification
- iPhone 12 metadata injection
- UK location randomization
- Timestamp randomization

---

**Last Updated**: January 2025

