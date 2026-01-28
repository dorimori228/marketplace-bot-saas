#!/usr/bin/env python3
"""
Image Cropping Module
Creates unique cropped versions of images to avoid Facebook's duplicate detection.
"""

import os
import random
import math
from PIL import Image, ImageOps
import hashlib

class ImageCropper:
    """Creates unique cropped versions of images for each upload."""
    
    def __init__(self):
        """Initialize the image cropper with cropping strategies."""
        # Cropping strategies for different aspect ratios
        self.crop_strategies = [
            'center',      # Center crop
            'top_left',    # Top-left corner
            'top_right',   # Top-right corner
            'bottom_left', # Bottom-left corner
            'bottom_right', # Bottom-right corner
            'random',       # Random position
            'smart'        # Smart crop based on content
        ]
        
        # Size variations (percentage of original) - More aggressive cropping
        self.size_variations = [
            (0.70, 0.85),  # 70-85% of original (more noticeable crop)
            (0.75, 0.90),  # 75-90% of original
            (0.80, 0.95),  # 80-95% of original
        ]
        
        # Aspect ratio variations
        self.aspect_ratios = [
            (1.0, 1.0),    # Square
            (1.2, 1.0),    # Slightly wider
            (1.0, 1.2),    # Slightly taller
            (1.3, 1.0),    # Wider
            (1.0, 1.3),    # Taller
            (1.5, 1.0),    # Much wider
            (1.0, 1.5),    # Much taller
        ]
    
    def generate_crop_parameters(self, image_width, image_height, strategy='random'):
        """
        Generate crop parameters based on strategy and image dimensions.
        
        Args:
            image_width (int): Original image width
            image_height (int): Original image height
            strategy (str): Cropping strategy to use
            
        Returns:
            dict: Crop parameters including position, size, and aspect ratio
        """
        # Choose random size variation
        size_min, size_max = random.choice(self.size_variations)
        scale_factor = random.uniform(size_min, size_max)
        
        # Choose random aspect ratio
        aspect_ratio_w, aspect_ratio_h = random.choice(self.aspect_ratios)
        
        # Calculate target dimensions
        target_width = int(image_width * scale_factor)
        target_height = int(image_height * scale_factor)
        
        # Adjust for aspect ratio
        if aspect_ratio_w > aspect_ratio_h:
            # Wider aspect ratio
            target_width = max(target_width, int(target_height * aspect_ratio_w / aspect_ratio_h))
        elif aspect_ratio_h > aspect_ratio_w:
            # Taller aspect ratio
            target_height = max(target_height, int(target_width * aspect_ratio_h / aspect_ratio_w))
        
        # Ensure dimensions don't exceed original
        target_width = min(target_width, image_width)
        target_height = min(target_height, image_height)
        
        # Calculate crop position based on strategy
        if strategy == 'center':
            left = (image_width - target_width) // 2
            top = (image_height - target_height) // 2
        elif strategy == 'top_left':
            left = 0
            top = 0
        elif strategy == 'top_right':
            left = image_width - target_width
            top = 0
        elif strategy == 'bottom_left':
            left = 0
            top = image_height - target_height
        elif strategy == 'bottom_right':
            left = image_width - target_width
            top = image_height - target_height
        elif strategy == 'random':
            left = random.randint(0, max(0, image_width - target_width))
            top = random.randint(0, max(0, image_height - target_height))
        elif strategy == 'smart':
            # Smart crop: try to avoid edges and center
            margin_x = max(0, (image_width - target_width) // 4)
            margin_y = max(0, (image_height - target_height) // 4)
            left = random.randint(margin_x, max(margin_x, image_width - target_width - margin_x))
            top = random.randint(margin_y, max(margin_y, image_height - target_height - margin_y))
        else:
            # Default to center
            left = (image_width - target_width) // 2
            top = (image_height - target_height) // 2
        
        # Ensure crop box is within image bounds
        left = max(0, min(left, image_width - target_width))
        top = max(0, min(top, image_height - target_height))
        right = left + target_width
        bottom = top + target_height
        
        return {
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom,
            'width': target_width,
            'height': target_height,
            'scale_factor': scale_factor,
            'aspect_ratio': (aspect_ratio_w, aspect_ratio_h),
            'strategy': strategy
        }
    
    def crop_image(self, image_path, output_path=None, strategy='random'):
        """
        Crop an image to create a unique version.
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path to save cropped image (optional)
            strategy (str): Cropping strategy to use
            
        Returns:
            dict: Information about the cropping operation
        """
        try:
            # Open image
            image = Image.open(image_path)
            original_size = image.size
            original_width, original_height = original_size
            
            # Generate crop parameters
            crop_params = self.generate_crop_parameters(original_width, original_height, strategy)
            
            # Perform the crop
            crop_box = (crop_params['left'], crop_params['top'], 
                      crop_params['right'], crop_params['bottom'])
            cropped_image = image.crop(crop_box)
            
            # Determine output path
            if output_path is None:
                # Create output path in same directory
                dir_path = os.path.dirname(image_path)
                filename, ext = os.path.splitext(os.path.basename(image_path))
                output_path = os.path.join(dir_path, f"{filename}_cropped{ext}")
            
            # Save cropped image
            cropped_image.save(output_path, quality=95, optimize=True)
            
            # Calculate crop statistics
            crop_area = crop_params['width'] * crop_params['height']
            original_area = original_width * original_height
            area_ratio = crop_area / original_area
            
            return {
                'success': True,
                'original_path': image_path,
                'output_path': output_path,
                'original_size': f"{original_width}x{original_height}",
                'cropped_size': f"{crop_params['width']}x{crop_params['height']}",
                'crop_box': crop_box,
                'scale_factor': f"{crop_params['scale_factor']:.3f}",
                'area_ratio': f"{area_ratio:.3f}",
                'strategy': strategy,
                'aspect_ratio': f"{crop_params['aspect_ratio'][0]}:{crop_params['aspect_ratio'][1]}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_path': image_path
            }
    
    def create_unique_crops(self, image_paths, output_dir=None, max_crops_per_image=3):
        """
        Create multiple unique cropped versions of each image.
        
        Args:
            image_paths (list): List of image paths
            output_dir (str): Directory to save cropped images (optional)
            max_crops_per_image (int): Maximum number of crops per image
            
        Returns:
            list: List of cropping results
        """
        results = []
        
        for image_path in image_paths:
            try:
                # Create multiple crops of the same image
                image_crops = []
                
                for i in range(max_crops_per_image):
                    # Use different strategies for variety
                    strategy = random.choice(self.crop_strategies)
                    
                    # Determine output path
                    if output_dir:
                        filename, ext = os.path.splitext(os.path.basename(image_path))
                        output_path = os.path.join(output_dir, f"{filename}_crop_{i+1}{ext}")
                    else:
                        dir_path = os.path.dirname(image_path)
                        filename, ext = os.path.splitext(os.path.basename(image_path))
                        output_path = os.path.join(dir_path, f"{filename}_crop_{i+1}{ext}")
                    
                    # Create crop
                    crop_result = self.crop_image(image_path, output_path, strategy)
                    
                    if crop_result['success']:
                        image_crops.append(crop_result)
                        print(f"✅ Created crop {i+1}/{max_crops_per_image} for {os.path.basename(image_path)}")
                        print(f"   📐 Size: {crop_result['cropped_size']} (from {crop_result['original_size']})")
                        print(f"   🎯 Strategy: {crop_result['strategy']}")
                        print(f"   📊 Area: {crop_result['area_ratio']} of original")
                    else:
                        print(f"❌ Failed to create crop {i+1} for {os.path.basename(image_path)}: {crop_result['error']}")
                
                results.append({
                    'original_path': image_path,
                    'crops': image_crops,
                    'success_count': len(image_crops),
                    'total_attempts': max_crops_per_image
                })
                
            except Exception as e:
                results.append({
                    'original_path': image_path,
                    'crops': [],
                    'success_count': 0,
                    'total_attempts': max_crops_per_image,
                    'error': str(e)
                })
                print(f"❌ Error processing {os.path.basename(image_path)}: {e}")
        
        return results
    
    def get_best_crop(self, image_path, output_path=None):
        """
        Get the best cropped version of an image using smart cropping.
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path to save cropped image (optional)
            
        Returns:
            dict: Information about the best crop
        """
        # Try different strategies and pick the best one
        strategies = ['smart', 'center', 'random']
        best_result = None
        best_score = 0
        
        for strategy in strategies:
            result = self.crop_image(image_path, output_path, strategy)
            if result['success']:
                # Score based on area ratio and aspect ratio
                area_ratio = float(result['area_ratio'])
                aspect_ratio = result['aspect_ratio']
                
                # Prefer crops that are 70-90% of original area
                if 0.7 <= area_ratio <= 0.9:
                    score = area_ratio * 2
                else:
                    score = area_ratio
                
                # Bonus for square or standard aspect ratios
                if aspect_ratio in ['1.0:1.0', '1.2:1.0', '1.0:1.2']:
                    score += 0.5
                
                if score > best_score:
                    best_score = score
                    best_result = result
        
        return best_result if best_result else {'success': False, 'error': 'No suitable crop found'}

def main():
    """Test the image cropper."""
    cropper = ImageCropper()
    
    print("🧪 Image Cropper Test")
    print("=" * 40)
    
    # Test with sample images
    test_images = []
    for root, dirs, files in os.walk('accounts'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(root, file))
                if len(test_images) >= 2:  # Test with 2 images
                    break
        if len(test_images) >= 2:
            break
    
    if not test_images:
        print("❌ No test images found in accounts directory")
        return
    
    print(f"📸 Found {len(test_images)} test images")
    print()
    
    # Test cropping
    for image_path in test_images:
        print(f"🔄 Testing crop for: {os.path.basename(image_path)}")
        result = cropper.get_best_crop(image_path)
        
        if result['success']:
            print(f"✅ Best crop created: {result['cropped_size']} (from {result['original_size']})")
            print(f"   📊 Area: {result['area_ratio']} of original")
            print(f"   🎯 Strategy: {result['strategy']}")
        else:
            print(f"❌ Failed to create crop: {result['error']}")
        print()

if __name__ == "__main__":
    main()
