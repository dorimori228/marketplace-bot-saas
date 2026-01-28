# Auto-Login Setup Guide

This guide explains how to set up auto-login functionality for new users of the Facebook Marketplace Bot.

## 🚀 Quick Start for New Users

### For Yumi Account (or any new user):

1. **Run the setup script:**
   ```bash
   python setup_yumi.py
   ```
   Or for any other account:
   ```bash
   python setup_new_user.py
   ```

2. **Follow the instructions:**
   - A browser window will open to Facebook
   - Log in with your Facebook credentials
   - Complete any 2FA if prompted
   - The bot will automatically save your login cookies
   - Future runs will auto-login automatically!

## 📋 What Happens During Setup

1. **Account Directory Creation**: Creates `accounts/[username]/` folder
2. **Browser Launch**: Opens Facebook in a browser window
3. **Manual Login**: You log in manually (one-time only)
4. **Cookie Detection**: Bot detects when you're logged in
5. **Cookie Saving**: Saves login cookies to `cookies.json`
6. **Validation**: Verifies cookies are saved correctly

## 🔄 How Auto-Login Works

### First Time (Setup):
- No cookies exist → Manual login required
- User logs in manually → Cookies saved
- Setup complete!

### Subsequent Times:
- Cookies exist → Load cookies automatically
- Navigate to Facebook → Already logged in
- Ready to use!

## 📁 File Structure

```
accounts/
├── yumi/
│   ├── cookies.json          # Auto-login cookies
│   ├── listings.db           # Listings database
│   └── listings/             # Listing images and data
├── jay/
│   ├── cookies.pkl
│   └── ...
└── abbie/
    ├── cookies.pkl
    └── ...
```

## 🛠️ Available Scripts

### Setup Scripts:
- `setup_new_user.py` - General new user setup
- `setup_yumi.py` - Quick setup for yumi account
- `setup_real_account.py` - Manual cookie entry (legacy)

### Test Scripts:
- `test_auto_login.py` - Test auto-login functionality
- `test_login.py` - Test login with existing accounts

### Usage Examples:

```bash
# Setup new user
python setup_new_user.py

# Setup yumi specifically
python setup_yumi.py

# Test auto-login for specific account
python test_auto_login.py yumi

# Test all accounts
python test_auto_login.py
```

## 🔧 Troubleshooting

### Common Issues:

1. **"No cookies found"**
   - Run setup script first
   - Make sure you completed the manual login

2. **"Auto-login failed"**
   - Cookies may be expired
   - Run setup again to refresh cookies

3. **"Manual login timeout"**
   - Take your time with 2FA
   - Make sure you're fully logged in
   - Try running setup again

4. **"Browser won't open"**
   - Check Chrome installation
   - Try running as administrator
   - Check antivirus software

### Cookie Issues:

- **Cookies expired**: Run setup again
- **Invalid cookies**: Delete `cookies.json` and run setup
- **Missing cookies**: Check file permissions

## 🔐 Security Notes

- Cookies are stored locally in your `accounts/` folder
- Never share your `cookies.json` files
- Cookies contain your login session - keep them secure
- If compromised, log out of Facebook and run setup again

## 📊 Cookie Information

The bot saves these important cookies:
- `c_user` - User ID
- `xs` - Session token
- `datr` - Device token
- `sb` - Session browser
- `fr` - Facebook token

## 🎯 Best Practices

1. **One-time setup**: Only need to do manual login once
2. **Regular testing**: Use `test_auto_login.py` to verify
3. **Backup cookies**: Keep your `accounts/` folder backed up
4. **Update when needed**: Re-run setup if cookies expire

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Run the test script to diagnose
3. Try running setup again
4. Check the console output for error messages

## 🎉 Success!

Once setup is complete, you can use the bot normally:
- Run `python app.py` for the web interface
- Run `python bot.py` directly
- The bot will auto-login every time!

No more manual login required! 🚀
