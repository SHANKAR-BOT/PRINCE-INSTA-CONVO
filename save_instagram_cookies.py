#!/usr/bin/env python3
"""
Instagram Cookie Saver
Manually login karke cookies save karo
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import pickle
import time

def save_cookies_manually(username):
    """
    Browser kholo aur manually login karo
    Cookies automatically save ho jayenge
    """
    print("🌐 Opening browser for manual Instagram login...")
    print(f"📝 Will save cookies for username: {username}")
    
    chrome_options = Options()
    # NON-HEADLESS MODE - browser dikhega
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1200,900')
    
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            print(f'✅ Found browser at: {chromium_path}')
            break
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            print(f'✅ Found ChromeDriver at: {driver_path}')
            break
    
    try:
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        print("\n" + "="*60)
        print("📱 INSTRUCTIONS:")
        print("="*60)
        print("1. Browser window open hogi")
        print("2. Instagram pe manually login karo")
        print("3. Login successful hone ke baad yaha 'done' type karo")
        print("4. Cookies automatically save ho jayengi")
        print("="*60 + "\n")
        
        driver.get('https://www.instagram.com/')
        time.sleep(3)
        
        input("⏸️  Press ENTER after you have logged in successfully...")
        
        current_url = driver.current_url
        if 'instagram.com' in current_url and 'login' not in current_url.lower():
            cookies_dir = Path('/tmp/instagram_cookies')
            cookies_dir.mkdir(exist_ok=True)
            cookies_path = cookies_dir / f"{username}_cookies.pkl"
            
            cookies = driver.get_cookies()
            with open(cookies_path, 'wb') as f:
                pickle.dump(cookies, f)
            
            print(f"\n✅ SUCCESS! Cookies saved for @{username}")
            print(f"📁 Saved to: {cookies_path}")
            print("\n🚀 Ab tum automation use kar sakte ho!")
        else:
            print("\n❌ Login incomplete! Current URL:", current_url)
            print("Please make sure you're logged in and try again.")
        
        time.sleep(2)
        driver.quit()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "🔐 Instagram Cookie Saver" + "\n")
    username = input("Enter your Instagram username: ").strip()
    
    if username:
        save_cookies_manually(username)
    else:
        print("❌ Username required!")
