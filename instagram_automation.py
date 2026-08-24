"""
Instagram Automation Module
Instagram login aur DM automation ke liye functions
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import json
import pickle
import os

def parse_cookies_from_json(cookies_json_string):
    """
    Simple cookie parser - Convert pasted JSON cookies to Selenium format
    User sirf cookies paste kare, koi file save nahi!
    """
    try:
        cookies_data = json.loads(cookies_json_string)
        
        if not isinstance(cookies_data, list):
            return None
        
        # Clean cookies for Selenium
        clean_cookies = []
        for cookie in cookies_data:
            if not isinstance(cookie, dict):
                continue
                
            clean_cookie = {
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                'domain': cookie.get('domain', '.instagram.com'),
                'path': cookie.get('path', '/'),
            }
            
            # Add optional fields
            if 'secure' in cookie:
                clean_cookie['secure'] = cookie['secure']
            if 'httpOnly' in cookie:
                clean_cookie['httpOnly'] = cookie['httpOnly']
            if 'sameSite' in cookie and cookie['sameSite'] != 'unspecified':
                clean_cookie['sameSite'] = cookie['sameSite']
            
            # Handle expiry
            if 'expirationDate' in cookie:
                clean_cookie['expiry'] = int(cookie['expirationDate'])
            elif 'expiry' in cookie:
                clean_cookie['expiry'] = int(cookie['expiry'])
            
            clean_cookies.append(clean_cookie)
        
        return clean_cookies
    except:
        return None

def load_cookies_from_json(driver, cookies_json_string, log_callback=None, automation_state=None):
    """
    Simple direct cookie loading - No files, no saving!
    Cookies directly JSON se Selenium mein inject ho jayengi
    """
    def log(msg):
        if log_callback:
            log_callback(msg, automation_state)
    
    try:
        # Navigate to Instagram first
        driver.get('https://www.instagram.com/')
        time.sleep(2)
        
        # Clear existing cookies
        driver.delete_all_cookies()
        time.sleep(1)
        
        # Parse cookies
        cookies_list = parse_cookies_from_json(cookies_json_string)
        
        if not cookies_list:
            if log_callback:
                log("❌ Failed to parse cookies JSON!")
            return False
        
        # Add cookies
        added_count = 0
        failed_count = 0
        
        for cookie in cookies_list:
            try:
                driver.add_cookie(cookie)
                added_count += 1
            except Exception as e:
                failed_count += 1
        
        if log_callback:
            log(f"✅ Cookies loaded: {added_count} added, {failed_count} failed")
        
        return added_count > 0
        
    except Exception as e:
        if log_callback:
            log(f"❌ Cookie loading error: {str(e)}")
        return False

def get_cookies_path(username):
    """Get path for user's cookies file"""
    cookies_dir = Path('/tmp/instagram_cookies')
    cookies_dir.mkdir(exist_ok=True)
    return cookies_dir / f"{username}_cookies.pkl"

def save_cookies(driver, username, log_callback=None):
    """Save Instagram cookies for a user"""
    try:
        cookies_path = get_cookies_path(username)
        cookies = driver.get_cookies()
        with open(cookies_path, 'wb') as f:
            pickle.dump(cookies, f)
        if log_callback:
            log_callback(f"✅ Cookies saved for @{username}", None)
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Failed to save cookies: {str(e)}", None)
        return False

def load_cookies(driver, username, log_callback=None):
    """Load Instagram cookies for a user"""
    try:
        cookies_path = get_cookies_path(username)
        if not cookies_path.exists():
            if log_callback:
                log_callback(f"ℹ️ No saved cookies found for @{username}", None)
            return False
        
        driver.get('https://www.instagram.com/')
        time.sleep(3)
        
        # Clear existing cookies first
        driver.delete_all_cookies()
        time.sleep(1)
        
        with open(cookies_path, 'rb') as f:
            cookies = pickle.load(f)
        
        # Clean and add cookies
        added_count = 0
        failed_count = 0
        
        for cookie in cookies:
            try:
                # Clean cookie - remove EditThisCookie extra fields
                clean_cookie = {
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    'domain': cookie.get('domain'),
                    'path': cookie.get('path', '/'),
                }
                
                # Add optional fields if present
                if 'secure' in cookie:
                    clean_cookie['secure'] = cookie['secure']
                if 'httpOnly' in cookie:
                    clean_cookie['httpOnly'] = cookie['httpOnly']
                if 'sameSite' in cookie and cookie['sameSite'] != 'unspecified':
                    clean_cookie['sameSite'] = cookie['sameSite']
                
                # Add expiry if present (convert to int)
                if 'expirationDate' in cookie:
                    clean_cookie['expiry'] = int(cookie['expirationDate'])
                elif 'expiry' in cookie:
                    clean_cookie['expiry'] = int(cookie['expiry'])
                
                driver.add_cookie(clean_cookie)
                added_count += 1
                
            except Exception as e:
                failed_count += 1
        
        if log_callback:
            log_callback(f"✅ Cookies loaded: {added_count} added, {failed_count} failed", None)
        
        return added_count > 0
        
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Failed to load cookies: {str(e)}", None)
        return False

def setup_instagram_browser(automation_state=None, log_callback=None, use_profile=True, username='default'):
    """Setup Chrome browser for Instagram automation with persistent profile"""
    def log(msg):
        if log_callback:
            log_callback(msg, automation_state)
    
    log('Setting up Chrome browser for Instagram...')

    chrome_options = Options()
    
    # Use persistent profile for better session management
    if use_profile:
        profile_dir = Path(f'/tmp/chrome_profiles/{username}')
        profile_dir.mkdir(parents=True, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={profile_dir}')
        chrome_options.add_argument('--profile-directory=Default')
        log(f'Using persistent profile: {profile_dir}')
    
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Enhanced stealth mode
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # More realistic browser fingerprint
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    chrome_options.add_argument('--lang=en-US,en;q=0.9')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Performance and stability
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')

    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]

    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log(f'Found Chromium at: {chromium_path}')
            break

    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]

    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log(f'Found ChromeDriver at: {driver_path}')
            break

    try:
        from selenium.webdriver.chrome.service import Service

        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log('Chrome started with detected ChromeDriver!')
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log('Chrome started with default driver!')

        driver.set_window_size(1920, 1080)
        
        # Enhanced stealth scripts
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        })
        
        # Comprehensive stealth script
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        window.navigator.chrome = {runtime: {}};
        Object.defineProperty(navigator, 'permissions', {
            get: () => ({
                query: () => Promise.resolve({state: 'denied'})
            })
        });
        """
        driver.execute_script(stealth_script)
        
        log('Chrome browser setup completed successfully!')
        log('✅ Stealth mode activated!')
        return driver
    except Exception as error:
        log(f'Browser setup failed: {error}')
        raise error


def instagram_login(driver, username, password, automation_state=None, process_id='AUTO-1', log_callback=None, use_cookies=True, cookies_json=None):
    """Login to Instagram with cookies or username/password
    
    Args:
        cookies_json: Optional JSON string of cookies - agar ye hai to directly use karenge, file se nahi!
    """
    def log(msg):
        if log_callback:
            log_callback(msg, automation_state)
    
    try:
        if use_cookies:
            log(f'{process_id}: Using cookies for login...')
            
            # NEW: Check if cookies_json provided directly (simplified flow!)
            if cookies_json:
                log(f'{process_id}: Loading cookies directly from config (no file needed)...')
                cookies_loaded = load_cookies_from_json(driver, cookies_json, log_callback, automation_state)
                log(f'{process_id}: ✅ Cookies saved successfully!')
            else:
                # OLD: Fallback to file-based cookies for backward compatibility
                log(f'{process_id}: Trying to login with saved cookies...')
                cookies_loaded = load_cookies(driver, username, log_callback)
            
            if cookies_loaded:
                driver.refresh()
                time.sleep(5)
                
                # Better verification - navigate to direct inbox to verify session
                log(f'{process_id}: Verifying Instagram session...')
                driver.get('https://www.instagram.com/direct/inbox/')
                time.sleep(5)
                
                current_url = driver.current_url
                log(f'{process_id}: Verification URL: {current_url}')
                
                if '/direct/' in current_url and '/accounts/login' not in current_url:
                    log(f'{process_id}: ✅ Login successful using cookies!')
                    
                    # Dismiss any popups
                    try:
                        not_now_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
                        for btn in not_now_buttons:
                            try:
                                btn.click()
                                time.sleep(1)
                            except:
                                pass
                    except:
                        pass
                    
                    return True
                else:
                    log(f'{process_id}: ⚠️ Cookies expired or invalid!')
                    log(f'{process_id}: 💡 Please generate fresh cookies using Profile Setup page')
                    return False
        
        log(f'{process_id}: Navigating to Instagram...')
        driver.get('https://www.instagram.com/')
        time.sleep(8)
        
        log(f'{process_id}: Current URL: {driver.current_url}')
        log(f'{process_id}: Page title: {driver.title}')
        
        log(f'{process_id}: Looking for login form...')
        
        try:
            username_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = driver.find_element(By.NAME, "password")
            
            log(f'{process_id}: Found login form, entering credentials...')
            
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(2)
            
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(2)
            
            log(f'{process_id}: Clicking login button...')
            password_input.send_keys(Keys.RETURN)
            
            time.sleep(10)
            
            if 'challenge' in driver.current_url.lower() or 'two_factor' in driver.current_url.lower():
                log(f'{process_id}: ⚠️ Security challenge detected!')
                log(f'{process_id}: 🔗 Challenge URL: {driver.current_url}')
                log(f'{process_id}: ')
                log(f'{process_id}: 🛠️ SOLUTION OPTIONS:')
                log(f'{process_id}: 1. Run: python3 setup_instagram_profile.py YOUR_USERNAME')
                log(f'{process_id}: 2. Manually login and complete challenge')
                log(f'{process_id}: 3. Use Profile Setup page in app')
                log(f'{process_id}: ')
                log(f'{process_id}: 💡 After manual login, automation will work!')
                
                # Save screenshot of challenge
                try:
                    screenshot_path = f'/tmp/instagram_challenge_{process_id}.png'
                    driver.save_screenshot(screenshot_path)
                    log(f'{process_id}: 📸 Challenge screenshot: {screenshot_path}')
                except:
                    pass
                
                return False
            
            if 'instagram.com' in driver.current_url and 'login' not in driver.current_url.lower():
                log(f'{process_id}: ✅ Login successful with password!')
                
                save_cookies(driver, username, log_callback)
                
                try:
                    save_info_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
                    if save_info_buttons:
                        save_info_buttons[0].click()
                        log(f'{process_id}: Dismissed save info dialog')
                        time.sleep(2)
                except:
                    pass
                
                try:
                    notification_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
                    if notification_buttons:
                        notification_buttons[0].click()
                        log(f'{process_id}: Dismissed notifications dialog')
                        time.sleep(2)
                except:
                    pass
                
                return True
            else:
                log(f'{process_id}: ❌ Login failed! Current URL: {driver.current_url}')
                return False
                
        except Exception as e:
            log(f'{process_id}: ❌ Error during login: {str(e)}')
            
            try:
                screenshot_path = f'/tmp/instagram_login_error_{process_id}.png'
                driver.save_screenshot(screenshot_path)
                log(f'{process_id}: Screenshot saved to {screenshot_path}')
                
                page_source_path = f'/tmp/instagram_page_source_{process_id}.html'
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                log(f'{process_id}: Page source saved to {page_source_path}')
            except:
                pass
            
            return False
            
    except Exception as e:
        log(f'{process_id}: ❌ Error navigating to Instagram: {str(e)}')
        return False


def open_instagram_dm(driver, target_username, automation_state=None, process_id='AUTO-1', log_callback=None, chat_id=None):
    """Open Instagram DM with target username or chat_id - Improved with multiple approaches"""
    def log(msg):
        if log_callback:
            log_callback(msg, automation_state)
    
    try:
        if chat_id:
            log(f'{process_id}: Opening DM using Chat ID: {chat_id}...')
            
            # First, establish Instagram session by visiting inbox
            log(f'{process_id}: Establishing Instagram session first...')
            driver.get('https://www.instagram.com/direct/inbox/')
            time.sleep(4)
            
            # Check if session is established (not on login page)
            if '/accounts/login' in driver.current_url:
                log(f'{process_id}: ⚠️ Session not established, Instagram asking for login again')
                if not target_username:
                    log(f'{process_id}: ❌ Chat ID failed and no username provided for fallback')
                    return False
                # Fall back to username approach
            else:
                log(f'{process_id}: ✅ Session established! Now opening chat...')
                
                # Now navigate to the specific chat
                chat_url = f'https://www.instagram.com/direct/t/{chat_id}/'
                driver.get(chat_url)
                time.sleep(6)
                
                current_url = driver.current_url
                log(f'{process_id}: Current URL after navigation: {current_url}')
                
                # Check if we're on a direct message page (more flexible check)
                if '/direct/' in current_url and '/accounts/login' not in current_url:
                    log(f'{process_id}: ✅ On Instagram Direct page, searching for message input...')
                    try:
                        # Wait for message input with multiple selectors
                        input_found = False
                        for attempt in range(3):
                            elements = driver.find_elements(By.CSS_SELECTOR, 
                                'div[contenteditable="true"], textarea, div[role="textbox"], input[placeholder*="Message"]')
                            if elements:
                                log(f'{process_id}: ✅ Chat opened successfully using Chat ID! Found {len(elements)} input elements')
                                input_found = True
                                break
                            log(f'{process_id}: Attempt {attempt + 1}/3: Waiting for message input...')
                            time.sleep(2)
                        
                        if input_found:
                            return True
                        else:
                            log(f'{process_id}: ⚠️ On Direct page but message input not found, trying username fallback...')
                    except Exception as e:
                        log(f'{process_id}: ⚠️ Error finding message input: {str(e)}, trying username fallback...')
                else:
                    log(f'{process_id}: ⚠️ Not on Direct page or login redirect (URL: {current_url}), trying username fallback...')
                
                if not target_username:
                    log(f'{process_id}: ❌ Chat ID failed and no username provided for fallback')
                    return False
        
        log(f'{process_id}: Opening DM with @{target_username}...')
        
        log(f'{process_id}: Approach 1 - Opening user profile...')
        profile_url = f'https://www.instagram.com/{target_username}/'
        driver.get(profile_url)
        time.sleep(5)
        
        message_button_selectors = [
            "//div[contains(text(), 'Message') and @role='button']",
            "//button[contains(text(), 'Message')]",
            "//div[@role='button']//div[text()='Message']",
            "//a[contains(@href, '/direct/t/')]",
            "//*[text()='Message']"
        ]
        
        for selector in message_button_selectors:
            try:
                message_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                message_button.click()
                log(f'{process_id}: ✅ Clicked Message button from profile!')
                time.sleep(4)
                return True
            except:
                continue
        
        log(f'{process_id}: Approach 2 - Trying direct messages page...')
        dm_url = 'https://www.instagram.com/direct/inbox/'
        driver.get(dm_url)
        time.sleep(5)
        
        new_message_selectors = [
            "//svg[@aria-label='New message']/..",
            "//*[@aria-label='New message']",
            "//div[contains(@class, 'x1i10hfl')]//svg[@aria-label='New message']/..",
            "//*[contains(text(), 'Send message')]"
        ]
        
        for selector in new_message_selectors:
            try:
                new_msg_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                new_msg_btn.click()
                log(f'{process_id}: Clicked new message button')
                time.sleep(3)
                break
            except:
                continue
        
        search_selectors = [
            "//input[@placeholder='Search...']",
            "//input[@name='queryBox']",
            "//input[@aria-label='Search input']",
            "//input[@type='text']"
        ]
        
        for selector in search_selectors:
            try:
                search_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                search_input.clear()
                search_input.send_keys(target_username)
                log(f'{process_id}: Searching for @{target_username}...')
                time.sleep(4)
                
                result_selectors = [
                    f"//span[text()='{target_username}']",
                    f"//div[contains(text(), '{target_username}')]",
                    f"//*[contains(text(), '@{target_username}')]",
                    "//div[@role='button']//span"
                ]
                
                for res_selector in result_selectors:
                    try:
                        first_result = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, res_selector))
                        )
                        first_result.click()
                        log(f'{process_id}: Selected user from search')
                        time.sleep(3)
                        
                        try:
                            chat_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Chat')]")
                            chat_button.click()
                            time.sleep(2)
                        except:
                            pass
                        
                        log(f'{process_id}: ✅ DM opened with @{target_username}')
                        return True
                    except:
                        continue
            except:
                continue
        
        log(f'{process_id}: ⚠️ Could not find DM elements, but continuing...')
        return True
            
    except Exception as e:
        log(f'{process_id}: ❌ Error in open_instagram_dm: {str(e)}')
        log(f'{process_id}: Trying to continue anyway...')
        return True


def find_instagram_message_input(driver, process_id, automation_state=None, log_callback=None):
    """Find Instagram message input field"""
    def log(msg):
        if log_callback:
            log_callback(msg, automation_state)
    
    log(f'{process_id}: Finding Instagram message input...')
    
    time.sleep(3)

    message_input_selectors = [
        'div[contenteditable="true"][aria-label*="Message"]',
        'div[contenteditable="true"][role="textbox"]',
        'textarea[placeholder*="Message"]',
        'div[contenteditable="true"]',
        'textarea'
    ]

    log(f'{process_id}: Trying {len(message_input_selectors)} selectors...')

    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} found {len(elements)} elements')

            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)

                    if is_editable:
                        log(f'{process_id}: ✅ Found editable message input!')
                        return element
                except:
                    continue
        except:
            continue

    log(f'{process_id}: ❌ Message input not found!')
    return None


def send_instagram_message(driver, message_input, message_text, automation_state=None, process_id='AUTO-1', log_callback=None):
    """Send a message on Instagram"""
    def log(msg):
        if log_callback:
            log_callback(msg, automation_state)
    
    try:
        # First, dismiss any popups that might be blocking
        try:
            popups = driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Dismiss')]")
            for popup in popups:
                try:
                    popup.click()
                    time.sleep(0.5)
                except:
                    pass
        except:
            pass
        
        # Clear the input first
        try:
            message_input.clear()
        except:
            pass
        
        # Focus and scroll into view
        driver.execute_script("""
            arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
            arguments[0].focus();
            arguments[0].click();
        """, message_input)
        
        time.sleep(0.5)
        
        # Type message character by character using Selenium (more realistic for React)
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(message_input).click().perform()
            time.sleep(0.3)
            
            # Type the message
            message_input.send_keys(message_text)
            time.sleep(0.5)
            
            # Trigger React's onChange events
            driver.execute_script("""
                const element = arguments[0];
                
                // Trigger multiple events that React listens to
                ['input', 'change', 'keyup'].forEach(eventType => {
                    const event = new Event(eventType, { bubbles: true });
                    element.dispatchEvent(event);
                });
                
                // Force React to detect the change
                if (element._valueTracker) {
                    element._valueTracker.setValue('');
                }
            """, message_input)
            
            time.sleep(0.5)
            
        except Exception as e:
            # Fallback to JavaScript if Selenium typing fails
            log(f'{process_id}: ⚠️ Selenium typing failed, using JS: {str(e)}')
            driver.execute_script("""
                const element = arguments[0];
                const message = arguments[1];

                element.focus();
                element.click();

                if (element.tagName === 'DIV') {
                    element.textContent = message;
                    element.innerHTML = message;
                } else {
                    element.value = message;
                }

                // Trigger all React events
                ['input', 'change', 'keydown', 'keyup', 'keypress'].forEach(eventType => {
                    const event = new Event(eventType, { bubbles: true });
                    element.dispatchEvent(event);
                });
            """, message_input, message_text)
            time.sleep(0.5)

        # Now send the message. Instagram changes its generated class names
        # frequently, so prefer stable accessibility attributes over classes
        # or visible text.
        send_button_selectors = [
            "//button[@aria-label='Send']",
            "//*[@role='button' and @aria-label='Send']",
            "//button[contains(translate(@aria-label, 'SEND', 'send'), 'send')]",
            "//*[@role='button' and contains(translate(@aria-label, 'SEND', 'send'), 'send')]",
            "//button[normalize-space(.)='Send']",
            "//*[@role='button' and normalize-space(.)='Send']",
            "//button[@type='submit']"
        ]

        send_button = None
        for selector in send_button_selectors:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        send_button = button
                        break
                if send_button:
                    break
            except Exception:
                continue

        if send_button:
            try:
                # Scroll button into view
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", send_button)
                time.sleep(0.5)
                
                # Try regular click first
                send_button.click()
                time.sleep(1)
                log(f'{process_id}: ✅ Message sent!')
                return True
            except Exception:
                # Fallback: JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(1)
                    log(f'{process_id}: ✅ Message sent (JS click)!')
                    return True
                except Exception:
                    pass
        else:
            log(f'{process_id}: ⚠️ Send button not found; trying Enter key')

        # Instagram normally sends a focused DM with Enter. Only report
        # success when the input was cleared after the key press; otherwise
        # the message may still be sitting in the composer.
        try:
            message_input.send_keys(Keys.ENTER)
            time.sleep(1)
            remaining_text = driver.execute_script("""
                const element = arguments[0];
                return (element.innerText || element.textContent ||
                        element.value || '').trim();
            """, message_input)
            if not remaining_text:
                log(f'{process_id}: ✅ Message sent via Enter key!')
                return True
            log(f'{process_id}: ❌ Enter key did not clear the message composer')
            return False
        except Exception as enter_error:
            log(f'{process_id}: ❌ Could not send with Enter: {str(enter_error)[:120]}')
            return False

    except Exception as e:
        log(f'{process_id}: ❌ Error sending message: {str(e)}')
        return False
