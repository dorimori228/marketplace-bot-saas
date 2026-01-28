#!/usr/bin/env python3
"""
Location Manager
Manages randomized locations for listings.
"""

import os
import json
from datetime import datetime

class LocationManager:
    """Manages randomized locations for listings."""
    
    def __init__(self, base_dir='accounts'):
        """
        Initialize the location manager.
        
        Args:
            base_dir (str): Base directory for account storage
        """
        self.base_dir = base_dir
    
    def store_randomized_locations(self, account, randomized_locations):
        """
        Store randomized locations for an account.
        
        Args:
            account (str): Account name
            randomized_locations (list): List of randomized location data
            
        Returns:
            dict: Storage result
        """
        try:
            # Create account directory if it doesn't exist
            account_dir = os.path.join(self.base_dir, account)
            os.makedirs(account_dir, exist_ok=True)
            
            # Create locations file
            locations_file = os.path.join(account_dir, 'randomized_locations.json')
            
            # Load existing locations
            existing_locations = {}
            if os.path.exists(locations_file):
                try:
                    with open(locations_file, 'r', encoding='utf-8') as f:
                        existing_locations = json.load(f)
                except:
                    existing_locations = {}
            
            # Update with new locations
            for location_data in randomized_locations:
                listing_id = str(location_data['listing_id'])
                existing_locations[listing_id] = {
                    'listing_id': listing_id,
                    'title': location_data['title'],
                    'new_location': location_data['new_location'],
                    'coordinates': location_data['coordinates'],
                    'updated_at': datetime.now().isoformat()
                }
            
            # Save updated locations
            with open(locations_file, 'w', encoding='utf-8') as f:
                json.dump(existing_locations, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'message': f'Stored {len(randomized_locations)} randomized locations',
                'stored_count': len(randomized_locations)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_randomized_location(self, account, listing_id):
        """
        Get randomized location for a specific listing.
        
        Args:
            account (str): Account name
            listing_id (str): Listing ID
            
        Returns:
            dict: Location data or None
        """
        try:
            locations_file = os.path.join(self.base_dir, account, 'randomized_locations.json')
            
            if not os.path.exists(locations_file):
                return None
            
            with open(locations_file, 'r', encoding='utf-8') as f:
                locations = json.load(f)
            
            listing_id_str = str(listing_id)
            if listing_id_str in locations:
                return locations[listing_id_str]
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting randomized location: {e}")
            return None
    
    def get_all_randomized_locations(self, account):
        """
        Get all randomized locations for an account.
        
        Args:
            account (str): Account name
            
        Returns:
            dict: All locations or empty dict
        """
        try:
            locations_file = os.path.join(self.base_dir, account, 'randomized_locations.json')
            
            if not os.path.exists(locations_file):
                return {}
            
            with open(locations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"⚠️ Error getting all randomized locations: {e}")
            return {}
    
    def clear_randomized_locations(self, account):
        """
        Clear all randomized locations for an account.
        
        Args:
            account (str): Account name
            
        Returns:
            bool: Success status
        """
        try:
            locations_file = os.path.join(self.base_dir, account, 'randomized_locations.json')
            
            if os.path.exists(locations_file):
                os.remove(locations_file)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error clearing randomized locations: {e}")
            return False

def main():
    """Test the location manager."""
    manager = LocationManager()
    
    print("Location Manager Test")
    print("=" * 30)
    
    # Test storing locations
    test_locations = [
        {
            'listing_id': '1',
            'title': 'Test Listing 1',
            'new_location': 'Leeds, England',
            'coordinates': '53.8758, -1.5146'
        },
        {
            'listing_id': '2', 
            'title': 'Test Listing 2',
            'new_location': 'Cardiff, Wales',
            'coordinates': '51.3917, -3.1620'
        }
    ]
    
    result = manager.store_randomized_locations('test_account', test_locations)
    if result['success']:
        print(f"Stored locations: {result['message']}")
    else:
        print(f"Failed to store: {result['error']}")
    
    # Test retrieving location
    location = manager.get_randomized_location('test_account', '1')
    if location:
        print(f"Retrieved location: {location['new_location']}")
    else:
        print("Failed to retrieve location")
    
    print("Location manager test completed")

if __name__ == "__main__":
    main()
