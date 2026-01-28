#!/usr/bin/env python3
"""
Description Variation Module
Generates unique variations of listing descriptions to avoid Facebook's duplicate detection.
"""

import os
import random
import re
import json
from datetime import datetime

class DescriptionVariator:
    """Generates unique variations of listing descriptions."""
    
    def __init__(self):
        """Initialize the description variator with variation strategies."""
        
        # Common description patterns and variations
        self.opening_patterns = [
            "🚚 Fast Delivery: 2-4 days",
            "⚡ Quick Delivery: 2-4 days", 
            "📦 Fast Shipping: 2-4 days",
            "🚛 Express Delivery: 2-4 days",
            "📮 Rapid Delivery: 2-4 days",
            "🚀 Lightning Fast: 2-4 days",
            "⚡ Super Fast: 2-4 days",
            "📦 Express Shipping: 2-4 days",
            "🚚 Priority Delivery: 2-4 days",
            "⚡ Rapid Transit: 2-4 days"
        ]
        
        self.sample_patterns = [
            "✅ Free Samples Available",
            "🎁 Free Samples Available",
            "📋 Free Samples Available", 
            "🆓 Free Samples Available",
            "✨ Free Samples Available",
            "🎯 Free Samples Available",
            "📝 Free Samples Available",
            "🎪 Free Samples Available",
            "🎨 Free Samples Available",
            "🌟 Free Samples Available"
        ]
        
        self.options_intro_patterns = [
            "💷 Options Available:",
            "💰 Options Available:",
            "💵 Options Available:",
            "💸 Options Available:",
            "💳 Options Available:"
        ]
        
        self.budget_patterns = [
            "- Budget Range (30mm)",
            "- Economy Range (30mm)",
            "- Standard Range (30mm)",
            "- Basic Range (30mm)",
            "- Entry Range (30mm)"
        ]
        
        self.mid_range_patterns = [
            "- Mid-Range (35mm)",
            "- Standard Range (35mm)",
            "- Professional Range (35mm)",
            "- Quality Range (35mm)",
            "- Premium Range (35mm)"
        ]
        
        self.premium_patterns = [
            "- Premium Range (40mm)",
            "- Luxury Range (40mm)",
            "- High-End Range (40mm)",
            "- Professional Range (40mm)",
            "- Deluxe Range (40mm)"
        ]
        
        # Additional description elements - REDUCED commercial overuse
        self.quality_descriptors = [
            "High Quality",
            "Premium Quality", 
            "Professional Grade",
            "Luxury Quality",
            "Superior Quality",
            "Top Quality",
            "Excellent Quality",
            "Plush",
            "Soft",
            "Durable",
            "Weather Resistant"
        ]
        
        self.durability_descriptors = [
            "Durable",
            "Long Lasting",
            "Hardwearing", 
            "Robust",
            "Weather Resistant",
            "UV Protected",
            "Fade Resistant",
            "Heavy Duty"
        ]
        
        self.installation_descriptors = [
            "Easy Installation",
            "Simple Installation",
            "Quick Installation",
            "DIY Friendly",
            "Professional Installation Available",
            "Installation Guide Included"
        ]
        
        self.warranty_patterns = [
            "2 Year Warranty",
            "3 Year Warranty", 
            "5 Year Warranty",
            "Extended Warranty Available",
            "Full Warranty Included",
            "Comprehensive Warranty"
        ]
        
        # Emoji variations
        self.emojis = {
            'delivery': ['🚚', '📦', '🚛', '✈️', '📮'],
            'quality': ['⭐', '✨', '💎', '🏆', '🌟'],
            'samples': ['🎁', '📋', '🆓', '✨', '🎯'],
            'options': ['💷', '💰', '💵', '💸', '💳'],
            'ranges': ['📏', '📐', '📊', '📈', '📉'],
            'warranty': ['🛡️', '🔒', '✅', '🆔', '📜']
        }
    
    def extract_description_components(self, description):
        """
        Extract key components from a description.
        
        Args:
            description (str): Original description
            
        Returns:
            dict: Extracted components
        """
        components = {
            'delivery_info': None,
            'samples_info': None,
            'options_info': None,
            'ranges': [],
            'additional_info': [],
            'original': description
        }
        
        # Extract delivery information
        delivery_patterns = [
            r'🚚\s*Fast\s+Delivery[^\\n]*',
            r'⚡\s*Quick\s+Delivery[^\\n]*',
            r'📦\s*Fast\s+Shipping[^\\n]*',
            r'🚛\s*Express\s+Delivery[^\\n]*',
            r'📮\s*Rapid\s+Delivery[^\\n]*'
        ]
        
        for pattern in delivery_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                components['delivery_info'] = match.group(0).strip()
                break
        
        # Extract samples information
        samples_patterns = [
            r'✅\s*Free\s+Samples[^\\n]*',
            r'🎁\s*Free\s+Samples[^\\n]*',
            r'📋\s*Free\s+Samples[^\\n]*',
            r'🆓\s*Free\s+Samples[^\\n]*',
            r'✨\s*Free\s+Samples[^\\n]*'
        ]
        
        for pattern in samples_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                components['samples_info'] = match.group(0).strip()
                break
        
        # Extract options information
        options_match = re.search(r'💷\s*Options\s+Available:', description, re.IGNORECASE)
        if options_match:
            components['options_info'] = options_match.group(0).strip()
        
        # Extract ranges
        range_patterns = [
            r'-?\s*Budget\s+Range\s*\(30mm\)',
            r'-?\s*Mid-Range\s*\(35mm\)',
            r'-?\s*Premium\s+Range\s*\(40mm\)',
            r'-?\s*Economy\s+Range\s*\(30mm\)',
            r'-?\s*Standard\s+Range\s*\(35mm\)',
            r'-?\s*Luxury\s+Range\s*\(40mm\)'
        ]
        
        for pattern in range_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            components['ranges'].extend(matches)
        
        return components
    
    def generate_variation(self, description, variation_type='random'):
        """
        Generate a variation of the given description.
        
        Args:
            description (str): Original description
            variation_type (str): Type of variation to generate
            
        Returns:
            dict: Variation result
        """
        try:
            # Extract components
            components = self.extract_description_components(description)
            
            if variation_type == 'random':
                variation_type = random.choice(['full_rewrite', 'element_substitution', 'emoji_variation', 'structure_change'])
            
            if variation_type == 'full_rewrite':
                return self._full_rewrite_variation(components)
            elif variation_type == 'element_substitution':
                return self._element_substitution_variation(components)
            elif variation_type == 'emoji_variation':
                return self._emoji_variation(components)
            elif variation_type == 'structure_change':
                return self._structure_change_variation(components)
            else:
                return self._full_rewrite_variation(components)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': description
            }
    
    def _full_rewrite_variation(self, components):
        """Create variation by rewriting the entire description."""
        original = components['original']
        
        # Build new description with variations
        new_parts = []
        
        # Delivery info
        delivery = random.choice(self.opening_patterns)
        new_parts.append(delivery)
        
        # Samples info
        samples = random.choice(self.samples_patterns)
        new_parts.append(samples)
        
        # Add spacing
        new_parts.append("")
        
        # Options intro
        options_intro = random.choice(self.options_intro_patterns)
        new_parts.append(options_intro)
        
        # Ranges with variations
        ranges = [
            random.choice(self.budget_patterns),
            random.choice(self.mid_range_patterns),
            random.choice(self.premium_patterns)
        ]
        
        for range_option in ranges:
            new_parts.append(range_option)
        
        # Add additional quality info
        new_parts.append("")
        quality = random.choice(self.quality_descriptors)
        durability = random.choice(self.durability_descriptors)
        installation = random.choice(self.installation_descriptors)
        
        additional_info = [
            f"✨ {quality} artificial grass",
            f"🛡️ {durability} construction",
            f"🔧 {installation}",
            f"🛡️ {random.choice(self.warranty_patterns)}"
        ]
        
        for info in additional_info:
            new_parts.append(info)
        
        new_description = "\n".join(new_parts)
        
        return {
            'success': True,
            'original': original,
            'variation': new_description,
            'type': 'full_rewrite',
            'changes': f"Completely rewrote description with new structure and content"
        }
    
    def _element_substitution_variation(self, components):
        """Create variation by substituting elements."""
        original = components['original']
        
        # Start with original and make substitutions
        new_description = original
        
        # Substitute delivery patterns
        if components['delivery_info']:
            new_delivery = random.choice(self.opening_patterns)
            new_description = new_description.replace(components['delivery_info'], new_delivery)
        
        # Substitute samples patterns
        if components['samples_info']:
            new_samples = random.choice(self.samples_patterns)
            new_description = new_description.replace(components['samples_info'], new_samples)
        
        # Substitute options intro
        if components['options_info']:
            new_options = random.choice(self.options_intro_patterns)
            new_description = new_description.replace(components['options_info'], new_options)
        
        # Substitute ranges
        for i, range_text in enumerate(components['ranges']):
            if '30mm' in range_text:
                new_range = random.choice(self.budget_patterns)
            elif '35mm' in range_text:
                new_range = random.choice(self.mid_range_patterns)
            elif '40mm' in range_text:
                new_range = random.choice(self.premium_patterns)
            else:
                continue
            
            new_description = new_description.replace(range_text, new_range)
        
        return {
            'success': True,
            'original': original,
            'variation': new_description,
            'type': 'element_substitution',
            'changes': f"Substituted elements in original description"
        }
    
    def _emoji_variation(self, components):
        """Create variation by changing emojis."""
        original = components['original']
        new_description = original
        
        # Replace delivery emojis
        delivery_emojis = self.emojis['delivery']
        for old_emoji in ['🚚', '⚡', '📦', '🚛', '📮']:
            if old_emoji in new_description:
                new_emoji = random.choice(delivery_emojis)
                new_description = new_description.replace(old_emoji, new_emoji)
        
        # Replace quality emojis
        quality_emojis = self.emojis['quality']
        for old_emoji in ['✅', '🎁', '📋', '🆓', '✨']:
            if old_emoji in new_description:
                new_emoji = random.choice(quality_emojis)
                new_description = new_description.replace(old_emoji, new_emoji)
        
        # Replace options emojis
        options_emojis = self.emojis['options']
        for old_emoji in ['💷', '💰', '💵', '💸', '💳']:
            if old_emoji in new_description:
                new_emoji = random.choice(options_emojis)
                new_description = new_description.replace(old_emoji, new_emoji)
        
        return {
            'success': True,
            'original': original,
            'variation': new_description,
            'type': 'emoji_variation',
            'changes': f"Changed emojis in description"
        }
    
    def _structure_change_variation(self, components):
        """Create variation by changing structure and order."""
        original = components['original']
        
        # Split into lines and reorder
        lines = original.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # Reorder lines randomly
        random.shuffle(non_empty_lines)
        
        # Add some new elements
        new_elements = [
            random.choice(self.quality_descriptors) + " artificial grass",
            random.choice(self.durability_descriptors) + " construction",
            random.choice(self.installation_descriptors)
        ]
        
        # Insert new elements at random positions
        for element in new_elements:
            insert_pos = random.randint(0, len(non_empty_lines))
            non_empty_lines.insert(insert_pos, f"✨ {element}")
        
        new_description = '\n'.join(non_empty_lines)
        
        return {
            'success': True,
            'original': original,
            'variation': new_description,
            'type': 'structure_change',
            'changes': f"Reordered lines and added new elements"
        }
    
    def generate_multiple_variations(self, description, count=5):
        """
        Generate multiple variations of a description.
        
        Args:
            description (str): Original description
            count (int): Number of variations to generate
            
        Returns:
            list: List of variation results
        """
        variations = []
        used_variations = set()
        
        # Try different variation types
        variation_types = ['full_rewrite', 'element_substitution', 'emoji_variation', 'structure_change']
        
        for i in range(count):
            variation_type = random.choice(variation_types)
            result = self.generate_variation(description, variation_type)
            
            if result['success'] and result['variation'] not in used_variations:
                variations.append(result)
                used_variations.add(result['variation'])
            else:
                # Try a different approach
                result = self.generate_variation(description, 'random')
                if result['success'] and result['variation'] not in used_variations:
                    variations.append(result)
                    used_variations.add(result['variation'])
        
        # If no variations were generated, create at least one simple variation
        if not variations:
            print("⚠️ No variations generated, creating fallback variation")
            fallback_result = self.generate_variation(description, 'full_rewrite')
            if fallback_result['success']:
                variations.append(fallback_result)
            else:
                # Last resort: create a simple timestamp variation
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                fallback_variation = f"{description}\n\n🆕 Updated: {timestamp}"
                variations.append({
                    'success': True,
                    'original': description,
                    'variation': fallback_variation,
                    'type': 'fallback',
                    'changes': f"Created fallback variation with timestamp"
                })
        
        return variations
    
    def get_next_description_variation(self, account, original_description):
        """
        Get the next description variation for an account, considering history.
        
        Args:
            account (str): Account name
            original_description (str): Original description to vary
            
        Returns:
            dict: Next description variation
        """
        try:
            # Generate new variations
            variations = self.generate_multiple_variations(original_description, 10)
            
            # Find a variation that hasn't been used
            for variation in variations:
                if variation['success']:
                    return variation
            
            # If no variations were generated, create a simple one
            print("⚠️ No variations generated, creating simple variation")
            simple_variation = self.generate_variation(original_description, 'random')
            if simple_variation['success']:
                return simple_variation
            
            # If all variations have been used, create a new one with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_description = f"{original_description}\n\n🆕 Updated: {timestamp}"
            
            return {
                'success': True,
                'original': original_description,
                'variation': new_description,
                'type': 'timestamp',
                'changes': f"Added timestamp to: {original_description[:50]}..."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': original_description
            }

def main():
    """Test the description variator."""
    variator = DescriptionVariator()
    
    print("🧪 Description Variator Test")
    print("=" * 40)
    
    # Test description
    test_description = """🚚 Fast Delivery: 2-4 days
✅ Free Samples Available

💷 Options Available:
- Budget Range (30mm)
- Mid-Range (35mm)
- Premium Range (40mm)"""
    
    print(f"🔄 Testing variations for description:")
    print(f"Original: {test_description}")
    print()
    
    # Generate multiple variations
    variations = variator.generate_multiple_variations(test_description, 3)
    
    for i, variation in enumerate(variations, 1):
        if variation['success']:
            print(f"Variation {i} ({variation['type']}):")
            print(variation['variation'])
            print()
        else:
            print(f"Variation {i}. Error: {variation['error']}")
    
    print("✅ Description variation test completed")

if __name__ == "__main__":
    main()
