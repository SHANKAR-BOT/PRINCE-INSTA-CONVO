import os
from openai import OpenAI

# Multiple Groq API keys with automatic fallback
# If one key fails, automatically tries the next one
# Load API keys from environment variables for security
def get_groq_api_keys():
    """
    Get Groq API keys from environment variables
    Supports up to 4 keys: GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3, GROQ_API_KEY_4
    Falls back to single GROQ_API_KEY for backwards compatibility
    """
    keys = []
    
    # Try to get up to 4 API keys
    for i in range(1, 5):
        key = os.environ.get(f"GROQ_API_KEY_{i}")
        if key:
            keys.append(key)
    
    # Fallback to single GROQ_API_KEY if no numbered keys found
    if not keys:
        single_key = os.environ.get("GROQ_API_KEY")
        if single_key:
            keys.append(single_key)
    
    return keys

GROQ_API_KEYS = get_groq_api_keys()

def get_openai_client(api_key):
    """Create OpenAI client with specific API key"""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

# Comprehensive system context about the Instagram DM Automation app
SYSTEM_CONTEXT = """
You are Pika, an AI Assistant for the Instagram DM Automation Tool created by Prince Malhotra.
You help users understand and use this application effectively.

**App Overview:**
This is a powerful Instagram automation tool that allows users to automatically send direct messages on Instagram. 
It has secure login, multi-user support, and real-time monitoring.

**Key Features:**
1. 🔐 **Secure Authentication** - Sign up with username and password
2. 📸 **Instagram DM Automation** - Send automated Instagram direct messages
3. 🤖 **Automated Messages** - Custom delays and message rotation
4. 📊 **Real-time Logs** - Monitor automation status live
5. 🔄 **Auto-Resume** - Continues automation after restarts
6. 💾 **Persistent Storage** - MongoDB Atlas for data
7. 🔒 **Encrypted Credentials** - Secure password encryption

**How to Use the App (Step by Step):**

**STEP 1: Sign Up / Login**
- New users: Click "Sign Up" tab, enter username and password
- Existing users: Click "Login" tab, enter credentials
- Session saves automatically for 7 days

**STEP 2: Setup Configuration**
After login, you need to configure these settings:
- **Target Instagram Username**: The person you want to send DMs to (without @)
- **Your Instagram Username**: Your Instagram account username
- **Instagram Password**: Your Instagram account password (encrypted and secure)
- **Message Prefix**: Text added before each message (e.g., "Good Morning")
- **Delay (seconds)**: Time between messages (default: 60 seconds)

**STEP 3: Instagram Cookies (Optional but Recommended)**
Instagram cookies help bypass login issues. 

**Method 1: Using EditThisCookie Extension (RECOMMENDED - EASIEST)**
1. Install EditThisCookie Extension:
   Link: https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol?hl=en-GB&utm_source=ext_sidebar
2. Login to Instagram in your browser
3. Click on the EditThisCookie icon in your browser toolbar
4. Click "Export" button (it will copy all cookies in JSON format)
5. Paste the exported cookies in the "Instagram Cookies" field in the app
6. Click "Save Configuration"

**Method 2: Using Manual Cookie Entry Form**
1. Go to "Instagram Cookies" page in the app
2. Use "Method 2: Manual Cookie Entry" form
3. Enter sessionid, csrftoken, and ds_user_id values individually
4. These values can be found in Developer Tools (F12 > Application > Cookies > instagram.com)
5. Click "Save Cookies"

Note: For bulk cookie paste, use JSON array format from EditThisCookie. For manual entry, use the dedicated form.

**STEP 4: Start Automation**
- Click "Start Automation" button
- Watch real-time logs below
- Automation will:
  * Open Instagram in browser
  * Login to your account
  * Navigate to target user's DM
  * Send messages with your prefix
  * Wait for specified delay
  * Repeat automatically

**STEP 5: Monitor & Stop**
- Real-time logs show every action
- Message counter displays total sent
- Click "Stop Automation" to halt anytime
- Logs are saved automatically

**Common Questions:**

Q: How do I get Instagram cookies?
A: **Easy Method (Recommended):** 
   1. Install EditThisCookie Extension: https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol?hl=en-GB&utm_source=ext_sidebar
   2. Login to Instagram
   3. Click EditThisCookie icon > Export (exports JSON format)
   4. Paste the JSON in "Instagram Cookies" field in app
   **Manual Method:** Use the "Manual Cookie Entry" form on the Instagram Cookies page and enter sessionid, csrftoken values individually

Q: What if automation stops?
A: It auto-resumes! Just refresh the page and it continues from where it stopped.

Q: Is my password safe?
A: Yes! Passwords are encrypted using industry-standard encryption.

Q: Can I use multiple accounts?
A: Yes! Each user has separate configurations and sessions.

Q: What is the best delay time?
A: 60-120 seconds recommended to avoid Instagram limits.

**Important Notes:**
- Keep automation within Instagram's limits to avoid blocks
- Use realistic delays (60+ seconds recommended)
- Monitor logs regularly
- Your data is private and encrypted

**Getting Help:**
Ask me anything about:
- How to set up your account
- How to configure settings
- How to find Instagram cookies
- Troubleshooting issues
- Best practices for automation

I can answer in Hindi, English, or Hinglish - just ask me in your preferred language!
"""


def get_ai_response(user_message, conversation_history=None):
    """
    Get Pika AI assistant response for user queries with automatic API key fallback
    
    Args:
        user_message: The user's question or message
        conversation_history: List of previous messages in format [{"role": "user"/"assistant", "content": "..."}]
    
    Returns:
        Pika AI assistant's response
    """
    messages = []
    
    messages.append({
        "role": "system",
        "content": SYSTEM_CONTEXT
    })
    
    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Try each API key until one works (automatic fallback)
    last_error = None
    for i, api_key in enumerate(GROQ_API_KEYS, 1):
        try:
            openai_client = get_openai_client(api_key)
            response = openai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1000
            )
            return response.choices[0].message.content
            
        except Exception as e:
            last_error = str(e)
            # Try next API key if this one failed
            if i < len(GROQ_API_KEYS):
                continue
            else:
                # All API keys failed
                return f"Sorry, Pika encountered an error with all API keys. Last error: {last_error}"
    
    return "Sorry, Pika couldn't process your request at this time."


def get_quick_guide(topic):
    """
    Get quick guides for specific topics
    
    Args:
        topic: One of ['signup', 'login', 'config', 'cookies', 'automation', 'troubleshoot']
    
    Returns:
        Quick guide text for the topic
    """
    guides = {
        'signup': """
**📝 Sign Up Guide:**
1. Click on "Sign Up" tab
2. Enter a unique username
3. Create a strong password
4. Click "Sign Up" button
5. You'll be automatically logged in!
        """,
        
        'login': """
**🔑 Login Guide:**
1. Click on "Login" tab
2. Enter your username
3. Enter your password
4. Click "Login" button
5. Your session will be saved for 7 days
        """,
        
        'config': """
**⚙️ Configuration Guide:**
1. **Target Username**: Instagram user to send DMs (without @)
2. **Your Username**: Your Instagram username
3. **Your Password**: Your Instagram password (encrypted)
4. **Message Prefix**: Text before each message
5. **Delay**: Seconds between messages (60+ recommended)
6. Click "Save Configuration" when done
        """,
        
        'cookies': """
**🍪 Instagram Cookies Guide:**

**Method 1: EditThisCookie Extension (EASIEST - RECOMMENDED)**
1. Install EditThisCookie Extension from:
   https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol?hl=en-GB&utm_source=ext_sidebar
2. Open Instagram.com and login to your account
3. Click on EditThisCookie extension icon in toolbar
4. Click "Export" button (copies all cookies in JSON format)
5. Paste in "Instagram Cookies" field in the app
6. Click "Save Configuration"

**Method 2: Manual Cookie Entry Form**
1. Go to "Instagram Cookies" page in the app
2. Use "Method 2: Manual Cookie Entry" form
3. Login to Instagram in browser and open Developer Tools (F12)
4. Go to Application > Cookies > https://instagram.com
5. Find these cookies and copy their VALUES:
   - sessionid (Required)
   - csrftoken (Optional)
   - ds_user_id (Optional)
6. Paste each value in the corresponding field in the form
7. Click "Save Cookies"

**Note:** App accepts JSON array format for bulk cookie import via EditThisCookie extension
        """,
        
        'automation': """
**🤖 Start Automation Guide:**
1. Make sure configuration is saved
2. Click "Start Automation" button
3. Watch real-time logs appear
4. Browser will open (headless mode)
5. Messages will be sent automatically
6. Monitor the message counter
7. Click "Stop Automation" to halt anytime
        """,
        
        'troubleshoot': """
**🔧 Troubleshooting Guide:**

**Problem: Automation won't start**
- Check if configuration is saved
- Verify Instagram credentials are correct
- Ensure cookies are properly formatted

**Problem: Messages not sending**
- Check internet connection
- Verify target username is correct
- Check Instagram account isn't blocked

**Problem: Login failed**
- Re-enter Instagram password
- Update Instagram cookies
- Check if Instagram requires verification

**Problem: App crashed**
- Refresh the page
- Auto-resume will continue from where it stopped
- Check the logs for error details
        """
    }
    
    return guides.get(topic, "Topic not found. Available topics: signup, login, config, cookies, automation, troubleshoot")


def get_welcome_message():
    """Returns a welcome message for Pika AI assistant"""
    return """
👋 **Namaste! Main Pika hoon - Aapki AI Assistant!**

Main aapki madad ke liye yahan hoon! 

I can help you with:
- ✅ Account setup (Sign up / Login)
- ⚙️ Configuration settings
- 🍪 Getting Instagram cookies
- 🚀 Starting automation
- 🔧 Troubleshooting issues
- 📱 Any other questions about the app

Aap mujhse Hindi, English, ya Hinglish mein baat kar sakte ho!

**Quick Start:**
Type questions like:
- "How do I sign up?"
- "Instagram cookies kaise nikaalun?"
- "What is the best delay time?"
- "Automation kaise start karein?"

Kya main aapki kisi cheez mein madad kar sakta hoon? 😊
    """
