# Unique Content Features for Facebook Marketplace Bot

This document describes the new features added to make your Facebook Marketplace bot create unique content for each upload, helping avoid Facebook's duplicate detection.

## 🎯 Overview

The bot now includes four major new features:

1. **Image Cropping System** - Creates unique cropped versions of images
2. **Title Variation System** - Generates similar but unique titles
3. **Description Variation System** - Generates unique description variations
4. **Original Storage System** - Stores original content for future reference

## 📸 Image Cropping Features

### What it does:
- Creates unique cropped versions of your images for each upload
- Uses multiple cropping strategies (center, corners, random, smart)
- Maintains image quality while changing dimensions
- Works alongside existing metadata modification

### How it works:
1. **Smart Cropping**: Analyzes images and chooses the best crop strategy
2. **Size Variations**: Creates crops that are 85-105% of original size
3. **Aspect Ratio Changes**: Varies aspect ratios to create unique dimensions
4. **Quality Preservation**: Maintains high image quality during cropping

### Example:
- Original: 1920x1080 image
- Cropped: 1680x945 image (87.5% of original area)
- Strategy: Smart crop focusing on main content

## 📝 Title Variation Features

### What it does:
- Generates unique variations of your listing titles
- Uses multiple variation strategies (word substitution, prefixes, suffixes, emojis)
- Tracks title history to avoid duplicates
- Maintains the core meaning while changing the wording

### Variation Types:
1. **Word Substitution**: Replaces words with synonyms
   - "40mm artificial grass" → "40mm synthetic turf"
2. **Prefix/Suffix Addition**: Adds descriptive terms
   - "Artificial Grass" → "Premium Artificial Grass - Fast Delivery"
3. **Word Order Changes**: Rearranges words
   - "40mm artificial grass rolls" → "Artificial grass 40mm rolls"
4. **Emoji Addition**: Adds relevant emojis
   - "Artificial Grass" → "🌱 Artificial Grass ⭐"

### Example Progression:
- Original: "40mm artificial grass rolls to thick 40mm artificial grass rolls"
- Variation 1: "Premium 40mm artificial grass rolls - Fast Delivery"
- Variation 2: "🌱 40mm synthetic turf rolls ⭐"
- Variation 3: "Artificial grass 40mm thick rolls - Professional Grade"

## 📄 Description Variation Features

### What it does:
- Generates unique variations of your listing descriptions
- Uses multiple variation strategies (full rewrite, element substitution, emoji changes, structure changes)
- Maintains the core information while changing presentation
- Creates fresh descriptions for each upload

### Variation Types:
1. **Full Rewrite**: Completely rewrites the description with new structure
2. **Element Substitution**: Replaces specific elements (delivery info, samples, options)
3. **Emoji Variation**: Changes emojis while keeping content
4. **Structure Change**: Reorders elements and adds new information

### Example Progression:
- Original: "🚚 Fast Delivery: 2-4 days\n✅ Free Samples Available\n\n💷 Options Available:\n- Budget Range (30mm)\n- Mid-Range (35mm)\n- Premium Range (40mm)"
- Variation 1: "⚡ Quick Delivery: 2-4 days\n🎁 Free Samples Available\n\n💰 Options Available:\n- Economy Range (30mm)\n- Standard Range (35mm)\n- Luxury Range (40mm)"
- Variation 2: "📦 Fast Shipping: 2-4 days\n✨ Free Samples Available\n\n💵 Options Available:\n- Budget Range (30mm)\n- Professional Range (35mm)\n- High-End Range (40mm)\n\n✨ High Quality artificial grass\n🛡️ Durable construction"

## 💾 Original Storage System

### What it does:
- Stores original images and titles for each account
- Enables the bot to find and reuse original content
- Tracks title history to generate new variations
- Organizes content by account and listing

### Storage Structure:
```
accounts/
├── account_name/
│   ├── originals/
│   │   ├── images/
│   │   │   ├── 20240115_143022_artificial_grass/
│   │   │   │   ├── original_01.jpg
│   │   │   │   └── original_02.jpg
│   │   │   └── 20240115_143055_garden_turf/
│   │   ├── titles/
│   │   └── metadata.json
│   └── listings/
```

## 🔄 How It All Works Together

### For New Listings:
1. **Store Originals**: Bot stores your original images, title, and description
2. **Generate Variations**: Creates unique title and description variations
3. **Crop Images**: Creates unique cropped versions of images
4. **Apply Metadata**: Adds iPhone 12 metadata to cropped images
5. **Upload**: Uses the unique content for Facebook upload

### For Relisting:
1. **Find Original**: Bot searches for original content in storage
2. **Generate New Variations**: Creates new unique title and description variations
3. **Crop Original Images**: Creates new cropped versions from stored originals
4. **Apply Metadata**: Adds fresh metadata to new crops
5. **Upload**: Uses the new unique content

## 🚀 Benefits

### For Facebook Detection:
- **Unique Images**: Each upload has different dimensions and crops
- **Unique Titles**: Each listing has a different title variation
- **Fresh Metadata**: Each image has new location and timestamp data
- **Perceptual Differences**: Subtle changes that humans won't notice

### For Your Workflow:
- **Automated**: No manual intervention required
- **Consistent**: Maintains your brand and product information
- **Scalable**: Works with multiple accounts and listings
- **Trackable**: Keeps history of all variations used

## 📋 Usage Examples

### Example 1: First Upload
```
Original Title: "40mm artificial grass rolls"
Generated Variation: "Premium 40mm artificial grass rolls - Fast Delivery"
Images: Cropped to 1680x945, 1720x980, 1650x920
Result: Unique listing that Facebook sees as new content
```

### Example 2: Relisting Same Product
```
Bot searches for: "40mm artificial grass rolls"
Finds original in storage
Generates new variation: "🌱 40mm synthetic turf rolls ⭐"
Uses original images with new crops
Result: Another unique listing
```

### Example 3: Multiple Accounts
```
Account 1: "40mm artificial grass rolls" → "Premium 40mm artificial grass"
Account 2: "40mm artificial grass rolls" → "🌱 40mm synthetic turf ⭐"
Each account maintains separate variation history
```

## 🛠️ Technical Details

### Files Added:
- `image_cropper.py` - Image cropping functionality
- `title_variator.py` - Title variation system
- `description_variator.py` - Description variation system
- `original_storage.py` - Original content storage
- `test_new_features.py` - Test script for new features
- `test_all_features.py` - Comprehensive test script
- `test_image_cropping.py` - Image cropping specific tests

### Files Modified:
- `bot.py` - Integrated new features into bot workflow
- `app.py` - Added account information to listing data

### Dependencies:
- PIL (Pillow) - Image processing
- json - Data storage
- hashlib - File hashing
- datetime - Timestamping

## 🧪 Testing

Run the comprehensive test script to verify everything works:

```bash
python test_all_features.py
```

This will test:
- Image cropping functionality
- Title variation generation
- Description variation generation
- Original storage system
- Integration between all features
- Complete image processing pipeline

You can also run specific tests:
```bash
python test_image_cropping.py  # Test only image cropping
python test_new_features.py    # Test basic functionality
```

## 📊 Monitoring

The bot provides detailed logging for all new features:

```
🔄 Generating unique title variation for: 40mm artificial grass rolls
✅ Generated unique title: Premium 40mm artificial grass rolls - Fast Delivery
   📝 Type: prefix_suffix
   🔄 Changes: Added prefix/suffix to: 40mm artificial grass rolls

🎯 Creating unique crop...
✅ Crop created: 1680x945 (from 1920x1080)
   📊 Area: 0.875 of original
   🎯 Strategy: smart

💾 Storing original images...
✅ Stored 3 original images
```

## 🔧 Configuration

### Image Cropping Settings:
- Size variations: 85-105% of original
- Aspect ratios: Square, 4:3, 16:9, and custom ratios
- Strategies: Center, corners, random, smart

### Title Variation Settings:
- Word variations: Extensive synonym database
- Prefixes: Premium, High Quality, Professional, etc.
- Suffixes: Fast Delivery, Free Delivery, UK Made, etc.
- Emojis: 🌱, ⭐, 🚚, 💰, etc.

### Storage Settings:
- Automatic cleanup of old files (30+ days)
- Metadata tracking for all content
- Account-specific organization

## 🎉 Results

With these new features, your bot will:

1. **Avoid Duplicate Detection**: Each upload is genuinely unique
2. **Maintain Quality**: Images and titles remain professional
3. **Scale Efficiently**: Works with multiple accounts and products
4. **Track History**: Knows what variations have been used
5. **Generate Fresh Content**: Always creates new unique content

The bot now creates truly unique content for each upload while maintaining your brand identity and product information. Facebook will see each listing as completely new content, helping you avoid detection and maintain successful listings.
