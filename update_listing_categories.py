#!/usr/bin/env python3
"""
Utility script to update categories for existing listings.
Run this to assign default categories to listings that don't have them.
"""

import sqlite3
import os

def update_listing_categories(account_name, default_category='Other Garden decor'):
    """
    Update all listings without a category to have the default category.
    
    Args:
        account_name: The account folder name
        default_category: Category to assign to listings without one
    """
    db_path = os.path.join('accounts', account_name, 'listings.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count listings without categories
        cursor.execute('''
            SELECT COUNT(*) FROM listings 
            WHERE category IS NULL OR category = ''
        ''')
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"✅ All listings in '{account_name}' already have categories assigned!")
            conn.close()
            return
        
        print(f"📋 Found {count} listing(s) without categories in account '{account_name}'")
        print(f"🔄 Updating to default category: '{default_category}'")
        
        # Update listings without categories
        cursor.execute('''
            UPDATE listings 
            SET category = ? 
            WHERE category IS NULL OR category = ''
        ''', (default_category,))
        
        conn.commit()
        updated = cursor.rowcount
        
        print(f"✅ Successfully updated {updated} listing(s)!")
        
        # Show category distribution
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM listings 
            GROUP BY category
        ''')
        
        print("\n📊 Category Distribution:")
        for row in cursor.fetchall():
            category = row[0] or 'Uncategorized'
            count = row[1]
            print(f"   - {category}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating categories: {e}")

def update_all_accounts(default_category='Other Garden decor'):
    """Update categories for all accounts."""
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
    
    for account in accounts:
        print(f"\n📁 Processing account: {account}")
        update_listing_categories(account, default_category)
        print("-" * 60)
    
    print("\n✅ All accounts processed!")

def interactive_update():
    """Interactive mode to update categories."""
    print("🔧 Listing Category Update Tool")
    print("=" * 60)
    
    # List available accounts
    accounts_dir = 'accounts'
    if not os.path.exists(accounts_dir):
        print(f"❌ Accounts directory not found: {accounts_dir}")
        return
    
    accounts = [d for d in os.listdir(accounts_dir) 
                if os.path.isdir(os.path.join(accounts_dir, d))]
    
    if not accounts:
        print("❌ No accounts found!")
        return
    
    print("\n📋 Available accounts:")
    for i, account in enumerate(accounts, 1):
        print(f"   {i}. {account}")
    
    print(f"   {len(accounts) + 1}. All accounts")
    print("   0. Exit")
    
    # Get user choice
    try:
        choice = input("\nSelect account number: ").strip()
        choice_num = int(choice)
        
        if choice_num == 0:
            print("👋 Exiting...")
            return
        
        # Select category
        print("\n📁 Available categories:")
        categories = [
            "Other Garden decor",
            "Other Rugs & carpets"
        ]
        for i, cat in enumerate(categories, 1):
            print(f"   {i}. {cat}")
        
        cat_choice = input("\nSelect category number (default 1): ").strip()
        cat_num = int(cat_choice) if cat_choice else 1
        
        if cat_num < 1 or cat_num > len(categories):
            print("❌ Invalid category choice!")
            return
        
        selected_category = categories[cat_num - 1]
        
        print("\n" + "=" * 60)
        
        if choice_num == len(accounts) + 1:
            # Update all accounts
            update_all_accounts(selected_category)
        elif choice_num > 0 and choice_num <= len(accounts):
            # Update specific account
            update_listing_categories(accounts[choice_num - 1], selected_category)
        else:
            print("❌ Invalid choice!")
            
    except ValueError:
        print("❌ Invalid input! Please enter a number.")
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        account = sys.argv[1]
        category = sys.argv[2] if len(sys.argv) > 2 else 'Other Garden decor'
        
        print(f"🔄 Updating account '{account}' with category '{category}'")
        update_listing_categories(account, category)
    else:
        # Interactive mode
        interactive_update()

