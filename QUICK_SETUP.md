# Quick Setup Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
python install_dependencies.py
```

Or manually:
```bash
pip install Pillow>=10.0.0 piexif>=1.1.3
```

### 2. Start the Bot
```bash
python app.py
```

### 3. Open Web Interface
Go to: http://localhost:5000

## 🎯 New Features

### Auto-Login for New Users
- Run `python setup_yumi.py` for new account setup
- One-time manual login, then automatic forever!

### Image Metadata Modification
- **Automatic**: Every image gets iPhone 12 metadata
- **UK Locations**: Random GPS coordinates from UK cities
- **Realistic Timestamps**: Within last 30 days
- **No Manual Work**: Completely automatic!

## 🧪 Testing

### Test Auto-Login:
```bash
python test_auto_login.py yumi
```

### Test Metadata:
```bash
python test_metadata.py
```

## 📁 Key Files

- `app.py` - Main web interface
- `bot.py` - Bot with auto-login and metadata
- `setup_yumi.py` - Quick setup for new users
- `image_metadata.py` - Metadata modification
- `install_dependencies.py` - Dependency installer

## 🎉 Ready to Use!

Your bot now has:
✅ **Auto-login** for new users  
✅ **iPhone 12 metadata** for all images  
✅ **Random UK locations** for authenticity  
✅ **Completely automatic** processing  

Just upload images and create listings - everything else is automatic! 🚀
