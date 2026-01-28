#!/usr/bin/env python3
"""
Image Metadata Modification Module
Modifies image EXIF data to appear as if taken on iPhone 12 from random UK locations.
"""

import os
import random
import datetime
from PIL import Image, ImageEnhance
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import json

class ImageMetadataModifier:
    """Modifies image metadata to appear as iPhone 12 photos from UK locations."""
    
    def __init__(self):
        """Initialize the metadata modifier with iPhone 12 camera specs."""
        # Perceptual shift ranges (±10% to ±25% for very noticeable changes)
        self.brightness_min = 0.85  # -15% to +25%
        self.brightness_max = 1.25
        self.contrast_min = 0.80    # -20% to +25%
        self.contrast_max = 1.25
        
        # Geometric manipulation ranges (±2% to ±5% resize for more noticeable changes)
        self.scale_min = 0.95       # -5%
        self.scale_max = 1.05       # +5%
        
        # JPEG quality range (88-92 instead of typical 90-95)
        self.quality_min = 88
        self.quality_max = 92
        
        self.iphone_12_specs = {
            'make': 'Apple',
            'model': 'iPhone 12',
            'software': '15.0',
            'orientation': 1,
            'x_resolution': 72,
            'y_resolution': 72,
            'resolution_unit': 2,
            'color_space': 1,
            'exif_version': b'0232',
            'flashpix_version': b'0100',
            'white_balance': 0,
            'digital_zoom_ratio': (1, 1),
            'focal_length': (4, 1),  # 4mm
            'focal_length_in_35mm_film': 26,
            'scene_capture_type': 0,
            'gain_control': 0,
            'contrast': 0,
            'saturation': 0,
            'sharpness': 0,
            'subject_distance_range': 0,
            'lens_specification': ((4, 1), (4, 1), (18, 10), (18, 10)),  # 4mm f/1.8
            'lens_make': 'Apple',
            'lens_model': 'iPhone 12 back dual wide camera 4.25mm f/1.6'
        }
        
        # UK major cities with coordinates (properly labeled with country)
        self.uk_locations = [
            # England
            {'name': 'London, United Kingdom', 'lat': 51.5074, 'lon': -0.1278},
            {'name': 'Manchester, United Kingdom', 'lat': 53.4808, 'lon': -2.2426},
            {'name': 'Birmingham, United Kingdom', 'lat': 52.4862, 'lon': -1.8904},
            {'name': 'Leeds, United Kingdom', 'lat': 53.8008, 'lon': -1.5491},
            {'name': 'Liverpool, United Kingdom', 'lat': 53.4084, 'lon': -2.9916},
            {'name': 'Bristol, United Kingdom', 'lat': 51.4545, 'lon': -2.5879},
            {'name': 'Newcastle, United Kingdom', 'lat': 54.9783, 'lon': -1.6178},
            {'name': 'Sheffield, United Kingdom', 'lat': 53.3811, 'lon': -1.4701},
            {'name': 'Nottingham, United Kingdom', 'lat': 52.9548, 'lon': -1.1581},
            {'name': 'Leicester, United Kingdom', 'lat': 52.6369, 'lon': -1.1398},
            {'name': 'Coventry, United Kingdom', 'lat': 52.4068, 'lon': -1.5197},
            {'name': 'Bradford, United Kingdom', 'lat': 53.7960, 'lon': -1.7594},
            {'name': 'Brighton, United Kingdom', 'lat': 50.8225, 'lon': -0.1372},
            {'name': 'Plymouth, United Kingdom', 'lat': 50.3755, 'lon': -4.1427},
            {'name': 'Southampton, United Kingdom', 'lat': 50.9097, 'lon': -1.4044},
            {'name': 'Reading, United Kingdom', 'lat': 51.4543, 'lon': -0.9781},
            # Wales
            {'name': 'Cardiff, Wales', 'lat': 51.4816, 'lon': -3.1791},
            {'name': 'Swansea, Wales', 'lat': 51.6214, 'lon': -3.9436},
            {'name': 'Newport, Wales', 'lat': 51.5842, 'lon': -2.9977},
            {'name': 'Bridgend, Wales', 'lat': 51.5042, 'lon': -3.5767},
            # Scotland
            {'name': 'Glasgow, Scotland', 'lat': 55.8642, 'lon': -4.2518},
            {'name': 'Edinburgh, Scotland', 'lat': 55.9533, 'lon': -3.1883}
        ]
    
    def generate_random_uk_location(self):
        """Generate a random UK location with slight coordinate variation."""
        base_location = random.choice(self.uk_locations)
        
        # Add small random variation to coordinates (±0.1 degrees ≈ ±11km)
        lat_variation = random.uniform(-0.1, 0.1)
        lon_variation = random.uniform(-0.1, 0.1)
        
        return {
            'name': base_location['name'],
            'lat': base_location['lat'] + lat_variation,
            'lon': base_location['lon'] + lon_variation
        }
    
    def generate_random_timestamp(self, days_back=30):
        """Generate a random timestamp within the last N days."""
        now = datetime.datetime.now()
        random_days = random.randint(1, days_back)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)
        
        photo_time = now - datetime.timedelta(
            days=random_days,
            hours=random_hours,
            minutes=random_minutes,
            seconds=random_seconds
        )
        
        return photo_time
    
    def apply_perceptual_shift(self, image):
        """
        Apply minimal random adjustments to brightness and contrast.
        Changes are subtle (±2% to ±5%) to avoid detection while maintaining quality.
        
        Args:
            image: PIL Image object
            
        Returns:
            tuple: (modified image, brightness_factor, contrast_factor)
        """
        # Generate random factors within safe ranges
        brightness_factor = random.uniform(self.brightness_min, self.brightness_max)
        contrast_factor = random.uniform(self.contrast_min, self.contrast_max)
        
        # Apply brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness_factor)
        
        # Apply contrast adjustment
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast_factor)
        
        return image, brightness_factor, contrast_factor
    
    def apply_geometric_manipulation(self, image):
        """
        Apply subtle geometric manipulation: resize by small amount, then crop.
        This changes pixel dimensions slightly to create a unique image signature.
        
        Args:
            image: PIL Image object
            
        Returns:
            tuple: (modified image, scale_factor, final_size)
        """
        original_width, original_height = image.size
        
        # Calculate scale factor (±0.3% to ±0.7%)
        scale_factor = random.uniform(self.scale_min, self.scale_max)
        
        # Calculate new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Resize image using high-quality resampling
        from PIL import Image as PILImage
        resized_image = image.resize((new_width, new_height), PILImage.LANCZOS)
        
        # Determine final dimensions (crop to common aspect ratios)
        # Try to maintain original aspect ratio but with slightly different dimensions
        aspect_ratio = original_width / original_height
        
        # Adjust final dimensions to be non-standard
        # Add or subtract 1-3 pixels from each dimension
        width_adjustment = random.randint(-3, 3)
        height_adjustment = random.randint(-3, 3)
        
        final_width = max(new_width + width_adjustment, 100)  # Minimum 100px
        final_height = max(new_height + height_adjustment, 100)
        
        # Ensure final dimensions don't exceed resized dimensions
        final_width = min(final_width, new_width)
        final_height = min(final_height, new_height)
        
        # Calculate crop box (center crop if needed)
        if final_width < new_width or final_height < new_height:
            left = (new_width - final_width) // 2
            top = (new_height - final_height) // 2
            right = left + final_width
            bottom = top + final_height
            
            final_image = resized_image.crop((left, top, right, bottom))
        else:
            final_image = resized_image
        
        return final_image, scale_factor, (final_width, final_height)
    
    def generate_random_jpeg_quality(self):
        """
        Generate random JPEG quality setting in non-standard range.
        
        Returns:
            int: Quality value between 88-92
        """
        return random.randint(self.quality_min, self.quality_max)
    
    def create_gps_exif(self, lat, lon, altitude=None):
        """Create GPS EXIF data for the given coordinates."""
        if altitude is None:
            altitude = random.randint(10, 200)  # Random altitude 10-200m
        
        # Convert to degrees, minutes, seconds format
        def deg_to_dms(deg):
            d = int(deg)
            m = int((deg - d) * 60)
            s = ((deg - d) * 60 - m) * 60
            return ((d, 1), (m, 1), (int(s * 100), 100))
        
        lat_dms = deg_to_dms(abs(lat))
        lon_dms = deg_to_dms(abs(lon))
        
        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: lat_dms,
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: lon_dms,
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: (altitude, 1),
            piexif.GPSIFD.GPSTimeStamp: (
                (random.randint(8, 18), 1),  # Hour
                (random.randint(0, 59), 1),  # Minute
                (random.randint(0, 59), 1)   # Second
            )
        }
        
        return gps_ifd
    
    def create_exif_data(self, location, timestamp):
        """Create complete EXIF data for iPhone 12."""
        # Create GPS data
        gps_ifd = self.create_gps_exif(location['lat'], location['lon'])
        
        # Create main EXIF data
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: timestamp.strftime('%Y:%m:%d %H:%M:%S'),
            piexif.ExifIFD.DateTimeDigitized: timestamp.strftime('%Y:%m:%d %H:%M:%S'),
            piexif.ExifIFD.ExifVersion: self.iphone_12_specs['exif_version'],
            piexif.ExifIFD.FlashpixVersion: self.iphone_12_specs['flashpix_version'],
            piexif.ExifIFD.WhiteBalance: self.iphone_12_specs['white_balance'],
            piexif.ExifIFD.DigitalZoomRatio: self.iphone_12_specs['digital_zoom_ratio'],
            piexif.ExifIFD.FocalLength: self.iphone_12_specs['focal_length'],
            piexif.ExifIFD.FocalLengthIn35mmFilm: self.iphone_12_specs['focal_length_in_35mm_film'],
            piexif.ExifIFD.SceneCaptureType: self.iphone_12_specs['scene_capture_type'],
            piexif.ExifIFD.GainControl: self.iphone_12_specs['gain_control'],
            piexif.ExifIFD.Contrast: self.iphone_12_specs['contrast'],
            piexif.ExifIFD.Saturation: self.iphone_12_specs['saturation'],
            piexif.ExifIFD.Sharpness: self.iphone_12_specs['sharpness'],
            piexif.ExifIFD.SubjectDistanceRange: self.iphone_12_specs['subject_distance_range'],
            piexif.ExifIFD.LensSpecification: self.iphone_12_specs['lens_specification'],
            piexif.ExifIFD.LensMake: self.iphone_12_specs['lens_make'],
            piexif.ExifIFD.LensModel: self.iphone_12_specs['lens_model']
        }
        
        # Create IFD0 data
        zeroth_ifd = {
            piexif.ImageIFD.Make: self.iphone_12_specs['make'],
            piexif.ImageIFD.Model: self.iphone_12_specs['model'],
            piexif.ImageIFD.Software: self.iphone_12_specs['software'],
            piexif.ImageIFD.Orientation: self.iphone_12_specs['orientation'],
            piexif.ImageIFD.XResolution: (self.iphone_12_specs['x_resolution'], 1),
            piexif.ImageIFD.YResolution: (self.iphone_12_specs['y_resolution'], 1),
            piexif.ImageIFD.ResolutionUnit: self.iphone_12_specs['resolution_unit'],
            # piexif.ImageIFD.ColorSpace: self.iphone_12_specs['color_space'],  # Not available in this piexif version
            piexif.ImageIFD.DateTime: timestamp.strftime('%Y:%m:%d %H:%M:%S')
        }
        
        # Combine all EXIF data
        exif_dict = {
            "0th": zeroth_ifd,
            "Exif": exif_ifd,
            "GPS": gps_ifd
        }
        
        return exif_dict
    
    def modify_image_metadata(self, image_path, output_path=None):
        """
        Apply comprehensive anti-duplicate detection pipeline:
        1. Metadata stripping (replaced with new iPhone 12 metadata)
        2. Perceptual shift (subtle brightness/contrast changes)
        3. Geometric manipulation (resize + crop to unique dimensions)
        4. Compression change (random JPEG quality 88-92)
        
        This creates a unique perceptual hash while maintaining visual quality.
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path to save modified image (optional)
            
        Returns:
            dict: Information about the modification
        """
        try:
            # Generate random location and timestamp for new metadata
            location = self.generate_random_uk_location()
            timestamp = self.generate_random_timestamp()
            
            # STEP 1: Open image (existing metadata will be stripped when saving)
            image = Image.open(image_path)
            original_size = image.size
            
            # Convert to RGB if needed (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image
            
            # STEP 2: Apply perceptual shift (noticeable brightness/contrast changes)
            image, brightness_factor, contrast_factor = self.apply_perceptual_shift(image)
            
            # STEP 2.5: Apply additional contrast enhancement for visibility
            from PIL import ImageEnhance
            contrast_enhancer = ImageEnhance.Contrast(image)
            additional_contrast = random.uniform(0.9, 1.1)  # Additional ±10% contrast
            image = contrast_enhancer.enhance(additional_contrast)
            
            # STEP 3: Apply geometric manipulation (resize + crop)
            image, scale_factor, final_size = self.apply_geometric_manipulation(image)
            
            # STEP 4: Create new EXIF data (replaces old metadata)
            exif_dict = self.create_exif_data(location, timestamp)
            exif_bytes = piexif.dump(exif_dict)
            
            # Generate random JPEG quality for unique compression signature
            jpeg_quality = self.generate_random_jpeg_quality()
            
            # Determine output path
            if output_path is None:
                output_path = image_path  # Overwrite original
            
            # Save with new EXIF data and random quality
            image.save(output_path, 'JPEG', exif=exif_bytes, quality=jpeg_quality, optimize=True)
            
            # Calculate actual changes for reporting
            brightness_change = (brightness_factor - 1.0) * 100
            contrast_change = (contrast_factor - 1.0) * 100
            additional_contrast_change = (additional_contrast - 1.0) * 100
            total_contrast_change = contrast_change + additional_contrast_change
            size_change = (scale_factor - 1.0) * 100
            
            # Return comprehensive modification info
            return {
                'success': True,
                'original_path': image_path,
                'output_path': output_path,
                'location': location,
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'camera': f"{self.iphone_12_specs['make']} {self.iphone_12_specs['model']}",
                'brightness_factor': f"{brightness_factor:.4f}",
                'contrast_factor': f"{contrast_factor:.4f}",
                'brightness_change_pct': f"{brightness_change:+.2f}%",
                'contrast_change_pct': f"{total_contrast_change:+.2f}%",
                'scale_factor': f"{scale_factor:.4f}",
                'size_change_pct': f"{size_change:+.2f}%",
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'final_size': f"{final_size[0]}x{final_size[1]}",
                'jpeg_quality': jpeg_quality
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_path': image_path
            }
    
    def modify_multiple_images(self, image_paths, output_dir=None):
        """
        Modify metadata for multiple images.
        
        Args:
            image_paths (list): List of image paths
            output_dir (str): Directory to save modified images (optional)
            
        Returns:
            list: List of modification results
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Determine output path
                if output_dir:
                    filename = os.path.basename(image_path)
                    name, ext = os.path.splitext(filename)
                    output_path = os.path.join(output_dir, f"{name}_modified{ext}")
                else:
                    output_path = None
                
                # Modify image
                result = self.modify_image_metadata(image_path, output_path)
                results.append(result)
                
                if result['success']:
                    print(f"✅ Modified image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
                    print(f"   📍 Location: {result['location']['name']} ({result['location']['lat']:.4f}, {result['location']['lon']:.4f})")
                    print(f"   📅 Date: {result['timestamp']}")
                else:
                    print(f"❌ Failed to modify image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
                    print(f"   Error: {result['error']}")
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_path': image_path
                })
                print(f"❌ Error processing image {i+1}/{len(image_paths)}: {e}")
        
        return results
    
    def get_image_info(self, image_path):
        """Get current image metadata information."""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if exif_data is None:
                return {'has_exif': False, 'message': 'No EXIF data found'}
            
            exif_info = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_info[tag] = value
            
            return {
                'has_exif': True,
                'exif_data': exif_info,
                'image_size': image.size,
                'image_mode': image.mode
            }
            
        except Exception as e:
            return {
                'has_exif': False,
                'error': str(e)
            }

def main():
    """Test the metadata modifier."""
    modifier = ImageMetadataModifier()
    
    print("🧪 Image Metadata Modifier Test")
    print("=" * 40)
    
    # Test with a sample image if available
    test_images = []
    for ext in ['.jpg', '.jpeg', '.png']:
        for root, dirs, files in os.walk('accounts'):
            for file in files:
                if file.lower().endswith(ext):
                    test_images.append(os.path.join(root, file))
                    if len(test_images) >= 3:  # Test with up to 3 images
                        break
            if len(test_images) >= 3:
                break
        if len(test_images) >= 3:
            break
    
    if not test_images:
        print("❌ No test images found in accounts directory")
        return
    
    print(f"📸 Found {len(test_images)} test images")
    print()
    
    # Test modification
    results = modifier.modify_multiple_images(test_images)
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Results: {successful}/{len(results)} images modified successfully")

if __name__ == "__main__":
    main()
