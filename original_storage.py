#!/usr/bin/env python3
"""
Original Storage Module
Manages storage of original images and titles for each account to enable unique variations.
"""

import os
import json
import shutil
from datetime import datetime
import hashlib

class OriginalStorage:
    """Manages storage of original images and titles for each account."""
    
    def __init__(self, base_dir='accounts'):
        """
        Initialize the original storage system.
        
        Args:
            base_dir (str): Base directory for account storage
        """
        self.base_dir = base_dir
    
    def create_account_storage(self, account):
        """
        Create storage structure for an account.
        
        Args:
            account (str): Account name
            
        Returns:
            bool: Success status
        """
        try:
            # Create directories
            account_dir = os.path.join(self.base_dir, account)
            originals_dir = os.path.join(account_dir, 'originals')
            images_dir = os.path.join(originals_dir, 'images')
            titles_dir = os.path.join(originals_dir, 'titles')
            
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(titles_dir, exist_ok=True)
            
            # Create metadata file
            metadata_file = os.path.join(originals_dir, 'metadata.json')
            if not os.path.exists(metadata_file):
                metadata = {
                    'account': account,
                    'created': datetime.now().isoformat(),
                    'images': {},
                    'titles': {},
                    'last_updated': datetime.now().isoformat()
                }
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating account storage: {e}")
            return False
    
    def store_original_images(self, account, image_paths, listing_title=None):
        """
        Store original images for an account.
        
        Args:
            account (str): Account name
            image_paths (list): List of image paths to store
            listing_title (str): Associated listing title (optional)
            
        Returns:
            dict: Storage result
        """
        try:
            # Ensure account storage exists
            if not self.create_account_storage(account):
                return {'success': False, 'error': 'Failed to create account storage'}
            
            # Create unique storage directory for this set of images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if listing_title:
                safe_title = self._sanitize_filename(listing_title)[:30]
                storage_dir = os.path.join(self.base_dir, account, 'originals', 'images', f"{timestamp}_{safe_title}")
            else:
                storage_dir = os.path.join(self.base_dir, account, 'originals', 'images', timestamp)
            
            os.makedirs(storage_dir, exist_ok=True)
            
            stored_images = []
            
            for i, image_path in enumerate(image_paths):
                try:
                    # Copy image to storage
                    filename = os.path.basename(image_path)
                    name, ext = os.path.splitext(filename)
                    stored_filename = f"original_{i+1:02d}{ext}"
                    stored_path = os.path.join(storage_dir, stored_filename)
                    
                    shutil.copy2(image_path, stored_path)
                    
                    # Calculate file hash for uniqueness
                    file_hash = self._calculate_file_hash(stored_path)
                    
                    stored_images.append({
                        'original_path': image_path,
                        'stored_path': stored_path,
                        'filename': stored_filename,
                        'file_hash': file_hash,
                        'size': os.path.getsize(stored_path)
                    })
                    
                    print(f"✅ Stored original image: {stored_filename}")
                    
                except Exception as e:
                    print(f"⚠️ Error storing image {i+1}: {e}")
                    continue
            
            # Update metadata
            self._update_image_metadata(account, stored_images, listing_title)
            
            return {
                'success': True,
                'stored_images': stored_images,
                'storage_dir': storage_dir,
                'count': len(stored_images)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def store_original_title(self, account, title, listing_id=None):
        """
        Store original title for an account.
        
        Args:
            account (str): Account name
            title (str): Original title
            listing_id (str): Associated listing ID (optional)
            
        Returns:
            dict: Storage result
        """
        try:
            # Ensure account storage exists
            if not self.create_account_storage(account):
                return {'success': False, 'error': 'Failed to create account storage'}
            
            # Create title entry
            title_entry = {
                'title': title,
                'listing_id': listing_id,
                'stored_at': datetime.now().isoformat(),
                'title_hash': self._calculate_string_hash(title)
            }
            
            # Update metadata
            self._update_title_metadata(account, title_entry)
            
            return {
                'success': True,
                'stored_title': title_entry,
                'message': f'Stored original title: {title}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_original_images(self, account, listing_title=None):
        """
        Get stored original images for an account.
        
        Args:
            account (str): Account name
            listing_title (str): Specific listing title to find (optional)
            
        Returns:
            list: List of stored image sets
        """
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata.json')
            
            if not os.path.exists(metadata_file):
                return []
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if listing_title:
                # Find specific listing
                for image_set in metadata.get('images', {}).values():
                    if image_set.get('listing_title') == listing_title:
                        return [image_set]
                return []
            else:
                # Return all image sets
                return list(metadata.get('images', {}).values())
                
        except Exception as e:
            print(f"⚠️ Error loading original images: {e}")
            return []
    
    def get_original_titles(self, account):
        """
        Get stored original titles for an account.
        
        Args:
            account (str): Account name
            
        Returns:
            list: List of stored titles
        """
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata.json')
            
            if not os.path.exists(metadata_file):
                return []
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return list(metadata.get('titles', {}).values())
            
        except Exception as e:
            print(f"⚠️ Error loading original titles: {e}")
            return []
    
    def find_matching_original(self, account, search_title):
        """
        Find original title that matches a search title.
        
        Args:
            account (str): Account name
            search_title (str): Title to search for
            
        Returns:
            dict: Matching original title or None
        """
        try:
            titles = self.get_original_titles(account)
            
            # Try exact match first
            for title_entry in titles:
                if title_entry['title'].lower() == search_title.lower():
                    return title_entry
            
            # Try partial match
            search_words = set(search_title.lower().split())
            best_match = None
            best_score = 0
            
            for title_entry in titles:
                title_words = set(title_entry['title'].lower().split())
                common_words = search_words.intersection(title_words)
                score = len(common_words) / len(search_words)
                
                if score > best_score and score > 0.5:  # At least 50% match
                    best_score = score
                    best_match = title_entry
            
            return best_match
            
        except Exception as e:
            print(f"⚠️ Error finding matching original: {e}")
            return None
    
    def _sanitize_filename(self, filename):
        """Sanitize filename for safe storage."""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[^\w\s-]', '', filename)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.strip('_')
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def _calculate_string_hash(self, text):
        """Calculate SHA256 hash of a string."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _update_image_metadata(self, account, stored_images, listing_title=None):
        """Update image metadata in storage."""
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata.json')
            
            # Load existing metadata
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {
                    'account': account,
                    'created': datetime.now().isoformat(),
                    'images': {},
                    'titles': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            # Add new image set
            image_set_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata['images'][image_set_id] = {
                'id': image_set_id,
                'listing_title': listing_title,
                'stored_at': datetime.now().isoformat(),
                'images': stored_images,
                'count': len(stored_images)
            }
            
            metadata['last_updated'] = datetime.now().isoformat()
            
            # Save updated metadata
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error updating image metadata: {e}")
    
    def _update_title_metadata(self, account, title_entry):
        """Update title metadata in storage."""
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata.json')
            
            # Load existing metadata
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {
                    'account': account,
                    'created': datetime.now().isoformat(),
                    'images': {},
                    'titles': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            # Add new title
            title_id = title_entry['title_hash'][:16]  # Use first 16 chars of hash as ID
            metadata['titles'][title_id] = title_entry
            
            metadata['last_updated'] = datetime.now().isoformat()
            
            # Save updated metadata
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error updating title metadata: {e}")
    
    def cleanup_old_storage(self, account, days_old=30):
        """
        Clean up old stored files.
        
        Args:
            account (str): Account name
            days_old (int): Remove files older than this many days
            
        Returns:
            dict: Cleanup result
        """
        try:
            originals_dir = os.path.join(self.base_dir, account, 'originals')
            if not os.path.exists(originals_dir):
                return {'success': True, 'cleaned': 0}
            
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            # Clean up old image directories
            images_dir = os.path.join(originals_dir, 'images')
            if os.path.exists(images_dir):
                for item in os.listdir(images_dir):
                    item_path = os.path.join(images_dir, item)
                    if os.path.isdir(item_path):
                        if os.path.getmtime(item_path) < cutoff_date:
                            shutil.rmtree(item_path)
                            cleaned_count += 1
            
            return {
                'success': True,
                'cleaned': cleaned_count,
                'message': f'Cleaned up {cleaned_count} old storage items'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def main():
    """Test the original storage system."""
    storage = OriginalStorage()
    
    print("🧪 Original Storage Test")
    print("=" * 40)
    
    # Test account
    test_account = "test_account"
    
    # Test creating storage
    print(f"🔄 Creating storage for account: {test_account}")
    result = storage.create_account_storage(test_account)
    if result:
        print("✅ Account storage created successfully")
    else:
        print("❌ Failed to create account storage")
        return
    
    # Test storing title
    test_title = "40mm artificial grass rolls to thick 40mm artificial grass rolls"
    print(f"🔄 Storing title: {test_title}")
    result = storage.store_original_title(test_account, test_title)
    if result['success']:
        print(f"✅ Title stored: {result['message']}")
    else:
        print(f"❌ Failed to store title: {result['error']}")
    
    # Test finding matching title
    print(f"🔄 Finding matching title for: {test_title}")
    match = storage.find_matching_original(test_account, test_title)
    if match:
        print(f"✅ Found matching title: {match['title']}")
    else:
        print("❌ No matching title found")
    
    print("✅ Original storage test completed")

if __name__ == "__main__":
    main()
