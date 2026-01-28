import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import json
import os
import pickle


class MarketplaceBot:
    def __init__(self, cookies_path, delay_factor=1.0):
        """
        Initialize the MarketplaceBot with undetected Chrome driver.
        
        Args:
            cookies_path (str): Path to the cookies.json or cookies.pkl file
            delay_factor (float): Multiplier for delays to control speed (1.0 = normal, 0.5 = faster, 2.0 = slower)
        """
        self.delay_factor = delay_factor
        self.cookies_path = cookies_path
        self.login_url = "https://www.facebook.com"
        self.is_logged_in_selector = 'div[aria-label="Account"]'  # Element that appears when logged in
        
        # Initialize Chrome driver with fallback options
        try:
            # Try undetected-chromedriver first
            print("Attempting to use undetected-chromedriver...")
            options = uc.ChromeOptions()
            # Force desktop user agent to avoid mobile redirects
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")
            self.driver = uc.Chrome(options=options)
            print("Undetected-chromedriver initialized successfully")
        except Exception as e:
            print(f"Undetected-chromedriver failed: {e}")
            print("Falling back to regular Selenium Chrome driver...")
            # Fallback to regular Selenium with webdriver-manager
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            # Force desktop user agent to avoid mobile redirects
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to automatically handle Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("Regular Selenium Chrome driver initialized")
        
        # Execute stealth script
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set up WebDriverWait with 15-second timeout
        self.wait = WebDriverWait(self.driver, 15)
        
        # Initialize login functionality
        self._add_login_functionality()
    
    def _sleep(self, min_seconds=1, max_seconds=3):
        """
        Sleep for a random time between min_seconds and max_seconds, multiplied by delay_factor.
        This mimics human behavior and helps avoid detection.
        """
        sleep_time = random.uniform(min_seconds, max_seconds) * self.delay_factor
        time.sleep(sleep_time)
    
    
    def _add_login_functionality(self):
        """Add login functionality similar to your working scraper."""
        if self._is_cookie_file():
            print("Loading cookies from file...")
            self._load_cookies()
            if self._is_logged_in(5):
                print("✅ Successfully logged in with cookies!")
                return
        
        print("⚠️  Cookies not found or invalid. Please login manually.")
        print("You have 5 minutes to login manually in the browser window.")
        print("After logging in, the bot will save cookies for future use.")
        
        # Navigate to Facebook login page
        self.driver.get(self.login_url)
        self._sleep(2, 3)
        
        # Check for mobile redirect and force desktop
        current_url = self.driver.current_url
        if "m.facebook.com" in current_url:
            print("Detected mobile redirect, forcing desktop version...")
            self.driver.get("https://www.facebook.com")
            self._sleep(2, 3)
        
        # Handle cookie consent popup
        self._handle_cookie_consent()
        
        if not self._is_logged_in(300):  # 5 minutes timeout
            print("❌ Login timeout. Please check your credentials and try again.")
            raise Exception("Manual login timeout")
        
        print("✅ Manual login successful! Saving cookies...")
        self._save_cookies()
    
    def _is_cookie_file(self):
        """Check if cookie file exists."""
        return os.path.exists(self.cookies_path)
    
    def _load_cookies(self):
        """Load cookies from file and navigate to Facebook."""
        try:
            # Check file extension to determine format
            if self.cookies_path.endswith('.pkl'):
                # Load from pickle file
                with open(self.cookies_path, 'rb') as f:
                    cookies = pickle.load(f)
            else:
                # Load from JSON file
                with open(self.cookies_path, 'r') as f:
                    cookies = json.load(f)
            
            # Navigate to Facebook first
            self.driver.get(self.login_url)
            self._sleep(2, 3)
            
            # Check if redirected to mobile and force desktop
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("Detected mobile redirect, forcing desktop version...")
                self.driver.get("https://www.facebook.com")
                self._sleep(2, 3)
            
            # Add cookies
            for cookie in cookies:
                try:
                    # Ensure cookie domain is correct for desktop
                    if cookie.get('domain') == '.facebook.com':
                        self.driver.add_cookie(cookie)
                    else:
                        # Fix domain for desktop
                        cookie['domain'] = '.facebook.com'
                        self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Warning: Could not add cookie {cookie.get('name', 'unknown')}: {e}")
            
            # Navigate to Facebook again to apply cookies
            self.driver.get(self.login_url)
            self._sleep(3, 5)
            
            # Check for mobile redirect again
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("Still on mobile, trying alternative desktop URL...")
                self.driver.get("https://www.facebook.com")
                self._sleep(3, 5)
            
            # Handle cookie consent popup
            self._handle_cookie_consent()
            
        except Exception as e:
            print(f"Error loading cookies: {e}")
    
    def _save_cookies(self):
        """Save current cookies to file."""
        try:
            cookies = self.driver.get_cookies()
            
            # Save as pickle file
            if self.cookies_path.endswith('.pkl'):
                with open(self.cookies_path, 'wb') as f:
                    pickle.dump(cookies, f)
            else:
                # Save as JSON file
                with open(self.cookies_path, 'w') as f:
                    json.dump(cookies, f, indent=2)
            
            print(f"✅ Cookies saved to: {self.cookies_path}")
            
        except Exception as e:
            print(f"Error saving cookies: {e}")
    
    def _is_logged_in(self, wait_time=None):
        """Check if user is logged in by looking for logged-in indicators."""
        if wait_time is None:
            wait_time = 15
        
        try:
            # Wait for logged-in indicator
            logged_in_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.is_logged_in_selector))
            )
            return logged_in_element is not None
        except:
            # Try alternative selectors
            alternative_selectors = [
                'div[aria-label="Menu"]',
                'div[data-testid="left_nav_menu"]',
                'a[href*="/me"]',
                'div[aria-label="Account"]'
            ]
            
            for selector in alternative_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        return True
                except:
                    continue
            
            return False
    
    def _handle_cookie_consent(self):
        """
        Handle Facebook's cookie consent popup if it appears.
        """
        try:
            print("Checking for cookie consent popup...")
            
            # Wait a moment for the popup to appear
            self._sleep(1, 2)
            
            # Try to find and click "Allow all cookies" button
            allow_cookies_selectors = [
                "//button[contains(text(), 'Allow all cookies')]",
                "//button[contains(text(), 'Allow All Cookies')]",
                "//div[@role='button' and contains(text(), 'Allow all cookies')]",
                "//div[@role='button' and contains(text(), 'Allow All Cookies')]",
                "//button[contains(@aria-label, 'Allow all cookies')]",
                "//button[contains(@aria-label, 'Allow All Cookies')]",
                "//button[contains(@class, 'cookie') and contains(text(), 'Allow')]",
                "//div[contains(@class, 'cookie')]//button[contains(text(), 'Allow')]"
            ]
            
            for selector in allow_cookies_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    if button.is_displayed() and button.is_enabled():
                        print("Found cookie consent popup, clicking 'Allow all cookies'...")
                        button.click()
                        self._sleep(2, 3)
                        print("Cookie consent handled successfully")
                        return
                except:
                    continue
            
            # If no "Allow all cookies" button found, try "Decline optional cookies"
            decline_selectors = [
                "//button[contains(text(), 'Decline optional cookies')]",
                "//button[contains(text(), 'Decline Optional Cookies')]",
                "//div[@role='button' and contains(text(), 'Decline optional cookies')]",
                "//button[contains(@aria-label, 'Decline optional cookies')]"
            ]
            
            for selector in decline_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    if button.is_displayed() and button.is_enabled():
                        print("Found cookie consent popup, clicking 'Decline optional cookies'...")
                        button.click()
                        self._sleep(2, 3)
                        print("Cookie consent handled successfully")
                        return
                except:
                    continue
            
            print("No cookie consent popup found or already handled")
            
        except Exception as e:
            print(f"Error handling cookie consent: {e}")
    
    
    def delete_listing_if_exists(self, title):
        """
        Delete a listing if it exists by searching for it in the user's selling listings.
        
        Args:
            title (str): The title of the listing to delete
        """
        try:
            print(f"Searching for listing with title: '{title}'")
            
            # Navigate to selling page
            self.driver.get("https://www.facebook.com/marketplace/you/selling")
            self._sleep(3, 5)
            
            # Check for mobile redirect
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("Detected mobile redirect on selling page, forcing desktop...")
                self.driver.get("https://www.facebook.com/marketplace/you/selling")
                self._sleep(3, 5)
            
            # Find and use the search input
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Search your listings"]'))
            )
            search_input.clear()
            search_input.send_keys(title)
            self._sleep(2, 3)
            
            # Look for the listing link
            try:
                listing_link = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{title}']"))
                )
                print(f"Found listing: {title}")
                
                # Click on the listing
                listing_link.click()
                self._sleep(2, 4)
                
                # Click the Delete button
                delete_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Delete"]'))
                )
                delete_button.click()
                self._sleep(1, 2)
                
                # Confirm deletion
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button']//span[text()='Delete']"))
                )
                confirm_button.click()
                print(f"Successfully deleted listing: {title}")
                self._sleep(2, 3)
                
            except TimeoutException:
                print(f"Listing '{title}' not found - nothing to delete")
                
        except Exception as e:
            print(f"Error during listing deletion: {e}")
            # Take a screenshot for debugging
            try:
                screenshot_path = f"error_delete_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
            except:
                pass
    
    def create_new_listing(self, listing_data):
        """
        Create a new listing on Facebook Marketplace.
        
        Args:
            listing_data (dict): Dictionary containing title, price, description, and image_paths
        """
        try:
            print("Starting to create new listing...")
            
            # Navigate to create listing page
            self.driver.get("https://www.facebook.com/marketplace/create/")
            self._sleep(3, 5)
            
            # Check for mobile redirect
            current_url = self.driver.current_url
            if "m.facebook.com" in current_url:
                print("Detected mobile redirect on create page, forcing desktop...")
                self.driver.get("https://www.facebook.com/marketplace/create/")
                self._sleep(3, 5)
            
            # Click on "Item for sale" card
            item_for_sale = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Item for sale']"))
            )
            item_for_sale.click()
            self._sleep(2, 4)
            
            # Upload images
            if listing_data.get('image_paths'):
                print(f"Uploading {len(listing_data['image_paths'])} images...")
                file_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                
                # Join all image paths with newlines
                image_paths = '\n'.join(listing_data['image_paths'])
                file_input.send_keys(image_paths)
                self._sleep(3, 5)
                print("Images uploaded successfully")
            
            # Fill in the title
            print("Filling in title...")
            title_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Title"]'))
            )
            title_input.clear()
            title_input.send_keys(listing_data['title'])
            self._sleep(1, 2)
            
            # Fill in the price
            print("Filling in price...")
            price_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Price"]'))
            )
            price_input.clear()
            price_input.send_keys(listing_data['price'])
            self._sleep(1, 2)
            
            # Set category based on product type
            print("Setting category...")
            category = listing_data.get('category', 'Other Garden decor')
            self._set_category(category)
            self._sleep(1, 2)
            
            # Set condition to "New"
            print("Setting condition to New...")
            self._set_condition("New")
            self._sleep(1, 2)
            
            # Fill in the description
            print("Filling in description...")
            description_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Description"]'))
            )
            # Click to focus the description field
            description_input.click()
            self._sleep(1, 2)
            
            # Find the inner editable element
            editable_element = description_input.find_element(By.CSS_SELECTOR, '[contenteditable="true"]')
            editable_element.clear()
            editable_element.send_keys(listing_data['description'])
            self._sleep(1, 2)
            
            # Fill in product tags if provided
            if listing_data.get('product_tags'):
                print("Filling in product tags...")
                self._fill_product_tags(listing_data['product_tags'])
                self._sleep(1, 2)
            
            # Fill in location
            if listing_data.get('location'):
                print("Filling in location...")
                self._fill_location(listing_data['location'])
                self._sleep(1, 2)
            
            # Click Next button
            print("Clicking Next button...")
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Next"]'))
            )
            next_button.click()
            self._sleep(3, 5)
            
            # Click Publish button
            print("Clicking Publish button...")
            publish_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Publish"]'))
            )
            publish_button.click()
            self._sleep(5, 8)
            
            print("Listing created successfully!")
            
        except Exception as e:
            print(f"Error during listing creation: {e}")
            # Take a screenshot for debugging
            try:
                screenshot_path = f"error_create_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
            except:
                pass
            raise e
    
    def _set_category(self, category):
        """Set the category for the listing."""
        try:
            # Click on category dropdown
            category_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[aria-label="Category"]'))
            )
            category_dropdown.click()
            self._sleep(1, 2)
            
            # Select the category
            category_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//span[text()='{category}']"))
            )
            category_option.click()
            self._sleep(1, 2)
            
        except Exception as e:
            print(f"Error setting category: {e}")
    
    def _set_condition(self, condition):
        """Set the condition for the listing."""
        try:
            # Click on condition dropdown
            condition_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[aria-label="Condition"]'))
            )
            condition_dropdown.click()
            self._sleep(1, 2)
            
            # Select the condition
            condition_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//span[text()='{condition}']"))
            )
            condition_option.click()
            self._sleep(1, 2)
            
        except Exception as e:
            print(f"Error setting condition: {e}")
    
    def _fill_product_tags(self, tags):
        """Fill in product tags."""
        try:
            # Look for product tags input field
            tags_input = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="tag" i], input[aria-label*="tag" i]')
            tags_input.clear()
            tags_input.send_keys(tags)
            
        except Exception as e:
            print(f"Error filling product tags: {e}")
    
    def _fill_location(self, location):
        """Fill in location."""
        try:
            # Look for location input field
            location_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Location"]'))
            )
            location_input.clear()
            location_input.send_keys(location)
            self._sleep(1, 2)
            
            # Click on first suggestion if available
            try:
                suggestion = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul[role="listbox"] li:first-child > div'))
                )
                suggestion.click()
                self._sleep(1, 2)
            except:
                pass  # No suggestions available
            
        except Exception as e:
            print(f"Error filling location: {e}")
    
    def close(self):
        """Close the browser driver."""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("Browser closed successfully")
        except Exception as e:
            print(f"Error closing browser: {e}")
