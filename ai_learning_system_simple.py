#!/usr/bin/env python3
"""
AI Learning System for Facebook Marketplace Bot (Windows Compatible)
Uses OpenAI API to learn from listing data and generate intelligent variations.
"""

import os
import json
import requests
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

class AILearningSystem:
    """AI-powered learning system for generating intelligent listing variations."""
    
    def __init__(self, openai_api_key: str = None, base_dir: str = 'accounts'):
        """
        Initialize the AI learning system.
        
        Args:
            openai_api_key (str): OpenAI API key (if None, will try to get from environment)
            base_dir (str): Base directory for account storage
        """
        self.base_dir = base_dir
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            print("WARNING: No OpenAI API key found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            print("   You can get your API key from: https://platform.openai.com/api-keys")
        
        # Learning data storage
        self.learning_data_file = os.path.join(base_dir, 'ai_learning_data.json')
        self.load_learning_data()
    
    def load_learning_data(self):
        """Load existing learning data from file."""
        try:
            if os.path.exists(self.learning_data_file):
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
                print(f"Loaded AI learning data: {len(self.learning_data.get('accounts', {}))} accounts")
            else:
                self.learning_data = {
                    'accounts': {},
                    'global_patterns': {},
                    'success_metrics': {},
                    'last_updated': datetime.now().isoformat()
                }
                print("Initialized new AI learning data")
        except Exception as e:
            print(f"WARNING: Error loading learning data: {e}")
            self.learning_data = {
                'accounts': {},
                'global_patterns': {},
                'success_metrics': {},
                'last_updated': datetime.now().isoformat()
            }
    
    def save_learning_data(self):
        """Save learning data to file."""
        try:
            self.learning_data['last_updated'] = datetime.now().isoformat()
            with open(self.learning_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
            print("AI learning data saved")
        except Exception as e:
            print(f"WARNING: Error saving learning data: {e}")
    
    def analyze_account_listings(self, account: str) -> Dict:
        """
        Analyze all listings for an account to learn patterns.
        
        Args:
            account (str): Account name
            
        Returns:
            Dict: Analysis results
        """
        try:
            print(f"Analyzing listings for account: {account}")
            
            # Get listings from database
            db_path = os.path.join(self.base_dir, account, 'listings.db')
            if not os.path.exists(db_path):
                print(f"⚠️ No database found for account: {account}")
                return {'success': False, 'error': 'No database found'}
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all listings
            cursor.execute('''
                SELECT title, description, category, price, status, created_at, updated_at
                FROM listings 
                WHERE status != 'deleted' OR status IS NULL
                ORDER BY created_at DESC
            ''')
            
            listings = cursor.fetchall()
            conn.close()
            
            if not listings:
                print(f"⚠️ No listings found for account: {account}")
                return {'success': False, 'error': 'No listings found'}
            
            # Initialize account data if not exists
            if account not in self.learning_data['accounts']:
                self.learning_data['accounts'][account] = {
                    'listings': [],
                    'patterns': {},
                    'success_metrics': {},
                    'last_analyzed': datetime.now().isoformat()
                }
            
            # Store listings data
            self.learning_data['accounts'][account]['listings'] = [
                {
                    'title': listing[0],
                    'description': listing[1],
                    'category': listing[2],
                    'price': listing[3],
                    'status': listing[4],
                    'created_at': listing[5],
                    'updated_at': listing[6]
                }
                for listing in listings
            ]
            
            # Analyze patterns
            self.learning_data['accounts'][account]['last_analyzed'] = datetime.now().isoformat()
            
            # Save updated data
            self.save_learning_data()
            
            print(f"✅ Analyzed {len(listings)} listings for account: {account}")
            return {
                'success': True,
                'listings_count': len(listings),
                'account': account
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing account listings: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_ai_title_variation(self, account: str, original_title: str, context: Dict = None) -> Dict:
        """
        Generate AI-powered title variation using OpenAI.
        
        Args:
            account (str): Account name
            original_title (str): Original title
            context (Dict): Additional context
            
        Returns:
            Dict: Variation result
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'No OpenAI API key available',
                    'variation': original_title
                }
            
            print(f"Generating AI title variation for: {original_title[:50]}...")
            
            # Create AI prompt
            prompt = f"""
You are an expert Facebook Marketplace listing optimizer. Generate a unique, engaging title variation for this listing:

Original Title: "{original_title}"

Requirements:
1. Keep the core product information
2. Make it unique and engaging
3. Optimize for Facebook Marketplace search
4. Maintain appropriate length (50-80 characters)
5. NO EMOJIS - use text only
6. Include numbers if relevant

Generate 3 different title variations, each on a new line starting with "VARIATION:"
"""
            
            # Call OpenAI API
            response = self._call_openai_api(prompt)
            
            if response['success']:
                variations = self._parse_ai_variations(response['content'])
                
                if variations:
                    # Select best variation
                    best_variation = variations[0]  # Simple selection
                    
                    return {
                        'success': True,
                        'variation': best_variation,
                        'type': 'ai_generated',
                        'all_variations': variations,
                        'confidence': 0.9
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Could not parse AI variations',
                        'variation': original_title
                    }
            else:
                return {
                    'success': False,
                    'error': response['error'],
                    'variation': original_title
                }
                
        except Exception as e:
            print(f"ERROR: Error generating AI title variation: {e}")
            return {
                'success': False,
                'error': str(e),
                'variation': original_title
            }
    
    def generate_ai_description_variation(self, account: str, original_description: str, context: Dict = None) -> Dict:
        """
        Generate AI-powered description variation using OpenAI.
        
        Args:
            account (str): Account name
            original_description (str): Original description
            context (Dict): Additional context
            
        Returns:
            Dict: Variation result
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'No OpenAI API key available',
                    'variation': original_description
                }
            
            print(f"Generating AI description variation for: {original_description[:50]}...")

            context = context or {}
            title = context.get('title', '')
            category = context.get('category', '')
            product_type = context.get('product_type', '')
            image_elements = context.get('image_elements', [])

            context_lines = []
            if title:
                context_lines.append(f'Title: "{title}"')
            if category:
                context_lines.append(f'Category: "{category}"')
            if product_type:
                context_lines.append(f"Detected product type: {product_type}")
            if image_elements:
                context_lines.append(f"Image clues: {', '.join(image_elements)}")

            context_block = "\n".join(context_lines) if context_lines else "No additional context."
            
            # Create AI prompt
            prompt = f"""
You are an expert Facebook Marketplace listing optimizer. Generate an accurate, unique description for this listing.

Context:
{context_block}

Original Description (may be a placeholder or generic):
"{original_description}"

Requirements:
1. Use the title/category/context to describe the correct product
2. Keep it accurate and specific to the item
3. Optimize for Facebook Marketplace
4. Maintain appropriate length (120-350 characters)
5. NO EMOJIS - use text only
6. Use bullet points if appropriate
7. Avoid adding unrelated product details

Generate 3 different description variations, each on a new line starting with "VARIATION:"
"""
            
            # Call OpenAI API
            response = self._call_openai_api(prompt)
            
            if response['success']:
                variations = self._parse_ai_variations(response['content'])
                
                if variations:
                    # Select best variation
                    best_variation = variations[0]  # Simple selection
                    
                    return {
                        'success': True,
                        'variation': best_variation,
                        'type': 'ai_generated',
                        'all_variations': variations,
                        'confidence': 0.9
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Could not parse AI variations',
                        'variation': original_description
                    }
            else:
                return {
                    'success': False,
                    'error': response['error'],
                    'variation': original_description
                }
                
        except Exception as e:
            print(f"ERROR: Error generating AI description variation: {e}")
            return {
                'success': False,
                'error': str(e),
                'variation': original_description
            }
    
    def _call_openai_api(self, prompt: str) -> Dict:
        """Call OpenAI API with the given prompt."""
        try:
            print("Calling OpenAI API...")
            
            # Import OpenAI
            try:
                import openai
            except ImportError:
                print("ERROR: OpenAI package not installed. Install with: pip install openai")
                return {
                    'success': False,
                    'error': 'OpenAI package not installed'
                }
            
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=self.api_key)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cost-effective model
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Facebook Marketplace listing optimizer. Generate unique, engaging variations that are optimized for Facebook Marketplace search and engagement."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=500,  # Limit tokens to control costs
                temperature=0.7,  # Balanced creativity
                top_p=0.9
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'content': content,
                'usage': response.usage  # Track token usage for cost monitoring
            }
            
        except Exception as e:
            print(f"ERROR: Error calling OpenAI API: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_ai_variations(self, content: str) -> List[str]:
        """Parse AI-generated variations from response content."""
        try:
            variations = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line:
                    # Handle different formats
                    if line.startswith('VARIATION:'):
                        variation = line.replace('VARIATION:', '').strip()
                        if variation:
                            variations.append(variation)
                    elif line.startswith('"') and line.endswith('"'):
                        # Handle quoted variations
                        variation = line.strip('"')
                        if variation:
                            variations.append(variation)
                    elif any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.']):
                        # Handle numbered variations
                        variation = line.split('.', 1)[1].strip().strip('"')
                        if variation:
                            variations.append(variation)
            
            return variations
            
        except Exception as e:
            print(f"ERROR: Error parsing AI variations: {e}")
            return []
    
    def get_learning_insights(self, account: str = None) -> Dict:
        """
        Get learning insights for an account or globally.
        
        Args:
            account (str): Account name (if None, returns global insights)
            
        Returns:
            Dict: Learning insights
        """
        try:
            if account:
                account_data = self.learning_data.get('accounts', {}).get(account, {})
                return {
                    'account': account,
                    'insights': account_data.get('analysis', {}),
                    'last_analyzed': account_data.get('last_analyzed'),
                    'total_listings': account_data.get('total_listings', 0)
                }
            else:
                # Global insights
                total_accounts = len(self.learning_data.get('accounts', {}))
                total_variations = len(self.learning_data.get('variations', {}))
                
                return {
                    'total_accounts': total_accounts,
                    'total_variations': total_variations,
                    'last_updated': self.learning_data.get('last_updated'),
                    'accounts': list(self.learning_data.get('accounts', {}).keys())
                }
                
        except Exception as e:
            print(f"ERROR: Error getting learning insights: {e}")
            return {'error': str(e)}
