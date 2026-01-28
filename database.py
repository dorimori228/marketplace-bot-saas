"""
Database utility functions for the Facebook Marketplace Bot.
This module provides helper functions for database operations.
"""

import sqlite3
import os
from datetime import datetime


def create_listings_table(db_path):
    """
    Create the listings table if it doesn't exist.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price TEXT NOT NULL,
                description TEXT,
                image_paths TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                facebook_listing_id TEXT,
                notes TEXT
            )
        ''')
        
        # Create index on title for faster searches
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_listings_title 
            ON listings(title)
        ''')
        
        # Create index on created_at for sorting
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_listings_created_at 
            ON listings(created_at)
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"Database table created/verified: {db_path}")
        
    except Exception as e:
        print(f"Error creating database table: {e}")


def insert_listing(db_path, listing_data):
    """
    Insert a new listing into the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        listing_data (dict): Dictionary containing listing information
        
    Returns:
        int: The ID of the inserted listing
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure table exists
        create_listings_table(db_path)
        
        cursor.execute('''
            INSERT INTO listings (title, price, description, image_paths, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            listing_data.get('title', ''),
            listing_data.get('price', ''),
            listing_data.get('description', ''),
            '|'.join(listing_data.get('image_paths', [])),
            listing_data.get('status', 'active')
        ))
        
        listing_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"Listing inserted with ID: {listing_id}")
        return listing_id
        
    except Exception as e:
        print(f"Error inserting listing: {e}")
        return None


def get_listings(db_path, limit=50, status='active'):
    """
    Retrieve listings from the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        limit (int): Maximum number of listings to return
        status (str): Filter by status ('active', 'deleted', 'all')
        
    Returns:
        list: List of listing dictionaries
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if status == 'all':
            cursor.execute('''
                SELECT id, title, price, description, image_paths, 
                       created_at, updated_at, status, facebook_listing_id, notes
                FROM listings
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, title, price, description, image_paths, 
                       created_at, updated_at, status, facebook_listing_id, notes
                FROM listings
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (status, limit))
        
        listings = []
        for row in cursor.fetchall():
            listings.append({
                'id': row[0],
                'title': row[1],
                'price': row[2],
                'description': row[3],
                'image_paths': row[4].split('|') if row[4] else [],
                'created_at': row[5],
                'updated_at': row[6],
                'status': row[7],
                'facebook_listing_id': row[8],
                'notes': row[9]
            })
        
        conn.close()
        return listings
        
    except Exception as e:
        print(f"Error retrieving listings: {e}")
        return []


def update_listing_status(db_path, listing_id, status, notes=None):
    """
    Update the status of a listing.
    
    Args:
        db_path (str): Path to the SQLite database file
        listing_id (int): ID of the listing to update
        status (str): New status ('active', 'deleted', 'sold', etc.)
        notes (str): Optional notes about the status change
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE listings 
            SET status = ?, updated_at = ?, notes = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), notes, listing_id))
        
        conn.commit()
        conn.close()
        
        print(f"Listing {listing_id} status updated to: {status}")
        
    except Exception as e:
        print(f"Error updating listing status: {e}")


def delete_listing(db_path, listing_id):
    """
    Soft delete a listing by setting its status to 'deleted'.
    
    Args:
        db_path (str): Path to the SQLite database file
        listing_id (int): ID of the listing to delete
    """
    update_listing_status(db_path, listing_id, 'deleted', 'Deleted via bot')


def get_database_stats(db_path):
    """
    Get statistics about the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        
    Returns:
        dict: Database statistics
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM listings')
        total_count = cursor.fetchone()[0]
        
        # Get count by status
        cursor.execute('''
            SELECT status, COUNT(*) 
            FROM listings 
            GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        # Get most recent listing
        cursor.execute('''
            SELECT title, created_at 
            FROM listings 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        recent = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_listings': total_count,
            'status_counts': status_counts,
            'most_recent': {
                'title': recent[0] if recent else None,
                'created_at': recent[1] if recent else None
            }
        }
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}


def backup_database(db_path, backup_dir='backups'):
    """
    Create a backup of the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        backup_dir (str): Directory to store backups
    """
    try:
        if not os.path.exists(db_path):
            print(f"Database file not found: {db_path}")
            return None
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"listings_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"Database backed up to: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"Error creating database backup: {e}")
        return None