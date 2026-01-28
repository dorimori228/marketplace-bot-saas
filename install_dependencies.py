#!/usr/bin/env python3
"""
Dependency installation script for Facebook Marketplace Bot.
Installs all required packages for the bot to work properly.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """Main installation function."""
    print("🚀 Facebook Marketplace Bot - Dependency Installer")
    print("=" * 60)
    print()
    
    # List of required packages
    required_packages = [
        ("flask", "Flask web framework"),
        ("selenium>=4.15.0", "Selenium WebDriver"),
        ("undetected-chromedriver>=3.5.0", "Undetected Chrome driver"),
        ("webdriver-manager", "WebDriver manager"),
        ("Pillow>=10.0.0", "PIL for image processing"),
        ("piexif>=1.1.3", "EXIF data manipulation")
    ]
    
    print("📋 Required packages:")
    for package, description in required_packages:
        print(f"   • {package} - {description}")
    print()
    
    # Check which packages are already installed
    print("🔍 Checking existing installations...")
    missing_packages = []
    
    for package, description in required_packages:
        package_name = package.split(">=")[0].split("==")[0]
        if check_package(package_name):
            print(f"✅ {package_name} - Already installed")
        else:
            print(f"❌ {package_name} - Not installed")
            missing_packages.append(package)
    
    if not missing_packages:
        print("\n🎉 All dependencies are already installed!")
        print("✅ You can run the bot now!")
        return True
    
    print(f"\n📦 Installing {len(missing_packages)} missing package(s)...")
    print()
    
    # Install missing packages
    success_count = 0
    for package in missing_packages:
        if install_package(package):
            success_count += 1
        print()
    
    # Summary
    print("📊 INSTALLATION SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully installed: {success_count}/{len(missing_packages)}")
    
    if success_count == len(missing_packages):
        print("\n🎉 All dependencies installed successfully!")
        print("✅ You can now run the bot!")
        print()
        print("🚀 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Start creating listings!")
        return True
    else:
        print(f"\n⚠️ {len(missing_packages) - success_count} package(s) failed to install")
        print("💡 Try running: pip install --upgrade pip")
        print("💡 Then run this script again")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)
