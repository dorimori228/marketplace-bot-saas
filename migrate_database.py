#!/usr/bin/env python3
"""
Database migration script to add missing columns to existing databases.
This will add category, product_tags, location, and notes columns if they don't exist.
"""

import sqlite3
import os

def migrate_database(db_path):
    """
    Migrate a single database to add missing columns.
    
    Args:
        db_path: Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(listings)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Existing columns: {', '.join(existing_columns)}")
        
        # Define columns to add
        columns_to_add = [
            ('category', 'TEXT'),
            ('product_tags', 'TEXT'),
            ('location', 'TEXT'),
            ('notes', 'TEXT')
        ]
        
        added_columns = []
        
        # Add missing columns
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE listings ADD COLUMN {column_name} {column_type}')
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️ Could not add column {column_name}: {e}")
            else:
                print(f"ℹ️ Column {column_name} already exists")
        
        # Set default values for newly added columns
        if added_columns:
            # Set default category for existing listings
            if 'category' in added_columns:
                cursor.execute("UPDATE listings SET category = 'Other Garden decor' WHERE category IS NULL")
                print("✅ Set default category for existing listings")
            
            # Set default empty strings for other new columns
            for col in ['product_tags', 'location', 'notes']:
                if col in added_columns:
                    cursor.execute(f"UPDATE listings SET {col} = '' WHERE {col} IS NULL")
                    print(f"✅ Set default empty values for {col}")
        
        conn.commit()
        
        # Show final column structure
        cursor.execute("PRAGMA table_info(listings)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Final columns: {', '.join(final_columns)}")
        
        # Show listing count
        cursor.execute("SELECT COUNT(*) FROM listings")
        count = cursor.fetchone()[0]
        print(f"📊 Total listings: {count}")
        
        conn.close()
        
        if added_columns:
            print(f"🎉 Migration successful! Added: {', '.join(added_columns)}")
        else:
            print("✅ Database already up to date!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def migrate_all_accounts():
    """Migrate all account databases."""
    accounts_dir = 'accounts'
    
    if not os.path.exists(accounts_dir):
        print(f"❌ Accounts directory not found: {accounts_dir}")
        return
    
    accounts = [d for d in os.listdir(accounts_dir) 
                if os.path.isdir(os.path.join(accounts_dir, d))]
    
    if not accounts:
        print("❌ No accounts found!")
        return
    
    print(f"🔍 Found {len(accounts)} account(s)")
    print("=" * 60)
    
    success_count = 0
    for account in accounts:
        print(f"\n📁 Migrating account: {account}")
        db_path = os.path.join(accounts_dir, account, 'listings.db')
        
        if migrate_database(db_path):
            success_count += 1
        
        print("-" * 60)
    
    print(f"\n✅ Migration complete! {success_count}/{len(accounts)} accounts migrated successfully.")

def migrate_single_account(account_name):
    """Migrate a specific account's database."""
    db_path = os.path.join('accounts', account_name, 'listings.db')
    
    print(f"🔄 Migrating database for account: {account_name}")
    print(f"📁 Database path: {db_path}")
    print("=" * 60)
    
    if migrate_database(db_path):
        print("🎉 Migration completed successfully!")
    else:
        print("❌ Migration failed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Migrate specific account
        account = sys.argv[1]
        migrate_single_account(account)
    else:
        # Migrate all accounts
        print("🔧 Database Migration Tool")
        print("=" * 60)
        print("This will add missing columns (category, product_tags, location, notes)")
        print("to your existing databases.")
        print()
        
        response = input("Continue with migration? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            migrate_all_accounts()
        else:
            print("👋 Migration cancelled.")
