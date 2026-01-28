# Facebook Marketplace Bot

A full-stack Python application that automates Facebook Marketplace listings with stealth and human-like behavior. The bot can delete old listings and post new ones using Selenium with undetected Chrome driver.

## Features

- **Multi-Account Support**: Each account has its own dedicated folder with cookies, database, and assets
- **Stealth Operation**: Uses undetected-chromedriver to avoid detection
- **Human-like Behavior**: Random delays and realistic interaction patterns
- **Web Interface**: Clean, modern UI served via Flask
- **Database Tracking**: SQLite database for each account to track listings
- **Threading**: Non-blocking operation with background processing

## Project Structure

```
facebook-marketplace-bot/
├── app.py                  # Flask backend and UI server
├── bot.py                  # Selenium bot class and logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── accounts/              # Account data directory
│   └── sample_account/    # Example account folder
│       └── cookies.json   # Facebook cookies (you need to populate this)
└── templates/
    └── index.html         # Web UI template
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Account Folders

For each Facebook account you want to use:

1. Create a new folder in the `accounts` directory (e.g., `accounts/my_account_name/`)
2. Add a `cookies.json` file to that folder with your Facebook cookies

### 3. Get Facebook Cookies

To get your Facebook cookies:

1. Log into Facebook in a regular browser
2. Open Developer Tools (F12)
3. Go to Application/Storage tab
4. Find Cookies for facebook.com
5. Copy the important cookies (c_user, xs, datr, etc.) into your `cookies.json` file

**Important cookies to include:**
- `c_user` - Your Facebook user ID
- `xs` - Session token
- `datr` - Device token
- Any other authentication cookies

### 4. Run the Application

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

## Usage

1. **Select Account**: Choose from your configured accounts
2. **Enter Listing Details**: Fill in title, price, and description
3. **Upload Photos**: Select multiple images for your listing
4. **Set Speed**: Adjust the delay factor (0.5x = faster, 2.0x = slower)
5. **Start Bot**: Click the button to begin the automation

## How It Works

1. **Delete Old Listing**: The bot searches for existing listings with the same title and deletes them
2. **Create New Listing**: Navigates to Facebook Marketplace create page and fills out the form
3. **Upload Images**: Automatically uploads all selected photos
4. **Publish**: Submits the listing for publication
5. **Database Logging**: Saves listing details to the account's SQLite database

## Security Features

- **Undetected Chrome Driver**: Bypasses common bot detection methods
- **Random Delays**: Human-like timing between actions
- **Realistic Behavior**: Mimics actual user interactions
- **Cookie Management**: Secure handling of authentication data

## Troubleshooting

### Common Issues

1. **"Cookies file not found"**: Make sure you've created the cookies.json file in your account folder
2. **"Listing not found"**: This is normal if no previous listing exists with that title
3. **Browser crashes**: Try reducing the speed factor or check your internet connection
4. **Login issues**: Update your cookies.json file with fresh authentication data

### Debug Mode

The bot automatically saves screenshots when errors occur. Look for files like `error_create_[timestamp].png` in your project directory.

## Account Management

Each account folder should contain:
- `cookies.json` - Facebook authentication cookies
- `listings.db` - SQLite database (created automatically)
- `listings_data/` - Directory for uploaded images (created automatically)

## Legal Notice

This tool is for educational purposes only. Make sure to comply with Facebook's Terms of Service and use responsibly. The authors are not responsible for any misuse of this software.

## Support

For issues or questions:
1. Check the console output for detailed error messages
2. Verify your cookies are valid and up-to-date
3. Ensure all dependencies are properly installed
4. Check that your internet connection is stable

## Version

Version 1.0 - Initial release with core functionality
