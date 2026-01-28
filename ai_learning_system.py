#!/usr/bin/env python3
"""
AI Learning System for Facebook Marketplace Bot
Uses Cursor AI API to learn from listing data and generate intelligent variations.
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
            print("⚠️ No OpenAI API key found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
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
            print(f"⚠️ Error loading learning data: {e}")
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
            print(f"⚠️ Error saving learning data: {e}")
    
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
            
            # Analyze patterns
            analysis = self._analyze_listing_patterns(listings, account)
            
            # Store analysis in learning data
            if account not in self.learning_data['accounts']:
                self.learning_data['accounts'][account] = {}
            
            self.learning_data['accounts'][account] = {
                'analysis': analysis,
                'last_analyzed': datetime.now().isoformat(),
                'total_listings': len(listings)
            }
            
            self.save_learning_data()
            
            print(f"✅ Analyzed {len(listings)} listings for account: {account}")
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            print(f"❌ Error analyzing account listings: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_listing_patterns(self, listings: List, account: str) -> Dict:
        """Analyze patterns in listing data."""
        try:
            # Extract patterns
            title_patterns = []
            description_patterns = []
            category_patterns = {}
            price_patterns = []
            
            for listing in listings:
                title, description, category, price, status, created_at, updated_at = listing
                
                # Title analysis
                if title:
                    title_patterns.append({
                        'text': title,
                        'length': len(title),
                        'words': len(title.split()),
                        'has_emoji': any(ord(char) > 127 for char in title),
                        'has_numbers': any(char.isdigit() for char in title)
                    })
                
                # Description analysis
                if description:
                    description_patterns.append({
                        'text': description,
                        'length': len(description),
                        'lines': len(description.split('\n')),
                        'has_emoji': any(ord(char) > 127 for char in description),
                        'has_bullets': '•' in description or '-' in description
                    })
                
                # Category analysis
                if category:
                    category_patterns[category] = category_patterns.get(category, 0) + 1
                
                # Price analysis
                if price:
                    try:
                        # Extract numeric price
                        price_clean = ''.join(filter(str.isdigit, price))
                        if price_clean:
                            price_patterns.append(int(price_clean))
                    except:
                        pass
            
            # Calculate statistics
            analysis = {
                'title_stats': {
                    'avg_length': sum(p['length'] for p in title_patterns) / len(title_patterns) if title_patterns else 0,
                    'avg_words': sum(p['words'] for p in title_patterns) / len(title_patterns) if title_patterns else 0,
                    'emoji_usage': sum(1 for p in title_patterns if p['has_emoji']) / len(title_patterns) if title_patterns else 0,
                    'number_usage': sum(1 for p in title_patterns if p['has_numbers']) / len(title_patterns) if title_patterns else 0
                },
                'description_stats': {
                    'avg_length': sum(p['length'] for p in description_patterns) / len(description_patterns) if description_patterns else 0,
                    'avg_lines': sum(p['lines'] for p in description_patterns) / len(description_patterns) if description_patterns else 0,
                    'emoji_usage': sum(1 for p in description_patterns if p['has_emoji']) / len(description_patterns) if description_patterns else 0,
                    'bullet_usage': sum(1 for p in description_patterns if p['has_bullets']) / len(description_patterns) if description_patterns else 0
                },
                'category_distribution': category_patterns,
                'price_stats': {
                    'min': min(price_patterns) if price_patterns else 0,
                    'max': max(price_patterns) if price_patterns else 0,
                    'avg': sum(price_patterns) / len(price_patterns) if price_patterns else 0
                },
                'total_listings': len(listings)
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing patterns: {e}")
            return {}
    
    def generate_ai_title_variation(self, account: str, original_title: str, context: Dict = None) -> Dict:
        """
        Generate AI-powered title variation using Cursor AI.
        
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
                    'error': 'No Cursor API key available',
                    'variation': original_title
                }
            
            print(f"🤖 Generating AI title variation for: {original_title[:50]}...")
            
            # Get account learning data
            account_data = self.learning_data.get('accounts', {}).get(account, {})
            analysis = account_data.get('analysis', {})
            
            # Build context for AI
            ai_context = self._build_ai_context(account, analysis, context)
            
            # Create AI prompt
            prompt = f"""
You are an expert Facebook Marketplace listing optimizer. Generate ONE unique, engaging title variation for this listing.

Original Title: "{original_title}"

Account Context:
- Account: {account}
- Total Listings: {analysis.get('total_listings', 0)}
- Average Title Length: {analysis.get('title_stats', {}).get('avg_length', 0):.0f} characters

Requirements:
1. Keep the core product information
2. Make it unique and engaging
3. Optimize for Facebook Marketplace search
4. Keep length under 100 characters (STRICT LIMIT)
5. Use product-specific keywords: "plush", "soft", "durable", "weather-resistant", "pet-friendly", "eco-friendly"
6. For carpets, use specific carpet types: "twist", "saxony", "loop", "plush", "berber"
7. DO NOT repeat the title multiple times
8. DO NOT duplicate any words or phrases within the title
9. Output ONLY the new title variation, nothing else

Generate ONE title variation ONLY. Start your response with "VARIATION:" followed by the single title.
Do NOT include multiple variations. Do NOT repeat the title.
"""

            # Call OpenAI API
            response = self._call_openai_api(prompt)

            if response['success']:
                print(f"🤖 [AI Response] Raw content: {response['content'][:200]}...")
                variations = self._parse_ai_variations(response['content'])
                
                if variations:
                    # Select best variation
                    best_variation = self._select_best_variation(variations, original_title, analysis)
                    
                    # Apply length limit to AI-generated title and remove duplications
                    from title_variator import TitleVariator
                    title_variator = TitleVariator()
                    best_variation = title_variator._ensure_title_length_limit(best_variation, 100)
                    
                    # Store learning data
                    self._store_variation_learning(account, original_title, best_variation, 'title')
                    
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
            print(f"❌ Error generating AI title variation: {e}")
            return {
                'success': False,
                'error': str(e),
                'variation': original_title
            }
    
    def generate_ai_description_variation(self, account: str, original_description: str, context: Dict = None) -> Dict:
        """
        Generate AI-powered description variation using Cursor AI.
        
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
                    'error': 'No Cursor API key available',
                    'variation': original_description
                }
            
            print(f"🤖 Generating AI description variation for: {original_description[:50]}...")
            
            # Get account learning data
            account_data = self.learning_data.get('accounts', {}).get(account, {})
            analysis = account_data.get('analysis', {})
            
            # Create AI prompt
            prompt = f"""
You are an expert Facebook Marketplace listing optimizer. Generate a unique, engaging description variation for this listing:

Original Description:
"{original_description}"

Account Context:
- Account: {account}
- Total Listings: {analysis.get('total_listings', 0)}
- Average Description Length: {analysis.get('description_stats', {}).get('avg_length', 0):.0f} characters
- Average Lines: {analysis.get('description_stats', {}).get('avg_lines', 0):.1f}
- Emoji Usage Rate: {analysis.get('description_stats', {}).get('emoji_usage', 0):.1%}
- Bullet Usage Rate: {analysis.get('description_stats', {}).get('bullet_usage', 0):.1%}

Requirements:
1. Keep all essential product information
2. Make it unique and engaging
3. Optimize for Facebook Marketplace
4. Maintain appropriate length ({analysis.get('description_stats', {}).get('avg_length', 200):.0f} chars average)
5. Use emojis if appropriate ({analysis.get('description_stats', {}).get('emoji_usage', 0):.1%} usage rate)
6. Use bullet points if appropriate ({analysis.get('description_stats', {}).get('bullet_usage', 0):.1%} usage rate)
7. Keep the same structure and key information

Generate 3 different description variations, each on a new line starting with "VARIATION:"
"""
            
            # Call OpenAI API
            response = self._call_openai_api(prompt)
            
            if response['success']:
                variations = self._parse_ai_variations(response['content'])
                
                if variations:
                    # Select best variation
                    best_variation = self._select_best_variation(variations, original_description, analysis)
                    
                    # Store learning data
                    self._store_variation_learning(account, original_description, best_variation, 'description')
                    
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
            print(f"❌ Error generating AI description variation: {e}")
            return {
                'success': False,
                'error': str(e),
                'variation': original_description
            }
    
    def _call_openai_api(self, prompt: str) -> Dict:
        """Call OpenAI API with the given prompt."""
        try:
            print("🤖 Calling OpenAI API...")
            
            # Import OpenAI
            try:
                import openai
            except ImportError:
                print("❌ OpenAI package not installed. Install with: pip install openai")
                return {
                    'success': False,
                    'error': 'OpenAI package not installed'
                }
            
            # Set API key
            openai.api_key = self.api_key
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
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
            print(f"❌ Error calling OpenAI API: {e}")
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
                if line.strip().startswith('VARIATION:'):
                    variation = line.replace('VARIATION:', '').strip()
                    if variation:
                        # SAFETY: Clean and validate the variation
                        variation = self._clean_variation(variation)
                        variations.append(variation)
                        # CRITICAL: Only take the FIRST variation, ignore the rest
                        break

            # If no VARIATION: prefix found, try to extract first line as variation
            if not variations and content.strip():
                first_line = content.strip().split('\n')[0]
                first_line = self._clean_variation(first_line)
                if first_line:
                    variations.append(first_line)

            # SAFETY: Return only the first variation, never multiple
            if variations:
                print(f"✅ [AI Parser] Returning ONLY first variation: {variations[0][:50]}...")
                return [variations[0]]

            return variations

        except Exception as e:
            print(f"❌ Error parsing AI variations: {e}")
            return []

    def _clean_variation(self, text: str) -> str:
        """Clean and validate a variation to remove duplications."""
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())

            # Detect and remove duplications
            words = text.split()

            # Check for triple duplication
            if len(words) >= 9:
                chunk_size = len(words) // 3
                chunk1 = ' '.join(words[:chunk_size])
                chunk2 = ' '.join(words[chunk_size:chunk_size*2])
                chunk3 = ' '.join(words[chunk_size*2:chunk_size*3])

                if chunk1 == chunk2 == chunk3:
                    print(f"⚠️ [AI] Detected triple duplication, using single instance")
                    return chunk1

            # Check for double duplication
            if len(words) >= 6:
                chunk_size = len(words) // 2
                chunk1 = ' '.join(words[:chunk_size])
                chunk2 = ' '.join(words[chunk_size:chunk_size*2])

                if chunk1 == chunk2:
                    print(f"⚠️ [AI] Detected double duplication, using single instance")
                    return chunk1

            # Enforce 100 character limit
            if len(text) > 100:
                print(f"⚠️ [AI] Title too long ({len(text)} chars), truncating to 100")
                # Truncate at word boundary
                words = text.split()
                truncated = ""
                for word in words:
                    if len(truncated + " " + word) <= 100:
                        truncated += (" " + word) if truncated else word
                    else:
                        break
                return truncated if truncated else text[:100]

            return text

        except Exception as e:
            print(f"⚠️ Error cleaning variation: {e}")
            return text

    def _select_best_variation(self, variations: List[str], original: str, analysis: Dict) -> str:
        """Select the best variation based on analysis and requirements."""
        try:
            if not variations:
                return original

            # Select first valid variation that's not a duplicate
            for variation in variations:
                # Additional safety check
                cleaned = self._clean_variation(variation)
                if cleaned and len(cleaned) <= 100:
                    print(f"✅ Selected variation: {cleaned} (length: {len(cleaned)})")
                    return cleaned

            # If all variations failed, return original
            print(f"⚠️ All variations invalid, using original")
            return original

        except Exception as e:
            print(f"❌ Error selecting best variation: {e}")
            return original
    
    def _build_ai_context(self, account: str, analysis: Dict, context: Dict) -> str:
        """Build context string for AI prompts."""
        try:
            context_parts = [
                f"Account: {account}",
                f"Total Listings: {analysis.get('total_listings', 0)}",
                f"Category Distribution: {analysis.get('category_distribution', {})}",
                f"Price Range: £{analysis.get('price_stats', {}).get('min', 0)} - £{analysis.get('price_stats', {}).get('max', 0)}"
            ]
            
            if context:
                for key, value in context.items():
                    context_parts.append(f"{key}: {value}")
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            print(f"❌ Error building AI context: {e}")
            return ""
    
    def _store_variation_learning(self, account: str, original: str, variation: str, type_: str):
        """Store variation learning data."""
        try:
            if 'variations' not in self.learning_data:
                self.learning_data['variations'] = {}
            
            variation_key = f"{account}_{type_}_{hashlib.md5(original.encode()).hexdigest()[:8]}"
            
            self.learning_data['variations'][variation_key] = {
                'account': account,
                'type': type_,
                'original': original,
                'variation': variation,
                'timestamp': datetime.now().isoformat()
            }
            
            self.save_learning_data()
            
        except Exception as e:
            print(f"❌ Error storing variation learning: {e}")
    
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
            print(f"❌ Error getting learning insights: {e}")
            return {'error': str(e)}
    
    def train_on_successful_listings(self, account: str, successful_listings: List[Dict]):
        """
        Train the AI system on successful listings to improve future variations.
        
        Args:
            account (str): Account name
            successful_listings (List[Dict]): List of successful listing data
        """
        try:
            print(f"🎓 Training AI system on {len(successful_listings)} successful listings for account: {account}")
            
            # Analyze successful patterns
            success_patterns = self._analyze_success_patterns(successful_listings)
            
            # Update learning data
            if account not in self.learning_data['accounts']:
                self.learning_data['accounts'][account] = {}
            
            self.learning_data['accounts'][account]['success_patterns'] = success_patterns
            self.learning_data['accounts'][account]['last_trained'] = datetime.now().isoformat()
            
            self.save_learning_data()
            
            print(f"✅ AI system trained on successful listings for account: {account}")
            
        except Exception as e:
            print(f"❌ Error training AI system: {e}")
    
    def _analyze_success_patterns(self, successful_listings: List[Dict]) -> Dict:
        """Analyze patterns in successful listings."""
        try:
            patterns = {
                'title_patterns': [],
                'description_patterns': [],
                'common_elements': {},
                'success_indicators': {}
            }
            
            for listing in successful_listings:
                # Analyze title patterns
                if 'title' in listing:
                    patterns['title_patterns'].append({
                        'length': len(listing['title']),
                        'has_emoji': any(ord(char) > 127 for char in listing['title']),
                        'has_numbers': any(char.isdigit() for char in listing['title'])
                    })
                
                # Analyze description patterns
                if 'description' in listing:
                    patterns['description_patterns'].append({
                        'length': len(listing['description']),
                        'has_emoji': any(ord(char) > 127 for char in listing['description']),
                        'has_bullets': '•' in listing['description'] or '-' in listing['description']
                    })
            
            return patterns
            
        except Exception as e:
            print(f"❌ Error analyzing success patterns: {e}")
            return {}
