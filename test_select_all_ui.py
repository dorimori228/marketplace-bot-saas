#!/usr/bin/env python3
"""
Test script to demonstrate the new Select All functionality in the UI.
This script creates some sample listings to test the Select All buttons.
"""

import os
import sqlite3
import json
from datetime import datetime

def create_sample_listings():
    """Create sample listings for testing the Select All functionality."""
    
    # Get the first available account
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        print("❌ No accounts directory found")
        return False
    
    accounts = [d for d in os.listdir(accounts_dir) if os.path.isdir(os.path.join(accounts_dir, d))]
    if not accounts:
        print("❌ No accounts found")
        return False
    
    account_name = accounts[0]
    account_dir = os.path.join(accounts_dir, account_name)
    db_path = os.path.join(account_dir, 'listings.db')
    
    print(f"✅ Using account: {account_name}")
    print(f"✅ Database path: {db_path}")
    
    # Create sample listings
    sample_listings = [
        {
            'title': 'Premium Artificial Grass 4m x 2m',
            'price': '£150',
            'description': 'High-quality artificial grass perfect for gardens. Fast delivery available.',
            'category': 'Other Garden decor',
            'product_tags': 'artificial grass, garden, outdoor',
            'location': 'London, UK',
            'image_paths': 'sample_image_1.jpg|sample_image_2.jpg',
            'status': 'active'
        },
        {
            'title': 'Decking Boards 2.4m x 150mm',
            'price': '£25',
            'description': 'Pressure treated decking boards. Perfect for outdoor projects.',
            'category': 'Other Garden decor',
            'product_tags': 'decking, wood, outdoor',
            'location': 'London, UK',
            'image_paths': 'sample_image_3.jpg',
            'status': 'active'
        },
        {
            'title': 'Garden Fencing Panels 6ft x 6ft',
            'price': '£45',
            'description': 'Sturdy garden fencing panels. Easy to install.',
            'category': 'Other Garden decor',
            'product_tags': 'fencing, garden, panels',
            'location': 'London, UK',
            'image_paths': 'sample_image_4.jpg|sample_image_5.jpg',
            'status': 'active'
        },
        {
            'title': 'Outdoor Lighting Set',
            'price': '£35',
            'description': 'LED outdoor lighting set with timer. Weather resistant.',
            'category': 'Other Garden decor',
            'product_tags': 'lighting, LED, outdoor',
            'location': 'London, UK',
            'image_paths': 'sample_image_6.jpg',
            'status': 'active'
        },
        {
            'title': 'Garden Furniture Set',
            'price': '£200',
            'description': 'Complete garden furniture set. Table and 4 chairs included.',
            'category': 'Other Garden decor',
            'product_tags': 'furniture, garden, table, chairs',
            'location': 'London, UK',
            'image_paths': 'sample_image_7.jpg|sample_image_8.jpg',
            'status': 'active'
        }
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create listings table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price TEXT NOT NULL,
                description TEXT,
                category TEXT,
                product_tags TEXT,
                location TEXT,
                image_paths TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                facebook_listing_id TEXT,
                notes TEXT
            )
        ''')
        
        # Clear existing listings (optional - remove this line to keep existing listings)
        cursor.execute('DELETE FROM listings')
        print("🧹 Cleared existing listings")
        
        # Insert sample listings
        for listing in sample_listings:
            cursor.execute('''
                INSERT INTO listings (title, price, description, category, product_tags, location, image_paths, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing['title'],
                listing['price'],
                listing['description'],
                listing['category'],
                listing['product_tags'],
                listing['location'],
                listing['image_paths'],
                listing['status']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created {len(sample_listings)} sample listings")
        print("\n🎉 Sample listings created successfully!")
        print("🌐 Now you can:")
        print("   1. Go to http://localhost:5000")
        print("   2. Select your account")
        print("   3. See the sample listings in the 'Relist Existing Listings' section")
        print("   4. Test the new 'Select All' and 'Deselect All' buttons!")
        print("\n📋 Sample listings created:")
        for i, listing in enumerate(sample_listings, 1):
            print(f"   {i}. {listing['title']} - {listing['price']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample listings: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Creating Sample Listings for Select All Testing")
    print("=" * 60)
    
    success = create_sample_listings()
    if success:
        print("\n✅ Test setup completed successfully!")
    else:
        print("\n❌ Test setup failed!")
