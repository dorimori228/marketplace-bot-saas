import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import get_browser_version_from_os
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
import time
import random
import json
import os
import pickle
import traceback
from datetime import datetime
from image_metadata import ImageMetadataModifier
from image_cropper import ImageCropper
from title_variator import TitleVariator
from description_variator import DescriptionVariator
from original_storage import OriginalStorage
from original_content_manager import OriginalContentManager
from ai_learning_system_simple import AILearningSystem


class MarketplaceBot:
    def __init__(self, cookies_path, delay_factor=1.0, proxy=None):
        """
        Initialize the MarketplaceBot with robust Chrome driver handling.
        
        Args:
            cookies_path (str): Path to the cookies.json or cookies.pkl file
            delay_factor (float): Multiplier for delays to control speed (1.0 = normal, 0.5 = faster, 2.0 = slower)
        """
        self.delay_factor = delay_factor
        self.cookies_path = cookies_path
        self.login_url = "https://www.facebook.com"
        self.is_logged_in_selector = 'div[aria-label="Account"]'
        self.driver = None
        self.proxy = proxy
        
        # Initialize Chrome driver with multiple fallback methods
        self._initialize_driver()
        
        # Set up WebDriverWait
        self.wait = WebDriverWait(self.driver, 15)
        
        # Initialize image metadata modifier
        self.metadata_modifier = ImageMetadataModifier()
        
        # Initialize new modules for unique content generation
        self.image_cropper = ImageCropper()
        self.title_variator = TitleVariator()
        self.description_variator = DescriptionVariator()
        self.original_storage = OriginalStorage()
        self.content_manager = OriginalContentManager()
        self.ai_learning = AILearningSystem()
        
        # Add login functionality
        self._add_login_functionality()
        
        # Initialize AI learning for the account
        self._initialize_ai_learning()

    def _initialize_driver(self):
        """Initialize Chrome driver with multiple fallback methods."""
        skip_undetected = os.getenv("BOT_SKIP_UNDETECTED", "").lower() in ["1", "true", "yes", "on"]
        initialization_methods = [
            self._init_regular_chrome,
            self._init_chrome_headless,
            self._init_chrome_minimal
        ]
        if not skip_undetected:
            initialization_methods.insert(0, self._init_undetected_chrome)
        
        for i, init_method in enumerate(initialization_methods):
            try:
                print(f"🔄 Attempting initialization method {i+1}...")
                self.driver = init_method()
                if self.driver:
                    print(f"✅ Driver initialized successfully with method {i+1}")
                    return
            except Exception as e:
                print(f"❌ Initialization method {i+1} failed: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                self.driver = None
                continue
        
        raise Exception("All Chrome driver initialization methods failed. Please check your Chrome installation.")

    def _init_undetected_chrome(self):
        """Initialize undetected Chrome driver."""
        options = uc.ChromeOptions()
        chrome_bin = os.getenv('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")
        
        driver = uc.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def _get_local_chrome_major(self):
        """Try to detect installed Chrome/Chromium major version."""
        candidates = ["google-chrome", "chrome", "chromium"]
        for name in candidates:
            try:
                version = get_browser_version_from_os(name)
                if version:
                    return version.split(".")[0]
            except Exception:
                continue
        return None

    def _init_regular_chrome(self):
        """Initialize regular Chrome driver with webdriver-manager."""
        options = ChromeOptions()
        chrome_bin = os.getenv('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
        if chromedriver_path:
            service = Service(chromedriver_path)
        else:
            major = self._get_local_chrome_major()
            driver_mgr = ChromeDriverManager(version=major) if major else ChromeDriverManager()
            service = Service(driver_mgr.install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def _init_chrome_headless(self):
        """Initialize Chrome driver in headless mode."""
        options = ChromeOptions()
        chrome_bin = os.getenv('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
        if chromedriver_path:
            service = Service(chromedriver_path)
        else:
            major = self._get_local_chrome_major()
            driver_mgr = ChromeDriverManager(version=major) if major else ChromeDriverManager()
            service = Service(driver_mgr.install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def _init_chrome_minimal(self):
        """Initialize Chrome driver with minimal options."""
        options = ChromeOptions()
        chrome_bin = os.getenv('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
        if chromedriver_path:
            service = Service(chromedriver_path)
        else:
            major = self._get_local_chrome_major()
            driver_mgr = ChromeDriverManager(version=major) if major else ChromeDriverManager()
            service = Service(driver_mgr.install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def _sleep(self, min_seconds=1, max_seconds=3):
        """Sleep for a random time to mimic human behavior."""
        sleep_time = random.uniform(min_seconds, max_seconds) * self.delay_factor
        time.sleep(sleep_time)

    def _sanitize_text_for_chromedriver(self, text):
        """
        Sanitize text to be compatible with ChromeDriver.
        ChromeDriver only supports characters in the BMP (Basic Multilingual Plane).
        This function tries to preserve emojis by using JavaScript injection as a fallback.
        """
        if not text:
            return text
        
        try:
            # Convert to string if not already
            text = str(text)
            
            # First, try to keep the text as-is and let ChromeDriver handle it
            # Most common emojis should work fine with modern ChromeDriver versions
            return text
            
        except Exception as e:
            print(f"⚠️ Error sanitizing text: {e}")
            # Fallback: return original text if sanitization fails
            return str(text)

    def _add_login_functionality(self):
        """Add login functionality with cookie handling."""
        try:
            if self._is_cookie_file():
                print("🍪 Cookie file found, attempting to load...")
                self._load_cookies()
                
                # Check if login was successful
                if self._is_logged_in():
                    print("✅ Successfully logged in with cookies!")
                    print("🚀 Auto-login successful - ready to use!")
                else:
                    print("⚠️ Cookie login failed, manual login required")
                    print("🔐 This is normal for new users or when cookies expire")
                    self._handle_manual_login()
            else:
                print("⚠️ No cookie file found - this appears to be a new user")
                print("🔐 Manual login required for first-time setup")
                self._handle_manual_login()
                
        except Exception as e:
            print(f"❌ Error during login process: {e}")
            print("🔐 Falling back to manual login...")
            self._handle_manual_login()

    def _is_cookie_file(self):
        """Check if cookie file exists."""
        return os.path.exists(self.cookies_path)

    def _load_cookies(self):
        """Load cookies from file and apply to browser."""
        try:
            # Load cookies from file
            if self.cookies_path.endswith('.pkl'):
                with open(self.cookies_path, 'rb') as f:
                    cookies = pickle.load(f)
            else:
                with open(self.cookies_path, 'r') as f:
                    cookies = json.load(f)

            print(f"🍪 Loaded {len(cookies)} cookies from {self.cookies_path}")

            # Navigate to Facebook first
            print("🌐 Navigating to Facebook...")
            self.driver.get(self.login_url)
            self._sleep(3, 5)

            # Handle mobile redirect
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("📱 Detected mobile redirect, forcing desktop version...")
                self.driver.get("https://www.facebook.com")
                self._sleep(2, 3)

            # Clear existing cookies first
            print("🧹 Clearing existing cookies...")
            self.driver.delete_all_cookies()
            self._sleep(1, 2)

            # Add cookies
            print("🍪 Adding cookies...")
            successful_cookies = 0
            for cookie in cookies:
                try:
                    # Ensure cookie has required fields
                    if not cookie.get('name') or not cookie.get('value'):
                        continue

                    sanitized = {
                        'name': cookie.get('name'),
                        'value': cookie.get('value'),
                        'domain': cookie.get('domain') or '.facebook.com',
                        'path': cookie.get('path') or '/'
                    }

                    # Normalize expiry
                    expiry = cookie.get('expiry') or cookie.get('expirationDate')
                    if expiry:
                        try:
                            sanitized['expiry'] = int(float(expiry))
                        except Exception:
                            pass

                    # Normalize sameSite
                    same_site = cookie.get('sameSite')
                    if same_site:
                        normalized = str(same_site).lower()
                        if normalized in ['no_restriction', 'none']:
                            sanitized['sameSite'] = 'None'
                        elif normalized in ['lax', 'strict']:
                            sanitized['sameSite'] = normalized.capitalize()

                    # Add the cookie
                    self.driver.add_cookie(sanitized)
                    successful_cookies += 1
                    
                except Exception as e:
                    print(f"⚠️ Could not add cookie {cookie.get('name', 'unknown')}: {e}")

            print(f"✅ Successfully added {successful_cookies}/{len(cookies)} cookies")

            # Refresh page to apply cookies
            print("🔄 Refreshing page to apply cookies...")
            self.driver.get(self.login_url)
            self._sleep(2, 3.5)

            # Handle mobile redirect again
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("📱 Still on mobile, trying alternative desktop URL...")
                self.driver.get("https://www.facebook.com")
                self._sleep(2, 3.5)

            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Final check - wait a bit more for page to fully load
            self._sleep(1, 2)

        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            import traceback
            traceback.print_exc()

    def _handle_cookie_consent(self):
        """Handle Facebook cookie consent popup."""
        try:
            # Look for cookie consent buttons
            consent_selectors = [
                'div[aria-label="Allow all cookies"]',
                'div[aria-label="Decline optional cookies"]',
                'button[data-testid="cookie-policy-manage-dialog-accept-button"]',
                'button[data-testid="cookie-policy-manage-dialog-decline-button"]'
            ]
            
            for selector in consent_selectors:
                try:
                    consent_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if consent_button.is_displayed():
                        consent_button.click()
                        print("✅ Clicked cookie consent button")
                        self._sleep(2, 3)
                        break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Could not handle cookie consent: {e}")

    def _is_logged_in(self):
        """Check if user is logged in."""
        try:
            # Wait a bit for page to load
            self._sleep(0.6, 1.2)
            
            # Check current URL first
            current_url = self.driver.current_url
            print(f"🔍 Current URL: {current_url}")
            
            # If we're on login page, we're not logged in
            if "login" in current_url.lower() or "signin" in current_url.lower():
                print("❌ On login page - not logged in")
                return False
            
            # Check for logged-in indicators with more comprehensive selectors
            logged_in_selectors = [
                'div[aria-label="Account"]',
                'div[aria-label="Menu"]', 
                'div[data-testid="left_nav_menu"]',
                'div[role="banner"]',
                'div[data-testid="search"]',
                'div[aria-label="Search"]',
                'div[data-testid="facebook-header"]',
                'div[role="main"]',
                'div[data-testid="home"]',
                'div[aria-label="Home"]',
                'div[data-testid="marketplace"]',
                'div[aria-label="Marketplace"]'
            ]
            
            for selector in logged_in_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        print(f"✅ Found logged-in indicator: {selector}")
                        return True
                except:
                    continue
            
            # Additional check: look for any Facebook navigation elements
            try:
                # Check if we can find the main Facebook interface
                main_content = self.driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')
                if main_content:
                    print("✅ Found main content area - likely logged in")
                    return True
            except:
                pass
            
            # Check for login form (if present, we're not logged in)
            try:
                login_form = self.driver.find_element(By.CSS_SELECTOR, 'form[data-testid="royal_login_form"]')
                if login_form and login_form.is_displayed():
                    print("❌ Found login form - not logged in")
                    return False
            except:
                pass
            
            print("⚠️ Could not determine login status - assuming not logged in")
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking login status: {e}")
            return False

    def _handle_manual_login(self):
        """Handle manual login process."""
        try:
            print("\n" + "="*60)
            print("🔐 MANUAL LOGIN REQUIRED")
            print("="*60)
            print("📋 INSTRUCTIONS:")
            print("1. A browser window will open to Facebook")
            print("2. Log in with your Facebook account credentials")
            print("3. Complete any 2FA if prompted")
            print("4. Navigate to Facebook Marketplace if needed")
            print("5. The bot will automatically detect when you're logged in")
            print("6. Your login will be saved for future auto-login")
            print("="*60)
            print("⏳ Waiting for manual login... (2 minutes)")
            print("💡 Tip: Make sure you're fully logged in before the timeout")
            print()
            
            # Navigate to Facebook login page
            self.driver.get(self.login_url)
            self._sleep(3, 5)
            
            # Handle mobile redirect
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("📱 Detected mobile redirect, forcing desktop version...")
                self.driver.get("https://www.facebook.com")
                self._sleep(3, 5)
            
            # Wait for manual login with progress indicator
            for i in range(120):  # 2 minutes
                if self._is_logged_in():
                    print("✅ Manual login successful!")
                    print("💾 Saving cookies for future auto-login...")
                    self._save_cookies()
                    print("🎉 Setup complete! Future runs will auto-login.")
                    return
                
                # Show progress every 10 seconds
                if i % 10 == 0 and i > 0:
                    remaining = (120 - i) // 10
                    print(f"⏳ Still waiting... {remaining}0 seconds remaining")
                
                time.sleep(1)
            
            print("⏰ Manual login timeout (2 minutes).")
            print("💡 This might happen if:")
            print("   - You need more time to complete 2FA")
            print("   - Facebook is asking for additional verification")
            print("   - The login process is taking longer than expected")
            print("🔄 Please try running the setup again.")
            
        except Exception as e:
            print(f"❌ Error during manual login: {e}")
            print("🔄 Please try running the setup again.")

    def _save_cookies(self):
        """Save current cookies to file."""
        try:
            cookies = self.driver.get_cookies()
            
            if not cookies:
                print("⚠️ No cookies found to save")
                return False
            
            # Save cookies
            if self.cookies_path.endswith('.pkl'):
                with open(self.cookies_path, 'wb') as f:
                    pickle.dump(cookies, f)
            else:
                with open(self.cookies_path, 'w') as f:
                    json.dump(cookies, f, indent=2)
            
            print(f"✅ Cookies saved to {self.cookies_path}")
            
            # Validate the saved cookies
            important_cookies = ['c_user', 'xs', 'datr', 'sb', 'fr']
            found_important = [cookie['name'] for cookie in cookies if cookie['name'] in important_cookies]
            
            print(f"🔑 Important cookies saved: {', '.join(found_important)}")
            print(f"📊 Total cookies saved: {len(cookies)}")
            
            # Verify file was created and readable
            if os.path.exists(self.cookies_path):
                file_size = os.path.getsize(self.cookies_path)
                print(f"📁 File size: {file_size} bytes")
                
                # Test loading the cookies back
                try:
                    if self.cookies_path.endswith('.pkl'):
                        with open(self.cookies_path, 'rb') as f:
                            test_cookies = pickle.load(f)
                    else:
                        with open(self.cookies_path, 'r') as f:
                            test_cookies = json.load(f)
                    
                    if len(test_cookies) == len(cookies):
                        print("✅ Cookie file validation successful!")
                        return True
                    else:
                        print("⚠️ Cookie count mismatch during validation")
                        return False
                        
                except Exception as validation_error:
                    print(f"⚠️ Cookie validation failed: {validation_error}")
                    return False
            else:
                print("❌ Cookie file was not created!")
                return False
                
        except Exception as e:
            print(f"❌ Error saving cookies: {e}")
            return False

    def _process_images_with_metadata(self, image_paths, account=None, listing_title=None, use_originals=True):
        """
        Process images to add iPhone 12 metadata with random UK locations and create unique crops.
        Always uses original images from main folder for consistency.
        
        Args:
            image_paths (list): List of image file paths (will be replaced with originals if use_originals=True)
            account (str): Account name for storage
            listing_title (str): Listing title for storage
            use_originals (bool): Whether to use original images from main folder
            
        Returns:
            list: List of processed image paths
        """
        try:
            print("📸 Processing images with iPhone 12 metadata and unique cropping...")
            
            # Get original images from main folder if requested
            if use_originals and account:
                print("🔍 Looking for original images in main folder...")
                original_images = self.content_manager.get_original_images(account, listing_title)
                
                if original_images:
                    print(f"✅ Found {len(original_images)} original images, using those instead")
                    image_paths = original_images
                else:
                    print("⚠️ No original images found in main folder, using provided images")
                    print(f"   📁 Account: {account}")
                    print(f"   📝 Title: {listing_title}")
                    print(f"   🔍 Available images: {len(image_paths)}")
            
            # Force processing: always process images to ensure uniqueness
            print("🔧 FORCE PROCESSING: Ensuring all images are processed for uniqueness...")
            print("🔧 FORCE PROCESSING: This will ALWAYS crop and adjust images!")
            
            print(f"🔧 Modifying {len(image_paths)} image(s) with random UK locations and cropping")
            print(f"🔧 Input images: {[os.path.basename(p) for p in image_paths]}")
            
            # Store original images if account is provided and not using originals
            if account and not use_originals:
                print("💾 Storing original images...")
                storage_result = self.original_storage.store_original_images(account, image_paths, listing_title)
                if storage_result['success']:
                    print(f"✅ Stored {storage_result['count']} original images")
                else:
                    print(f"⚠️ Failed to store original images: {storage_result['error']}")
            
            processed_paths = []
            
            for i, image_path in enumerate(image_paths, 1):
                try:
                    print(f"🔄 Processing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
                    
                    # Step 1: Create unique crop from original
                    print(f"   🎯 Creating unique crop from original...")
                    crop_result = self.image_cropper.get_best_crop(image_path)
                    
                    if crop_result['success']:
                        cropped_path = crop_result['output_path']
                        print(f"   ✅ Crop created: {crop_result['cropped_size']} (from {crop_result['original_size']})")
                        print(f"   📊 Area: {crop_result['area_ratio']} of original")
                        print(f"   🎯 Strategy: {crop_result['strategy']}")
                    else:
                        print(f"   ⚠️ Crop failed, using original: {crop_result['error']}")
                        cropped_path = image_path
                    
                    # Step 2: Apply metadata modification to cropped image
                    temp_dir = os.path.dirname(image_path)
                    filename, ext = os.path.splitext(os.path.basename(image_path))
                    temp_path = os.path.join(temp_dir, f"{filename}_processed{ext}")
                    
                    # Modify metadata on the cropped image
                    result = self.metadata_modifier.modify_image_metadata(cropped_path, temp_path)
                    
                    if result['success']:
                        processed_paths.append(temp_path)
                        print(f"✅ Image {i} processed successfully")
                        print(f"   📍 Location: {result['location']['name']} ({result['location']['lat']:.4f}, {result['location']['lon']:.4f})")
                        print(f"   📅 Date: {result['timestamp']}")
                        print(f"   📱 Camera: {result['camera']}")
                        print(f"   🎨 Perceptual Shift: Brightness {result['brightness_change_pct']}, Contrast {result['contrast_change_pct']}")
                        print(f"   📐 Size Change: {result['original_size']} → {result['final_size']} ({result['size_change_pct']})")
                        print(f"   💾 JPEG Quality: {result['jpeg_quality']}")
                        print(f"   🔒 Unique perceptual hash generated")
                        
                        # Keep the cropped image for debugging (don't clean up immediately)
                        if cropped_path != image_path:
                            print(f"   📁 Cropped image saved: {os.path.basename(cropped_path)}")
                    else:
                        print(f"⚠️ Failed to process image {i}, using original: {result['error']}")
                        processed_paths.append(image_path)
                        
                except Exception as e:
                    print(f"⚠️ Error processing image {i}, using original: {e}")
                    processed_paths.append(image_path)
            
            print(f"🎉 Image processing complete! {len(processed_paths)} images ready for upload")
            print(f"🔧 OUTPUT IMAGES: {[os.path.basename(p) for p in processed_paths]}")
            
            # Final validation: ensure all processed images exist
            valid_processed = []
            for i, path in enumerate(processed_paths):
                if os.path.exists(path):
                    valid_processed.append(path)
                    print(f"   ✅ Processed image {i+1}: {os.path.basename(path)}")
                    # Show file size to verify it's different
                    file_size = os.path.getsize(path)
                    print(f"      📊 File size: {file_size:,} bytes")
                else:
                    print(f"   ❌ Processed image {i+1}: {os.path.basename(path)} - FILE NOT FOUND")
            
            if valid_processed:
                return valid_processed
            else:
                print("⚠️ No valid processed images, falling back to originals")
                return image_paths
            
        except Exception as e:
            print(f"❌ Error in image processing: {e}")
            print("🔄 Using original images without metadata modification")
            
            # Ensure original images exist
            valid_originals = []
            for i, path in enumerate(image_paths):
                if os.path.exists(path):
                    valid_originals.append(path)
                    print(f"   ✅ Original image {i+1}: {os.path.basename(path)}")
                else:
                    print(f"   ❌ Original image {i+1}: {os.path.basename(path)} - FILE NOT FOUND")
            
            if valid_originals:
                return valid_originals
            else:
                print("❌ No valid images found at all!")
                return []

    def _generate_unique_title(self, original_title, account, allow_traditional=True):
        """
        Generate a unique title variation for the listing using AI learning system.
        
        Args:
            original_title (str): Original title
            account (str): Account name
            
        Returns:
            dict: Title variation result
        """
        try:
            print(f"🔄 Generating unique title variation for: {original_title}")
            
            # Store original title
            self.original_storage.store_original_title(account, original_title)
            
            # Try AI learning system first
            print("🤖 Attempting AI-powered title generation...")
            ai_result = self.ai_learning.generate_ai_title_variation(account, original_title)
            
            if ai_result['success']:
                new_title = ai_result['variation']
                # Apply length limit to AI-generated title
                new_title = self.title_variator._ensure_title_length_limit(new_title, 100)
                print(f"✅ AI generated unique title: {new_title} (length: {len(new_title)})")
                print(f"   🤖 Type: {ai_result['type']}")
                print(f"   🎯 Confidence: {ai_result.get('confidence', 0.9):.1%}")
                
                return {
                    'success': True,
                    'original_title': original_title,
                    'new_title': new_title,
                    'variation_info': ai_result,
                    'method': 'ai_learning'
                }
            else:
                print(f"⚠️ AI title generation failed: {ai_result.get('error', 'Unknown error')}")
                if not allow_traditional:
                    return {
                        'success': False,
                        'original_title': original_title,
                        'new_title': original_title,
                        'error': f"AI: {ai_result.get('error', 'Unknown')}"
                    }

                print("🔄 Falling back to traditional variation system...")
                
                # Fallback to traditional variation system
                variation_result = self.title_variator.get_next_title_variation(account, original_title)
                
                if variation_result['success']:
                    new_title = variation_result['variation']
                    # Apply length limit to traditional variation title
                    new_title = self.title_variator._ensure_title_length_limit(new_title, 100)
                    print(f"✅ Generated unique title using traditional method: {new_title} (length: {len(new_title)})")
                    print(f"   📝 Type: {variation_result['type']}")
                    print(f"   🔄 Changes: {variation_result['changes']}")
                    
                    return {
                        'success': True,
                        'original_title': original_title,
                        'new_title': new_title,
                        'variation_info': variation_result,
                        'method': 'traditional'
                    }
                else:
                    print(f"⚠️ Traditional title variation also failed: {variation_result.get('error', 'Unknown error')}")
                    return {
                        'success': False,
                        'original_title': original_title,
                        'new_title': original_title,
                        'error': f"AI: {ai_result.get('error', 'Unknown')}, Traditional: {variation_result.get('error', 'Unknown')}"
                    }
                
        except Exception as e:
            print(f"❌ Error generating title variation: {e}")
            return {
                'success': False,
                'original_title': original_title,
                'new_title': original_title,
                'error': str(e)
            }

    def _generate_unique_description(self, original_description, account, context=None, allow_traditional=True):
        """
        Generate a unique description variation for the listing using AI learning system.
        
        Args:
            original_description (str): Original description
            account (str): Account name
            
        Returns:
            dict: Description variation result
        """
        try:
            print(f"🔄 Generating unique description variation for: {original_description[:50]}...")
            
            # Store original description
            self.original_storage.store_original_title(account, original_description, listing_id="description")
            
            # Try AI learning system first
            print("🤖 Attempting AI-powered description generation...")
            ai_result = self.ai_learning.generate_ai_description_variation(account, original_description, context=context)
            
            if ai_result['success']:
                new_description = ai_result['variation']
                print(f"✅ AI generated unique description")
                print(f"   🤖 Type: {ai_result['type']}")
                print(f"   🎯 Confidence: {ai_result.get('confidence', 0.9):.1%}")
                
                return {
                    'success': True,
                    'original_description': original_description,
                    'new_description': new_description,
                    'variation_info': ai_result,
                    'method': 'ai_learning'
                }
            else:
                print(f"⚠️ AI description generation failed: {ai_result.get('error', 'Unknown error')}")
                if not allow_traditional:
                    return {
                        'success': False,
                        'original_description': original_description,
                        'new_description': original_description,
                        'error': f"AI: {ai_result.get('error', 'Unknown')}"
                    }

                print("🔄 Falling back to traditional variation system...")
                
                # Fallback to traditional variation system
                variation_result = self.description_variator.get_next_description_variation(account, original_description)
                
                if variation_result['success']:
                    new_description = variation_result['variation']
                    print(f"✅ Generated unique description using traditional method")
                    print(f"   📝 Type: {variation_result['type']}")
                    print(f"   🔄 Changes: {variation_result['changes']}")
                    
                    return {
                        'success': True,
                        'original_description': original_description,
                        'new_description': new_description,
                        'variation_info': variation_result,
                        'method': 'traditional'
                    }
                else:
                    print(f"⚠️ Traditional description variation also failed: {variation_result.get('error', 'Unknown error')}")
                    return {
                        'success': False,
                        'original_description': original_description,
                        'new_description': original_description,
                        'error': f"AI: {ai_result.get('error', 'Unknown')}, Traditional: {variation_result.get('error', 'Unknown')}"
                    }
                
        except Exception as e:
            print(f"❌ Error generating description variation: {e}")
            return {
                'success': False,
                'original_description': original_description,
                'new_description': original_description,
                'error': str(e)
            }

    def _cleanup_temp_images(self, processed_image_paths):
        """Clean up temporary processed images (only truly temporary ones)."""
        try:
            print("🧹 Cleaning up temporary processed images...")
            cleaned_count = 0
            
            for image_path in processed_image_paths:
                # Only clean up files that are clearly temporary (contain '_temp' in path)
                if '_temp' in image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        cleaned_count += 1
                        print(f"🗑️ Removed temporary file: {os.path.basename(image_path)}")
                    except Exception as e:
                        print(f"⚠️ Could not remove temporary file {image_path}: {e}")
                else:
                    # Keep processed images for user to see the changes
                    print(f"📁 Keeping processed image: {os.path.basename(image_path)}")
            
            if cleaned_count > 0:
                print(f"✅ Cleaned up {cleaned_count} temporary image(s)")
            else:
                print("ℹ️ No temporary images to clean up")
                
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

    def delete_listing_if_exists(self, title, _retry=False):
        """Search for a listing by title, and if found, delete it."""
        try:
            print(f"🔍 Searching for listing with title: '{title}'")
            title_lower = title.lower()
            self.last_delete_found = False
            self.last_delete_success = False

            # Check if we're already on the selling page
            current_url = self.driver.current_url
            if "marketplace/you/selling" not in current_url:
                print("🔗 Navigating to selling page...")
                self.driver.get("https://www.facebook.com/marketplace/you/selling")
                self._sleep(3, 5)

                # Handle mobile redirect
                current_url = self.driver.current_url
                if "m.facebook.com" in current_url:
                    print("📱 Detected mobile redirect on selling page, forcing desktop...")
                    self.driver.get("https://www.facebook.com/marketplace/you/selling")
                    self._sleep(2, 3)
            else:
                print("✅ Already on selling page")

            # Wait for page to load
            self._sleep(1, 1.5)

            # Use search box to search for the listing
            print("🔍 Using search box to find listing...")
            search_found = False

            search_selectors = [
                'input[aria-label="Search your listings"]',
                'input[aria-label*="Search"]',
                'input[placeholder*="Search"]',
                'input[type="search"]',
                'input[role="searchbox"]',
                "//input[contains(@aria-label, 'Search')]",
                "//input[contains(@placeholder, 'Search')]"
            ]

            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        search_input = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        search_input = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    
                    if search_input and search_input.is_displayed():
                        # Clear and type the search term
                        search_input.clear()
                        self._sleep(0.2, 0.4)
                        search_input.send_keys(title)
                        self._sleep(0.6, 1.0)  # Wait for search results to filter
                        print(f"✅ Entered search term '{title}' in search box")
                        search_found = True
                        break
                except Exception as e:
                    print(f"⚠️ Search selector {selector} failed: {str(e)[:100]}")
                    continue

            if not search_found:
                print("⚠️ Could not find search box - will try to find listing without search")

            # Now look for any listing on the page (after search)
            print("🔍 Looking for listing in search results...")
            listing_found = False
            listing_element = None

            # Wait a bit for search results to appear
            self._sleep(0.6, 1.0)

            # Try common listing selectors - look for listings that might contain the title
            listing_selectors = [
                'a[href*="/marketplace/item/"]',
                'div[role="article"]',
                'div[class*="x1yztbdb"]',
                'div[class*="x1n2onr6"]',  # Another common listing container class
            ]

            def _listing_still_present():
                # Re-run search and look for the listing title in results
                search_found_local = False
                for selector in search_selectors:
                    try:
                        if selector.startswith("//"):
                            search_input_local = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                        else:
                            search_input_local = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )

                        if search_input_local and search_input_local.is_displayed():
                            search_input_local.clear()
                            self._sleep(0.2, 0.4)
                            search_input_local.send_keys(title)
                            search_found_local = True
                            break
                    except Exception:
                        continue

                if search_found_local:
                    self._sleep(0.6, 1.0)

                for selector in listing_selectors:
                    try:
                        listings_local = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for listing in listings_local:
                            try:
                                listing_text_local = listing.text.lower()
                                if title_lower in listing_text_local:
                                    return True
                            except Exception:
                                continue
                    except Exception:
                        continue

                return False

            for selector in listing_selectors:
                try:
                    listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"🔍 Found {len(listings)} potential listings with selector: {selector}")
                    
                    # If we searched, try to find listing that contains the title text
                    if search_found and listings:
                        for listing in listings:
                            try:
                                listing_text = listing.text.lower()
                                # Check if listing contains the title (partial match is OK)
                                if title_lower in listing_text or any(word in listing_text for word in title_lower.split() if len(word) > 3):
                                    listing_element = listing
                                    listing_found = True
                                    self.last_delete_found = True
                                    print(f"✅ Found listing matching title using selector: {selector}")
                                    break
                            except:
                                continue

                    # If a matching listing was found, break out of the selector loop
                    if listing_found:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {str(e)[:100]}")
                    continue

            if not listing_found:
                print(f"ℹ️ No listing found matching search. Skipping deletion.")
                return False
            self.last_delete_found = True
            
            # Click on the listing with retry and improved click strategies
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.common.exceptions import ElementClickInterceptedException

            print("📍 Attempting to click on the first listing...")
            for click_attempt in range(3):
                try:
                    # Re-find the element on each attempt to avoid stale element issues
                    if click_attempt > 0:
                        print(f"  Re-finding element for attempt {click_attempt + 1}...")
                        listing_element = None
                        for selector in listing_selectors:
                            try:
                                listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                if listings:
                                    for listing in listings:
                                        try:
                                            listing_text = listing.text.lower()
                                            if title_lower in listing_text or any(word in listing_text for word in title_lower.split() if len(word) > 3):
                                                listing_element = listing
                                                print(f"  ✅ Re-found listing element")
                                                break
                                        except:
                                            continue
                                    if listing_element:
                                        break
                            except:
                                continue

                        if not listing_element:
                            print(f"  ⚠️ Could not re-find listing element")
                            raise Exception("Listing element not found on retry")

                    # Handle overlapping elements that might intercept clicks
                    self._handle_overlapping_elements()

                    # Scroll element into view first
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listing_element)
                    self._sleep(0.4, 0.7)

                    # Try multiple click strategies
                    click_success = False

                    # Strategy 1: Direct click
                    try:
                        listing_element.click()
                        click_success = True
                        print("✅ Direct click successful")
                    except ElementClickInterceptedException:
                        print(f"⚠️ Direct click intercepted on attempt {click_attempt + 1}")

                        # Strategy 2: JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", listing_element)
                            click_success = True
                            print("✅ JavaScript click successful")
                        except Exception as js_e:
                            print(f"⚠️ JavaScript click failed: {js_e}")

                            # Strategy 3: ActionChains click
                            try:
                                ActionChains(self.driver).move_to_element(listing_element).click().perform()
                                click_success = True
                                print("✅ ActionChains click successful")
                            except Exception as ac_e:
                                print(f"⚠️ ActionChains click failed: {ac_e}")

                                # Strategy 4: Force click with JavaScript
                                try:
                                    self.driver.execute_script("""
                                        var element = arguments[0];
                                        var event = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        element.dispatchEvent(event);
                                    """, listing_element)
                                    click_success = True
                                    print("✅ Force JavaScript click successful")
                                except Exception as force_e:
                                    print(f"⚠️ Force click failed: {force_e}")

                    if click_success:
                        # Restore overlapping elements
                        self._restore_overlapping_elements()
                        self._sleep(0.8, 1.2)  # Wait for popup to load
                        print("Successfully clicked on listing")
                        break
                    else:
                        raise Exception("All click strategies failed")

                except Exception as e:
                    print(f"⚠️ Click attempt {click_attempt + 1} failed: {e}")
                    if click_attempt < 2:
                        # Wait a bit before retrying
                        self._sleep(0.8, 1.2)
                    else:
                        print("⚠️ Could not click on listing, skipping deletion")
                        return False
            
            # Step 2: Click "More options" button (three dots)
            print("🔍 Looking for 'More options' button...")
            self._sleep(0.4, 0.6)

            more_options_clicked = False
            more_options_selectors = [
                '//div[contains(@aria-label, "More options")][@role="button"]',
                'div[aria-label*="More options"][role="button"]',
            ]

            for selector in more_options_selectors:
                try:
                    selector_type = By.CSS_SELECTOR if not selector.startswith('//') else By.XPATH
                    from selenium.webdriver.support.ui import WebDriverWait
                    short_wait = WebDriverWait(self.driver, 2)
                    more_btn = short_wait.until(EC.presence_of_element_located((selector_type, selector)))

                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_btn)
                    self._sleep(0.3, 0.4)

                    try:
                        more_btn.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", more_btn)

                    more_options_clicked = True
                    print("✅ Clicked 'More options'")
                    break
                except:
                    continue

            if not more_options_clicked:
                print("❌ Could not find 'More options' button")
                return False

            self._sleep(0.4, 0.6)

            # Step 3: Click "Delete listing" from menu
            print("🔍 Looking for 'Delete listing' option...")
            delete_clicked = False
            delete_selectors = [
                # User's exact delete button selector (PRIORITY 1)
                "body div[id='mount_0_0_ck'] div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j'] div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j'] div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j'] div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j'] div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j'] div:nth-child(1) div:nth-child(1) div:nth-child(1) div:nth-child(1) div:nth-child(2) div:nth-child(1) div:nth-child(2) div:nth-child(1) div:nth-child(4)",
                '//span[text()="Delete listing"]',
                '//span[contains(text(), "Delete listing")]',
                '//div[contains(., "Delete listing")]',
            ]

            for i, selector in enumerate(delete_selectors, 1):
                try:
                    print(f"  Trying selector {i}/{len(delete_selectors)}: {selector[:50]}...")
                    # Determine if selector is CSS or XPath
                    selector_type = By.CSS_SELECTOR if not selector.startswith('//') else By.XPATH

                    # Faster timeout - 2 seconds
                    from selenium.webdriver.support.ui import WebDriverWait
                    short_wait = WebDriverWait(self.driver, 2)
                    initial_delete_button = short_wait.until(
                        EC.presence_of_element_located((selector_type, selector))
                    )
                    print(f"  ✅ Found delete button (selector {i})")

                    # Make sure it's visible and scroll to it
                    if not initial_delete_button.is_displayed():
                        print(f"  ⚠️ Element found but not visible, trying next selector...")
                        continue
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", initial_delete_button)
                    self._sleep(0.3, 0.5)
                    
                    # Try multiple click strategies for delete button
                    delete_click_success = False
                    
                    # Strategy 1: Direct click
                    try:
                        initial_delete_button.click()
                        delete_click_success = True
                        print("Direct delete button click successful")
                    except ElementClickInterceptedException:
                        print("⚠️ Direct delete button click intercepted")
                        
                        # Strategy 2: JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", initial_delete_button)
                            delete_click_success = True
                            print("✅ JavaScript delete button click successful")
                        except Exception as js_e:
                            print(f"⚠️ JavaScript delete button click failed: {js_e}")
                            
                            # Strategy 3: ActionChains click
                            try:
                                ActionChains(self.driver).move_to_element(initial_delete_button).click().perform()
                                delete_click_success = True
                                print("✅ ActionChains delete button click successful")
                            except Exception as ac_e:
                                print(f"⚠️ ActionChains delete button click failed: {ac_e}")
                    
                    if delete_click_success:
                        delete_clicked = True
                        break
                    else:
                        raise Exception("All delete button click strategies failed")
                        
                except Exception as e:
                    print(f"  ⚠️ Selector {i} failed: {str(e)[:100]}")
                    continue

            if not delete_clicked:
                print("❌ Could not find delete button with any selector")
                print("💡 Tip: The listing detail page may have opened. Check if delete button is visible.")
                return False

            print("✅ Successfully clicked 'Delete listing'")

            # Step 4: Click the confirm "Delete" button in the popup
            try:
                print("🔍 Looking for confirm 'Delete' button...")
                self._sleep(0.4, 0.6)

                confirm_selectors = [
                    # User's new specific selectors (HIGHEST PRIORITY)
                    "(//span[@class='html-span xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x1hl2dhg x16tdsg8 x1vvkbs x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft'][normalize-space()='Delete'])[2]",
                    "//span[@class='xdmh292 x15dsfln x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1lliihq xtk6v10 xlh3980 xvmahel x1x9mg3 x1s688f']//span[@class='html-span xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x1hl2dhg x16tdsg8 x1vvkbs x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft'][normalize-space()='Delete']",
                    "div[role='none'] span[class='xdmh292 x15dsfln x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1lliihq xtk6v10 xlh3980 xvmahel x1x9mg3 x1s688f'] span[class='html-span xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x1hl2dhg x16tdsg8 x1vvkbs x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft']",
                    # Find span with "Delete" text and click grandparent div with role="none"
                    "//span[text()='Delete']/ancestor::div[@role='none'][1]",
                    # Alternative: find the div role=none that contains Delete text
                    "//div[@role='none' and contains(@class, 'x1ja2u2z') and .//span[text()='Delete']]",
                    # Try the direct class selector for the clickable parent div
                    "div[role='none'][class*='x1ja2u2z'][class*='x78zum5']",
                    # Original user selector - try clicking the innermost span
                    "span.html-span.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1hl2dhg.x16tdsg8.x1vvkbs.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft",
                    # User's exact full class selector
                    "div[class='x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x14ldlfn x1b1wa69 xws8118 x5fzff1 x972fbf x10w94by x1qhh985 x14e42zd x9f619 xpdmqnj x1g0dm76 xtvsq51 x1r1pt67']",
                    # Find any element with Delete text
                    "//span[contains(@class,'html-span') and text()='Delete']",
                    # User's confirmation dialog selector
                    "body div[id='mount_0_0_ck'] div[class='x9f619 x1n2onr6 x1ja2u2z'] div[class='x9f619 x1n2onr6 x1ja2u2z'] div[class='__fb-dark-mode'] div:nth-child(4) div:nth-child(2) div:nth-child(1) div:nth-child(1) span:nth-child(1)",
                    # Original exact CSS selector
                    "span[class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen x1s688f xtk6v10'] span[class='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft']",
                    # Simple aria-label fallbacks
                    '//div[@aria-label="Delete"][@role="button"]',
                    'div[aria-label="Delete"][role="button"]',
                    "//span[normalize-space(text())='Delete']/ancestor::*[@role='button'][1]",
                    "//button[normalize-space(text())='Delete']",
                    "//div[@role='button'][.//span[normalize-space(text())='Delete']]"
                ]

                confirm_delete_button = None
                for j, selector in enumerate(confirm_selectors, 1):
                    try:
                        print(f"  Trying confirm selector {j}/{len(confirm_selectors)}")
                        selector_type = By.CSS_SELECTOR if not selector.startswith('//') and not selector.startswith('(//') else By.XPATH

                        # Reduced timeout to 2 seconds for speed
                        short_wait = WebDriverWait(self.driver, 2)
                        confirm_delete_button = short_wait.until(
                            EC.presence_of_element_located((selector_type, selector))
                        )
                        print(f"  ✅ Found confirm button (selector {j})")
                        break
                    except Exception as ce:
                        continue
                
                if not confirm_delete_button:
                    print("⚠️ Could not find confirm delete button")
                    return False

            except Exception as e:
                print(f"⚠️ Could not find confirm delete button: {e}")
                return False
            
            # Try to click the confirm delete button with retry and improved strategies
            for attempt in range(3):
                try:
                    # Re-find the confirm button each attempt to avoid stale element
                    try:
                        confirm_delete_button = None
                        for selector in confirm_selectors:
                            selector_type = By.CSS_SELECTOR if not selector.startswith('//') and not selector.startswith('(//') else By.XPATH
                            short_wait = WebDriverWait(self.driver, 2)
                            confirm_delete_button = short_wait.until(
                                EC.element_to_be_clickable((selector_type, selector))
                            )
                            if confirm_delete_button:
                                break
                    except Exception as refind_error:
                        print(f"⚠️ Could not re-find confirm delete button: {refind_error}")

                    if not confirm_delete_button:
                        raise Exception("Confirm delete button not found")

                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_delete_button)
                    self._sleep(0.3, 0.5)
                    
                    # Try multiple click strategies for confirm delete button
                    confirm_click_success = False
                    
                    # Strategy 1: Direct click
                    try:
                        confirm_delete_button.click()
                        confirm_click_success = True
                        print(f"Direct confirm delete button click successful on attempt {attempt + 1}")
                    except ElementClickInterceptedException:
                        print(f"Direct confirm delete button click intercepted on attempt {attempt + 1}")
                        
                        # Strategy 2: JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", confirm_delete_button)
                            confirm_click_success = True
                            print(f"✅ JavaScript confirm delete button click successful on attempt {attempt + 1}")
                        except Exception as js_e:
                            print(f"⚠️ JavaScript confirm delete button click failed: {js_e}")
                            
                            # Strategy 3: ActionChains click
                            try:
                                ActionChains(self.driver).move_to_element(confirm_delete_button).click().perform()
                                confirm_click_success = True
                                print(f"✅ ActionChains confirm delete button click successful on attempt {attempt + 1}")
                            except Exception as ac_e:
                                print(f"⚠️ ActionChains confirm delete button click failed: {ac_e}")
                                
                                # Strategy 4: Force click with JavaScript
                                try:
                                    self.driver.execute_script("""
                                        var element = arguments[0];
                                        var event = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        element.dispatchEvent(event);
                                    """, confirm_delete_button)
                                    confirm_click_success = True
                                    print(f"✅ Force JavaScript confirm delete button click successful on attempt {attempt + 1}")
                                except Exception as force_e:
                                    print(f"⚠️ Force confirm delete button click failed: {force_e}")
                    
                    if confirm_click_success:
                        # Wait for dialog to close or deletion to complete
                        try:
                            WebDriverWait(self.driver, 4).until(
                                EC.invisibility_of_element(confirm_delete_button)
                            )
                        except Exception:
                            pass
                        break
                    else:
                        raise Exception("All confirm delete button click strategies failed")
                        
                except Exception as e:
                    print(f"⚠️ Confirm delete button click attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        # Try scrolling to a different position to avoid overlapping elements
                        self.driver.execute_script("window.scrollBy(0, -50);")
                        self._sleep(2, 3)
                    else:
                        print("⚠️ All confirm delete button attempts failed")
                        return False
            
            self._sleep(0.8, 1.2)
            # Try to confirm deletion by checking for toast or missing listing
            try:
                toast = self.driver.find_elements(By.XPATH, "//*[contains(text(),'deleted') or contains(text(),'Deleted')]")
                if toast:
                    print(f"✅ Deletion confirmed via toast for: '{title}'")
                else:
                    print(f"✅ Delete action completed for: '{title}'")
            except Exception:
                print(f"✅ Delete action completed for: '{title}'")

            # SKIP verification to avoid searching again - trust the delete worked
            print("ℹ️ Skipping verification (going straight to create to avoid re-searching)")
            self.last_delete_success = True

            # Navigate to create listing page after successful deletion
            print("🚀 Navigating to create listing page...")
            self.driver.get("https://www.facebook.com/marketplace/create/")
            self._sleep(3, 5)
            
            # Handle mobile redirect
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("📱 Detected mobile redirect on create page, forcing desktop...")
                self.driver.get("https://www.facebook.com/marketplace/create/")
                self._sleep(3, 5)
            
            print("✅ Ready to create new listing")
            return True

        except Exception as e:
            print(f"⚠️ Error during listing deletion: {e}")
            return False
        finally:
            # Always restore overlapping elements
            self._restore_overlapping_elements()

    def _handle_overlapping_elements(self):
        """Temporarily hide overlapping elements that might intercept clicks."""
        try:
            # Hide common overlapping elements that might interfere with clicks
            overlapping_selectors = [
                'a[aria-label="Reels"]',
                'a[href*="/reel/"]',
                'div[role="banner"]',
                'div[data-testid="header"]'
            ]
            
            for selector in overlapping_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        self.driver.execute_script("arguments[0].style.display = 'none';", element)
                except:
                    continue
                    
            self._sleep(0.5, 1)
        except Exception as e:
            print(f"⚠️ Could not handle overlapping elements: {e}")

    def _restore_overlapping_elements(self):
        """Restore previously hidden overlapping elements."""
        try:
            # Restore common overlapping elements
            overlapping_selectors = [
                'a[aria-label="Reels"]',
                'a[href*="/reel/"]',
                'div[role="banner"]',
                'div[data-testid="header"]'
            ]
            
            for selector in overlapping_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        self.driver.execute_script("arguments[0].style.display = '';", element)
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Could not restore overlapping elements: {e}")

    def _detect_product_type(self, title, category):
        """Detect product type from title and category with improved logic."""
        title_lower = title.lower()
        category_lower = category.lower()

        print(f"🔍 Analyzing title: '{title}'")
        print(f"🔍 Analyzing category: '{category}'")

        # CHECK FOR GRASS FIRST - Priority for user's products
        # Check for artificial grass keywords (most specific for user's business)
        grass_keywords = ['artificial grass', 'fake grass', 'astro turf', 'synthetic grass', 'turf', 'grass', 'lawn', 'astro', 'fake lawn', 'synthetic lawn']
        grass_score = sum(1 for keyword in grass_keywords if keyword in title_lower)

        # Also check category for garden/outdoor indicators
        is_garden_category = 'garden' in category_lower or 'decor' in category_lower or 'outdoor' in category_lower

        if grass_score > 0 or is_garden_category:
            print(f"✅ Detected ARTIFICIAL GRASS (score: {grass_score}, garden category: {is_garden_category})")
            return 'artificial_grass'

        # Check for composite decking keywords
        decking_keywords = ['decking', 'composite', 'board', 'plank', 'timber', 'wood', 'deck', 'composite board']
        decking_score = sum(1 for keyword in decking_keywords if keyword in title_lower)
        if decking_score > 0:
            print(f"✅ Detected COMPOSITE DECKING (score: {decking_score})")
            return 'composite_decking'

        # Check for carpet keywords LAST - with exclusions to prevent false positives
        # Exclude if grass/lawn/turf/astro detected (prevents grass from being classified as carpet)
        grass_exclusions = ['grass', 'lawn', 'turf', 'astro', 'synthetic']
        has_grass_indicator = any(exclusion in title_lower for exclusion in grass_exclusions)

        if not has_grass_indicator:
            # More specific carpet keywords - removed generic terms like 'pile' and 'flooring'
            carpet_keywords = ['carpet', 'rug', 'underlay', 'felt', 'backing', 'twist pile', 'saxony', 'berber', 'carpet like']
            carpet_score = sum(1 for keyword in carpet_keywords if keyword in title_lower)

            if carpet_score > 0 or 'carpet' in category_lower or 'rug' in category_lower:
                print(f"✅ Detected CARPET (score: {carpet_score})")
                return 'carpet'

        # Default fallback - be conservative
        print("⚠️ Could not detect product type, using general")
        return 'general'

    def _generate_product_specific_description(self, product_type, original_title, original_description, ai_elements=None):
        """Generate product-specific description based on detected product type with AI elements."""
        try:
            if product_type == 'carpet':
                return self._generate_carpet_description(original_title, original_description, ai_elements)
            elif product_type == 'artificial_grass':
                return self._generate_artificial_grass_description(original_title, original_description, ai_elements)
            elif product_type == 'composite_decking':
                return self._generate_decking_description(original_title, original_description, ai_elements)
            else:
                # Fallback to artificial grass
                return self._generate_artificial_grass_description(original_title, original_description, ai_elements)
        except Exception as e:
            print(f"⚠️ Error generating product-specific description: {e}")
            return {
                'success': True,
                'variation': original_description,
                'type': 'fallback_original'
            }

    def _generate_carpet_description(self, original_title, original_description, ai_elements=None):
        """Generate carpet-specific description with AI-enhanced features."""
        
        # Carpet-specific options
        delivery_options = [
            "Fast Delivery: 2–4 days 🚛",
            "Quick Delivery: 2-4 days 🚚",
            "Express Delivery: 2-4 days 📦",
            "Fast Shipping: 2-4 days ⚡"
        ]
        
        sample_options = [
            "✅ FREE samples available – message us today",
            "🎁 Free samples offered",
            "📋 Free samples available",
            "✨ Free samples available"
        ]
        
        backing_options = [
            "Felt Backed available",
            "Action Backed available", 
            "Hessian Backed available"
        ]
        
        material_options = [
            "All bleachable and 100% polypropylene",
            "100% polypropylene - all bleachable",
            "Bleachable 100% polypropylene",
            "100% polypropylene material - bleachable"
        ]
        
        size_options = [
            "Rolls in 4m & 5m sizes ✂️",
            "Available in 4m & 5m widths 📏",
            "4m & 5m widths available 📐",
            "4m & 5m wide rolls 📊"
        ]
        
        color_options = [
            "30+ colours available 🏡",
            "30+ colours to choose from 🌈",
            "Wide range of colours available 🎨",
            "30+ colour options 🎨"
        ]
        
        # Add AI-detected features if available
        ai_features = []
        if ai_elements:
            for element in ai_elements:
                if any(keyword in element.lower() for keyword in ['grey', 'gray', 'brown', 'blue', 'red', 'black']):
                    ai_features.append(f"AI-detected: {element.title()} color")
                elif 'soft' in element.lower() or 'plush' in element.lower():
                    ai_features.append(f"AI-detected: {element.title()} texture")
        
        # Build description parts
        description_parts = [
            random.choice(delivery_options),
            random.choice(sample_options),
            ""
        ]
        
        # Add AI features if available
        if ai_features:
            description_parts.extend(ai_features)
            description_parts.append("")
        
        description_parts.extend([
            "Felt Backed available",
            "Action Backed available", 
            "Hessian Backed available",
            random.choice(material_options),
            "",
            random.choice(size_options),
            random.choice(color_options),
            "",
            "Message me for more info or to order!"
        ])
        
        return {
            'success': True,
            'variation': '\n'.join(description_parts),
            'type': 'carpet_specific'
        }

    def _generate_artificial_grass_description(self, original_title, original_description, ai_elements=None):
        """Generate artificial grass-specific description with AI-enhanced features."""
        
        # Artificial grass-specific options
        delivery_options = [
            "🚀 Lightning Fast Delivery: 2-4 days",
            "⚡ Super Quick Delivery: 2-4 days", 
            "📦 Express Shipping: 2-4 days",
            "🚛 Priority Delivery: 2-4 days",
            "📮 Rapid Transit: 2-4 days"
        ]
        
        sample_options = [
            "✅ Free Samples Available",
            "🎁 Free Samples Available",
            "📋 Free Samples Available",
            "🆓 Free Samples Available",
            "✨ Free Samples Available"
        ]
        
        options_intros = [
            "💰 Options Available:",
            "💷 Options Available:",
            "💵 Options Available:",
            "💸 Options Available:",
            "💳 Options Available:"
        ]
        
        # Artificial grass specific features
        warranty_options = [
            "10 year warranty on UV",
            "10 year UV warranty",
            "10 year UV protection warranty",
            "10 year warranty against UV damage",
            "10 year UV resistance warranty"
        ]
        
        backing_options = [
            "Latex backing",
            "Premium latex backing",
            "High quality latex backing",
            "Durable latex backing",
            "Professional latex backing"
        ]
        
        safety_options = [
            "No harmful chemicals like zinc, benzene or arsenic",
            "Free from harmful chemicals like zinc, benzene or arsenic",
            "Safe - no harmful chemicals like zinc, benzene or arsenic",
            "Chemical-free - no zinc, benzene or arsenic",
            "Non-toxic - no harmful chemicals like zinc, benzene or arsenic"
        ]
        
        friendly_options = [
            "Child and pet friendly",
            "Safe for children and pets",
            "Child and pet safe",
            "Family and pet friendly",
            "Safe for kids and pets"
        ]
        
        drainage_options = [
            "Larger drainage holes for proper drainage",
            "Enhanced drainage holes for better drainage",
            "Improved drainage holes for optimal drainage",
            "Superior drainage holes for excellent drainage",
            "Advanced drainage holes for perfect drainage"
        ]
        
        delivery_collection_options = [
            "Delivery & Collection available",
            "Delivery and Collection available",
            "Delivery & Collection service available",
            "Delivery and Collection service available",
            "Delivery & Collection options available"
        ]
        
        # Add AI-detected features if available
        ai_features = []
        if ai_elements:
            for element in ai_elements:
                if any(keyword in element.lower() for keyword in ['green', 'lush', 'natural', 'vibrant']):
                    ai_features.append(f"AI-detected: {element.title()} appearance")
                elif 'grass' in element.lower() or 'lawn' in element.lower():
                    ai_features.append(f"AI-detected: {element.title()} texture")
        
        new_description_parts = [
            random.choice(delivery_options),
            random.choice(sample_options),
            ""
        ]
        
        # Add AI features if available
        if ai_features:
            new_description_parts.extend(ai_features)
            new_description_parts.append("")
        
        new_description_parts.extend([
            random.choice(options_intros),
            "- Budget Range (30mm)",
            "- Mid Range (40mm)",
            "- Premium Range (50mm)",
            "",
            f"✨ {random.choice(warranty_options)}",
            f"🛡️ {random.choice(backing_options)}",
            f"🌱 {random.choice(safety_options)}",
            f"👶 {random.choice(friendly_options)}",
            f"💧 {random.choice(drainage_options)}",
            f"🚚 {random.choice(delivery_collection_options)}"
        ])
        
        return {
            'success': True,
            'variation': '\n'.join(new_description_parts),
            'type': 'artificial_grass_specific'
        }

    def _generate_decking_description(self, original_title, original_description, ai_elements=None):
        """Generate composite decking-specific description with AI-enhanced features."""
        
        # Decking-specific options
        delivery_options = [
            "Fast Delivery: 2–4 days 🚛",
            "Quick Delivery: 2-4 days 🚚",
            "Express Delivery: 2-4 days 📦"
        ]
        
        sample_options = [
            "✅ FREE samples available – message us today",
            "🎁 Free samples offered",
            "📋 Free samples available",
            "✨ Free samples available"
        ]
        
        decking_features = [
            "✨ Why Choose Our Decking?",
            "🏗️ Premium Decking Features:",
            "⭐ Decking Highlights:",
            "🔧 Quality Decking Features:"
        ]
        
        size_options = [
            "✔ Size: 4.8m x 150mm x 25mm",
            "✔ Size: 3.6m x 150mm x 25mm",
            "✔ Size: 5.4m x 150mm x 25mm",
            "✔ Size: 4.2m x 150mm x 25mm"
        ]
        
        feature_options = [
            "✔ Grooved Anti-Slip Surface – Ideal for wet conditions",
            "✔ No Rot, No Warping – Engineered for durability", 
            "✔ Zero Upkeep Needed – No staining or maintenance required",
            "✔ Woodgrain Embossed Finish – Classic timber appearance",
            "✔ UV stabilised",
            "✔ Pet Friendly",
            "✔ Low maintenance, anti-slip surface, realistic woodgrain finish – built for UK weather"
        ]
        
        warranty_options = [
            "🛡️ 10 year warranty",
            "🛡️ 10 year guarantee",
            "🛡️ 10 year manufacturer warranty"
        ]
        
        delivery_options_final = [
            "🚚 Free Delivery on Orders Over £190 – Straight to your door",
            "🚚 Free delivery available",
            "🚚 Delivery & Collection available"
        ]
        
        # Add AI-detected features if available
        ai_features = []
        if ai_elements:
            for element in ai_elements:
                if any(keyword in element.lower() for keyword in ['brown', 'wood', 'grain', 'natural']):
                    ai_features.append(f"AI-detected: {element.title()} appearance")
                elif 'wood' in element.lower() or 'grain' in element.lower():
                    ai_features.append(f"AI-detected: {element.title()} texture")
        
        # Build description parts
        description_parts = [
            "Message for a quote",
            ""
        ]
        
        # Add AI features if available
        if ai_features:
            description_parts.extend(ai_features)
            description_parts.append("")
        
        description_parts.extend([
            random.choice(decking_features),
            "",
            random.choice(size_options),
            random.choice(feature_options),
            random.choice(feature_options),
            random.choice(feature_options),
            random.choice(feature_options),
            "",
            random.choice(sample_options),
            random.choice(delivery_options_final)
        ])
        
        return {
            'success': True,
            'variation': '\n'.join(description_parts),
            'type': 'decking_specific'
        }

    def _find_listing_by_title(self, title):
        """Find listing by title using proven method."""
        try:
            print(f"🔍 Searching for listing with title: '{title}'")
            
            # Look for listing with exact title match using multiple strategies
            exact_match_found = False
            listing_element = None
            
            # Strategy 1: Look for listing container that contains the title
            print(f"🔍 Searching for listing container with exact title: '{title}'")
            listing_containers = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="x1yztbdb"]')
            for container in listing_containers:
                try:
                    if title in container.text:
                        print(f"🎯 Found listing container with title: '{title}'")
                        listing_element = container
                        exact_match_found = True
                        break
                except:
                    continue
            
            # Strategy 2: Look for exact text match in spans and click parent container
            if not exact_match_found:
                print(f"🔍 Searching for span with exact title: '{title}'")
                all_spans = self.driver.find_elements(By.TAG_NAME, 'span')
                
                for span in all_spans:
                    try:
                        span_text = span.text.strip()
                        if span_text == title and len(span_text) > 0:
                            print(f"🎯 Found exact title match in span: '{span_text}'")
                            # Try to get the parent container
                            try:
                                parent = span.find_element(By.XPATH, "./ancestor::div[contains(@class, 'x1yztbdb')]")
                                listing_element = parent
                            except:
                                listing_element = span
                            exact_match_found = True
                            break
                    except:
                        continue
            
            # Strategy 3: If not found, try looking in div elements
            if not exact_match_found:
                print("🔍 Trying div elements for title match...")
                all_divs = self.driver.find_elements(By.TAG_NAME, 'div')
                
                for div in all_divs:
                    try:
                        div_text = div.text.strip()
                        if div_text == title and len(div_text) > 0:
                            print(f"🎯 Found exact title match in div: '{div_text}'")
                            listing_element = div
                            exact_match_found = True
                            break
                    except:
                        continue
            
            # Strategy 4: If still not found, try XPath with exact text match
            if not exact_match_found:
                print("🔍 Trying XPath exact text match...")
                try:
                    exact_element = self.driver.find_element(By.XPATH, f'//*[text()="{title}"]')
                    print(f"🎯 Found exact title match via XPath: '{title}'")
                    listing_element = exact_element
                    exact_match_found = True
                except:
                    pass
            
            if not exact_match_found:
                print(f"ℹ️ No exact title match found for: '{title}'")
                print("📋 Available listings on page:")
                # Show what listings are actually available
                try:
                    listing_texts = []
                    all_spans = self.driver.find_elements(By.TAG_NAME, 'span')
                    for span in all_spans[:20]:  # Check first 20 spans
                        try:
                            text = span.text.strip()
                            if len(text) > 5 and len(text) < 100:  # Reasonable title length
                                listing_texts.append(text)
                        except:
                            continue
                    
                    for i, text in enumerate(set(listing_texts)[:5]):  # Show up to 5 unique listings
                        print(f"  {i+1}. '{text}'")
                except:
                    pass
                return None
            
            return listing_element
                
        except Exception as e:
            print(f"⚠️ Error finding listing by title: {e}")
            return None

    def create_new_listing(self, listing_data):
        """Create a new listing on Facebook Marketplace using robust selectors."""
        try:
            print("🚀 Starting to create new listing...")
            
            # Check if we're already on the create page (after deletion)
            current_url = self.driver.current_url
            if "marketplace/create" not in current_url:
                print("🔗 Navigating to create listing page...")
                self.driver.get("https://www.facebook.com/marketplace/create/")
                self._sleep(3, 5)
                
                # Handle mobile redirect
                current_url = self.driver.current_url
                if "m.facebook.com" in current_url:
                    print("📱 Detected mobile redirect on create page, forcing desktop...")
                    self.driver.get("https://www.facebook.com/marketplace/create/")
                    self._sleep(3, 5)
            else:
                print("✅ Already on create listing page")
            
            # Some layouts land directly on the item form.
            def _listing_form_present():
                selectors = [
                    (By.XPATH, "//label//*[text()='Title']/ancestor::label"),
                    (By.XPATH, "//label//*[text()='Price']/ancestor::label"),
                    (By.XPATH, "//textarea[contains(@aria-label, 'Description')]"),
                    (By.XPATH, "//input[contains(@aria-label, 'Title')]"),
                    (By.XPATH, "//input[contains(@aria-label, 'Price')]")
                ]
                for by, selector in selectors:
                    try:
                        if self.driver.find_elements(by, selector):
                            return True
                    except Exception:
                        continue
                return False

            if not _listing_form_present():
                # Click "Item for sale" using robust selector
                print("🔍 Looking for 'Item for sale' button...")
                item_for_sale_selectors = [
                    "//span[normalize-space()='Item for sale']/ancestor::div[@role='button']",
                    "//span[normalize-space()='Item for Sale']/ancestor::div[@role='button']",
                    "//span[contains(., 'Item for sale')]/ancestor::div[@role='button']",
                    "//div[contains(@aria-label, 'Item for sale')]",
                    "//div[contains(@aria-label, 'Item for Sale')]"
                ]

                item_clicked = False
                for selector in item_for_sale_selectors:
                    try:
                        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        self._safe_click(element)
                        print("✅ Clicked 'Item for sale' button")
                        item_clicked = True
                        break
                    except Exception:
                        continue

                if not item_clicked:
                    # Fallback: go directly to item create URL
                    print("⚠️ 'Item for sale' button not found. Opening item create URL...")
                    self.driver.get("https://www.facebook.com/marketplace/create/item")
                    self._sleep(3, 5)

            if not _listing_form_present():
                raise Exception("Could not reach item listing form")
            
            self._sleep(2, 3)
            
            # Store original listing content securely
            account = listing_data.get('account', 'unknown')
            original_title = listing_data.get('title', '')
            original_description = listing_data.get('description', '')
            
            # Get the TRUE original title from storage (not the current title)
            try:
                stored_original = self.content_manager.get_original_listing(account, original_title)
                if stored_original:
                    true_original_title = stored_original.get('title', original_title)
                    true_original_description = stored_original.get('description', original_description)
                    print(f"🔍 Found true original title: {true_original_title}")
                    print(f"🔍 Found true original description: {true_original_description[:50]}...")
                else:
                    true_original_title = original_title
                    true_original_description = original_description
                    print(f"⚠️ No stored original found, using current: {original_title}")
            except Exception as e:
                print(f"⚠️ Error getting true original: {e}")
                true_original_title = original_title
                true_original_description = original_description
            
            print("💾 Storing original listing content securely...")
            storage_result = self.content_manager.store_original_listing(account, listing_data)
            if storage_result['success']:
                print(f"✅ Stored original listing: {storage_result['message']}")
                print(f"   📁 Listing ID: {storage_result['listing_id']}")
                print(f"   🖼️ Images stored: {storage_result['images_stored']}")
            else:
                print(f"⚠️ Failed to store original listing: {storage_result['error']}")
            
            ai_enabled = listing_data.get('ai_enabled', True)
            if isinstance(ai_enabled, str):
                ai_enabled = ai_enabled.strip().lower() in ['true', '1', 'yes', 'on']

            print(f"🤖 AI content generation: {'enabled' if ai_enabled else 'disabled'}")

            title_result = {'success': False}
            description_result = {'success': False}
            product_type = 'general'
            ai_elements = []

            if ai_enabled:
                # AI image analysis for better context (optional)
                try:
                    from ai_image_analyzer import AIImageAnalyzer
                    ai_analyzer = AIImageAnalyzer()

                    image_paths = listing_data.get('image_paths', [])
                    if image_paths and isinstance(image_paths, list):
                        print(f"🤖 Running AI image analysis on {len(image_paths)} images...")
                        ai_analysis = ai_analyzer.analyze_listing_images(image_paths)

                        if ai_analysis.get('success'):
                            product_type = ai_analysis.get('product_type', 'general')
                            ai_elements = ai_analysis.get('description_elements', [])
                            ai_confidence = ai_analysis.get('confidence', 0)
                            print(f"🤖 AI detected: {product_type} (confidence: {ai_confidence:.2f})")
                        else:
                            print(f"⚠️ AI analysis failed: {ai_analysis.get('error', 'Unknown error')}")
                    else:
                        print("⚠️ No images available for AI analysis")
                except Exception as e:
                    print(f"⚠️ AI image analysis error: {e}")

                if product_type == 'general':
                    product_type = self._detect_product_type(true_original_title, listing_data.get('category', ''))

                context = {
                    'title': true_original_title,
                    'category': listing_data.get('category', ''),
                    'product_type': product_type,
                    'image_elements': ai_elements
                }

                print("🔄 Generating AI-based title and description...")
                print(f"   📌 Input original title: {true_original_title}")
                title_result = self._generate_unique_title(true_original_title, account, allow_traditional=False)
                print(f"   📌 AI result: {title_result}")
                description_result = self._generate_unique_description(
                    true_original_description,
                    account,
                    context=context,
                    allow_traditional=False
                )

                generated_title = title_result['new_title'] if title_result.get('success') else true_original_title

                # SAFETY: Remove duplications and enforce character limit using title_variator
                generated_title = self.title_variator._ensure_title_length_limit(generated_title, 100)

                # Additional manual duplication check as extra safety
                words = generated_title.split()
                if len(words) >= 6:
                    # Check for pattern: "ABC ABC" duplication
                    chunk_size = len(words) // 2
                    chunk1 = ' '.join(words[:chunk_size])
                    chunk2 = ' '.join(words[chunk_size:chunk_size*2])
                    if chunk1 == chunk2:
                        generated_title = chunk1
                        print(f"⚠️ [FINAL CHECK] Removed title duplication!")

                listing_data['title'] = generated_title
                print(f"📝 Using title: {listing_data['title']} (length: {len(listing_data['title'])})")

                base_description = description_result['new_description'] if description_result.get('success') else true_original_description

                # Apply account-specific writing style for known product types only
                if product_type in ['carpet', 'artificial_grass', 'composite_decking']:
                    try:
                        from account_writing_styles import AccountWritingStyles
                        account_name = self.cookies_path.split(os.sep)[-2] if os.sep in self.cookies_path else 'default'
                        style_manager = AccountWritingStyles(account_name)

                        styled_description = style_manager.format_description(base_description, product_type)
                        listing_data['description'] = styled_description
                        print(f"✅ Applied {style_manager.style} writing style for account: {account_name}")
                        print(f"📝 Styled description (first 150 chars): {styled_description[:150]}...")
                    except Exception as style_error:
                        print(f"⚠️ Failed to apply writing style: {style_error}")
                        listing_data['description'] = base_description
                else:
                    listing_data['description'] = base_description
            else:
                listing_data['title'] = true_original_title
                listing_data['description'] = true_original_description
                print("🧾 AI disabled - using original title and description")
            
            # Process images with metadata modification and cropping (always use originals)
            print("🔄 Starting image processing pipeline...")
            print(f"   📁 Input images: {listing_data['image_paths']}")
            print(f"   👤 Account: {account}")
            print(f"   📝 Title: {original_title}")
            
            processed_image_paths = self._process_images_with_metadata(
                listing_data['image_paths'], 
                account=account, 
                listing_title=original_title,
                use_originals=True
            )
            
            print(f"   📤 Processed images: {processed_image_paths}")
            
            # Final safety check: ensure we have valid images
            if not processed_image_paths:
                print("⚠️ No processed images returned, using original images as fallback")
                processed_image_paths = listing_data['image_paths']
            
            # Validate all images exist
            valid_processed = []
            for i, path in enumerate(processed_image_paths):
                if os.path.exists(path):
                    valid_processed.append(path)
                    print(f"   ✅ Image {i+1}: {os.path.basename(path)}")
                else:
                    print(f"   ❌ Image {i+1}: {os.path.basename(path)} - FILE NOT FOUND")
            
            if not valid_processed:
                print("❌ No valid images found after processing")
                print("🔄 Attempting to find any images in account directory...")
                
                # Last resort: find any images in account directory
                account_dir = os.path.join('accounts', account)
                if os.path.exists(account_dir):
                    for root, dirs, files in os.walk(account_dir):
                        for file in files:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                                image_path = os.path.join(root, file)
                                if os.path.exists(image_path):
                                    valid_processed.append(image_path)
                                    if len(valid_processed) >= 3:  # Limit to 3 images
                                        break
                        if len(valid_processed) >= 3:
                            break
                
                if valid_processed:
                    print(f"✅ Found {len(valid_processed)} fallback images")
                else:
                    raise Exception("No valid images found anywhere for upload")
            
            processed_image_paths = valid_processed
            
            # Upload images using robust method
            print("📸 Uploading processed images...")
            
            # Debug: Check if processed images exist
            print(f"🔍 Checking {len(processed_image_paths)} processed images...")
            valid_images = []
            for i, image_path in enumerate(processed_image_paths):
                if os.path.exists(image_path):
                    file_size = os.path.getsize(image_path)
                    print(f"   ✅ Image {i+1}: {os.path.basename(image_path)} ({file_size:,} bytes)")
                    valid_images.append(image_path)
                else:
                    print(f"   ❌ Image {i+1}: {os.path.basename(image_path)} - FILE NOT FOUND")
            
            if not valid_images:
                print("❌ No valid processed images found!")
                print("🔄 Falling back to original images...")
                valid_images = listing_data['image_paths']
                
                # Check original images
                for i, image_path in enumerate(valid_images):
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        print(f"   ✅ Original {i+1}: {os.path.basename(image_path)} ({file_size:,} bytes)")
                    else:
                        print(f"   ❌ Original {i+1}: {os.path.basename(image_path)} - FILE NOT FOUND")
            
            if not valid_images:
                print("❌ No valid images found for upload")
                print("🔍 Checking if we can find any images in the accounts directory...")
                
                # Try to find any images in the account directory
                account_dir = os.path.join('accounts', account)
                if os.path.exists(account_dir):
                    for root, dirs, files in os.walk(account_dir):
                        for file in files:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                                image_path = os.path.join(root, file)
                                if os.path.exists(image_path):
                                    print(f"   📸 Found image: {image_path}")
                                    valid_images.append(image_path)
                                    if len(valid_images) >= 3:  # Limit to 3 images
                                        break
                        if len(valid_images) >= 3:
                            break
                
                if valid_images:
                    print(f"✅ Found {len(valid_images)} images in account directory")
                else:
                    print("❌ No images found anywhere")
                    raise Exception("No valid images found for upload")
            
            # Convert all paths to absolute paths (required by Selenium)
            absolute_paths = []
            for image_path in valid_images:
                if not os.path.isabs(image_path):
                    abs_path = os.path.abspath(image_path)
                    print(f"   📁 Converting to absolute: {image_path} → {abs_path}")
                    absolute_paths.append(abs_path)
                else:
                    absolute_paths.append(image_path)
            
            image_paths = '\n'.join(absolute_paths)
            print(f"📤 Uploading {len(absolute_paths)} images to Facebook...")
            print(f"   📁 Using absolute paths for Selenium compatibility")
            
            file_input_selectors = [
                'input[accept="image/*,image/heif,image/heic"]',
                'input[type="file"]',
                'input[accept*="image"]'
            ]
            
            images_uploaded = False
            for selector in file_input_selectors:
                try:
                    print(f"🔍 Trying file input selector: {selector}")
                    file_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"📤 Sending {len(absolute_paths)} absolute image paths to file input...")
                    
                    # Verify all paths exist before sending
                    for i, path in enumerate(absolute_paths):
                        if os.path.exists(path):
                            print(f"   ✅ Path {i+1}: {os.path.basename(path)} exists")
                        else:
                            print(f"   ❌ Path {i+1}: {os.path.basename(path)} - FILE NOT FOUND")
                            raise Exception(f"Image file not found: {path}")
                    
                    # Send the absolute paths to the file input
                    file_input.send_keys(image_paths)
                    print("✅ Images uploaded successfully")
                    images_uploaded = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to upload with selector {selector}: {e}")
                    # If it's a path issue, try to fix it
                    if "path is not absolute" in str(e):
                        print("   🔧 Detected relative path issue, trying to fix...")
                        # The paths should already be absolute, but let's double-check
                        for i, path in enumerate(absolute_paths):
                            if not os.path.isabs(path):
                                abs_path = os.path.abspath(path)
                                print(f"   📁 Converting path {i+1}: {path} → {abs_path}")
                                absolute_paths[i] = abs_path
                        image_paths = '\n'.join(absolute_paths)
                        print("   🔄 Retrying with corrected paths...")
                        try:
                            file_input.send_keys(image_paths)
                            print("✅ Images uploaded successfully on retry")
                            images_uploaded = True
                            break
                        except Exception as retry_e:
                            print(f"   ❌ Retry failed: {retry_e}")
                    continue
            
            if not images_uploaded:
                print("❌ All file input selectors failed")
                print("🔍 Available elements on page:")
                try:
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
                    print(f"   Found {len(file_inputs)} file input elements")
                    for i, inp in enumerate(file_inputs):
                        try:
                            print(f"   Input {i+1}: {inp.get_attribute('accept')} - {inp.get_attribute('aria-label')}")
                        except:
                            print(f"   Input {i+1}: Could not get attributes")
                except Exception as debug_e:
                    print(f"   Debug error: {debug_e}")
                raise Exception("Could not upload images")
            
            self._sleep(3, 5)
            
            # Fill title using robust XPath
            print("📝 Filling title...")
            title_selectors = [
                "//span[text()='Title']/following-sibling::input",
                "//span[text()='Title']/following::input[1]",
                'input[aria-label="Title"]'
            ]

            # SAFETY CHECK: Ensure title is valid and not duplicated
            original_title = listing_data['title']

            # Remove any accidental duplications (if title appears multiple times in a row)
            words = original_title.split()

            # Check for triple duplication first (more specific)
            if len(words) >= 9:
                chunk_size = len(words) // 3
                chunk1 = ' '.join(words[:chunk_size])
                chunk2 = ' '.join(words[chunk_size:chunk_size*2])
                chunk3 = ' '.join(words[chunk_size*2:chunk_size*3])

                if chunk1 == chunk2 == chunk3:
                    listing_data['title'] = chunk1
                    print(f"⚠️ [FORM FILL] Detected TRIPLE duplication! Fixed to: {listing_data['title']}")

            # Check for double duplication
            if len(words) >= 6:
                chunk_size = len(words) // 2
                chunk1 = ' '.join(words[:chunk_size])
                chunk2 = ' '.join(words[chunk_size:chunk_size*2])

                if chunk1 == chunk2:
                    listing_data['title'] = chunk1
                    print(f"⚠️ [FORM FILL] Detected DOUBLE duplication! Fixed to: {listing_data['title']}")

            # Enforce Facebook's 100 character limit
            if len(listing_data['title']) > 100:
                # Truncate at word boundary
                words = listing_data['title'].split()
                truncated = ""
                for word in words:
                    if len(truncated + " " + word) <= 100:
                        truncated += (" " + word) if truncated else word
                    else:
                        break
                listing_data['title'] = truncated if truncated else listing_data['title'][:100]
                print(f"⚠️ Title too long! Truncated to: {listing_data['title']}")

            # Normalize superscript characters to prevent verification issues
            listing_data['title'] = listing_data['title'].replace('²', '2').replace('³', '3').replace('¹', '1')

            print(f"✅ Final title to use: {listing_data['title']} (length: {len(listing_data['title'])})")

            title_filled = False
            for selector in title_selectors:
                try:
                    if selector.startswith("//"):
                        title_input = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                    self._safe_click(title_input)
                    # Use a more robust method that simulates real typing
                    try:
                        # Clear the field first
                        title_input.clear()
                        self._sleep(0.2, 0.5)

                        # ABSOLUTE FINAL CHECK - Last defense before typing
                        title_text = listing_data['title']

                        # Check one more time for duplication patterns
                        words = title_text.split()
                        if len(words) >= 6:
                            half = len(words) // 2
                            first_half = ' '.join(words[:half])
                            second_half = ' '.join(words[half:half*2])
                            if first_half == second_half:
                                title_text = first_half
                                print(f"🚨 [LAST DEFENSE] Caught duplication right before typing!")
                                print(f"   Using: {title_text}")

                        # Ensure length limit one final time
                        if len(title_text) > 100:
                            words = title_text.split()
                            truncated = ""
                            for word in words:
                                if len(truncated + " " + word) <= 100:
                                    truncated += (" " + word) if truncated else word
                                else:
                                    break
                            title_text = truncated if truncated else title_text[:100]
                            print(f"🚨 [LAST DEFENSE] Truncated to: {title_text}")

                        print(f"⌨️ About to type: '{title_text}' (length: {len(title_text)})")

                        # Type the title character by character to simulate real human typing
                        for char in title_text:
                            title_input.send_keys(char)
                            self._sleep(0.05, 0.15)  # Slower, more human-like delay between characters

                        print(f"✅ Title filled using character-by-character typing: {title_text}")

                        # Verify the value was actually set
                        self._sleep(0.5, 1.0)  # Wait for field to update
                        actual_value = title_input.get_attribute('value')

                        # Normalize for comparison (handle superscript characters)
                        def normalize_for_comparison(text):
                            return text.replace('²', '2').replace('³', '3').replace('¹', '1')

                        expected_normalized = normalize_for_comparison(title_text)
                        actual_normalized = normalize_for_comparison(actual_value)

                        if actual_normalized == expected_normalized:
                            print(f"✅ Title verification successful: '{actual_value}'")
                        elif len(actual_value) > len(title_text) * 1.5:
                            # If actual value is way longer, it might be duplicated
                            print(f"🚨 DUPLICATION DETECTED! Expected length: {len(title_text)}, Got: {len(actual_value)}")
                            print(f"   Expected: '{title_text}'")
                            print(f"   Got: '{actual_value}'")
                            # Force clear using JavaScript
                            print("🔄 Force clearing and resetting with JavaScript...")
                            self.driver.execute_script("""
                                var element = arguments[0];
                                var value = arguments[1];
                                element.value = '';
                                element.focus();
                                element.value = value;
                                element.dispatchEvent(new Event('input', { bubbles: true }));
                                element.dispatchEvent(new Event('change', { bubbles: true }));
                            """, title_input, title_text)
                            self._sleep(0.5, 1.0)
                            actual_value = title_input.get_attribute('value')
                            print(f"✅ After JavaScript fix: '{actual_value}'")
                        else:
                            # Minor difference (like ² vs 2) - this is OK, don't retry
                            print(f"ℹ️ Minor character difference detected (expected vs actual):")
                            print(f"   Expected: '{title_text}'")
                            print(f"   Got: '{actual_value}'")
                            print(f"   This is likely just formatting (e.g., ² vs 2) - proceeding...")
                        
                        # Small delay to ensure Facebook validates the field
                        self._sleep(0.5, 1.0)
                    except Exception as typing_error:
                        print(f"⚠️ Character-by-character typing failed: {typing_error}, trying JavaScript...")
                        # Fallback to JavaScript method
                        try:
                            self.driver.execute_script("""
                                var element = arguments[0];
                                var value = arguments[1];
                                
                                // Clear the field
                                element.value = '';
                                element.focus();
                                
                                // Set the new value
                                element.value = value;
                                
                                // Trigger events to ensure Facebook detects the change
                                element.dispatchEvent(new Event('input', { bubbles: true }));
                                element.dispatchEvent(new Event('change', { bubbles: true }));
                                element.dispatchEvent(new Event('blur', { bubbles: true }));
                            """, title_input, listing_data['title'])
                            print(f"✅ Title filled using JavaScript fallback: {listing_data['title']}")
                            self._sleep(0.5, 1.0)
                        except Exception as js_error:
                            print(f"❌ All title methods failed: {js_error}")
                            raise
                    title_filled = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to fill title with selector {selector}: {e}")
                    continue
            
            if not title_filled:
                raise Exception("Could not fill title")
            
            self._sleep(1, 2)
            
            # Fill price using robust XPath
            print("💰 Filling price...")
            price_selectors = [
                "//span[text()='Price']/following-sibling::input",
                "//span[text()='Price']/following::input[1]",
                'input[aria-label="Price"]'
            ]

            price_filled = False
            for selector in price_selectors:
                try:
                    if selector.startswith("//"):
                        price_input = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        price_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                    # Scroll into view to ensure visibility
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", price_input)
                    self._sleep(0.5, 1.0)

                    self._safe_click(price_input)
                    self._sleep(0.3, 0.6)  # Wait for field to be fully focused

                    # Simple and reliable price field filling
                    try:
                        # More thorough clearing of the price field
                        price_input.clear()
                        self._sleep(0.2, 0.5)

                        # Select all text and delete to ensure complete clearing
                        price_input.send_keys(Keys.CONTROL + "a")
                        price_input.send_keys(Keys.DELETE)
                        self._sleep(0.3, 0.6)

                        # Set the price using standard send_keys
                        # CRITICAL: Only send the price value, NO enter or tab keys
                        price_input.send_keys(listing_data['price'])
                        print(f"✅ Price filled: {listing_data['price']}")

                        # Clear any pending keyboard events that might trigger unwanted actions
                        self.driver.execute_script("window.focus();")
                        self._sleep(0.2, 0.4)

                        # CRITICAL: Trigger blur event to commit the value
                        # This ensures Facebook processes the price before we move on
                        self.driver.execute_script("""
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            arguments[0].blur();
                        """, price_input)

                        # Wait for Facebook to validate the price field (increased delay)
                        self._sleep(1.5, 2.5)

                        # Re-find the element to avoid stale reference
                        if selector.startswith("//"):
                            price_input = self.driver.find_element(By.XPATH, selector)
                        else:
                            price_input = self.driver.find_element(By.CSS_SELECTOR, selector)

                        # Verify the value was actually set
                        actual_value = price_input.get_attribute('value')

                        # Clean the actual value for comparison (remove currency symbols, commas, etc.)
                        clean_expected = listing_data['price'].replace('£', '').replace(',', '').replace('$', '').strip()
                        clean_actual = actual_value.replace('£', '').replace(',', '').replace('$', '').strip()

                        if clean_actual == clean_expected:
                            print(f"✅ Price verification successful: '{actual_value}'")
                        else:
                            print(f"⚠️ Price verification failed. Expected: '{listing_data['price']}', Got: '{actual_value}'")
                            print(f"   Clean comparison - Expected: '{clean_expected}', Got: '{clean_actual}'")

                            # Try to set it again if verification failed
                            print("🔄 Retrying price field...")
                            self._safe_click(price_input)
                            self._sleep(0.3, 0.6)
                            price_input.clear()
                            price_input.send_keys(Keys.CONTROL + "a")
                            price_input.send_keys(Keys.DELETE)
                            self._sleep(0.3, 0.6)
                            price_input.send_keys(listing_data['price'])

                            # Trigger events again
                            self.driver.execute_script("""
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                arguments[0].blur();
                            """, price_input)
                            self._sleep(1.5, 2.5)

                            # Verify retry
                            if selector.startswith("//"):
                                price_input = self.driver.find_element(By.XPATH, selector)
                            else:
                                price_input = self.driver.find_element(By.CSS_SELECTOR, selector)

                            actual_value = price_input.get_attribute('value')
                            clean_actual = actual_value.replace('£', '').replace(',', '').replace('$', '').strip()
                            if clean_actual == clean_expected:
                                print(f"✅ Price retry successful: '{actual_value}'")
                            else:
                                print(f"❌ Price retry failed. Expected: '{listing_data['price']}', Got: '{actual_value}'")
                                # Try JavaScript method as last resort
                                print("🔄 Trying JavaScript method...")
                                self.driver.execute_script("""
                                    arguments[0].value = arguments[1];
                                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                    arguments[0].blur();
                                """, price_input, listing_data['price'])
                                self._sleep(1.5, 2.5)

                        # Additional delay to ensure Facebook completes validation
                        self._sleep(1.0, 2.0)

                        # Check for any validation errors that might have appeared
                        try:
                            validation_errors = self.driver.find_elements(By.CSS_SELECTOR, '[role="alert"], .error')
                            for error in validation_errors:
                                if error.is_displayed() and error.text.strip():
                                    print(f"⚠️ Validation error detected: {error.text.strip()}")
                                    raise Exception(f"Price validation error: {error.text.strip()}")
                        except:
                            pass  # No validation errors found

                    except Exception as price_error:
                        print(f"❌ Price field filling failed: {price_error}")
                        raise
                    price_filled = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to fill price with selector {selector}: {e}")
                    continue

            if not price_filled:
                raise Exception("Could not fill price")

            # CRITICAL: Detect if form was closed/navigated away after price entry
            print("🔍 Checking if we're still on the create listing page...")
            try:
                current_url = self.driver.current_url
                if 'marketplace/create' not in current_url and 'marketplace/item' not in current_url:
                    print(f"⚠️ Form closed unexpectedly! Current URL: {current_url}")
                    print(f"🔄 Navigating back to create page...")
                    self.driver.get("https://www.facebook.com/marketplace/create/item")
                    self._sleep(3, 5)
                    raise Exception("Form was closed after price entry - you may need to adjust timing or check for popup blockers")
                else:
                    print(f"✅ Still on create page: {current_url}")
            except Exception as url_check_error:
                print(f"⚠️ URL check failed: {url_check_error}")

            # Final verification that both fields still have their values
            print("🔍 Final verification of title and price fields...")
            try:
                # Check title field with multiple selectors
                title_field = None
                title_field_selectors = [
                    'input[aria-label="Title"]',
                    "//span[text()='Title']/following-sibling::input",
                    "//span[text()='Title']/following::input[1]",
                    'input[placeholder*="Title"]'
                ]

                for selector in title_field_selectors:
                    try:
                        if selector.startswith("//"):
                            found_fields = self.driver.find_elements(By.XPATH, selector)
                        else:
                            found_fields = self.driver.find_elements(By.CSS_SELECTOR, selector)

                        if found_fields and found_fields[0].is_displayed():
                            title_field = found_fields
                            break
                    except:
                        continue

                if title_field:
                    title_value = title_field[0].get_attribute('value')
                    if title_value == listing_data['title']:
                        print(f"✅ Title field verified: '{title_value}'")
                    else:
                        print(f"⚠️ Title field lost value. Expected: '{listing_data['title']}', Got: '{title_value}'")
                        # Try to refill if lost with multiple strategies
                        print("🔄 Refilling title field...")
                        title_field[0].clear()
                        self._sleep(0.2, 0.4)
                        title_field[0].send_keys(listing_data['title'])
                        self._sleep(0.5, 1.0)
                        # Verify refill worked
                        title_value = title_field[0].get_attribute('value')
                        if title_value != listing_data['title']:
                            # Try JavaScript method
                            self.driver.execute_script("""
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            """, title_field[0], listing_data['title'])
                            self._sleep(0.5, 1.0)
                            title_value = title_field[0].get_attribute('value')
                            if title_value != listing_data['title']:
                                raise Exception(f"Title field refill failed. Expected: '{listing_data['title']}', Got: '{title_value}'")
                            else:
                                print(f"✅ Title refilled successfully using JavaScript")
                        else:
                            print(f"✅ Title refilled successfully")
                else:
                    print("⚠️ Title field not found for verification - may have changed, continuing...")

                # Check price field with multiple selectors
                price_field = None
                price_field_selectors = [
                    'input[aria-label="Price"]',
                    "//span[text()='Price']/following-sibling::input",
                    "//span[text()='Price']/following::input[1]",
                    'input[placeholder*="Price"]'
                ]

                for selector in price_field_selectors:
                    try:
                        if selector.startswith("//"):
                            found_fields = self.driver.find_elements(By.XPATH, selector)
                        else:
                            found_fields = self.driver.find_elements(By.CSS_SELECTOR, selector)

                        if found_fields and found_fields[0].is_displayed():
                            price_field = found_fields
                            break
                    except:
                        continue

                if price_field:
                    price_value = price_field[0].get_attribute('value')
                    clean_expected = listing_data['price'].replace('£', '').replace(',', '').replace('$', '').strip()
                    clean_actual = price_value.replace('£', '').replace(',', '').replace('$', '').strip() if price_value else ''
                    if clean_actual == clean_expected:
                        print(f"✅ Price field verified: '{price_value}'")
                    else:
                        print(f"⚠️ Price field lost value. Expected: '{listing_data['price']}', Got: '{price_value}'")
                        # Try to refill if lost with multiple strategies
                        print("🔄 Refilling price field...")
                        price_field[0].clear()
                        price_field[0].send_keys(Keys.CONTROL + "a")
                        price_field[0].send_keys(Keys.DELETE)
                        self._sleep(0.2, 0.4)
                        price_field[0].send_keys(listing_data['price'])
                        self._sleep(0.5, 1.0)
                        # Verify refill worked
                        price_value = price_field[0].get_attribute('value')
                        clean_actual = price_value.replace('£', '').replace(',', '').replace('$', '').strip() if price_value else ''
                        if clean_actual != clean_expected:
                            # Try JavaScript method
                            self.driver.execute_script("""
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            """, price_field[0], listing_data['price'])
                            self._sleep(0.5, 1.0)
                            price_value = price_field[0].get_attribute('value')
                            clean_actual = price_value.replace('£', '').replace(',', '').replace('$', '').strip() if price_value else ''
                            if clean_actual != clean_expected:
                                raise Exception(f"Price field refill failed. Expected: '{listing_data['price']}', Got: '{price_value}'")
                            else:
                                print(f"✅ Price refilled successfully using JavaScript")
                        else:
                            print(f"✅ Price refilled successfully")
                else:
                    print("⚠️ Price field not found for verification - may have changed, continuing...")

            except Exception as e:
                print(f"⚠️ Field verification warning: {e}")
                # Don't raise exception - just log warning and continue
                print("Continuing with listing creation...")

            # CRITICAL: Extra delay before interacting with other fields
            # This prevents premature form navigation/closure
            print("⏳ Waiting for form to stabilize after price entry...")
            self._sleep(2, 3)

            # Set category using robust method
            category = listing_data.get('category', 'Other Garden decor')
            self._set_category_robust(category)
            self._sleep(1, 2)
            
            # Set condition using robust method
            self._set_condition_robust("New")
            self._sleep(1, 2)
            
            # Click "More details" to reveal description and other fields (AFTER condition)
            self._click_more_details()
            self._sleep(1, 2)
            
            # Fill description using robust XPath
            print("📄 Filling description...")
            description_selectors = [
                "//span[text()='Description']/following::textarea[1]",
                "//span[text()='Description']/following::div[@contenteditable='true'][1]",
                'div[aria-label="Description"] [contenteditable="true"]'
            ]
            
            description_filled = False
            for selector in description_selectors:
                try:
                    if selector.startswith("//"):
                        desc_element = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        desc_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    
                    self._safe_click(desc_element)
                    desc_element.clear()
                    # Use a method that preserves formatting by simulating proper typing
                    try:
                        # Method 1: Try using JavaScript with proper text content setting
                        # Set the text content and then trigger events to preserve formatting
                        self.driver.execute_script("""
                            var element = arguments[0];
                            var text = arguments[1];
                            
                            // Clear the element
                            element.innerHTML = '';
                            
                            // Set the text content with proper line breaks
                            element.textContent = text;
                            
                            // Trigger focus and input events
                            element.focus();
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                        """, desc_element, listing_data['description'])
                        print("✅ Description filled using JavaScript with proper formatting")
                    except Exception as js_error:
                        print(f"⚠️ JavaScript method failed: {js_error}, trying send_keys...")
                        # Fallback to send_keys if JavaScript fails
                        desc_element.send_keys(listing_data['description'])
                        print("✅ Description filled using send_keys")
                    description_filled = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to fill description with selector {selector}: {e}")
                    continue
            
            if not description_filled:
                raise Exception("Could not fill description")
            
            self._sleep(1, 2)
            
            # Fill product tags if provided
            if listing_data.get('product_tags'):
                self._fill_product_tags_robust(listing_data['product_tags'])
                self._sleep(1, 2)
            
            # Fill location if provided
            if listing_data.get('location'):
                # Check for randomized location first
                account = listing_data.get('account', 'unknown')
                listing_id = listing_data.get('listing_id')
                
                # Try to get randomized location
                randomized_location = None
                if account and listing_id:
                    try:
                        from location_manager import LocationManager
                        location_manager = LocationManager()
                        location_data = location_manager.get_randomized_location(account, listing_id)
                        if location_data:
                            randomized_location = location_data['new_location']
                            print(f"🎯 Using randomized location: {randomized_location}")
                    except Exception as e:
                        print(f"⚠️ Error getting randomized location: {e}")
                
                # Use randomized location if available, otherwise use original
                location_to_use = randomized_location if randomized_location else listing_data['location']
                
                # Clear browser location cache before setting new location
                self._clear_location_cache()
                self._fill_location_robust(location_to_use)
                self._sleep(1, 2)
            
            # CRITICAL: Verify we're still on the create page before proceeding
            print("🔍 Final check: Verifying we're still on the create listing page...")
            try:
                current_url = self.driver.current_url
                if 'marketplace/create' not in current_url and 'marketplace/item' not in current_url:
                    print(f"❌ Form closed unexpectedly before Next/Publish! Current URL: {current_url}")
                    # Take screenshot for debugging
                    try:
                        screenshot_path = f"error_form_closed_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        print(f"📸 Screenshot saved: {screenshot_path}")
                    except:
                        pass
                    raise Exception(f"Form was closed during listing creation. Last URL: {current_url}")
                else:
                    print(f"✅ Confirmed still on create page")
            except Exception as final_url_check:
                if 'marketplace' not in str(final_url_check).lower():
                    raise

            # Try to click Next button (if it exists)
            # Some accounts (like jon) go straight to Publish without a Next button
            print("➡️ Checking for Next button...")
            next_selectors = [
                # Try text-based selector first (works for new layout)
                "//span[contains(text(),'Next')]",
                "//span[text()='Next']",
                # Try finding parent clickable element of Next text
                "//span[contains(text(),'Next')]/ancestor::div[contains(@class, 'x78zum5')]",
                "//span[contains(text(),'Next')]/ancestor::div[@role='none']",
                "//span[contains(text(),'Next')]/ancestor::div",
                # Standard aria-label selectors
                'div[aria-label="Next"]',
                '//div[@aria-label="Next"]',
                'button[aria-label="Next"]'
            ]
            
            next_clicked = False
            next_button_found = False
            
            # First, check if Next button exists
            for selector in next_selectors:
                try:
                    if selector.startswith("//"):
                        next_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if next_button and next_button.is_displayed():
                        next_button_found = True
                        print("✅ Next button found, attempting to click...")
                        break
                except:
                    continue
            
            # Only try to click if Next button was found
            if next_button_found:
                for selector in next_selectors:
                    try:
                        # Re-find element right before clicking to avoid stale element issues
                        if selector.startswith("//"):
                            next_button = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                        else:
                            next_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        
                        # Scroll into view
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", next_button)
                        self._sleep(0.5, 1)
                        
                        # Try multiple click strategies
                        click_success = False
                        
                        # Strategy 1: Direct click
                        try:
                            next_button.click()
                            print(f"✅ Next button clicked (direct): {selector[:50]}")
                            click_success = True
                        except Exception as e1:
                            # Strategy 2: JavaScript click
                            try:
                                self.driver.execute_script("arguments[0].click();", next_button)
                                print(f"✅ Next button clicked (JavaScript): {selector[:50]}")
                                click_success = True
                            except Exception as e2:
                                # Strategy 3: Try clicking parent
                                try:
                                    if next_button.tag_name == 'span':
                                        parent = next_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'x78zum5')]")
                                        self.driver.execute_script("arguments[0].click();", parent)
                                        print(f"✅ Next button clicked (parent): {selector[:50]}")
                                        click_success = True
                                except:
                                    pass
                        
                        if click_success:
                            next_clicked = True
                            break
                    except Exception as e:
                        print(f"⚠️ Failed to click Next with selector {selector[:50]}: {str(e)[:50]}")
                        continue
                
                if next_clicked:
                    self._sleep(2, 3)
                    # Handle group selection screen if it appears
                    self._handle_group_selection()
                else:
                    print("⚠️ Next button found but could not be clicked, proceeding to Publish...")
            else:
                print("ℹ️ No Next button found - this account goes straight to Publish (like jon account)")
                # Skip group selection since we're going straight to publish
            
            # Validate form before publishing
            print("🔍 Validating form before publishing...")
            try:
                # Check if there are any validation errors
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="alert"], .error, [aria-invalid="true"]')
                if error_elements:
                    print("⚠️ Found validation errors:")
                    for error in error_elements:
                        if error.text.strip():
                            print(f"   - {error.text.strip()}")
                
                # Check if required fields are filled
                title_field = self.driver.find_elements(By.CSS_SELECTOR, 'input[aria-label="Title"]')
                price_field = self.driver.find_elements(By.CSS_SELECTOR, 'input[aria-label="Price"]')
                
                if title_field and not title_field[0].get_attribute('value'):
                    print("⚠️ Title field appears to be empty")
                if price_field and not price_field[0].get_attribute('value'):
                    print("⚠️ Price field appears to be empty")
                    
            except Exception as e:
                print(f"⚠️ Could not validate form: {e}")
            
            # Click Publish button
            print("📢 Clicking Publish button...")
            
            # First, wait a moment for the page to settle
            self._sleep(1, 2)
            
            # Scroll to bottom to ensure publish button is visible
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._sleep(0.5, 1)
            
            publish_selectors = [
                # Try text-based selectors first (most reliable)
                "//span[contains(text(),'Publish')]",
                "//span[text()='Publish']",
                "//div[contains(text(),'Publish')]",
                # Try finding parent clickable element of Publish text
                "//span[contains(text(),'Publish')]/ancestor::div[contains(@class, 'x78zum5')]",
                "//span[contains(text(),'Publish')]/ancestor::div[@role='button']",
                "//span[contains(text(),'Publish')]/ancestor::div[@role='none']",
                "//span[contains(text(),'Publish')]/ancestor::div[contains(@tabindex, '0')]",
                "//span[contains(text(),'Publish')]/ancestor::div",
                # Standard aria-label selectors
                'div[aria-label="Publish"]:not([aria-disabled])',
                '//div[@aria-label="Publish" and not(@aria-disabled)]',
                'button[aria-label="Publish"]',
                'div[aria-label="Publish"]',  # Try without disabled check
                '//div[@aria-label="Publish"]',  # Try without disabled check
                'button[type="submit"]',  # Try submit button
                '[data-testid="publish-button"]',  # Test ID selector
                # Try class-based selector (exact match for jon account)
                "//span[@class='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84']"
            ]
            
            publish_clicked = False
            for selector in publish_selectors:
                try:
                    # Re-find element right before clicking to avoid stale element issues
                    if selector.startswith("//"):
                        publish_button = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        publish_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    
                    # Check if element is visible and enabled
                    if not publish_button.is_displayed():
                        print(f"⚠️ Publish button found but not visible: {selector[:50]}")
                        continue
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", publish_button)
                    self._sleep(0.8, 1.5)
                    
                    # Try multiple click strategies
                    click_success = False
                    
                    # Strategy 1: Wait for element to be clickable, then direct click
                    try:
                        if selector.startswith("//"):
                            clickable_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            clickable_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        clickable_button.click()
                        print(f"✅ Publish button clicked (direct): {selector[:50]}")
                        click_success = True
                    except Exception as e1:
                        print(f"⚠️ Direct click failed: {str(e1)[:50]}")
                        
                        # Strategy 2: Try JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", publish_button)
                            print(f"✅ Publish button clicked (JavaScript): {selector[:50]}")
                            click_success = True
                        except Exception as e2:
                            print(f"⚠️ JavaScript click failed: {str(e2)[:50]}")
                            
                            # Strategy 3: Try clicking parent element if it's a span
                            try:
                                if publish_button.tag_name == 'span':
                                    # Try to find the clickable parent div
                                    parent = publish_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'x78zum5')][1]")
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                                    self._sleep(0.5, 1)
                                    self.driver.execute_script("arguments[0].click();", parent)
                                    print(f"✅ Publish button clicked (parent): {selector[:50]}")
                                    click_success = True
                            except Exception as e3:
                                print(f"⚠️ Parent click failed: {str(e3)[:50]}")
                                
                                # Strategy 4: Try ActionChains
                                try:
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    ActionChains(self.driver).move_to_element(publish_button).pause(0.3).click().perform()
                                    print(f"✅ Publish button clicked (ActionChains): {selector[:50]}")
                                    click_success = True
                                except Exception as e4:
                                    print(f"⚠️ ActionChains click failed: {str(e4)[:50]}")
                    
                    if click_success:
                        publish_clicked = True
                        break
                    else:
                        print(f"⚠️ All click strategies failed for selector: {selector[:50]}")
                        continue
                        
                except Exception as e:
                    print(f"⚠️ Failed to find Publish with selector {selector[:50]}: {str(e)[:50]}")
                    continue
            
            if not publish_clicked:
                # Try to find any publish-related button by text
                try:
                    print("🔍 Trying to find any publish button by text...")
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    all_divs = self.driver.find_elements(By.XPATH, "//div[@role='button']")
                    all_elements = list(all_buttons) + list(all_divs)
                    
                    for element in all_elements:
                        try:
                            element_text = element.text.lower()
                            if element.is_displayed() and ("publish" in element_text or "post" in element_text):
                                if element.is_enabled() or element.get_attribute("aria-disabled") != "true":
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    self._sleep(0.5, 1)
                                    self._safe_click(element)
                                    print(f"✅ Found and clicked publish button: {element_text[:50]}")
                                    publish_clicked = True
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"⚠️ Could not find any publish button: {e}")
                
                if not publish_clicked:
                    # Take screenshot for debugging
                    try:
                        screenshot_path = f"error_publish_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        print(f"📸 Screenshot saved: {screenshot_path}")
                    except:
                        pass
                    raise Exception("Could not click Publish button - form may not be valid")
            
            self._sleep(5, 8)
            print("🎉 Listing created successfully!")

            # Clean up temporary processed images
            self._cleanup_temp_images(processed_image_paths)

            # Return the new title and description so UI can be updated
            return {
                'success': True,
                'new_title': listing_data['title'],
                'new_description': listing_data['description'],
                'original_title': original_title,
                'original_description': original_description
            }

        except Exception as e:
            print(f"❌ Error during listing creation: {e}")
            print(f"📊 Error details: {traceback.format_exc()}")
            
            # Clean up temporary images even on error
            try:
                if 'processed_image_paths' in locals():
                    self._cleanup_temp_images(processed_image_paths)
            except:
                pass
            
            # Save screenshot for debugging
            try:
                screenshot_path = f"error_create_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
            except:
                pass
            
            raise e

    def _safe_click(self, element):
        """Safely click an element with fallback methods."""
        try:
            element.click()
        except Exception:
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except Exception:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)
                element.click()

    def _set_category_robust(self, category):
        """Set the listing category by first clicking the category field, then selecting the hierarchy."""
        try:
            print(f"🏷️ Setting category to: {category}")

            # Verify we're still on the create page before attempting category selection
            try:
                current_url = self.driver.current_url
                if 'marketplace/create' not in current_url and 'marketplace/item' not in current_url:
                    print(f"❌ Not on create page before category selection! URL: {current_url}")
                    raise Exception("Form closed before category selection")
            except Exception as url_error:
                print(f"⚠️ URL verification error: {url_error}")
                raise

            # First, click on the category field to open the dropdown
            print("🔍 Clicking category field to open dropdown...")
            category_field_clicked = False
            category_field_selectors = [
                # Try the exact span class selector you provided
                "//span[@class='x1jchvi3 x1fcty0u x132q4wb x193iq5w x1al4vs7 xmper1u x1lliihq x11dcrhx xzwoauc x6ikm8r x10wlt62 x47corl x10l6tqk xlyipyv xoyzfg9 xhb22t3 x11xpdln x1r7x56h xuxw1ft xi81zsa' and text()='Category']",
                # Try finding by text "Category" (more flexible)
                "//span[text()='Category']",
                "//span[contains(text(),'Category')]",
                # Fallback selectors
                'input[placeholder="Category"]',
                'div[aria-label="Category"]',
                "//span[text()='Category']/following-sibling::input",
                "//input[contains(@placeholder, 'Category')]",
                "//div[contains(@aria-label, 'Category')]",
                'div[role="combobox"]',
                'div[data-testid*="category"]'
            ]
            
            for selector in category_field_selectors:
                try:
                    if selector.startswith("//"):
                        category_field = self.driver.find_element(By.XPATH, selector)
                    else:
                        category_field = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if category_field.is_displayed():
                        # If it's a span element, try to click the parent container
                        if category_field.tag_name == 'span':
                            try:
                                # Try to find the clickable parent
                                parent = category_field.find_element(By.XPATH, "./..")
                                self._safe_click(parent)
                                print(f"✅ Category field parent clicked (span): {selector[:50]}")
                            except:
                                # Fallback to clicking the span itself
                                self._safe_click(category_field)
                                print(f"✅ Category field clicked (span): {selector[:50]}")
                        else:
                            self._safe_click(category_field)
                            print(f"✅ Category field clicked: {selector[:50]}")

                        category_field_clicked = True
                        break
                except Exception as cat_err:
                    print(f"⚠️ Failed with selector {selector[:50]}: {str(cat_err)[:50]}")
                    continue
            
            if not category_field_clicked:
                print("⚠️ Could not find category field to click")
                return

            # Wait for dropdown to open and be visible (optimized for speed)
            self._sleep(0.8, 1.2)
            
            # Map UI categories to Facebook category hierarchy
            category_mapping = {
                "Other Garden decor": ["Patio and garden", "Garden decor", "Other Garden Decor"],
                "Other Rugs & carpets": ["Home and kitchen", "Home decor", "Rugs & carpets", "Other Rugs & carpets"]
            }

            default_path = ["Patio and garden", "Garden decor", "Other Garden Decor"]

            # Allow custom category paths (comma-separated or arrow-separated)
            custom_path = []
            if isinstance(category, str):
                if "," in category:
                    custom_path = [part.strip() for part in category.split(",") if part.strip()]
                elif "→" in category:
                    custom_path = [part.strip() for part in category.split("→") if part.strip()]
                elif ">" in category:
                    custom_path = [part.strip() for part in category.split(">") if part.strip()]

            # Get the category path for the selected category
            category_path = custom_path if custom_path else category_mapping.get(category, default_path)
            print(f"📍 Category path: {' → '.join(category_path)}")
            
            # Click through each level of the category hierarchy
            for i, category_level in enumerate(category_path):
                print(f"🔍 Clicking category level {i+1}: {category_level}")

                # Wait a bit for the dropdown menu to appear/update (optimized for speed)
                if i > 0:
                    self._sleep(0.5, 0.8)  # Wait for submenu to load
                else:
                    # Shorter wait for the initial dropdown to open
                    self._sleep(0.5, 0.8)
                
                # Find and click the category option
                category_clicked = False
                
                # First, try the simple, reliable selectors for jon account layout
                # These are the exact selectors that work for the new Facebook layout
                # Use case-insensitive matching to handle variations
                simple_selectors = {
                    "Patio and garden": [
                        "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'patio and garden')]",
                        "//span[contains(text(),'Patio and garden')]",
                        "//span[contains(text(),'Patio & Garden')]"
                    ],
                    "Garden decor": [
                        "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'garden decor')]",
                        "//span[contains(text(),'Garden decor')]",
                        "//span[contains(text(),'Garden Decor')]"
                    ],
                    "Other Garden Decor": [
                        "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'other garden decor')]",
                        "//span[contains(text(),'Other Garden Decor')]"
                    ]
                }
                
                # Try the simple selector first if available
                if category_level in simple_selectors:
                    selectors_to_try = simple_selectors[category_level]
                    print(f"🎯 Trying simple selectors for: {category_level}")
                    try:
                        # Use WebDriverWait to find the element
                        from selenium.webdriver.support.ui import WebDriverWait
                        short_wait = WebDriverWait(self.driver, 8)  # Increased timeout
                        category_element = None
                        
                        # Try each selector variation until one works
                        for selector in selectors_to_try:
                            try:
                                category_element = short_wait.until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                print(f"✅ Found element using selector: {selector[:50]}...")
                                break
                            except:
                                continue
                        
                        if not category_element:
                            raise Exception("No selector variation found the element")
                        print(f"✅ Found element for: {category_level}")
                        
                        # Scroll element into view (optimized for speed)
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});", category_element)
                        self._sleep(0.3, 0.5)  # Shorter wait after scrolling
                        
                        # Try multiple click strategies
                        click_success = False
                        
                        # Strategy 1: Try clicking the element directly
                        try:
                            category_element.click()
                            print(f"✅ Direct click successful: {category_level}")
                            click_success = True
                        except Exception as e1:
                            print(f"⚠️ Direct click failed: {str(e1)[:50]}")
                            
                            # Strategy 2: Try JavaScript click on the element
                            try:
                                self.driver.execute_script("arguments[0].click();", category_element)
                                print(f"✅ JavaScript click successful: {category_level}")
                                click_success = True
                            except Exception as e2:
                                print(f"⚠️ JavaScript click failed: {str(e2)[:50]}")
                                
                                # Strategy 3: Try clicking parent element
                                try:
                                    parent = category_element.find_element(By.XPATH, "./..")
                                    self.driver.execute_script("arguments[0].click();", parent)
                                    print(f"✅ Parent click successful: {category_level}")
                                    click_success = True
                                except Exception as e3:
                                    print(f"⚠️ Parent click failed: {str(e3)[:50]}")
                                    
                                    # Strategy 4: Try ActionChains
                                    try:
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        ActionChains(self.driver).move_to_element(category_element).click().perform()
                                        print(f"✅ ActionChains click successful: {category_level}")
                                        click_success = True
                                    except Exception as e4:
                                        print(f"⚠️ ActionChains click failed: {str(e4)[:50]}")
                        
                        if click_success:
                            category_clicked = True
                            if i < len(category_path) - 1:
                                self._sleep(0.6, 1.0)  # Optimized wait for next level to appear
                        else:
                            print(f"❌ All click strategies failed for: {category_level}")
                            
                    except Exception as e:
                        print(f"⚠️ Simple selector failed to find element: {str(e)[:100]}")
                
                # If simple selector didn't work, try alternative approaches
                if not category_clicked:
                    # Try finding the element and clicking its parent or using alternative methods
                    try:
                        # Try to find any element with the text
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{category_level}')]")
                        print(f"🔍 Found {len(elements)} elements containing '{category_level}'")
                        
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    # Scroll into view (optimized for speed)
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});", element)
                                    self._sleep(0.2, 0.4)
                                    
                                    # Try clicking the element or its clickable parent
                                    try:
                                        # Try direct click
                                        element.click()
                                        print(f"✅ Clicked element directly: {category_level}")
                                        category_clicked = True
                                        break
                                    except:
                                        # Try JavaScript click
                                        self.driver.execute_script("arguments[0].click();", element)
                                        print(f"✅ Clicked via JavaScript: {category_level}")
                                        category_clicked = True
                                        break
                            except:
                                continue
                    except Exception as e:
                        print(f"⚠️ Alternative search failed: {str(e)[:100]}")
                
                # If new layout selectors didn't work, try standard selectors
                if not category_clicked:
                    # Normalize category level for matching (handle variations)
                    normalized_level = category_level.replace("&", "and").replace("&amp;", "and")
                    category_selectors = [
                        f"//span[text()='{category_level}']",
                        f"//span[text()='{normalized_level}']",
                        f"//span[contains(text(), '{category_level}')]",
                        f"//div[contains(text(), '{category_level}')]",
                        f"//div[@role='option'][contains(text(), '{category_level}')]",
                        f"//li[contains(text(), '{category_level}')]",
                        f"//div[contains(@aria-label, '{category_level}')]",
                        f"//div[data-testid*='{category_level.lower().replace(' ', '_').replace('&', '')}']"
                    ]
                    
                    for selector in category_selectors:
                        try:
                            # Try with WebDriverWait for better reliability
                            category_element = self.wait.until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            if category_element.is_displayed():
                                # Scroll into view before clicking
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", category_element)
                                self._sleep(0.5, 1)
                                self._safe_click(category_element)
                                print(f"✅ Clicked: {category_level}")
                                category_clicked = True
                                if i < len(category_path) - 1:
                                    self._sleep(1, 2)  # Wait for next level
                                break
                        except Exception as e:
                            print(f"⚠️ Standard selector {selector} failed: {str(e)[:50]}")
                            continue
                
                if not category_clicked:
                    print(f"⚠️ Could not find category: {category_level}")
                    # Try alternative approach - look for any clickable element with the text
                    try:
                        # Look for any element containing the category text
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{category_level}')]")
                        print(f"🔍 Found {len(elements)} elements containing '{category_level}'")
                        for element in elements:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    # Scroll into view
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    self._sleep(0.5, 1)
                                    self._safe_click(element)
                                    print(f"✅ Clicked alternative element for: {category_level}")
                                    category_clicked = True
                                    if i < len(category_path) - 1:
                                        self._sleep(1, 2)  # Wait for next level
                                    break
                            except Exception as e:
                                continue
                    except Exception as e:
                        print(f"⚠️ Alternative search failed: {str(e)[:100]}")
                
                if not category_clicked:
                    print(f"❌ Failed to click category: {category_level}")
                    # Take a screenshot for debugging
                    try:
                        screenshot_path = f"error_category_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        print(f"📸 Screenshot saved: {screenshot_path}")
                    except:
                        pass
                    return
                
                # Wait for the next level to load (except for the last level)
                if i < len(category_path) - 1:
                    self._sleep(1, 2)
            
            print(f"✅ Category selection completed: {category}")
                
        except Exception as e:
            print(f"⚠️ Error setting category: {e}")

    def _set_condition_robust(self, condition):
        """Set the listing condition using fast, optimized dropdown selection."""
        try:
            print(f"🔧 Setting condition to: {condition}")
            
            # Use shorter timeout for faster selection (most common selectors first)
            from selenium.webdriver.support.ui import WebDriverWait
            short_wait = WebDriverWait(self.driver, 3)  # 3 second timeout instead of default 10-20
            
            # Try to find and click the condition dropdown (most common selectors first)
            condition_dropdown_selectors = [
                'label[aria-label="Condition"]',  # Most common
                "//span[text()='Condition']",  # Second most common
                "//label[contains(@aria-label, 'Condition')]",
                "//div[contains(@aria-label, 'Condition')]",
            ]
            
            dropdown_clicked = False
            for selector in condition_dropdown_selectors:
                try:
                    # Use find_elements with short timeout instead of wait.until for speed
                    if selector.startswith("//"):
                        dropdowns = self.driver.find_elements(By.XPATH, selector)
                    else:
                        dropdowns = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    # Find the first visible dropdown
                    for dropdown in dropdowns:
                        try:
                            if dropdown.is_displayed():
                                # Scroll into view quickly
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
                                self._sleep(0.3, 0.5)  # Shorter wait
                                self._safe_click(dropdown)
                                print("✅ Condition dropdown clicked")
                                dropdown_clicked = True
                                break
                        except:
                            continue
                    
                    if dropdown_clicked:
                        break
                except Exception as e:
                    # Only log if it's not a timeout (to reduce noise)
                    if "timeout" not in str(e).lower():
                        print(f"⚠️ Condition dropdown selector failed: {selector[:50]}")
                    continue
            
            if not dropdown_clicked:
                # Try with wait as fallback (but with short timeout)
                try:
                    dropdown = short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[aria-label="Condition"]')))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
                    self._sleep(0.3, 0.5)
                    self._safe_click(dropdown)
                    print("✅ Condition dropdown clicked (fallback)")
                    dropdown_clicked = True
                except:
                    print("⚠️ Could not find condition dropdown")
                    return
            
            # Wait for dropdown to open (shorter wait)
            self._sleep(1, 1.5)  # Reduced from 1.5-2.5
            
            # Select the condition with multiple selector strategies (fast approach)
            condition_selectors = [
                f'//span[text()="{condition}"]',  # Most common - try first
                f'//span[@dir="auto"][text()="{condition}"]',
                f'//span[contains(text(), "{condition}")]',
                f'//div[@role="option"][contains(text(), "{condition}")]',
            ]
            
            condition_selected = False
            for selector in condition_selectors:
                try:
                    # Use find_elements for speed instead of wait.until
                    condition_elements = self.driver.find_elements(By.XPATH, selector)
                    
                    for condition_element in condition_elements:
                        try:
                            if condition_element.is_displayed():
                                # Scroll into view quickly
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", condition_element)
                                self._sleep(0.2, 0.4)  # Shorter wait
                                
                                # Try click (fastest method first)
                                try:
                                    condition_element.click()
                                    print(f"✅ Condition set to: {condition}")
                                    condition_selected = True
                                    self._sleep(0.3, 0.5)
                                    break
                                except:
                                    # Fallback to JavaScript click
                                    self.driver.execute_script("arguments[0].click();", condition_element)
                                    print(f"✅ Condition set to: {condition} (JS)")
                                    condition_selected = True
                                    self._sleep(0.3, 0.5)
                                    break
                        except:
                            continue
                    
                    if condition_selected:
                        break
                except Exception as e:
                    # Only log non-timeout errors
                    if "timeout" not in str(e).lower():
                        print(f"⚠️ Condition selector failed: {selector[:50]}")
                    continue
            
            if not condition_selected:
                print(f"⚠️ Could not select condition: {condition}")
                # Try to find all visible condition options for debugging
                try:
                    all_options = self.driver.find_elements(By.XPATH, "//span[contains(@dir, 'auto')] | //div[@role='option']")
                    print(f"🔍 Found {len(all_options)} potential condition options")
                    for i, opt in enumerate(all_options[:5]):  # Show first 5
                        if opt.is_displayed():
                            print(f"  Option {i+1}: {opt.text[:50]}")
                except:
                    pass
                
        except Exception as e:
            print(f"⚠️ Error setting condition: {e}")

    def _fill_product_tags_robust(self, tags):
        """Fill product tags using robust selectors."""
        try:
            # Parse and validate tags
            if isinstance(tags, str):
                # Split by comma and clean up
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            else:
                tag_list = tags if isinstance(tags, list) else []

            # Limit to 20 tags
            if len(tag_list) > 20:
                print(f"⚠️ Tag limit exceeded ({len(tag_list)} tags). Limiting to 20 tags.")
                tag_list = tag_list[:20]

            # Format as comma-separated string
            formatted_tags = ', '.join(tag_list)
            print(f"🏷️ Setting product tags ({len(tag_list)} tags): {formatted_tags}")

            # Try to find the product tags field using user's exact selector first, then fallbacks
            tags_selectors = [
                # User's exact selector - find the span then the input field
                "//span[@class='x1jchvi3 x1fcty0u x132q4wb x193iq5w x1al4vs7 xmper1u x1lliihq x11dcrhx xzwoauc x6ikm8r x10wlt62 x47corl x10l6tqk xlyipyv xoyzfg9 xhb22t3 x11xpdln x1r7x56h xuxw1ft xi81zsa' and text()='Product tags']/ancestor::div[contains(@class, 'x1n2onr6')]//input",
                # Alternative: find span by ID
                "//span[@id='_r_5d_' and text()='Product tags']/ancestor::div[contains(@class, 'x1n2onr6')]//input",
                # Find by text and following input
                "//span[text()='Product tags']/following-sibling::input",
                "//span[text()='Product tags']/following::input[1]",
                "//span[text()='Product tags']/parent::*/following-sibling::*/descendant::input",
                # Generic fallbacks
                'input[aria-label="Product tags"]',
                "//input[contains(@placeholder, 'tag')]",
                "//input[contains(@aria-label, 'tag')]"
            ]

            tags_filled = False
            for selector in tags_selectors:
                try:
                    if selector.startswith("//"):
                        tags_input = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        tags_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", tags_input)
                    self._sleep(0.5, 1.0)

                    self._safe_click(tags_input)
                    self._sleep(0.3, 0.5)
                    tags_input.clear()
                    self._sleep(0.2, 0.3)

                    # Use JavaScript to set the comma-separated tags
                    try:
                        self.driver.execute_script("""
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        """, tags_input, formatted_tags)
                        self._sleep(0.5, 1.0)
                        print(f"✅ Product tags set using JavaScript: {formatted_tags}")
                    except Exception as js_error:
                        print(f"⚠️ JavaScript method failed: {js_error}, trying send_keys...")
                        # Fallback to send_keys if JavaScript fails
                        tags_input.send_keys(formatted_tags)
                        self._sleep(0.5, 1.0)
                        print(f"✅ Product tags set using send_keys: {formatted_tags}")

                    tags_filled = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to fill product tags with selector {selector}: {e}")
                    continue

            if not tags_filled:
                print("⚠️ Could not fill product tags - field may not be available for this listing")

        except Exception as e:
            print(f"⚠️ Error setting product tags: {e}")

    def _click_more_details(self):
        """Click the 'More details' button to reveal additional fields, but only if not already expanded."""
        try:
            print("🔍 Checking if 'More details' needs to be clicked...")
            
            # First, check if description field is already visible
            if self._is_description_visible():
                print("✅ Description field is already visible - skipping 'More details' click")
                return
            
            print("🔍 Description not visible - looking for 'More details' button...")
            
            more_details_selectors = [
                # Specific selector from user's HTML
                "//span[@id='_r_3i_' and text()='More details']",
                "//span[contains(@class, 'x193iq5w') and text()='More details']",
                # General selectors
                "//span[text()='More details']",
                "//div[contains(text(), 'More details')]",
                "//button[contains(text(), 'More details')]",
                "//div[contains(text(), 'Attract more interest')]",
                "//div[contains(text(), 'more details')]",
                'div[aria-label*="More details"]',
                'button[aria-label*="More details"]',
                'div[data-testid*="more-details"]',
                'div[role="button"][contains(text(), "More details")]',
                "//div[contains(@class, 'more') and contains(text(), 'details')]",
                "//div[contains(@class, 'expand')]"
            ]
            
            more_details_clicked = False
            for selector in more_details_selectors:
                try:
                    if selector.startswith("//"):
                        more_details_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        more_details_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if more_details_button.is_displayed():
                        self._safe_click(more_details_button)
                        print("✅ 'More details' button clicked")
                        more_details_clicked = True
                        break
                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue
            
            if not more_details_clicked:
                print("⚠️ Could not find 'More details' button with standard selectors")
                # Try alternative approach - look for any element containing "more details" text
                try:
                    print("🔍 Trying alternative approach - searching for any element with 'more details' text...")
                    elements = self.driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more details')]")
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self._safe_click(element)
                            print("✅ 'More details' button clicked (alternative method)")
                            more_details_clicked = True
                            break
                except Exception as e:
                    print(f"⚠️ Alternative approach also failed: {e}")
                
        except Exception as e:
            print(f"⚠️ Error clicking 'More details': {e}")

    def _is_description_visible(self):
        """Check if the description field is already visible on the page."""
        try:
            print("🔍 Checking if description field is visible...")
            
            description_selectors = [
                "//span[text()='Description']/following::textarea[1]",
                "//span[text()='Description']/following::div[@contenteditable='true'][1]",
                "//textarea[contains(@aria-label, 'Description')]",
                "//div[@contenteditable='true' and contains(@aria-label, 'Description')]",
                "//textarea[contains(@placeholder, 'Description')]",
                "//div[@contenteditable='true' and contains(@placeholder, 'Description')]",
                'textarea[aria-label*="Description"]',
                'div[contenteditable="true"][aria-label*="Description"]',
                'textarea[placeholder*="Description"]',
                'div[contenteditable="true"][placeholder*="Description"]'
            ]
            
            for selector in description_selectors:
                try:
                    if selector.startswith("//"):
                        description_element = self.driver.find_element(By.XPATH, selector)
                    else:
                        description_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if description_element.is_displayed():
                        print("✅ Description field is visible")
                        return True
                except:
                    continue
            
            print("⚠️ Description field is not visible")
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking description visibility: {e}")
            return False

    def _clear_location_cache(self):
        """Clear browser location cache and geolocation data to prevent cached locations."""
        try:
            print("🧹 Clearing browser location cache...")
            
            # Clear geolocation data
            self.driver.execute_script("""
                // Clear geolocation cache
                if (navigator.geolocation) {
                    navigator.geolocation.clearWatch = function() {};
                }
                
                // Clear localStorage location data
                try {
                    localStorage.removeItem('location');
                    localStorage.removeItem('userLocation');
                    localStorage.removeItem('lastLocation');
                    localStorage.removeItem('geolocation');
                    localStorage.removeItem('fb_location');
                    localStorage.removeItem('marketplace_location');
                } catch(e) {}
                
                // Clear sessionStorage location data
                try {
                    sessionStorage.removeItem('location');
                    sessionStorage.removeItem('userLocation');
                    sessionStorage.removeItem('lastLocation');
                    sessionStorage.removeItem('geolocation');
                    sessionStorage.removeItem('fb_location');
                    sessionStorage.removeItem('marketplace_location');
                } catch(e) {}
                
                // Clear any location cookies
                document.cookie = 'location=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                document.cookie = 'userLocation=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                document.cookie = 'lastLocation=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                document.cookie = 'geolocation=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                document.cookie = 'fb_location=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                document.cookie = 'marketplace_location=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            """)
            
            # Small delay to let the clearing take effect
            self._sleep(1, 2)
            print("✅ Browser location cache cleared")
            
        except Exception as e:
            print(f"⚠️ Error clearing location cache: {e}")

    def _fill_location_robust(self, location):
        """Fill location with enhanced clearing and verification to prevent cached locations."""
        try:
            print(f"📍 Setting location: {location}")
            print(f"🔍 Target location breakdown: '{location}'")
            
            location_selectors = [
                'input[aria-label="Location"]',
                "//span[text()='Location']/following-sibling::input",
                "//input[contains(@placeholder, 'location')]",
                "//input[contains(@aria-label, 'Location')]"
            ]
            
            location_filled = False
            for selector in location_selectors:
                try:
                    if selector.startswith("//"):
                        location_input = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        location_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    
                    print(f"🎯 Found location input with selector: {selector}")
                    
                    # Enhanced clearing process
                    self._enhanced_location_clear(location_input)
                    
                    # Human-like location typing
                    print(f"⌨️ Human-like typing location: '{location}'")
                    location_input.clear()
                    
                    # Type character by character with human-like delays
                    for i, char in enumerate(location):
                        location_input.send_keys(char)
                        # Human-like typing delay (faster than before but still human-like)
                        self._sleep(0.1, 0.3)
                        
                        # Small pause every few characters (like a human would do)
                        if (i + 1) % 3 == 0:
                            self._sleep(0.2, 0.4)
                    
                    # Wait for autocomplete dropdown to appear
                    self._sleep(2, 3)
                    
                    # Click the first suggestion from dropdown
                    autocomplete_success = self._enhanced_autocomplete_selection(location)
                    
                    if autocomplete_success:
                        print(f"✅ Location set successfully: '{location}'")
                        location_filled = True
                        break
                    else:
                        # Fallback: Press Enter to confirm the typed location
                        print("⚠️ Autocomplete selection failed, trying Enter key...")
                        try:
                            location_input.send_keys(Keys.ENTER)
                            self._sleep(1, 2)
                            print(f"✅ Location confirmed with Enter key: '{location}'")
                            location_filled = True
                            break
                        except Exception as enter_error:
                            print(f"⚠️ Enter key failed: {enter_error}")
                            location_filled = True
                            break
                    
                except Exception as e:
                    print(f"⚠️ Failed to fill location with selector {selector}: {e}")
                    continue
            
            if not location_filled:
                print("⚠️ Could not fill location with any method")
                
        except Exception as e:
            print(f"⚠️ Error setting location: {e}")

    def _enhanced_location_clear(self, location_input):
        """Enhanced method to completely clear location field."""
        try:
            print("🧹 Enhanced location clearing...")
            
            # Method 1: Triple clear with different approaches
            location_input.send_keys(Keys.CONTROL + "a")
            location_input.send_keys(Keys.DELETE)
            self._sleep(0.3, 0.5)
            
            location_input.send_keys(Keys.CONTROL + "a")
            location_input.send_keys(Keys.BACKSPACE)
            self._sleep(0.3, 0.5)
            
            # Method 2: JavaScript clear
            self.driver.execute_script("arguments[0].value = '';", location_input)
            self._sleep(0.3, 0.5)
            
            # Method 3: Trigger events to ensure clearing is registered
            self.driver.execute_script("""
                var element = arguments[0];
                element.value = '';
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
                element.dispatchEvent(new Event('focus', { bubbles: true }));
            """, location_input)
            
            self._sleep(0.5, 1.0)
            
            # Verify clearing
            current_value = location_input.get_attribute('value')
            if current_value:
                print(f"⚠️ Location field still has value after clearing: '{current_value}'")
                # Force clear with JavaScript
                self.driver.execute_script("arguments[0].value = ''; arguments[0].innerHTML = '';", location_input)
                self._sleep(0.5, 1.0)
            else:
                print("✅ Location field successfully cleared")
                
        except Exception as e:
            print(f"⚠️ Error during enhanced clearing: {e}")

    def _enhanced_location_typing(self, location_input, location):
        """Enhanced location typing with better verification."""
        try:
            print(f"⌨️ Enhanced location typing: '{location}'")
            
            # Method 1: Human-like typing with verification
            try:
                for i, char in enumerate(location):
                    location_input.send_keys(char)
                    self._sleep(0.05, 0.15)
                    
                    # Check progress every 5 characters
                    if (i + 1) % 5 == 0:
                        current_value = location_input.get_attribute('value')
                        expected_so_far = location[:i+1]
                        if current_value != expected_so_far:
                            print(f"⚠️ Typing mismatch at char {i+1}. Expected: '{expected_so_far}', Got: '{current_value}'")
                
                # Final verification
                self._sleep(1, 2)
                actual_value = location_input.get_attribute('value')
                
                if actual_value == location:
                    print(f"✅ Location typing successful: '{actual_value}'")
                    return True
                else:
                    print(f"⚠️ Location typing mismatch. Expected: '{location}', Got: '{actual_value}'")
                    
            except Exception as typing_error:
                print(f"⚠️ Human typing failed: {typing_error}")
            
            # Method 2: JavaScript fallback with events
            try:
                print("🔄 Trying JavaScript method...")
                self.driver.execute_script("""
                    var element = arguments[0];
                    var value = arguments[1];
                    
                    // Clear and set value
                    element.value = '';
                    element.value = value;
                    
                    // Trigger all relevant events
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new Event('keyup', { bubbles: true }));
                    element.dispatchEvent(new Event('blur', { bubbles: true }));
                    element.focus();
                """, location_input, location)
                
                self._sleep(1, 2)
                actual_value = location_input.get_attribute('value')
                
                if actual_value == location:
                    print(f"✅ JavaScript method successful: '{actual_value}'")
                    return True
                else:
                    print(f"⚠️ JavaScript method failed. Expected: '{location}', Got: '{actual_value}'")
                    
            except Exception as js_error:
                print(f"⚠️ JavaScript method error: {js_error}")
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error in enhanced typing: {e}")
            return False

    def _enhanced_autocomplete_selection(self, expected_location):
        """Enhanced autocomplete selection that looks for the exact location match."""
        try:
            print(f"🔍 Enhanced autocomplete selection for: '{expected_location}'")
            
            # Wait for suggestions to appear
            self._sleep(3, 4)  # Increased wait time
            
            # Look for autocomplete suggestions with more comprehensive selectors
            suggestion_selectors = [
                'ul[role="listbox"] li',
                'div[role="option"]',
                'div[data-testid*="suggestion"]',
                'div[class*="suggestion"]',
                'li[class*="suggestion"]',
                'div[class*="autocomplete"] li',
                'div[class*="dropdown"] li',
                'div[class*="menu"] li',
                'li[class*="option"]',
                'div[class*="item"]'
            ]
            
            suggestions = []
            for selector in suggestion_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        suggestions = elements
                        print(f"✅ Found {len(suggestions)} suggestions with selector: {selector}")
                    break
                except:
                    continue
            
            if not suggestions:
                print("⚠️ No autocomplete suggestions found - continuing without selection")
                return True  # Return True to continue without autocomplete
            
            # Print all available suggestions for debugging
            print(f"📋 All available suggestions:")
            for i, suggestion in enumerate(suggestions[:10]):  # Show first 10
                try:
                    text = suggestion.text.strip()
                    if text:
                        print(f"   {i+1}. '{text}'")
                except:
                    continue
            
            # Enhanced matching logic
            best_match = None
            best_match_score = 0
            
            for suggestion in suggestions:
                try:
                    suggestion_text = suggestion.text.strip()
                    if not suggestion_text:
                        continue
                    
                    # Calculate match score
                    score = self._calculate_location_match_score(expected_location, suggestion_text)
                    
                    print(f"🔍 Suggestion: '{suggestion_text}' - Score: {score}")
                    
                    if score > best_match_score:
                        best_match_score = score
                        best_match = suggestion
                    
                except Exception as e:
                    print(f"⚠️ Error checking suggestion: {e}")
                    continue
            
            # Simply click the first suggestion (Facebook's autocomplete is usually accurate)
            if suggestions:
                try:
                    # Re-find suggestions to avoid stale element
                    self._sleep(0.5, 1.0)  # Wait for suggestions to stabilize
                    fresh_suggestions = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="option"]')

                    if fresh_suggestions:
                        first_suggestion = fresh_suggestions[0]
                        # Get text before clicking
                        suggestion_text = first_suggestion.text.strip()

                        # Try multiple click strategies
                        try:
                            self._safe_click(first_suggestion)
                            print(f"✅ Clicked first suggestion: '{suggestion_text}'")
                        except:
                            # Fallback: JavaScript click
                            try:
                                self.driver.execute_script("arguments[0].click();", first_suggestion)
                                print(f"✅ Clicked first suggestion (JS): '{suggestion_text}'")
                            except Exception as js_err:
                                print(f"⚠️ Failed to click suggestion, pressing Enter instead")
                                # Just press Enter to select
                                location_input.send_keys(Keys.ENTER)

                        self._sleep(1, 2)
                        return True
                    else:
                        print("⚠️ Suggestions disappeared. Continuing without autocomplete selection.")
                        return True
                except Exception as e:
                    print(f"⚠️ Failed to click first suggestion: {e}")
                    # Fallback: Just press Enter
                    try:
                        location_input.send_keys(Keys.ENTER)
                        print("✅ Pressed Enter to confirm location")
                    except:
                        pass
                    return True  # Continue anyway
            else:
                print("⚠️ No suggestions found. Continuing without autocomplete selection.")
                return True  # Continue without selection
                
        except Exception as e:
            print(f"⚠️ Error in enhanced autocomplete selection: {e}")
            return True  # Continue without selection

    def _calculate_location_match_score(self, expected_location, suggestion_text):
        """Calculate how well a suggestion matches the expected location."""
        try:
            expected_lower = expected_location.lower()
            suggestion_lower = suggestion_text.lower()
            
            # Exact match gets highest score
            if expected_lower == suggestion_lower:
                return 100
            
            # Split into parts for better matching
            expected_parts = [part.strip() for part in expected_lower.split(',')]
            suggestion_parts = [part.strip() for part in suggestion_lower.split(',')]
            
            score = 0
            
            # Check for exact city match
            if expected_parts[0] == suggestion_parts[0]:
                score += 50
            
            # Check for country match
            if len(expected_parts) > 1 and len(suggestion_parts) > 1:
                if expected_parts[1] == suggestion_parts[1]:
                    score += 30
                elif expected_parts[1] in suggestion_parts[1] or suggestion_parts[1] in expected_parts[1]:
                    score += 20
            
            # Check for partial city match
            if expected_parts[0] in suggestion_lower:
                score += 25
            elif suggestion_parts[0] in expected_lower:
                score += 25
            
            # Check for any common words
            expected_words = set(expected_parts[0].split())
            suggestion_words = set(suggestion_parts[0].split())
            common_words = expected_words.intersection(suggestion_words)
            if common_words:
                score += len(common_words) * 10
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            print(f"⚠️ Error calculating match score: {e}")
            return 0

    def _verify_final_location(self, expected_location):
        """Verify that the final location was set correctly."""
        try:
            print(f"🔍 Final location verification for: '{expected_location}'")
            
            # Wait a moment for the location to be processed
            self._sleep(2, 3)
            
            # Look for location display elements on the page
            location_display_selectors = [
                'input[aria-label="Location"]',
                'input[placeholder*="location"]',
                'input[placeholder*="Location"]',
                'div[data-testid*="location"]',
                'span[data-testid*="location"]'
            ]
            
            current_location = None
            for selector in location_display_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            current_value = element.get_attribute('value') or element.text.strip()
                            if current_value:
                                current_location = current_value
                                print(f"🔍 Found location display: '{current_value}'")
                                
                                # Check if it matches our expected location
                                if expected_location.lower() in current_value.lower():
                                    print(f"✅ Location verification successful: '{current_value}' matches expected '{expected_location}'")
                                    return True
                                elif current_value.lower() in expected_location.lower():
                                    print(f"✅ Location verification successful: '{current_value}' is contained in expected '{expected_location}'")
                                    return True
                                else:
                                    print(f"⚠️ Location mismatch: Expected '{expected_location}', Found '{current_value}'")
                                    
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
            
            # If we found a location but it doesn't match, try to correct it
            if current_location and current_location.lower() != expected_location.lower():
                print(f"🔄 Attempting to correct location from '{current_location}' to '{expected_location}'")
                correction_success = self._correct_wrong_location(expected_location)
                if correction_success:
                    print(f"✅ Location correction successful")
                    return True
                else:
                    print(f"⚠️ Location correction failed, but continuing with current location")
                    return False
            
            print("⚠️ Could not find location display for verification")
            return False
            
        except Exception as e:
            print(f"⚠️ Error in final location verification: {e}")
            return False

    def _correct_wrong_location(self, expected_location):
        """Try to correct a wrong location selection."""
        try:
            print(f"🔧 Attempting to correct location to: '{expected_location}'")
            
            # Find the location input again
            location_selectors = [
                'input[aria-label="Location"]',
                "//span[text()='Location']/following-sibling::input",
                "//input[contains(@placeholder, 'location')]",
                "//input[contains(@aria-label, 'Location')]"
            ]
            
            for selector in location_selectors:
                try:
                    if selector.startswith("//"):
                        location_input = self.driver.find_element(By.XPATH, selector)
                    else:
                        location_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if location_input.is_displayed():
                        # Clear and retype
                        self._enhanced_location_clear(location_input)
                        
                        # Type the correct location
                        for char in expected_location:
                            location_input.send_keys(char)
                            self._sleep(0.1, 0.2)
                        
                        # Press Enter to confirm
                        location_input.send_keys(Keys.ENTER)
                        self._sleep(1, 2)
                        
                        print(f"✅ Location correction completed: '{expected_location}'")
                        return True
                        
                except Exception as e:
                    continue
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error correcting location: {e}")
            return False

    def _click_top_location_result(self):
        """Click the top location autocomplete result."""
        try:
            print("🔍 Looking for top location result...")
            
            location_result_selectors = [
                'ul[role="listbox"] li:first-child',
                'div[role="option"]:first-child',
                "//ul[@role='listbox']//li[1]",
                "//div[@role='option'][1]",
                "//div[contains(@class, 'autocomplete')]//li[1]",
                "//div[contains(@class, 'suggestion')]//li[1]"
            ]
            
            result_clicked = False
            for selector in location_result_selectors:
                try:
                    if selector.startswith("//"):
                        result_element = self.driver.find_element(By.XPATH, selector)
                    else:
                        result_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if result_element.is_displayed():
                        self._safe_click(result_element)
                        print("✅ Top location result clicked")
                        result_clicked = True
                        break
                except:
                    continue
            
            if not result_clicked:
                print("⚠️ Could not find top location result")
                
        except Exception as e:
            print(f"⚠️ Error clicking top location result: {e}")

    def _set_category(self, category):
        """Set the listing category (legacy method)."""
        try:
            category_selectors = {
                'Other Garden decor': '//span[text()="Other Garden decor"]',
                'Other Rugs & carpets': '//span[text()="Other Rugs & carpets"]'
            }
            
            if category in category_selectors:
                category_element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, category_selectors[category]))
                )
                category_element.click()
                print(f"✅ Category set to: {category}")
        except Exception as e:
            print(f"⚠️ Error setting category: {e}")

    def _set_condition(self, condition):
        """Set the listing condition (legacy method)."""
        try:
            condition_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f'//span[text()="{condition}"]'))
            )
            condition_element.click()
            print(f"✅ Condition set to: {condition}")
        except Exception as e:
            print(f"⚠️ Error setting condition: {e}")

    def _fill_product_tags(self, tags):
        """Fill product tags (legacy method)."""
        try:
            tags_input = self.driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Product tags"]')
            tags_input.clear()
            tags_input.send_keys(tags)
            print(f"✅ Product tags set: {tags}")
        except Exception as e:
            print(f"⚠️ Error setting product tags: {e}")

    def _fill_location(self, location):
        """Fill location (legacy method)."""
        try:
            location_input = self.driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Location"]')
            location_input.clear()
            location_input.send_keys(location)
            print(f"✅ Location set: {location}")
        except Exception as e:
            print(f"⚠️ Error setting location: {e}")

    def _handle_group_selection(self):
        """Handle the group selection screen that appears after clicking Next."""
        try:
            print("🔍 Checking for group selection screen...")
            
            # Wait a moment for the page to load
            self._sleep(2, 3)
            
            # Check if we're on the group selection screen by looking for group checkboxes
            group_checkbox_selectors = [
                'div[role="checkbox"][aria-checked="false"]',
                'div[aria-checked="false"][role="checkbox"]',
                '//div[@role="checkbox" and @aria-checked="false"]',
                '//div[@aria-checked="false" and @role="checkbox"]'
            ]
            
            group_checkboxes = []
            for selector in group_checkbox_selectors:
                try:
                    if selector.startswith("//"):
                        checkboxes = self.driver.find_elements(By.XPATH, selector)
                    else:
                        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if checkboxes:
                        group_checkboxes = checkboxes
                        print(f"✅ Found {len(group_checkboxes)} group checkboxes")
                        break
                except:
                    continue
            
            if not group_checkboxes:
                print("ℹ️ No group selection screen found - proceeding to publish")
                return
            
            print(f"📋 Group selection screen detected - selecting all {len(group_checkboxes)} groups...")
            
            # Select all available groups
            selected_count = 0
            for i, checkbox in enumerate(group_checkboxes):
                try:
                    # Check if the checkbox is visible and clickable
                    if checkbox.is_displayed() and checkbox.is_enabled():
                        # Scroll the checkbox into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        self._sleep(0.5, 1.0)
                        
                        # Click the checkbox
                        self._safe_click(checkbox)
                        selected_count += 1
                        print(f"✅ Selected group {i+1}/{len(group_checkboxes)}")
                        
                        # Small delay between selections to avoid overwhelming the page
                        self._sleep(0.3, 0.7)
                    else:
                        print(f"⚠️ Group {i+1} checkbox not clickable, skipping")
                        
                except Exception as e:
                    print(f"⚠️ Failed to select group {i+1}: {e}")
                    continue
            
            print(f"🎉 Successfully selected {selected_count}/{len(group_checkboxes)} groups")
            
            # Wait a moment for the selections to register
            self._sleep(1, 2)
            
        except Exception as e:
            print(f"⚠️ Error handling group selection: {e}")
            # Don't raise the exception - continue with the listing process even if group selection fails

    def _initialize_ai_learning(self):
        """Initialize AI learning system for the current account."""
        try:
            # Extract account name from cookies path
            account_name = self._extract_account_from_cookies_path()
            if account_name:
                print(f"🤖 Initializing AI learning for account: {account_name}")
                
                # Analyze existing listings to learn patterns
                analysis_result = self.ai_learning.analyze_account_listings(account_name)
                
                if analysis_result['success']:
                    print(f"✅ AI learning initialized for account: {account_name}")
                    print(f"   📊 Analyzed {analysis_result['analysis'].get('total_listings', 0)} listings")
                else:
                    print(f"⚠️ AI learning initialization failed: {analysis_result.get('error', 'Unknown error')}")
            else:
                print("⚠️ Could not determine account name for AI learning")
                
        except Exception as e:
            print(f"⚠️ Error initializing AI learning: {e}")
    
    def _extract_account_from_cookies_path(self):
        """Extract account name from cookies file path."""
        try:
            if self.cookies_path:
                # Extract account name from path like 'accounts/account_name/cookies.json'
                path_parts = self.cookies_path.replace('\\', '/').split('/')
                if 'accounts' in path_parts:
                    accounts_index = path_parts.index('accounts')
                    if accounts_index + 1 < len(path_parts):
                        return path_parts[accounts_index + 1]
            return None
        except Exception as e:
            print(f"⚠️ Error extracting account name: {e}")
            return None

    def close(self):
        """Close the browser driver."""
        try:
            if self.driver:
                print("🔒 Closing browser...")
                self.driver.quit()
                print("✅ Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")

