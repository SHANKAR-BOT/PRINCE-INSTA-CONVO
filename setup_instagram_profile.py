#!/usr/bin/env python3
"""
Instagram Profile Setup Tool
Manually login karke browser profile save karo
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import time
import sys

def setup_instagram_profile(username):
    """
    Open browser for manual Instagram login and save profile
    """
    print("\n" + "="*70)
    print("🔐 INSTAGRAM PROFILE SETUP TOOL")
    print("="*70)
    print(f"📝 Setting up profile for: {username}")
    print("="*70 + "\n")
    
    # Create profile directory
    profile_dir = Path(f'/tmp/chrome_profiles/{username}')
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    chrome_options = Options()
    
    # Use persistent profile
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    
    # NON-HEADLESS mode for manual login
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1200,900')
    
    # Stealth mode
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Find Chrome/Chromium
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            print(f'✅ Found browser: {chromium_path}')
            break
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            print(f'✅ Found ChromeDriver: {driver_path}')
            break
    
    try:
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        print("\n" + "="*70)
        print("📱 BROWSER WINDOW OPENED!")
        print("="*70)
        print()
        print("📝 INSTRUCTIONS:")
        print("1. Browser window open ho gaya hai")
        print("2. Instagram pe LOGIN karo (apne real credentials se)")
        print("3. Agar 2FA/OTP aaye to complete karo")
        print("4. Login SUCCESSFUL hone ke baad")
        print("5. Yaha ENTER press karo")
        print()
        print("⚠️  IMPORTANT:")
        print("   - 'Save login info' ko YES karo")
        print("   - 'Turn on Notifications' ko NOT NOW karo")
        print("   - Make sure you see your Instagram FEED")
        print()
        print("="*70 + "\n")
        
        # Navigate to Instagram
        print("🌐 Opening Instagram...")
        driver.get('https://www.instagram.com/')
        time.sleep(3)
        
        # Wait for manual login
        input("⏸️  Press ENTER after you have SUCCESSFULLY logged in and see your feed... ")
        
        # Verify login
        current_url = driver.current_url
        print(f"\n📍 Current URL: {current_url}")
        
        if 'instagram.com' in current_url and 'login' not in current_url.lower():
            print("\n" + "="*70)
            print("✅ SUCCESS! LOGIN VERIFIED!")
            print("="*70)
            print(f"📁 Profile saved to: {profile_dir}")
            print()
            print("🎉 Ab tum automation use kar sakte ho!")
            print("   - Profile automatically load hogi")
            print("   - Password nahi chahiye")
            print("   - Session maintain rahega")
            print()
            print("💡 TIP: Agar automation fail hoga to yeh script phir se run karo")
            print("="*70 + "\n")
        else:
            print("\n" + "="*70)
            print("❌ LOGIN INCOMPLETE!")
            print("="*70)
            print(f"Current URL: {current_url}")
            print()
            print("⚠️  Please make sure you:")
            print("   1. Entered correct credentials")
            print("   2. Completed 2FA if required")
            print("   3. Can see your Instagram feed")
            print()
            print("🔄 Please run this script again to retry")
            print("="*70 + "\n")
        
        time.sleep(3)
        driver.quit()
        
        print("✅ Browser closed. Profile saved!\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        driver.quit() if 'driver' in locals() else None
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        driver.quit() if 'driver' in locals() else None
        sys.exit(1)


if __name__ == "__main__":
    print("\n🔐 Instagram Profile Setup Tool\n")
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter your Instagram username: ").strip()
    
    if not username:
        print("❌ Username required!")
        sys.exit(1)
    
    setup_instagram_profile(username)
