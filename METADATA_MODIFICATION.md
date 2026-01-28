# Image Metadata Modification Guide

This guide explains the automatic image metadata modification feature that makes your listing photos appear as if they were taken on an iPhone 12 from random UK locations.

## 🎯 What It Does

Every time you create a listing, the bot automatically:

1. **Modifies image metadata** to appear as iPhone 12 photos
2. **Adds random UK GPS coordinates** for authentic location data
3. **Sets realistic timestamps** (within the last 30 days)
4. **Includes proper camera specifications** (focal length, lens info, etc.)
5. **Cleans up temporary files** after upload

## 📱 iPhone 12 Camera Specifications

The bot uses authentic iPhone 12 camera metadata:

- **Make**: Apple
- **Model**: iPhone 12
- **Focal Length**: 4mm
- **Lens**: iPhone 12 back dual wide camera 4.25mm f/1.6
- **Software**: iOS 15.0
- **Resolution**: 72 DPI
- **Color Space**: sRGB

## 🇬🇧 UK Locations

Photos are randomly assigned GPS coordinates from 20 major UK cities:

- London, Manchester, Birmingham, Leeds
- Glasgow, Edinburgh, Liverpool, Bristol
- Newcastle, Sheffield, Nottingham, Leicester
- Coventry, Bradford, Cardiff, Belfast
- Brighton, Plymouth, Southampton, Reading

Each location includes small random variations (±0.1 degrees ≈ ±11km) for authenticity.

## 🔧 How It Works

### Automatic Processing:
1. **Image Upload**: When you upload images through the web interface
2. **Metadata Modification**: Bot automatically processes each image
3. **Temporary Files**: Creates modified versions with new metadata
4. **Upload**: Uses modified images for Facebook listing
5. **Cleanup**: Removes temporary files after successful upload

### What Gets Modified:
- **Camera Information**: Make, model, software version
- **GPS Data**: Latitude, longitude, altitude
- **Timestamps**: Date and time (random within last 30 days)
- **Camera Settings**: Focal length, lens specifications
- **Technical Data**: Resolution, color space, orientation

## 📊 Example Output

When processing images, you'll see output like:

```
📸 Processing images with iPhone 12 metadata...
🔧 Modifying 3 image(s) with random UK locations

🔄 Processing image 1/3: product_photo.jpg
✅ Image 1 processed successfully
   📍 Location: Manchester (53.4808, -2.2426)
   📅 Date: 2024-01-15 14:23:45
   📱 Camera: Apple iPhone 12

🔄 Processing image 2/3: product_detail.jpg
✅ Image 2 processed successfully
   📍 Location: Birmingham (52.4862, -1.8904)
   📅 Date: 2024-01-12 09:15:30
   📱 Camera: Apple iPhone 12

🎉 Image processing complete! 3 images ready for upload
```

## 🛠️ Technical Details

### Dependencies:
- **Pillow**: Image processing and EXIF handling
- **piexif**: EXIF data manipulation
- **Python 3.7+**: Required for modern features

### File Processing:
- **Input**: Original images (JPG, PNG, etc.)
- **Processing**: Creates temporary modified versions
- **Output**: Images with iPhone 12 metadata
- **Cleanup**: Removes temporary files automatically

### Error Handling:
- **Fallback**: If metadata modification fails, uses original images
- **Logging**: Detailed error messages and progress updates
- **Cleanup**: Always removes temporary files, even on errors

## 🧪 Testing

### Test the functionality:
```bash
python test_metadata.py
```

### View metadata info:
```bash
python test_metadata.py --info
```

### Test with specific images:
```python
from image_metadata import ImageMetadataModifier

modifier = ImageMetadataModifier()
result = modifier.modify_image_metadata('your_image.jpg', 'output.jpg')
print(result)
```

## 📁 File Structure

```
facebook-marketplace-bot/
├── image_metadata.py          # Main metadata modification module
├── test_metadata.py           # Test script
├── METADATA_MODIFICATION.md   # This guide
├── requirements.txt           # Updated with Pillow and piexif
└── bot.py                     # Updated with metadata integration
```

## 🔒 Privacy & Security

### What's Safe:
- **Local Processing**: All metadata modification happens locally
- **No Upload**: Original images are never sent to external services
- **Temporary Files**: Modified images are deleted after upload
- **Random Data**: All location and timestamp data is randomly generated

### What's Modified:
- **EXIF Data Only**: Image content remains unchanged
- **Metadata Only**: No visual changes to the actual photos
- **Reversible**: Original images are preserved

## 🎯 Benefits

### Authenticity:
- **Realistic Metadata**: Photos appear as genuine iPhone 12 shots
- **UK Locations**: Random but realistic UK GPS coordinates
- **Recent Dates**: Timestamps within the last 30 days
- **Proper Specs**: Accurate iPhone 12 camera specifications

### Automation:
- **Zero Manual Work**: Completely automatic processing
- **Seamless Integration**: Works with existing bot workflow
- **Error Recovery**: Falls back to original images if needed
- **Clean Operation**: No leftover temporary files

## 🚀 Usage

The metadata modification is **completely automatic**! Just:

1. **Upload images** through the web interface as usual
2. **Create your listing** normally
3. **The bot handles everything** - metadata modification, upload, cleanup
4. **Your photos appear authentic** with iPhone 12 metadata and UK locations

## 🔧 Troubleshooting

### Common Issues:

1. **"No EXIF data found"**
   - Normal for some image formats
   - Bot will add new metadata

2. **"Failed to process image"**
   - Check image file permissions
   - Ensure image is not corrupted
   - Bot will use original image as fallback

3. **"Temporary files not cleaned up"**
   - Check file permissions
   - Manually delete files with `_temp` in filename
   - Usually resolves on next run

### Dependencies:
```bash
pip install Pillow>=10.0.0 piexif>=1.1.3
```

## 📈 Performance

- **Processing Time**: ~1-2 seconds per image
- **File Size**: Minimal increase due to EXIF data
- **Memory Usage**: Low - processes one image at a time
- **Storage**: Temporary files are automatically cleaned up

## 🎉 Result

Your Facebook Marketplace listings will now have:

✅ **Authentic iPhone 12 metadata**  
✅ **Random UK GPS locations**  
✅ **Realistic timestamps**  
✅ **Professional camera specifications**  
✅ **Completely automatic processing**  

No more suspicious metadata that might indicate automated posting! 🚀
