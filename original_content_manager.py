#!/usr/bin/env python3
"""
Original Content Manager
Manages secure storage and retrieval of original listing content for each account.
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
import uuid

class OriginalContentManager:
    """Manages original content storage and retrieval for each account."""
    
    def __init__(self, base_dir='accounts'):
        """
        Initialize the original content manager.
        
        Args:
            base_dir (str): Base directory for account storage
        """
        self.base_dir = base_dir
    
    def create_account_structure(self, account):
        """
        Create the main folder structure for an account.
        
        Args:
            account (str): Account name
            
        Returns:
            bool: Success status
        """
        try:
            # Main account directory
            account_dir = os.path.join(self.base_dir, account)
            
            # Original content structure
            originals_dir = os.path.join(account_dir, 'originals')
            main_photos_dir = os.path.join(originals_dir, 'main_photos')
            backup_dir = os.path.join(originals_dir, 'backup')
            metadata_dir = os.path.join(originals_dir, 'metadata')
            
            # Create directories
            for directory in [originals_dir, main_photos_dir, backup_dir, metadata_dir]:
                os.makedirs(directory, exist_ok=True)
            
            # Create metadata file
            metadata_file = os.path.join(metadata_dir, 'content_index.json')
            if not os.path.exists(metadata_file):
                index_data = {
                    'account': account,
                    'created': datetime.now().isoformat(),
                    'listings': {},
                    'last_updated': datetime.now().isoformat()
                }
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created account structure for: {account}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating account structure: {e}")
            return False
    
    def store_original_listing(self, account, listing_data):
        """
        Store original listing content securely.
        
        Args:
            account (str): Account name
            listing_data (dict): Complete listing data
            
        Returns:
            dict: Storage result
        """
        try:
            # Ensure account structure exists
            if not self.create_account_structure(account):
                return {'success': False, 'error': 'Failed to create account structure'}
            
            # Generate unique listing ID
            listing_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create listing directory
            listing_dir = os.path.join(self.base_dir, account, 'originals', 'main_photos', f"{timestamp}_{listing_id}")
            os.makedirs(listing_dir, exist_ok=True)
            
            # Store original images
            original_images = []
            if 'image_paths' in listing_data and listing_data['image_paths']:
                for i, image_path in enumerate(listing_data['image_paths']):
                    if os.path.exists(image_path):
                        # Copy original image
                        filename = f"original_{i+1:02d}{os.path.splitext(image_path)[1]}"
                        dest_path = os.path.join(listing_dir, filename)
                        shutil.copy2(image_path, dest_path)
                        
                        # Calculate hash for verification
                        file_hash = self._calculate_file_hash(dest_path)
                        
                        original_images.append({
                            'original_path': image_path,
                            'stored_path': dest_path,
                            'filename': filename,
                            'file_hash': file_hash,
                            'size': os.path.getsize(dest_path)
                        })
            
            # Store listing metadata
            listing_metadata = {
                'listing_id': listing_id,
                'timestamp': timestamp,
                'created': datetime.now().isoformat(),
                'title': listing_data.get('title', ''),
                'description': listing_data.get('description', ''),
                'price': listing_data.get('price', ''),
                'category': listing_data.get('category', ''),
                'location': listing_data.get('location', ''),
                'product_tags': listing_data.get('product_tags', ''),
                'images': original_images,
                'image_count': len(original_images),
                'status': 'active'
            }
            
            # Save metadata file
            metadata_file = os.path.join(listing_dir, 'listing_metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(listing_metadata, f, indent=2, ensure_ascii=False)
            
            # Update main index
            self._update_content_index(account, listing_id, listing_metadata)
            
            # Create backup
            self._create_backup(account, listing_id, listing_metadata)
            
            return {
                'success': True,
                'listing_id': listing_id,
                'listing_dir': listing_dir,
                'images_stored': len(original_images),
                'message': f'Stored original listing with {len(original_images)} images'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_original_listing(self, account, listing_title=None, listing_id=None):
        """
        Get original listing content.
        
        Args:
            account (str): Account name
            listing_title (str): Title to search for (optional)
            listing_id (str): Specific listing ID (optional)
            
        Returns:
            dict: Original listing data or None
        """
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata', 'content_index.json')
            
            if not os.path.exists(metadata_file):
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            if listing_id:
                # Get specific listing by ID
                if listing_id in index_data['listings']:
                    return index_data['listings'][listing_id]
            elif listing_title:
                # Find listing by title
                for listing_id, listing_data in index_data['listings'].items():
                    if listing_data.get('title', '').lower() == listing_title.lower():
                        return listing_data
            else:
                # Get most recent active listing
                active_listings = [
                    listing for listing in index_data['listings'].values()
                    if listing.get('status') == 'active'
                ]
                if active_listings:
                    return max(active_listings, key=lambda x: x.get('created', ''))
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting original listing: {e}")
            return None
    
    def get_original_images(self, account, listing_title=None, listing_id=None):
        """
        Get original images for a listing.
        
        Args:
            account (str): Account name
            listing_title (str): Title to search for (optional)
            listing_id (str): Specific listing ID (optional)
            
        Returns:
            list: List of original image paths
        """
        try:
            listing_data = self.get_original_listing(account, listing_title, listing_id)
            
            if not listing_data:
                return []
            
            # Get image paths from stored images
            image_paths = []
            for image_info in listing_data.get('images', []):
                if os.path.exists(image_info['stored_path']):
                    image_paths.append(image_info['stored_path'])
            
            return image_paths
            
        except Exception as e:
            print(f"⚠️ Error getting original images: {e}")
            return []
    
    def update_listing_status(self, account, listing_id, status):
        """
        Update listing status.
        
        Args:
            account (str): Account name
            listing_id (str): Listing ID
            status (str): New status
            
        Returns:
            bool: Success status
        """
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata', 'content_index.json')
            
            if not os.path.exists(metadata_file):
                return False
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            if listing_id in index_data['listings']:
                index_data['listings'][listing_id]['status'] = status
                index_data['listings'][listing_id]['last_updated'] = datetime.now().isoformat()
                index_data['last_updated'] = datetime.now().isoformat()
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, indent=2, ensure_ascii=False)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error updating listing status: {e}")
            return False
    
    def get_all_listings(self, account):
        """
        Get all listings for an account.
        
        Args:
            account (str): Account name
            
        Returns:
            list: List of all listings
        """
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata', 'content_index.json')
            
            if not os.path.exists(metadata_file):
                return []
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            return list(index_data['listings'].values())
            
        except Exception as e:
            print(f"⚠️ Error getting all listings: {e}")
            return []
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def _update_content_index(self, account, listing_id, listing_metadata):
        """Update the main content index."""
        try:
            metadata_file = os.path.join(self.base_dir, account, 'originals', 'metadata', 'content_index.json')
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            index_data['listings'][listing_id] = listing_metadata
            index_data['last_updated'] = datetime.now().isoformat()
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error updating content index: {e}")
    
    def _create_backup(self, account, listing_id, listing_metadata):
        """Create backup of listing data."""
        try:
            backup_dir = os.path.join(self.base_dir, account, 'originals', 'backup')
            backup_file = os.path.join(backup_dir, f"{listing_id}_backup.json")
            
            backup_data = {
                'backup_created': datetime.now().isoformat(),
                'listing_metadata': listing_metadata
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error creating backup: {e}")
    
    def restore_from_backup(self, account, listing_id):
        """
        Restore listing from backup.
        
        Args:
            account (str): Account name
            listing_id (str): Listing ID to restore
            
        Returns:
            dict: Restore result
        """
        try:
            backup_file = os.path.join(self.base_dir, account, 'originals', 'backup', f"{listing_id}_backup.json")
            
            if not os.path.exists(backup_file):
                return {'success': False, 'error': 'Backup file not found'}
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            listing_metadata = backup_data['listing_metadata']
            
            # Restore to main index
            self._update_content_index(account, listing_id, listing_metadata)
            
            return {
                'success': True,
                'message': f'Restored listing {listing_id} from backup',
                'listing_data': listing_metadata
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def main():
    """Test the original content manager."""
    manager = OriginalContentManager()
    
    print("🧪 Original Content Manager Test")
    print("=" * 40)
    
    # Test account
    test_account = "test_account"
    
    # Test creating structure
    print(f"🔄 Creating structure for account: {test_account}")
    result = manager.create_account_structure(test_account)
    if result:
        print("✅ Account structure created successfully")
    else:
        print("❌ Failed to create account structure")
        return
    
    # Test storing listing
    test_listing = {
        'title': 'Test Artificial Grass',
        'description': 'Test description',
        'price': '£100',
        'category': 'Garden',
        'location': 'London',
        'image_paths': []  # Would contain actual image paths
    }
    
    print(f"🔄 Storing test listing...")
    result = manager.store_original_listing(test_account, test_listing)
    if result['success']:
        print(f"✅ Listing stored: {result['message']}")
        print(f"   📁 Listing ID: {result['listing_id']}")
    else:
        print(f"❌ Failed to store listing: {result['error']}")
    
    print("✅ Original content manager test completed")

if __name__ == "__main__":
    main()
