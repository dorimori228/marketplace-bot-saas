from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import json
import threading
import sqlite3
from datetime import datetime
from bot import MarketplaceBot
from database_enhanced import (
    init_enhanced_tables, log_activity, get_activity_log,
    save_template, get_templates, delete_template, increment_template_usage,
    get_analytics_summary, update_account_stats, get_account_stats,
    track_analytics
)

app = Flask(__name__)

@app.route('/static/logo/<path:filename>')
def serve_logo(filename):
    """Serve logo files."""
    logo_dir = os.path.join(os.getcwd(), 'logo')
    return send_from_directory(logo_dir, filename)

@app.route('/image/<path:filepath>')
def serve_image(filepath):
    """Serve listing images."""
    # Images are stored in accounts/account_name/images/
    # The filepath will be like: accounts/account_name/images/filename.jpg
    try:
        # Get the directory and filename from the full path
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        full_dir = os.path.join(os.getcwd(), directory)
        return send_from_directory(full_dir, filename)
    except Exception as e:
        print(f"Error serving image: {e}")
        return "Image not found", 404

def get_accounts():
    """Get list of account directories."""
    accounts_dir = os.path.join(os.getcwd(), 'accounts')
    if not os.path.exists(accounts_dir):
        return []
    
    accounts = []
    for item in os.listdir(accounts_dir):
        item_path = os.path.join(accounts_dir, item)
        if os.path.isdir(item_path):
            accounts.append(item)
    
    return accounts

def run_bot_process(account_name, listing_data):
    """
    Run the bot process in a separate thread.
    This function handles the complete bot workflow.
    """
    bot = None
    try:
        print(f"Starting bot process for account: {account_name}")
        
        # Construct paths for this account
        account_dir = os.path.join('accounts', account_name)
        
        # Look for cookies file (either .json or .pkl)
        cookies_path = None
        for ext in ['.pkl', '.json']:
            potential_path = os.path.join(account_dir, f'cookies{ext}')
            if os.path.exists(potential_path):
                cookies_path = potential_path
                break
        
        if not cookies_path:
            cookies_path = os.path.join(account_dir, 'cookies.json')  # Default fallback
        
        db_path = os.path.join(account_dir, 'listings.db')
        
        # Ensure account directory exists
        os.makedirs(account_dir, exist_ok=True)
        
        # Initialize the bot
        delay_factor = float(listing_data.get('speed', 1.0))
        proxy = listing_data.get('proxy')
        bot = MarketplaceBot(cookies_path, delay_factor, proxy=proxy)
        
        # Delete existing listing if it exists
        if listing_data.get('title'):
            # Use original_title if available, otherwise use current title
            search_title = listing_data.get('original_title', listing_data['title'])
            delete_success = bot.delete_listing_if_exists(search_title)
            if delete_success:
                print(f"✅ Successfully deleted existing listing: {search_title}")
            elif getattr(bot, 'last_delete_found', False):
                print(f"⚠️ Listing was found but delete failed: {search_title}")
            else:
                print(f"ℹ️ No existing listing found to delete: {search_title}")
            print("📝 Continuing with listing creation...")

        # Create new listing and get the result with new title/description
        result = bot.create_new_listing(listing_data)

        # Update database with new title if listing was successful
        if result and result.get('success'):
            print(f"✅ Listing created with new title: {result['new_title']}")
            # Update the database entry with new title and description
            # Find by original title and update to new title to avoid duplicates
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Find the listing by original title
                original_title = result.get('original_title', listing_data['title'])
                cursor.execute('SELECT id FROM listings WHERE title = ?', (original_title,))
                existing = cursor.fetchone()

                if existing:
                    # Update the existing listing with the new title
                    listing_id = existing[0]
                    cursor.execute('''
                        UPDATE listings
                        SET title = ?,
                            description = ?,
                            updated_at = CURRENT_TIMESTAMP,
                            status = 'active'
                        WHERE id = ?
                    ''', (result['new_title'], result['new_description'], listing_id))
                    print(f"✅ Database updated: '{original_title}' → '{result['new_title']}'")
                else:
                    print(f"⚠️ Original listing not found in database: {original_title}")

                conn.commit()
                conn.close()
            except Exception as db_error:
                print(f"⚠️ Failed to update database: {db_error}")

        print(f"Bot process completed successfully for account: {account_name}")
        
    except Exception as e:
        print(f"Error in bot process for account {account_name}: {e}")
    finally:
        if bot:
            bot.close()

def run_multiple_bot_process(account_name, listings_data):
    """Run the bot process for multiple listings in a single session."""
    bot = None
    try:
        print(f"🤖 Starting multiple bot process for account: {account_name}")
        print(f"📋 Processing {len(listings_data)} listings...")
        
        # Construct paths
        account_dir = os.path.join('accounts', account_name)
        
        # Find cookies file (try both .pkl and .json)
        cookies_path = None
        for ext in ['.pkl', '.json']:
            potential_path = os.path.join(account_dir, f'cookies{ext}')
            if os.path.exists(potential_path):
                cookies_path = potential_path
                break
        
        if not cookies_path:
            cookies_path = os.path.join(account_dir, 'cookies.json')  # Default fallback
        
        db_path = os.path.join(account_dir, 'listings.db')
        
        # Ensure account directory exists
        os.makedirs(account_dir, exist_ok=True)
        
        # Initialize the bot once for all listings
        delay_factor = float(listings_data[0].get('speed', 1.0))
        proxy = listings_data[0].get('proxy')
        bot = MarketplaceBot(cookies_path, delay_factor, proxy=proxy)
        
        # Process each listing sequentially
        successful_listings = 0
        failed_listings = 0
        
        for i, listing_data in enumerate(listings_data, 1):
            try:
                print(f"\n🔄 Processing listing {i}/{len(listings_data)}: {listing_data['title']}")
                
                # Delete existing listing if it exists
                if listing_data.get('title'):
                    # Use original_title if available, otherwise use current title
                    search_title = listing_data.get('original_title', listing_data['title'])
                    print(f"🗑️ Attempting to delete existing listing: {search_title}")
                    delete_success = bot.delete_listing_if_exists(search_title)
                    if delete_success:
                        print(f"✅ Successfully deleted existing listing: {search_title}")
                    elif getattr(bot, 'last_delete_found', False):
                        print(f"⚠️ Listing was found but delete failed: {search_title}")
                    else:
                        print(f"ℹ️ No existing listing found to delete: {search_title}")
                    print("📝 Continuing with listing creation...")
                
                # Create new listing
                print(f"📝 Creating new listing: {listing_data['title']}")
                result = bot.create_new_listing(listing_data)

                if result and result.get('success'):
                    # Update database with new title/description
                    listing_data['title'] = result['new_title']
                    listing_data['description'] = result['new_description']
                    listing_data['original_title'] = result['original_title']

                    # Update existing listing status instead of creating new entry
                    update_listing_status(db_path, listing_data)
                    successful_listings += 1
                    print(f"✅ Listing {i}/{len(listings_data)} completed successfully")
                    print(f"   New title: {result['new_title']}")
                else:
                    failed_listings += 1
                    print(f"❌ Listing {i}/{len(listings_data)} failed to create")
                
                # Add a small delay between listings to avoid rate limiting
                if i < len(listings_data):
                    print("⏳ Waiting 3 seconds before next listing...")
                    import time
                    time.sleep(3)
                    
            except Exception as e:
                failed_listings += 1
                print(f"❌ Error processing listing {i} ({listing_data.get('title', 'Unknown')}): {str(e)}")
                # Continue with next listing instead of stopping
                continue
        
        print(f"\n🎉 Batch processing completed for account: {account_name}")
        print(f"📊 Results: {successful_listings} successful, {failed_listings} failed out of {len(listings_data)} total")
        
    except Exception as e:
        print(f"❌ Error in multiple bot process for account {account_name}: {str(e)}")
    finally:
        try:
            if bot:
                bot.close()
                print("🔒 Browser closed successfully")
        except:
            pass

def run_delete_only_process(account_name, listings_data):
    """Run the bot process to delete listings without re-uploading."""
    bot = None
    try:
        print(f"🗑️ Starting delete-only process for account: {account_name}")
        print(f"📋 Deleting {len(listings_data)} listings...")

        # Construct paths
        account_dir = os.path.join('accounts', account_name)

        # Find cookies file (try both .pkl and .json)
        cookies_path = None
        for ext in ['.pkl', '.json']:
            potential_path = os.path.join(account_dir, f'cookies{ext}')
            if os.path.exists(potential_path):
                cookies_path = potential_path
                break

        if not cookies_path:
            cookies_path = os.path.join(account_dir, 'cookies.json')  # Default fallback

        db_path = os.path.join(account_dir, 'listings.db')

        # Ensure account directory exists
        os.makedirs(account_dir, exist_ok=True)

        # Initialize the bot once for all listings
        delay_factor = 1.0  # Use normal speed for deletion
        proxy = listings_data[0].get('proxy') if listings_data else None
        bot = MarketplaceBot(cookies_path, delay_factor, proxy=proxy)

        # Process each listing sequentially
        successful_deletions = 0
        failed_deletions = 0

        for i, listing_data in enumerate(listings_data, 1):
            try:
                title = listing_data.get('title', '')
                listing_id = listing_data.get('listing_id')

                print(f"\n🗑️ Deleting listing {i}/{len(listings_data)}: {title}")

                # Delete the listing
                delete_success = bot.delete_listing_if_exists(title)

                if delete_success:
                    successful_deletions += 1
                    print(f"✅ Listing {i}/{len(listings_data)} deleted successfully")

                    # Update database to mark as deleted
                    if listing_id:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE listings
                            SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (listing_id,))
                        conn.commit()
                        conn.close()
                        print(f"   Database updated: marked as deleted")
                else:
                    failed_deletions += 1
                    print(f"⚠️ Listing {i}/{len(listings_data)} not found or failed to delete")

                # Add a small delay between deletions to avoid rate limiting
                if i < len(listings_data):
                    print("⏳ Waiting 2 seconds before next deletion...")
                    import time
                    time.sleep(2)

            except Exception as e:
                failed_deletions += 1
                print(f"❌ Error deleting listing {i} ({listing_data.get('title', 'Unknown')}): {str(e)}")
                # Continue with next listing instead of stopping
                continue

        print(f"\n🎉 Batch deletion completed for account: {account_name}")
        print(f"📊 Results: {successful_deletions} deleted, {failed_deletions} failed out of {len(listings_data)} total")

    except Exception as e:
        print(f"❌ Error in delete-only process for account {account_name}: {str(e)}")
    finally:
        try:
            if bot:
                bot.close()
                print("🔒 Browser closed successfully")
        except:
            pass

def save_listing_to_db(db_path, listing_data):
    """
    Save the listing data to the account's SQLite database.
    If a listing with the same title already exists, update it instead of creating a duplicate.

    Args:
        db_path (str): Path to the SQLite database file
        listing_data (dict): Dictionary containing listing information
    """
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

        # Check if a listing with this title already exists
        cursor.execute('SELECT id FROM listings WHERE title = ?', (listing_data['title'],))
        existing = cursor.fetchone()

        if existing:
            # Update existing listing
            listing_id = existing[0]
            cursor.execute('''
                UPDATE listings
                SET price = ?,
                    description = ?,
                    category = ?,
                    product_tags = ?,
                    location = ?,
                    image_paths = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    status = 'active'
                WHERE id = ?
            ''', (
                listing_data['price'],
                listing_data['description'],
                listing_data.get('category', 'Other Garden decor'),
                listing_data.get('product_tags', ''),
                listing_data.get('location', ''),
                '|'.join(listing_data.get('image_paths', [])),
                listing_id
            ))
            print(f"✅ Updated existing listing in database (ID: {listing_id})")
        else:
            # Insert the new listing
            cursor.execute('''
                INSERT INTO listings (title, price, description, category, product_tags, location, image_paths, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing_data['title'],
                listing_data['price'],
                listing_data['description'],
                listing_data.get('category', 'Other Garden decor'),
                listing_data.get('product_tags', ''),
                listing_data.get('location', ''),
                '|'.join(listing_data.get('image_paths', [])),
                'active'
            ))
            listing_id = cursor.lastrowid
            print(f"✅ Created new listing in database (ID: {listing_id})")

        conn.commit()
        conn.close()

        return listing_id

    except Exception as e:
        print(f"Error saving to database: {e}")

def update_listing_status(db_path, listing_data):
    """
    Update the status of an existing listing instead of creating a new one.
    
    Args:
        db_path (str): Path to the SQLite database file
        listing_data (dict): Dictionary containing listing information
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find the existing listing by title and update its status
        cursor.execute('''
            UPDATE listings 
            SET status = 'relisted', 
                updated_at = CURRENT_TIMESTAMP,
                title = ?,
                description = ?,
                location = ?
            WHERE title = ? AND status = 'active'
        ''', (
            listing_data['title'],
            listing_data['description'],
            listing_data.get('location', ''),
            listing_data.get('original_title', listing_data['title'])  # Use original title to find the listing
        ))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            print(f"Updated listing status to 'relisted': {listing_data['title']}")
        else:
            print(f"No active listing found to update for: {listing_data['title']}")
            # If no existing listing found, create a new one
            save_listing_to_db(db_path, listing_data)
        
    except Exception as e:
        print(f"Error updating listing status: {e}")
        # Fallback to creating new entry
        save_listing_to_db(db_path, listing_data)

@app.route('/')
def index():
    """Render the main page with account selection."""
    accounts = get_accounts()
    return render_template('index.html', accounts=accounts)

def _handle_listing_request(action_override=None):
    """Handle listing save/create requests from the UI."""
    try:
        # Get form data
        account = request.form.get('account')
        title = request.form.get('title')
        price = request.form.get('price')
        description = request.form.get('description')
        category = request.form.get('category', 'Other Garden decor')
        product_tags = request.form.get('product_tags', '')
        location = request.form.get('location', '')
        speed = request.form.get('speed', '1.0')
        proxy = request.form.get('proxy', '').strip() or None
        ai_enabled_raw = request.form.get('ai_enabled', 'true')
        ai_enabled = str(ai_enabled_raw).strip().lower() in ['true', '1', 'yes', 'on']

        # Debug: Print received form data
        print("Received form data:")
        print(f"  Account: {account}")
        print(f"  Title: {title}")
        print(f"  Price: {price}")
        print(f"  Description: {description[:50]}..." if description else "  Description: None")
        print(f"  Category: {category}")
        print(f"  Product Tags: {product_tags}")
        print(f"  Location: {location}")
        print(f"  Speed: {speed}")
        print(f"  Proxy: {proxy}")
        print(f"  AI Enabled: {ai_enabled}")

        # Validate required fields
        missing_fields = []
        if not account:
            missing_fields.append('Account')
        if not title:
            missing_fields.append('Title')
        if not price:
            missing_fields.append('Price')
        if not description:
            missing_fields.append('Description')
        if not location:
            missing_fields.append('Location')

        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Handle file uploads
        uploaded_files = request.files.getlist('photos')
        if not uploaded_files or uploaded_files[0].filename == '':
            return jsonify({
                'success': False,
                'message': 'At least one photo is required'
            }), 400

        # Create organized listing folder structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]

        listing_dir = os.path.join('accounts', account, 'listings', f"{timestamp}_{safe_title}")
        os.makedirs(listing_dir, exist_ok=True)

        # Save uploaded photos with proper naming
        image_paths = []
        for i, file in enumerate(uploaded_files):
            if file and file.filename:
                # Get file extension
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    continue

                # Save image with organized naming
                image_filename = f"image_{i+1:02d}{file_ext}"
                image_path = os.path.join(listing_dir, image_filename)
                file.save(image_path)
                image_paths.append(os.path.abspath(image_path))
                print(f"Saved image: {image_path}")

        # Create listing data text file
        data_file_path = os.path.join(listing_dir, 'listing_data.txt')
        with open(data_file_path, 'w', encoding='utf-8') as f:
            f.write("LISTING DATA\n")
            f.write("============\n\n")
            f.write(f"Title: {title}\n")
            f.write(f"Price: {price}\n")
            f.write(f"Category: {category}\n")
            f.write(f"Product Tags: {product_tags}\n")
            f.write(f"Location: {location}\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Description:\n")
            f.write(f"{description}\n\n")
            f.write(f"Images ({len(image_paths)}):\n")
            for i, path in enumerate(image_paths, 1):
                f.write(f"  {i}. {os.path.basename(path)}\n")

        print(f"Saved listing data to: {data_file_path}")

        # Bundle listing data
        listing_data = {
            'title': title,
            'price': price,
            'description': description,
            'category': category,
            'product_tags': product_tags,
            'location': location,
            'image_paths': image_paths,
            'speed': speed,
            'account': account,
            'listing_id': None,
            'ai_enabled': ai_enabled,
            'proxy': proxy
        }

        # Save to database immediately
        db_path = os.path.join('accounts', account, 'listings.db')
        listing_id = save_listing_to_db(db_path, listing_data)
        listing_data['listing_id'] = listing_id

        # Check action parameter
        action = action_override or request.form.get('action', 'start_bot')

        if action == 'save_only':
            return jsonify({
                'success': True,
                'message': 'Listing saved successfully! Click "Start Bot & Create" to begin posting to Facebook.'
            })

        # Start bot in a separate thread
        bot_thread = threading.Thread(
            target=run_bot_process,
            args=(account, listing_data)
        )
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({
            'success': True,
            'message': f'Listing created and saved! Bot started for account "{account}". Check console for progress updates.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting bot: {str(e)}'
        }), 500


@app.route('/start_bot', methods=['POST'])
def start_bot():
    """Handle the bot start request."""
    return _handle_listing_request()


@app.route('/save_listing', methods=['POST'])
def save_listing():
    """Save listing without starting the bot."""
    return _handle_listing_request(action_override='save_only')


@app.route('/create_listing', methods=['POST'])
def create_listing():
    """Save listing and start the bot."""
    return _handle_listing_request(action_override='start_bot')

@app.route('/accounts')
def list_accounts():
    """API endpoint to get list of accounts."""
    accounts = get_accounts()
    return jsonify({'accounts': accounts})

@app.route('/add_account', methods=['POST'])
def add_account():
    """Add a new account with cookies from JSON string."""
    try:
        data = request.get_json()
        account_name = data.get('account_name', '').strip()
        cookies_json = data.get('cookies_json', '').strip()

        if not account_name:
            return jsonify({
                'success': False,
                'message': 'Account name is required'
            }), 400

        if not cookies_json:
            return jsonify({
                'success': False,
                'message': 'Cookies JSON is required'
            }), 400

        # Parse the cookies JSON string
        try:
            cookies = json.loads(cookies_json)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'message': f'Invalid JSON format: {str(e)}'
            }), 400

        if not isinstance(cookies, list):
            return jsonify({
                'success': False,
                'message': 'Cookies must be an array'
            }), 400

        # Call the existing add_account_cookies logic
        return add_account_cookies_logic(account_name, cookies)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding account: {str(e)}'
        }), 500

@app.route('/add_account_cookies', methods=['POST'])
def add_account_cookies():
    """Add a new account with cookies."""
    try:
        data = request.get_json()
        account_name = data.get('account_name', '').strip()
        cookies = data.get('cookies', [])
        
        if not account_name:
            return jsonify({
                'success': False,
                'message': 'Account name is required'
            }), 400
        
        if not cookies or not isinstance(cookies, list):
            return jsonify({
                'success': False,
                'message': 'Cookies must be a non-empty array'
            }), 400

        # Call the shared logic
        return add_account_cookies_logic(account_name, cookies)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding account: {str(e)}'
        }), 500

def add_account_cookies_logic(account_name, cookies):
    """Shared logic for adding an account with cookies."""
    try:
        # Create account directory
        account_dir = os.path.join('accounts', account_name)
        
        # Check if account already exists
        if os.path.exists(account_dir):
            return jsonify({
                'success': False,
                'message': f'Account "{account_name}" already exists'
            }), 400
        
        # Create account directory
        os.makedirs(account_dir, exist_ok=True)
        
        # Save cookies to cookies.json
        cookies_path = os.path.join(account_dir, 'cookies.json')
        
        # Convert cookies to format expected by the bot
        # The bot expects cookies in a specific format, so we'll save them as-is
        # but ensure they have the required fields
        formatted_cookies = []
        for cookie in cookies:
            # Ensure required fields exist
            formatted_cookie = {
                'name': cookie.get('name', ''),
                'value': cookie.get('value', ''),
                'domain': cookie.get('domain', '.facebook.com'),
                'path': cookie.get('path', '/'),
            }
            
            # Add optional fields if they exist
            # Selenium expects 'expiry' (not 'expires')
            if 'expiry' in cookie:
                formatted_cookie['expiry'] = int(cookie['expiry'])
            elif 'expires' in cookie:
                formatted_cookie['expiry'] = int(cookie['expires'])
            elif 'expirationDate' in cookie:
                # Convert expirationDate (Unix timestamp) to expiry
                exp_date = cookie.get('expirationDate')
                if exp_date and exp_date > 0:
                    formatted_cookie['expiry'] = int(exp_date)
                # If no expiry, don't add it (session cookie)
            # else: no expiry field = session cookie
            
            if 'httpOnly' in cookie:
                formatted_cookie['httpOnly'] = cookie['httpOnly']
            else:
                formatted_cookie['httpOnly'] = False
            
            if 'secure' in cookie:
                formatted_cookie['secure'] = cookie['secure']
            else:
                formatted_cookie['secure'] = True
            
            # Convert sameSite to Selenium-compatible values
            # Selenium expects: "Strict", "Lax", or "None" (capitalized)
            if 'sameSite' in cookie:
                same_site = cookie['sameSite']
                # Convert common variations to Selenium format
                if same_site in ['no_restriction', 'None', 'none']:
                    formatted_cookie['sameSite'] = 'None'
                elif same_site in ['Lax', 'lax']:
                    formatted_cookie['sameSite'] = 'Lax'
                elif same_site in ['Strict', 'strict']:
                    formatted_cookie['sameSite'] = 'Strict'
                elif same_site in ['unspecified', 'Unspecified']:
                    # Default unspecified to Lax (common for session cookies)
                    formatted_cookie['sameSite'] = 'Lax'
                else:
                    # Unknown value, default to None
                    formatted_cookie['sameSite'] = 'None'
            else:
                formatted_cookie['sameSite'] = 'None'
            
            formatted_cookies.append(formatted_cookie)
        
        # Save cookies to file
        import json
        with open(cookies_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_cookies, f, indent=2, ensure_ascii=False)
        
        # Initialize database for the account
        db_path = os.path.join(account_dir, 'listings.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Account "{account_name}" created successfully with {len(formatted_cookies)} cookies!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in account creation: {str(e)}'
        }), 500

@app.route('/get_updated_content/<account>/<listing_title>')
def get_updated_content(account, listing_title):
    """Get updated title and description for a listing."""
    try:
        from original_content_manager import OriginalContentManager
        content_manager = OriginalContentManager()
        
        # Get original listing
        original_listing = content_manager.get_original_listing(account, listing_title)
        
        if not original_listing:
            return jsonify({
                'success': False,
                'message': 'Original listing not found'
            })
        
        # Generate new variations
        from title_variator import TitleVariator
        from description_variator import DescriptionVariator
        
        title_variator = TitleVariator()
        description_variator = DescriptionVariator()
        
        # Generate title variation
        title_result = title_variator.get_next_title_variation(account, original_listing['title'])
        description_result = description_variator.get_next_description_variation(account, original_listing['description'])
        
        return jsonify({
            'success': True,
            'original_title': original_listing['title'],
            'new_title': title_result['variation'] if title_result['success'] else original_listing['title'],
            'original_description': original_listing['description'],
            'new_description': description_result['variation'] if description_result['success'] else original_listing['description'],
            'title_variation_type': title_result.get('type', 'none'),
            'description_variation_type': description_result.get('type', 'none')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting updated content: {str(e)}'
        })

@app.route('/randomize_locations', methods=['POST'])
def randomize_locations():
    """Randomize locations for selected listings."""
    try:
        data = request.get_json()
        account = data.get('account')
        listing_ids = data.get('listing_ids', [])
        
        print(f"DEBUG: Received randomize_locations request")
        print(f"  Account: {account}")
        print(f"  Listing IDs: {listing_ids}")
        
        if not account or not listing_ids:
            return jsonify({
                'success': False,
                'message': 'Account and listing IDs are required'
            })
        
        # Get listings from the regular database (not original_content_manager)
        db_path = os.path.join('accounts', account, 'listings.db')
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'message': f'No database found for account: {account}'
            })
        
        # Connect to database and get listings
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all listings
        cursor.execute('SELECT id, title, price, description, category, location, status FROM listings WHERE status = "active"')
        all_listings = cursor.fetchall()
        conn.close()
        
        print(f"DEBUG: Found {len(all_listings)} listings in database")
        
        # Filter selected listings by ID
        selected_listings = []
        for listing in all_listings:
            listing_id, title, price, description, category, location, status = listing
            if str(listing_id) in [str(id) for id in listing_ids]:
                selected_listings.append({
                    'id': listing_id,
                    'title': title,
                    'price': price,
                    'description': description,
                    'category': category,
                    'location': location,
                    'status': status
                })
        
        print(f"DEBUG: Found {len(selected_listings)} selected listings")
        
        if not selected_listings:
            return jsonify({
                'success': False,
                'message': 'No selected listings found in database'
            })
        
        # Generate random locations for each listing (ensuring no duplicates)
        from image_metadata import ImageMetadataModifier
        metadata_modifier = ImageMetadataModifier()

        randomized_locations = []
        used_locations = set()  # Track used location names to avoid duplicates

        for listing in selected_listings:
            # Generate a random UK location, retry if duplicate
            max_attempts = 50  # Prevent infinite loop
            attempts = 0
            random_location = None

            while attempts < max_attempts:
                temp_location = metadata_modifier.generate_random_uk_location()
                if temp_location['name'] not in used_locations:
                    random_location = temp_location
                    used_locations.add(random_location['name'])
                    break
                attempts += 1

            # If we couldn't find a unique location after max attempts, use the last one anyway
            if random_location is None:
                random_location = metadata_modifier.generate_random_uk_location()

            randomized_locations.append({
                'listing_id': listing['id'],
                'title': listing['title'],
                'new_location': random_location['name'],
                'coordinates': f"{random_location['lat']:.4f}, {random_location['lon']:.4f}"
            })
        
        print(f"DEBUG: Generated {len(randomized_locations)} random locations")
        
        # Store the randomized locations for the bot to use
        from location_manager import LocationManager
        location_manager = LocationManager()
        storage_result = location_manager.store_randomized_locations(account, randomized_locations)
        
        if storage_result['success']:
            print(f"✅ Stored randomized locations: {storage_result['message']}")
        else:
            print(f"⚠️ Failed to store locations: {storage_result['error']}")
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(randomized_locations)} random locations',
            'locations': randomized_locations
        })
        
    except Exception as e:
        print(f"DEBUG: Error in randomize_locations: {e}")
        return jsonify({
            'success': False,
            'message': f'Error randomizing locations: {str(e)}'
        })

@app.route('/account/<account_name>/listings')
def get_listings(account_name):
    """Get listings for a specific account."""
    try:
        print(f"📋 Getting listings for account: {account_name}")
        db_path = os.path.join('accounts', account_name, 'listings.db')
        print(f"📁 Database path: {db_path}")
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            return jsonify({'listings': []})
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, check what columns actually exist in the database
        cursor.execute("PRAGMA table_info(listings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Build the SELECT query based on available columns
        base_columns = ['id', 'title', 'price', 'description', 'image_paths', 'created_at', 'status']
        select_columns = []
        
        for col in base_columns:
            if col in columns:
                select_columns.append(col)
        
        # Add optional columns if they exist
        optional_columns = ['category', 'product_tags', 'location', 'notes']
        for col in optional_columns:
            if col in columns:
                select_columns.append(col)
        
        # Execute query with available columns
        query = f'''
            SELECT {', '.join(select_columns)}
            FROM listings
            WHERE status != 'deleted' OR status IS NULL
            ORDER BY created_at DESC
        '''
        
        cursor.execute(query)
        listings = []
        
        for row in cursor.fetchall():
            listing = {}
            
            # Map the row data to the listing dict
            for i, col in enumerate(select_columns):
                if col == 'image_paths':
                    # Keep as string with | separator for frontend to split
                    listing[col] = row[i] if row[i] else ''
                elif col == 'category':
                    listing[col] = row[i] if row[i] else 'Other Garden decor'  # Default category
                elif col in ['product_tags', 'location', 'notes']:
                    listing[col] = row[i] if row[i] else ''
                else:
                    listing[col] = row[i]
            
            # Ensure all expected fields exist with defaults
            if 'category' not in listing:
                listing['category'] = 'Other Garden decor'
            if 'product_tags' not in listing:
                listing['product_tags'] = ''
            if 'location' not in listing:
                listing['location'] = ''
            if 'notes' not in listing:
                listing['notes'] = ''
            
            listings.append(listing)

        conn.close()
        print(f"✅ Returning {len(listings)} listings for {account_name}")
        return jsonify({'listings': listings})

    except Exception as e:
        print(f"❌ Error getting listings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/relist_listings', methods=['POST'])
def relist_listings():
    """Relist selected listings."""
    try:
        data = request.get_json()
        account_name = data.get('account')
        listing_ids = data.get('listing_ids', [])
        
        if not account_name or not listing_ids:
            return jsonify({'success': False, 'message': 'Account and listing IDs are required'}), 400
        
        db_path = os.path.join('accounts', account_name, 'listings.db')
        if not os.path.exists(db_path):
            return jsonify({'error': 'Database not found'}), 404
        
        # Get listings to relist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in listing_ids])
        cursor.execute(f'''
            SELECT id, title, price, description, category, product_tags, location, image_paths
            FROM listings 
            WHERE id IN ({placeholders}) AND (status = 'active' OR status = 'relisted' OR status IS NULL)
        ''', listing_ids)
        
        listings_to_relist = cursor.fetchall()
        conn.close()
        
        if not listings_to_relist:
            return jsonify({'success': False, 'message': 'No active listings found to relist'}), 400
        
        # Prepare all listings data
        all_listings_data = []
        for listing in listings_to_relist:
            # listing[1] is the CURRENT title in database (which is what's on Facebook)
            # We use this as original_title so the bot can find and delete the existing listing
            listing_data = {
                'title': listing[1],  # Keep same title (or this could be varied)
                'price': listing[2],
                'description': listing[3],  # Keep same description (or this could be varied)
                'category': listing[4] or 'Other Garden decor',
                'product_tags': listing[5] or '',
                'location': listing[6] or '',
                'image_paths': listing[7].split('|') if listing[7] else [],
                'speed': '1.0',
                'account': account_name,
                'listing_id': listing[0],  # Include the database ID
                'original_title': listing[1]  # Use current title to find the listing on Facebook
            }
            all_listings_data.append(listing_data)
        
        # Process all listings in a single bot session to avoid multiple windows
        bot_thread = threading.Thread(
            target=run_multiple_bot_process,
            args=(account_name, all_listings_data)
        )
        bot_thread.daemon = True
        bot_thread.start()
        
        return jsonify({
            'success': True, 
            'message': f'Started relisting {len(listings_to_relist)} listing(s) in sequence. Check console for progress updates.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting relist process: {str(e)}'}), 500

@app.route('/delete_listings', methods=['POST'])
def delete_listings():
    """Delete selected listings without re-uploading."""
    try:
        data = request.get_json()
        account_name = data.get('account')
        listing_ids = data.get('listing_ids', [])

        if not account_name or not listing_ids:
            return jsonify({'success': False, 'message': 'Account and listing IDs are required'}), 400

        db_path = os.path.join('accounts', account_name, 'listings.db')
        if not os.path.exists(db_path):
            return jsonify({'error': 'Database not found'}), 404

        # Get listings to delete
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        placeholders = ','.join(['?' for _ in listing_ids])
        cursor.execute(f'''
            SELECT id, title
            FROM listings
            WHERE id IN ({placeholders}) AND (status = 'active' OR status = 'relisted' OR status IS NULL)
        ''', listing_ids)

        listings_to_delete = cursor.fetchall()
        conn.close()

        if not listings_to_delete:
            return jsonify({'success': False, 'message': 'No active listings found to delete'}), 400

        # Prepare listings data for deletion
        all_listings_data = []
        for listing in listings_to_delete:
            listing_data = {
                'listing_id': listing[0],
                'title': listing[1]
            }
            all_listings_data.append(listing_data)

        # Process all deletions in a single bot session
        bot_thread = threading.Thread(
            target=run_delete_only_process,
            args=(account_name, all_listings_data)
        )
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({
            'success': True,
            'message': f'Started deleting {len(listings_to_delete)} listing(s) in sequence. Check console for progress updates.'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting delete process: {str(e)}'}), 500

@app.route('/account/<account_name>/check_title', methods=['POST'])
def check_title_exists(account_name):
    """Check if a title already exists for the account."""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({'exists': False, 'message': ''})
        
        db_path = os.path.join('accounts', account_name, 'listings.db')
        
        if not os.path.exists(db_path):
            return jsonify({'exists': False, 'message': ''})
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for exact title match (case-insensitive)
        cursor.execute('''
            SELECT id, title, status, created_at
            FROM listings 
            WHERE LOWER(title) = LOWER(?) AND (status != 'deleted' OR status IS NULL)
        ''', (title,))
        
        existing_listing = cursor.fetchone()
        conn.close()
        
        if existing_listing:
            listing_id, existing_title, status, created_at = existing_listing
            return jsonify({
                'exists': True,
                'message': f'⚠️ Title "{existing_title}" already exists (ID: {listing_id}, Status: {status}, Created: {created_at})'
            })
        else:
            return jsonify({'exists': False, 'message': ''})
            
    except Exception as e:
        return jsonify({'exists': False, 'message': f'Error checking title: {str(e)}'}), 500

@app.route('/account/<account_name>/listings/<int:listing_id>/delete', methods=['POST'])
def delete_listing(account_name, listing_id):
    """Delete a listing from the database."""
    try:
        db_path = os.path.join('accounts', account_name, 'listings.db')
        
        if not os.path.exists(db_path):
            return jsonify({'success': False, 'message': 'Account database not found'}), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Actually delete the listing from the database
        cursor.execute('''
            DELETE FROM listings 
            WHERE id = ?
        ''', (listing_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Listing not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Listing deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting listing: {str(e)}'}), 500

@app.route('/account/<account_name>/update_categories', methods=['POST'])
def update_categories(account_name):
    """Update categories for listings without one assigned."""
    try:
        data = request.get_json()
        default_category = data.get('default_category', 'Other Garden decor')
        
        db_path = os.path.join('accounts', account_name, 'listings.db')
        
        if not os.path.exists(db_path):
            return jsonify({'success': False, 'message': 'Account database not found'}), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count listings without categories
        cursor.execute('''
            SELECT COUNT(*) FROM listings 
            WHERE category IS NULL OR category = ''
        ''')
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            conn.close()
            return jsonify({
                'success': True, 
                'message': 'All listings already have categories assigned!',
                'updated': 0
            })
        
        # Update listings without categories
        cursor.execute('''
            UPDATE listings 
            SET category = ? 
            WHERE category IS NULL OR category = ''
        ''', (default_category,))
        
        conn.commit()
        updated = cursor.rowcount
        
        # Get category distribution
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM listings 
            GROUP BY category
        ''')
        
        category_stats = {}
        for row in cursor.fetchall():
            category_stats[row[0] or 'Uncategorized'] = row[1]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully updated {updated} listing(s) to category: {default_category}',
            'updated': updated,
            'category_stats': category_stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating categories: {str(e)}'}), 500

@app.route('/account/<account_name>/ai_analyze', methods=['POST'])
def ai_analyze_account(account_name):
    """Analyze account listings using AI learning system."""
    try:
        from ai_learning_system import AILearningSystem
        
        ai_system = AILearningSystem()
        result = ai_system.analyze_account_listings(account_name)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'AI analysis completed for account: {account_name}',
                'analysis': result['analysis']
            })
        else:
            return jsonify({
                'success': False,
                'message': f'AI analysis failed: {result.get("error", "Unknown error")}'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error in AI analysis: {str(e)}'}), 500

@app.route('/account/<account_name>/ai_insights')
def get_ai_insights(account_name):
    """Get AI learning insights for an account."""
    try:
        from ai_learning_system import AILearningSystem
        
        ai_system = AILearningSystem()
        insights = ai_system.get_learning_insights(account_name)
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting AI insights: {str(e)}'}), 500

@app.route('/ai_global_insights')
def get_global_ai_insights():
    """Get global AI learning insights."""
    try:
        from ai_learning_system import AILearningSystem
        
        ai_system = AILearningSystem()
        insights = ai_system.get_learning_insights()
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting global AI insights: {str(e)}'}), 500

@app.route('/accounts/<path:image_path>')
def serve_listing_image(image_path):
    """Serve listing images."""
    try:
        # Normalize the path - convert all slashes to forward slashes
        normalized_path = image_path.replace('\\', '/')
        
        # Construct the full path to the image
        full_path = os.path.join('accounts', normalized_path)
        
        # Security check - ensure the path is within accounts directory
        if not os.path.exists(full_path) or not full_path.replace('\\', '/').startswith('accounts/'):
            return "Image not found", 404
        
        # Check if it's an image file
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(full_path.lower().endswith(ext) for ext in allowed_extensions):
            return "Invalid file type", 400
        
        return send_file(full_path)
    except Exception as e:
        return f"Error serving image: {str(e)}", 500

# ============================================================================
# PROFESSIONAL FEATURES ROUTES
# ============================================================================

@app.route('/templates', methods=['GET'])
def get_all_templates():
    """Get all listing templates."""
    try:
        # Get any account to access database (templates are global)
        accounts = get_accounts()
        if not accounts:
            return jsonify({'success': True, 'templates': []})

        account_dir = os.path.join('accounts', accounts[0])
        db_path = os.path.join(account_dir, 'listings.db')

        # Initialize enhanced tables if needed
        init_enhanced_tables(db_path)

        templates = get_templates(db_path)
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/templates/save', methods=['POST'])
def save_new_template():
    """Save a new listing template."""
    try:
        template_data = request.json

        # Get any account to access database
        accounts = get_accounts()
        if not accounts:
            return jsonify({'success': False, 'message': 'No accounts found'}), 400

        account_dir = os.path.join('accounts', accounts[0])
        db_path = os.path.join(account_dir, 'listings.db')

        # Initialize enhanced tables if needed
        init_enhanced_tables(db_path)

        template_id = save_template(db_path, template_data)

        if template_id:
            return jsonify({'success': True, 'message': 'Template saved successfully', 'template_id': template_id})
        else:
            return jsonify({'success': False, 'message': 'Template with this name already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/templates/<int:template_id>/delete', methods=['POST'])
def remove_template(template_id):
    """Delete a listing template."""
    try:
        # Get any account to access database
        accounts = get_accounts()
        if not accounts:
            return jsonify({'success': False, 'message': 'No accounts found'}), 400

        account_dir = os.path.join('accounts', accounts[0])
        db_path = os.path.join(account_dir, 'listings.db')

        success = delete_template(db_path, template_id)

        if success:
            return jsonify({'success': True, 'message': 'Template deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete template'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/templates/<int:template_id>/apply', methods=['POST'])
def apply_template(template_id):
    """Apply a template and increment usage counter."""
    try:
        # Get any account to access database
        accounts = get_accounts()
        if not accounts:
            return jsonify({'success': False, 'message': 'No accounts found'}), 400

        account_dir = os.path.join('accounts', accounts[0])
        db_path = os.path.join(account_dir, 'listings.db')

        # Get template data
        templates = get_templates(db_path)
        template = next((t for t in templates if t['id'] == template_id), None)

        if not template:
            return jsonify({'success': False, 'message': 'Template not found'}), 404

        # Increment usage counter
        increment_template_usage(db_path, template_id)

        return jsonify({'success': True, 'template': template})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/activity_log', methods=['GET'])
def get_activity():
    """Get activity log entries."""
    try:
        account_name = request.args.get('account', None)
        limit = int(request.args.get('limit', 100))

        # Get any account to access database
        accounts = get_accounts()
        if not accounts:
            return jsonify({'success': True, 'activities': []})

        account_dir = os.path.join('accounts', accounts[0])
        db_path = os.path.join(account_dir, 'listings.db')

        # Initialize enhanced tables if needed
        init_enhanced_tables(db_path)

        activities = get_activity_log(db_path, limit, account_name)
        return jsonify({'success': True, 'activities': activities})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/analytics/summary', methods=['GET'])
def get_analytics():
    """Get analytics summary for dashboard."""
    try:
        account_name = request.args.get('account', None)
        days = int(request.args.get('days', 30))

        # Get any account to access database
        accounts = get_accounts()
        if not accounts:
            return jsonify({'success': True, 'analytics': {'action_stats': {}, 'daily_activity': []}})

        account_dir = os.path.join('accounts', accounts[0])
        db_path = os.path.join(account_dir, 'listings.db')

        # Initialize enhanced tables if needed
        init_enhanced_tables(db_path)

        analytics = get_analytics_summary(db_path, account_name, days)
        return jsonify({'success': True, 'analytics': analytics})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/analytics/accounts', methods=['GET'])
def get_all_account_stats():
    """Get statistics for all accounts."""
    try:
        accounts = get_accounts()
        all_stats = []

        for account_name in accounts:
            account_dir = os.path.join('accounts', account_name)
            db_path = os.path.join(account_dir, 'listings.db')

            # Initialize enhanced tables if needed
            init_enhanced_tables(db_path)

            stats = get_account_stats(db_path, account_name)
            if stats:
                stats['account_name'] = account_name
                all_stats.append(stats)

        return jsonify({'success': True, 'accounts': all_stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/analytics/account/<account_name>', methods=['GET'])
def get_single_account_stats(account_name):
    """Get statistics for a specific account."""
    try:
        account_dir = os.path.join('accounts', account_name)
        db_path = os.path.join(account_dir, 'listings.db')

        # Initialize enhanced tables if needed
        init_enhanced_tables(db_path)

        stats = get_account_stats(db_path, account_name)

        if stats:
            stats['account_name'] = account_name
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'success': False, 'message': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # Ensure accounts directory exists
    os.makedirs('accounts', exist_ok=True)

    # Initialize enhanced database tables for all accounts
    for account in get_accounts():
        account_dir = os.path.join('accounts', account)
        db_path = os.path.join(account_dir, 'listings.db')
        try:
            init_enhanced_tables(db_path)
            print(f"✅ Enhanced tables initialized for account: {account}")
        except Exception as e:
            print(f"⚠️ Error initializing enhanced tables for {account}: {e}")

    print("Facebook Marketplace Bot Server")
    print("=" * 40)
    print("Server starting on http://localhost:5000")
    print("Make sure to:")
    print("1. Create account folders in the 'accounts' directory")
    print("2. Add cookies.json files to each account folder")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("=" * 40)

    app.run(debug=True, host='0.0.0.0', port=5000)
