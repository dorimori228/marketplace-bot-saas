#!/usr/bin/env python3
"""
Title Variation Module
Generates similar but unique titles to avoid Facebook's duplicate detection.
"""

import os
import random
import re
import json
from datetime import datetime

class TitleVariator:
    """Generates unique variations of listing titles."""
    
    def __init__(self):
        """Initialize the title variator with variation strategies."""
        
        # Common word variations and synonyms
        self.word_variations = {
            # Size/quantity variations
            '40mm': ['40mm thick', '40mm premium', '40mm high quality', '40mm professional'],
            'thick': ['thick', 'dense', 'premium', 'high quality', 'professional grade'],
            'rolls': ['rolls', 'roll', 'pieces', 'lengths', 'sections'],
            'artificial': ['artificial', 'synthetic', 'fake', 'imitation'],
            'grass': ['grass', 'turf', 'lawn', 'ground cover'],
            
            # Quality descriptors - REDUCED commercial usage
            'premium': ['premium', 'high quality', 'professional', 'luxury', 'deluxe'],
            'high quality': ['high quality', 'premium', 'professional', 'luxury', 'deluxe'],
            'professional': ['professional', 'premium', 'high quality', 'luxury', 'deluxe'],
            
            # Action words
            'delivery': ['delivery', 'shipping', 'dispatch', 'postage'],
            'available': ['available', 'in stock', 'ready', 'for sale'],
            'free': ['free', 'complimentary', 'no charge', 'included'],
            
            # Size descriptors
            'large': ['large', 'big', 'oversized', 'generous'],
            'small': ['small', 'compact', 'mini', 'petite'],
            'medium': ['medium', 'standard', 'regular', 'normal'],
            
            # Material descriptors
            'durable': ['durable', 'long lasting', 'hardwearing', 'robust'],
            'soft': ['soft', 'comfortable', 'gentle', 'plush'],
            'realistic': ['realistic', 'lifelike', 'natural looking', 'authentic'],
            
            # Product-specific keywords from supplier websites
            'carpet': ['carpet', 'rug', 'flooring', 'carpeting'],
            'herringbone': ['herringbone', 'patterned', 'textured'],
            'loop': ['loop', 'pile', 'twist', 'saxony'],
            'saxony': ['saxony', 'plush', 'soft', 'luxurious'],
            'twist': ['twist', 'durable', 'hard-wearing', 'robust'],
            'plush': ['plush', 'soft', 'luxurious', 'comfortable'],
            'berber': ['berber', 'textured', 'patterned', 'durable'],
            'felt': ['felt', 'foam backed', 'backed'],
            'action': ['action', 'premium backing', 'enhanced backing'],
            'hessian': ['hessian', 'natural backing', 'traditional backing'],
            'decking': ['decking', 'composite', 'boards', 'planks'],
            'cladding': ['cladding', 'panels', 'boards'],
            'underlay': ['underlay', 'padding', 'cushioning'],
            'acoustic': ['acoustic', 'soundproof', 'sound dampening'],
            'shockpad': ['shockpad', 'cushioning', 'padding'],
            'slatted': ['slatted', 'horizontal', 'vertical']
        }
        
        # Prefix variations - REDUCED commercial, added product-specific
        self.prefixes = [
            'Premium',
            'High Quality',
            'Luxury',
            'Deluxe',
            'Garden',
            'Outdoor',
            'Indoor',
            'Heavy Duty',
            'Lightweight',
            'Eco Friendly',
            'Weather Resistant',
            'UV Protected',
            'Pet Friendly',
            'Child Safe',
            'Multi-Tone',
            'Fade Resistant'
        ]
        
        # Suffix variations
        self.suffixes = [
            'Fast Delivery',
            'Free Delivery',
            'UK Made',
            'Best Quality',
            'Top Rated',
            'Customer Favorite',
            'Limited Stock',
            'Sale Price',
            'Special Offer',
            'New Arrival',
            'Popular Choice',
            'Highly Recommended',
            '5 Star Rated',
            'Premium Grade',
            'Professional Quality'
        ]
        
        # Word order variations
        self.word_order_patterns = [
            '{size} {material} {product} {quality}',
            '{quality} {size} {material} {product}',
            '{product} {size} {material} {quality}',
            '{material} {product} {size} {quality}',
            '{quality} {product} {size} {material}'
        ]
        
        # Emoji variations removed - Facebook doesn't allow emojis in titles
    
    def extract_keywords(self, title):
        """
        Extract key components from a title.
        
        Args:
            title (str): Original title
            
        Returns:
            dict: Extracted components
        """
        title_lower = title.lower()
        
        # Extract size information
        size_match = re.search(r'(\d+mm)', title_lower)
        size = size_match.group(1) if size_match else None
        
        # Extract material
        material = None
        if 'artificial' in title_lower:
            material = 'artificial'
        elif 'synthetic' in title_lower:
            material = 'synthetic'
        elif 'fake' in title_lower:
            material = 'fake'
        
        # Extract product type
        product = None
        if 'grass' in title_lower:
            product = 'grass'
        elif 'turf' in title_lower:
            product = 'turf'
        elif 'lawn' in title_lower:
            product = 'lawn'
        
        # Extract quantity
        quantity = None
        if 'rolls' in title_lower:
            quantity = 'rolls'
        elif 'roll' in title_lower:
            quantity = 'roll'
        
        # Extract quality descriptors
        quality = []
        for quality_word in ['premium', 'high quality', 'professional', 'luxury', 'deluxe']:
            if quality_word in title_lower:
                quality.append(quality_word)
        
        return {
            'size': size,
            'material': material,
            'product': product,
            'quantity': quantity,
            'quality': quality,
            'original': title
        }
    
    def generate_variation(self, title, variation_type='random'):
        """
        Generate a variation of the given title.
        
        Args:
            title (str): Original title
            variation_type (str): Type of variation to generate
            
        Returns:
            dict: Variation result
        """
        try:
            # Extract components
            components = self.extract_keywords(title)
            
            if variation_type == 'random':
                variation_type = random.choice(['word_substitution', 'prefix_suffix', 'word_order'])
            
            if variation_type == 'word_substitution':
                return self._word_substitution_variation(components)
            elif variation_type == 'prefix_suffix':
                return self._prefix_suffix_variation(components)
            elif variation_type == 'word_order':
                return self._word_order_variation(components)
            # Emoji addition removed - Facebook doesn't allow emojis in titles
            else:
                return self._word_substitution_variation(components)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': title
            }
    
    def _ensure_title_length_limit(self, title, max_length=100):
        """
        Ensure title doesn't exceed the maximum length and remove duplications.

        Args:
            title (str): Title to check
            max_length (int): Maximum allowed length (Facebook limit is 100)

        Returns:
            str: Truncated and de-duplicated title if needed (NO dots added)
        """
        # SAFETY: Detect and remove title duplications
        words = title.split()
        if len(words) > 6:
            # Check for triple duplication first (more specific)
            chunk_size = len(words) // 3
            if chunk_size > 0:
                chunk1 = ' '.join(words[:chunk_size])
                chunk2 = ' '.join(words[chunk_size:chunk_size*2])
                chunk3 = ' '.join(words[chunk_size*2:chunk_size*3])

                if chunk1 == chunk2 == chunk3:
                    # Title is tripled! Use only one instance
                    title = chunk1
                    print(f"⚠️ [TitleVariator] Detected and removed triple duplication")

            # Check for double duplication
            chunk_size = len(words) // 2
            if chunk_size > 0:
                chunk1 = ' '.join(words[:chunk_size])
                chunk2 = ' '.join(words[chunk_size:chunk_size*2])

                if chunk1 == chunk2:
                    # Title is doubled! Use only one instance
                    title = chunk1
                    print(f"⚠️ [TitleVariator] Detected and removed double duplication")

        if len(title) <= max_length:
            return title

        # Try to truncate at word boundaries WITHOUT adding dots
        words = title.split()
        truncated = ""

        for word in words:
            if len(truncated + " " + word) <= max_length:
                truncated += (" " + word) if truncated else word
            else:
                break

        if truncated:
            return truncated  # NO DOTS - just return the truncated title
        else:
            # If even first word is too long, truncate character by character
            return title[:max_length]  # NO DOTS - just truncate
    
    def _word_substitution_variation(self, components):
        """Create variation by substituting words with synonyms."""
        title = components['original']
        variations = []
        
        # Try to substitute each word
        words = title.split()
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Find variations for this word
            if word_lower in self.word_variations:
                for variation in self.word_variations[word_lower]:
                    new_words = words.copy()
                    new_words[i] = variation
                    new_title = ' '.join(new_words)
                    variations.append(new_title)
        
        # If no variations found, try partial matches
        if not variations:
            for word in words:
                word_lower = word.lower()
                for key, values in self.word_variations.items():
                    if key in word_lower or word_lower in key:
                        for variation in values:
                            new_title = title.replace(word, variation)
                            variations.append(new_title)
        
        if variations:
            chosen_variation = random.choice(variations)
            # Apply length limit
            chosen_variation = self._ensure_title_length_limit(chosen_variation)
            return {
                'success': True,
                'original': title,
                'variation': chosen_variation,
                'type': 'word_substitution',
                'changes': f"Substituted words in: {title}"
            }
        else:
            return self._prefix_suffix_variation(components)
    
    def _prefix_suffix_variation(self, components):
        """Create variation by adding prefixes or suffixes."""
        title = components['original']
        
        # Randomly choose prefix or suffix
        if random.choice([True, False]):
            # Add prefix
            prefix = random.choice(self.prefixes)
            new_title = f"{prefix} {title}"
        else:
            # Add suffix
            suffix = random.choice(self.suffixes)
            new_title = f"{title} - {suffix}"
        
        # Apply length limit
        new_title = self._ensure_title_length_limit(new_title)
        
        return {
            'success': True,
            'original': title,
            'variation': new_title,
            'type': 'prefix_suffix',
            'changes': f"Added prefix/suffix to: {title}"
        }
    
    def _word_order_variation(self, components):
        """Create variation by changing word order."""
        title = components['original']
        words = title.split()
        
        # Try different word orders
        if len(words) >= 3:
            # Shuffle words while keeping some structure
            if len(words) >= 4:
                # Keep first and last words, shuffle middle
                first_word = words[0]
                last_word = words[-1]
                middle_words = words[1:-1]
                random.shuffle(middle_words)
                new_words = [first_word] + middle_words + [last_word]
            else:
                # Shuffle all words
                new_words = words.copy()
                random.shuffle(new_words)
            
            new_title = ' '.join(new_words)
            
            # Apply length limit
            new_title = self._ensure_title_length_limit(new_title)
            
            return {
                'success': True,
                'original': title,
                'variation': new_title,
                'type': 'word_order',
                'changes': f"Rearranged words in: {title}"
            }
        else:
            # Fallback to prefix/suffix
            return self._prefix_suffix_variation(components)
    
    # Emoji addition method removed - Facebook doesn't allow emojis in titles
    
    def generate_multiple_variations(self, title, count=5):
        """
        Generate multiple variations of a title.
        
        Args:
            title (str): Original title
            count (int): Number of variations to generate
            
        Returns:
            list: List of variation results
        """
        variations = []
        used_variations = set()
        
        # Try different variation types (emojis removed)
        variation_types = ['word_substitution', 'prefix_suffix', 'word_order']
        
        for i in range(count):
            variation_type = random.choice(variation_types)
            result = self.generate_variation(title, variation_type)
            
            if result['success'] and result['variation'] not in used_variations:
                variations.append(result)
                used_variations.add(result['variation'])
            else:
                # Try a different approach
                result = self.generate_variation(title, 'random')
                if result['success'] and result['variation'] not in used_variations:
                    variations.append(result)
                    used_variations.add(result['variation'])
        
        return variations
    
    def save_title_history(self, account, original_title, new_title, output_dir='accounts'):
        """
        Save title history for an account.
        
        Args:
            account (str): Account name
            original_title (str): Original title
            new_title (str): New title variation
            output_dir (str): Directory to save history
        """
        try:
            history_file = os.path.join(output_dir, account, 'title_history.json')
            
            # Load existing history
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Add new entry
            entry = {
                'timestamp': datetime.now().isoformat(),
                'original_title': original_title,
                'new_title': new_title,
                'type': 'variation'
            }
            
            history.append(entry)
            
            # Save updated history
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error saving title history: {e}")
            return False
    
    def load_title_history(self, account, output_dir='accounts'):
        """
        Load title history for an account.
        
        Args:
            account (str): Account name
            output_dir (str): Directory containing history
            
        Returns:
            list: Title history
        """
        try:
            history_file = os.path.join(output_dir, account, 'title_history.json')
            
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ Error loading title history: {e}")
            return []
    
    def get_next_title_variation(self, account, original_title, output_dir='accounts'):
        """
        Get the next title variation for an account, considering history.
        
        Args:
            account (str): Account name
            original_title (str): Original title to vary
            output_dir (str): Directory containing history
            
        Returns:
            dict: Next title variation
        """
        try:
            # Load history
            history = self.load_title_history(account, output_dir)
            
            # Find existing variations for this original title
            existing_variations = []
            for entry in history:
                if entry['original_title'] == original_title:
                    existing_variations.append(entry['new_title'])
            
            # Generate new variations
            variations = self.generate_multiple_variations(original_title, 10)
            
            # Find a variation that hasn't been used
            for variation in variations:
                if variation['variation'] not in existing_variations:
                    # Save this variation to history
                    self.save_title_history(account, original_title, variation['variation'], output_dir)
                    return variation
            
            # If all variations have been used, create a new one with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_title = f"{original_title} - {timestamp}"
            
            # Save to history
            self.save_title_history(account, original_title, new_title, output_dir)
            
            return {
                'success': True,
                'original': original_title,
                'variation': new_title,
                'type': 'timestamp',
                'changes': f"Added timestamp to: {original_title}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': original_title
            }

def main():
    """Test the title variator."""
    variator = TitleVariator()
    
    print("🧪 Title Variator Test")
    print("=" * 40)
    
    # Test titles
    test_titles = [
        "Premium Artificial Grass 4m x 2m",
        "High Quality Garden Turf - Fast Delivery",
        "Professional Grade Synthetic Lawn",
        "40mm Plush Carpet Like Artificial Grass"
    ]
    
    for title in test_titles:
        print(f"🔄 Testing variations for: {title}")
        
        # Generate multiple variations
        variations = variator.generate_multiple_variations(title, 3)
        
        for i, variation in enumerate(variations, 1):
            if variation['success']:
                print(f"  {i}. {variation['variation']} ({variation['type']})")
            else:
                print(f"  {i}. Error: {variation['error']}")
        
        print()

if __name__ == "__main__":
    main()
