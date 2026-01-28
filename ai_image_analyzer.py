#!/usr/bin/env python3
"""
AI Image Analyzer for Facebook Marketplace Bot
Analyzes listing images to detect product type, colors, and features.
"""

import os
import cv2
import numpy as np
from PIL import Image
import requests
import json
from datetime import datetime

class AIImageAnalyzer:
    """AI-powered image analysis for product detection and description generation."""
    
    def __init__(self):
        """Initialize the AI image analyzer."""
        self.color_keywords = {
            'green': ['green', 'lush', 'grass', 'natural', 'vibrant'],
            'grey': ['grey', 'gray', 'silver', 'charcoal', 'neutral'],
            'brown': ['brown', 'tan', 'beige', 'natural', 'wood'],
            'blue': ['blue', 'navy', 'royal', 'sky'],
            'red': ['red', 'crimson', 'burgundy', 'maroon'],
            'black': ['black', 'dark', 'charcoal', 'ebony']
        }
        
        self.product_indicators = {
            'artificial_grass': {
                'colors': ['green'],
                'textures': ['grass', 'lawn', 'turf'],
                'patterns': ['uniform', 'grass-like']
            },
            'carpet': {
                'colors': ['grey', 'brown', 'blue', 'red', 'black'],
                'textures': ['soft', 'plush', 'twist', 'pile'],
                'patterns': ['textured', 'fibrous']
            },
            'decking': {
                'colors': ['brown', 'grey', 'black'],
                'textures': ['wood', 'grain', 'smooth'],
                'patterns': ['woodgrain', 'striped']
            }
        }
    
    def analyze_image(self, image_path):
        """Analyze a single image for product type and features."""
        try:
            print(f"🔍 Analyzing image: {os.path.basename(image_path)}")
            
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return {'success': False, 'error': 'Could not load image'}
            
            # Resize for analysis
            image = cv2.resize(image, (400, 400))
            
            # Analyze colors
            color_analysis = self._analyze_colors(image)
            
            # Analyze texture
            texture_analysis = self._analyze_texture(image)
            
            # Detect product type
            product_type = self._detect_product_from_image(color_analysis, texture_analysis)
            
            # Generate description elements
            description_elements = self._generate_description_elements(product_type, color_analysis, texture_analysis)
            
            return {
                'success': True,
                'product_type': product_type,
                'colors': color_analysis['dominant_colors'],
                'texture': texture_analysis['texture_type'],
                'description_elements': description_elements,
                'confidence': self._calculate_confidence(color_analysis, texture_analysis, product_type)
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing image: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_colors(self, image):
        """Analyze dominant colors in the image."""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Reshape image to 1D array
            pixels = hsv.reshape(-1, 3)
            
            # Use K-means to find dominant colors
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(pixels)
            
            # Get dominant colors
            colors = kmeans.cluster_centers_
            labels = kmeans.labels_
            
            # Count occurrences of each color
            color_counts = np.bincount(labels)
            dominant_indices = np.argsort(color_counts)[::-1]
            
            dominant_colors = []
            for idx in dominant_indices[:3]:  # Top 3 colors
                h, s, v = colors[idx]
                color_name = self._hsv_to_color_name(h, s, v)
                dominant_colors.append({
                    'name': color_name,
                    'hsv': [h, s, v],
                    'percentage': (color_counts[idx] / len(labels)) * 100
                })
            
            return {
                'dominant_colors': dominant_colors,
                'is_green_dominant': any('green' in color['name'] for color in dominant_colors),
                'is_grey_dominant': any('grey' in color['name'] for color in dominant_colors),
                'is_brown_dominant': any('brown' in color['name'] for color in dominant_colors)
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing colors: {e}")
            return {
                'dominant_colors': [],
                'is_green_dominant': False,
                'is_grey_dominant': False,
                'is_brown_dominant': False
            }
    
    def _analyze_texture(self, image):
        """Analyze texture patterns in the image."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture features
            # 1. Local Binary Pattern (LBP)
            lbp = self._calculate_lbp(gray)
            
            # 2. Gabor filters for texture
            gabor_responses = self._calculate_gabor_responses(gray)
            
            # 3. Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Determine texture type
            texture_type = self._classify_texture(lbp, gabor_responses, edge_density)
            
            return {
                'texture_type': texture_type,
                'edge_density': edge_density,
                'is_grass_like': 'grass' in texture_type.lower(),
                'is_carpet_like': 'carpet' in texture_type.lower(),
                'is_wood_like': 'wood' in texture_type.lower()
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing texture: {e}")
            return {
                'texture_type': 'unknown',
                'edge_density': 0,
                'is_grass_like': False,
                'is_carpet_like': False,
                'is_wood_like': False
            }
    
    def _hsv_to_color_name(self, h, s, v):
        """Convert HSV values to color name."""
        # Define color ranges in HSV
        if v < 30:
            return 'black'
        elif s < 30:
            return 'grey'
        elif h < 15 or h > 165:
            return 'red'
        elif 15 <= h < 35:
            return 'orange'
        elif 35 <= h < 85:
            return 'yellow'
        elif 85 <= h < 165:
            return 'green'
        elif 165 <= h < 200:
            return 'blue'
        elif 200 <= h < 250:
            return 'purple'
        else:
            return 'pink'
    
    def _calculate_lbp(self, image):
        """Calculate Local Binary Pattern for texture analysis."""
        try:
            # Simple LBP implementation
            lbp = np.zeros_like(image)
            for i in range(1, image.shape[0] - 1):
                for j in range(1, image.shape[1] - 1):
                    center = image[i, j]
                    binary = ''
                    # 8-neighborhood
                    neighbors = [
                        image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                        image[i, j+1], image[i+1, j+1], image[i+1, j],
                        image[i+1, j-1], image[i, j-1]
                    ]
                    for neighbor in neighbors:
                        binary += '1' if neighbor >= center else '0'
                    lbp[i, j] = int(binary, 2)
            
            return lbp
        except:
            return np.zeros_like(image)
    
    def _calculate_gabor_responses(self, image):
        """Calculate Gabor filter responses for texture analysis."""
        try:
            responses = []
            for angle in [0, 45, 90, 135]:
                kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 10, 0.5, 0, ktype=cv2.CV_32F)
                response = cv2.filter2D(image, cv2.CV_8UC3, kernel)
                responses.append(np.mean(response))
            return responses
        except:
            return [0, 0, 0, 0]
    
    def _classify_texture(self, lbp, gabor_responses, edge_density):
        """Classify texture based on features."""
        try:
            # Simple texture classification
            if edge_density > 0.1:
                if np.mean(gabor_responses) > 50:
                    return 'grass-like'
                else:
                    return 'carpet-like'
            elif edge_density < 0.05:
                return 'wood-like'
            else:
                return 'uniform'
        except:
            return 'unknown'
    
    def _detect_product_from_image(self, color_analysis, texture_analysis):
        """Detect product type from image analysis."""
        try:
            # Score each product type
            scores = {
                'artificial_grass': 0,
                'carpet': 0,
                'decking': 0
            }
            
            # Color-based scoring
            if color_analysis['is_green_dominant']:
                scores['artificial_grass'] += 3
            if color_analysis['is_grey_dominant']:
                scores['carpet'] += 2
            if color_analysis['is_brown_dominant']:
                scores['decking'] += 2
            
            # Texture-based scoring
            if texture_analysis['is_grass_like']:
                scores['artificial_grass'] += 3
            if texture_analysis['is_carpet_like']:
                scores['carpet'] += 3
            if texture_analysis['is_wood_like']:
                scores['decking'] += 3
            
            # Return product with highest score
            best_product = max(scores, key=scores.get)
            confidence = scores[best_product] / 6.0  # Normalize to 0-1
            
            print(f"🔍 Product detection scores: {scores}")
            print(f"✅ Detected: {best_product} (confidence: {confidence:.2f})")
            
            return best_product
            
        except Exception as e:
            print(f"⚠️ Error detecting product: {e}")
            return 'artificial_grass'  # Default fallback
    
    def _generate_description_elements(self, product_type, color_analysis, texture_analysis):
        """Generate description elements based on analysis."""
        try:
            elements = []
            
            # Add color information
            dominant_colors = [color['name'] for color in color_analysis['dominant_colors'][:2]]
            if dominant_colors:
                color_text = f"{', '.join(dominant_colors).title()} colored"
                elements.append(color_text)
            
            # Add texture information
            if texture_analysis['texture_type'] != 'unknown':
                elements.append(f"{texture_analysis['texture_type']} texture")
            
            # Add product-specific elements
            if product_type == 'artificial_grass':
                elements.extend(['lush green', 'realistic appearance', 'natural look'])
            elif product_type == 'carpet':
                elements.extend(['soft feel', 'durable construction', 'comfortable'])
            elif product_type == 'decking':
                elements.extend(['weather resistant', 'low maintenance', 'durable'])
            
            return elements
            
        except Exception as e:
            print(f"⚠️ Error generating description elements: {e}")
            return []
    
    def _calculate_confidence(self, color_analysis, texture_analysis, product_type):
        """Calculate confidence score for the analysis."""
        try:
            confidence = 0.5  # Base confidence
            
            # Color confidence
            if color_analysis['dominant_colors']:
                confidence += 0.2
            
            # Texture confidence
            if texture_analysis['texture_type'] != 'unknown':
                confidence += 0.2
            
            # Product-specific confidence
            if product_type == 'artificial_grass' and color_analysis['is_green_dominant']:
                confidence += 0.1
            elif product_type == 'carpet' and (color_analysis['is_grey_dominant'] or color_analysis['is_brown_dominant']):
                confidence += 0.1
            elif product_type == 'decking' and color_analysis['is_brown_dominant']:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except:
            return 0.5
    
    def analyze_listing_images(self, image_paths):
        """Analyze multiple images for a listing."""
        try:
            if not image_paths:
                return {'success': False, 'error': 'No images provided'}
            
            print(f"🔍 Analyzing {len(image_paths)} images for listing...")
            
            all_analyses = []
            for i, image_path in enumerate(image_paths):
                if os.path.exists(image_path):
                    analysis = self.analyze_image(image_path)
                    if analysis['success']:
                        all_analyses.append(analysis)
                        print(f"✅ Image {i+1} analyzed successfully")
                    else:
                        print(f"⚠️ Image {i+1} analysis failed: {analysis.get('error', 'Unknown error')}")
                else:
                    print(f"⚠️ Image {i+1} not found: {image_path}")
            
            if not all_analyses:
                return {'success': False, 'error': 'No images could be analyzed'}
            
            # Combine analyses
            combined_analysis = self._combine_analyses(all_analyses)
            
            return {
                'success': True,
                'product_type': combined_analysis['product_type'],
                'colors': combined_analysis['colors'],
                'texture': combined_analysis['texture'],
                'description_elements': combined_analysis['description_elements'],
                'confidence': combined_analysis['confidence'],
                'images_analyzed': len(all_analyses)
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing listing images: {e}")
            return {'success': False, 'error': str(e)}
    
    def _combine_analyses(self, analyses):
        """Combine multiple image analyses into a single result."""
        try:
            # Vote on product type
            product_votes = {}
            for analysis in analyses:
                product_type = analysis['product_type']
                product_votes[product_type] = product_votes.get(product_type, 0) + 1
            
            best_product = max(product_votes, key=product_votes.get)
            
            # Combine colors
            all_colors = []
            for analysis in analyses:
                all_colors.extend(analysis['colors'])
            
            # Get most common colors
            color_counts = {}
            for color in all_colors:
                color_name = color['name']
                color_counts[color_name] = color_counts.get(color_name, 0) + 1
            
            top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Combine textures
            texture_votes = {}
            for analysis in analyses:
                texture = analysis['texture']
                texture_votes[texture] = texture_votes.get(texture, 0) + 1
            
            best_texture = max(texture_votes, key=texture_votes.get)
            
            # Combine description elements
            all_elements = []
            for analysis in analyses:
                all_elements.extend(analysis['description_elements'])
            
            # Remove duplicates and get most common
            element_counts = {}
            for element in all_elements:
                element_counts[element] = element_counts.get(element, 0) + 1
            
            top_elements = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate average confidence
            avg_confidence = sum(analysis['confidence'] for analysis in analyses) / len(analyses)
            
            return {
                'product_type': best_product,
                'colors': [{'name': color, 'count': count} for color, count in top_colors],
                'texture': best_texture,
                'description_elements': [element for element, count in top_elements],
                'confidence': avg_confidence
            }
            
        except Exception as e:
            print(f"⚠️ Error combining analyses: {e}")
            return {
                'product_type': 'artificial_grass',
                'colors': [],
                'texture': 'unknown',
                'description_elements': [],
                'confidence': 0.5
            }
