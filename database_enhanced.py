"""
Enhanced database utilities for professional features:
- Activity logs
- Listing templates
- Analytics tracking
"""

import sqlite3
import json
from datetime import datetime


def init_enhanced_tables(db_path):
    """Initialize all enhanced tables for professional features."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Activity Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action_type TEXT NOT NULL,
            listing_id INTEGER,
            listing_title TEXT,
            status TEXT,
            details TEXT,
            account_name TEXT,
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    # Listing Templates Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listing_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT,
            price_template TEXT,
            description_template TEXT,
            location TEXT,
            product_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            use_count INTEGER DEFAULT 0
        )
    ''')

    # Analytics Table - tracks listing performance over time
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listing_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER,
            listing_title TEXT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            account_name TEXT,
            success BOOLEAN DEFAULT 1,
            error_message TEXT,
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    # Account Stats Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_stats (
            account_name TEXT PRIMARY KEY,
            total_listings INTEGER DEFAULT 0,
            successful_listings INTEGER DEFAULT 0,
            failed_listings INTEGER DEFAULT 0,
            total_deletions INTEGER DEFAULT 0,
            last_activity TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_account ON activity_log(account_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_listing ON listing_analytics(listing_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON listing_analytics(timestamp DESC)')

    conn.commit()
    conn.close()
    print(f"✅ Enhanced database tables initialized: {db_path}")


def log_activity(db_path, action_type, listing_id=None, listing_title=None,
                 status='success', details='', account_name=''):
    """Log an activity to the activity log."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO activity_log
            (action_type, listing_id, listing_title, status, details, account_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action_type, listing_id, listing_title, status, details, account_name))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False


def get_activity_log(db_path, limit=50, account_name=None):
    """Retrieve activity log entries."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if account_name:
            cursor.execute('''
                SELECT id, timestamp, action_type, listing_id, listing_title,
                       status, details, account_name
                FROM activity_log
                WHERE account_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (account_name, limit))
        else:
            cursor.execute('''
                SELECT id, timestamp, action_type, listing_id, listing_title,
                       status, details, account_name
                FROM activity_log
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'timestamp': row[1],
                'action_type': row[2],
                'listing_id': row[3],
                'listing_title': row[4],
                'status': row[5],
                'details': row[6],
                'account_name': row[7]
            })

        conn.close()
        return logs
    except Exception as e:
        print(f"Error retrieving activity log: {e}")
        return []


def save_template(db_path, template_data):
    """Save a listing template."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO listing_templates
            (name, description, category, price_template, description_template,
             location, product_tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            template_data.get('name'),
            template_data.get('description', ''),
            template_data.get('category', ''),
            template_data.get('price_template', ''),
            template_data.get('description_template', ''),
            template_data.get('location', ''),
            template_data.get('product_tags', '')
        ))

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        log_activity(db_path, 'template_created', None, template_data.get('name'),
                    'success', f"Template '{template_data.get('name')}' created")

        return template_id
    except sqlite3.IntegrityError:
        print(f"Template with name '{template_data.get('name')}' already exists")
        return None
    except Exception as e:
        print(f"Error saving template: {e}")
        return None


def get_templates(db_path):
    """Retrieve all listing templates."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, category, price_template,
                   description_template, location, product_tags,
                   created_at, use_count
            FROM listing_templates
            ORDER BY use_count DESC, name ASC
        ''')

        templates = []
        for row in cursor.fetchall():
            templates.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'price_template': row[4],
                'description_template': row[5],
                'location': row[6],
                'product_tags': row[7],
                'created_at': row[8],
                'use_count': row[9]
            })

        conn.close()
        return templates
    except Exception as e:
        print(f"Error retrieving templates: {e}")
        return []


def increment_template_usage(db_path, template_id):
    """Increment the usage counter for a template."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE listing_templates
            SET use_count = use_count + 1, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), template_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error incrementing template usage: {e}")
        return False


def delete_template(db_path, template_id):
    """Delete a listing template."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get template name for logging
        cursor.execute('SELECT name FROM listing_templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        template_name = result[0] if result else 'Unknown'

        cursor.execute('DELETE FROM listing_templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()

        log_activity(db_path, 'template_deleted', None, template_name,
                    'success', f"Template '{template_name}' deleted")

        return True
    except Exception as e:
        print(f"Error deleting template: {e}")
        return False


def track_analytics(db_path, listing_id, listing_title, action, account_name,
                   success=True, error_message=''):
    """Track listing analytics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO listing_analytics
            (listing_id, listing_title, action, account_name, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (listing_id, listing_title, action, account_name, success, error_message))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error tracking analytics: {e}")
        return False


def get_analytics_summary(db_path, account_name=None, days=30):
    """Get analytics summary for dashboard."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Date filter
        date_filter = f"datetime('now', '-{days} days')"

        # Total actions by type
        if account_name:
            cursor.execute(f'''
                SELECT action, COUNT(*), SUM(success), SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END)
                FROM listing_analytics
                WHERE account_name = ? AND timestamp >= {date_filter}
                GROUP BY action
            ''', (account_name,))
        else:
            cursor.execute(f'''
                SELECT action, COUNT(*), SUM(success), SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END)
                FROM listing_analytics
                WHERE timestamp >= {date_filter}
                GROUP BY action
            ''')

        action_stats = {}
        for row in cursor.fetchall():
            action_stats[row[0]] = {
                'total': row[1],
                'successful': row[2],
                'failed': row[3]
            }

        # Daily activity chart data
        if account_name:
            cursor.execute(f'''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM listing_analytics
                WHERE account_name = ? AND timestamp >= {date_filter}
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            ''', (account_name,))
        else:
            cursor.execute(f'''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM listing_analytics
                WHERE timestamp >= {date_filter}
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            ''')

        daily_activity = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

        conn.close()

        return {
            'action_stats': action_stats,
            'daily_activity': daily_activity
        }
    except Exception as e:
        print(f"Error getting analytics summary: {e}")
        return {'action_stats': {}, 'daily_activity': []}


def update_account_stats(db_path, account_name, action='listing', success=True):
    """Update account statistics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if account stats exist
        cursor.execute('SELECT * FROM account_stats WHERE account_name = ?', (account_name,))
        if cursor.fetchone() is None:
            # Create new account stats
            cursor.execute('''
                INSERT INTO account_stats (account_name, last_activity)
                VALUES (?, ?)
            ''', (account_name, datetime.now().isoformat()))

        # Update stats based on action
        if action == 'listing':
            if success:
                cursor.execute('''
                    UPDATE account_stats
                    SET total_listings = total_listings + 1,
                        successful_listings = successful_listings + 1,
                        last_activity = ?
                    WHERE account_name = ?
                ''', (datetime.now().isoformat(), account_name))
            else:
                cursor.execute('''
                    UPDATE account_stats
                    SET total_listings = total_listings + 1,
                        failed_listings = failed_listings + 1,
                        last_activity = ?
                    WHERE account_name = ?
                ''', (datetime.now().isoformat(), account_name))
        elif action == 'deletion':
            cursor.execute('''
                UPDATE account_stats
                SET total_deletions = total_deletions + 1,
                    last_activity = ?
                WHERE account_name = ?
            ''', (datetime.now().isoformat(), account_name))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating account stats: {e}")
        return False


def get_account_stats(db_path, account_name):
    """Get statistics for a specific account."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT total_listings, successful_listings, failed_listings,
                   total_deletions, last_activity, status
            FROM account_stats
            WHERE account_name = ?
        ''', (account_name,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'total_listings': result[0],
                'successful_listings': result[1],
                'failed_listings': result[2],
                'total_deletions': result[3],
                'last_activity': result[4],
                'status': result[5],
                'success_rate': round((result[1] / result[0] * 100) if result[0] > 0 else 0, 1)
            }
        else:
            return {
                'total_listings': 0,
                'successful_listings': 0,
                'failed_listings': 0,
                'total_deletions': 0,
                'last_activity': None,
                'status': 'new',
                'success_rate': 0
            }
    except Exception as e:
        print(f"Error getting account stats: {e}")
        return None
