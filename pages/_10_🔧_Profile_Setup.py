import streamlit as st
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import chat_ui

st.set_page_config(page_title="Instagram Profile Setup", page_icon="🔧")

chat_ui.init_chat_state()

st.title("🔧 Instagram Browser Profile Setup")

main_col, chat_col = st.columns([2, 1])

with chat_col:
    chat_ui.render_chat_panel()

with main_col:
    st.markdown("""
    ### Why do you need a Browser Profile?

Instagram blocks automation **very aggressively**. Even with valid cookies, they can detect:
- 🤖 Bot-like behavior
- 🖥️ Different device fingerprints  
- 📍 Missing browser data (localStorage, session storage)
- 🔍 Headless browser signatures

**Solution:** Use a **persistent browser profile** that looks like a real, logged-in Chrome session! ✨
""")

st.divider()

st.markdown("""
### 🎯 How It Works:

1. **Manual Login** - You login once using a real Chrome window
2. **Profile Saved** - All session data, cookies, and fingerprints are saved
3. **Automation Uses It** - Future automation runs use this saved profile
4. **Instagram Thinks** - It's the same browser session every time! 🎭

---
""")

st.info("💡 **Pro Tip**: This is more reliable than just using cookies because Instagram sees the complete browser session!")

st.divider()

st.subheader("📋 Setup Instructions")

st.markdown("""
### Option 1: Using Python Script (Recommended)

Run this command in your terminal:

```bash
python3 setup_instagram_profile.py YOUR_INSTAGRAM_USERNAME
```

**Example:**
```bash
python3 setup_instagram_profile.py prince_malhotra
```

**What happens:**
1. Chrome window will open
2. You manually login to Instagram
3. Complete any 2FA/security challenges
4. Press ENTER after seeing your feed
5. Profile automatically saved! ✅

---

### Option 2: Using Streamlit (Experimental)

⚠️ **Note**: This runs in headless mode so you won't see the browser.  
Use Option 1 for best results!
""")

st.divider()

st.subheader("🔍 Check Profile Status")

instagram_username = st.text_input("Instagram Username", placeholder="your_instagram_username")

col1, col2 = st.columns(2)

with col1:
    if st.button("📁 Check Profile", use_container_width=True):
        if instagram_username:
            profile_dir = Path(f'/tmp/chrome_profiles/{instagram_username}')
            if profile_dir.exists():
                # Count files in profile
                file_count = sum(1 for _ in profile_dir.rglob('*') if _.is_file())
                
                st.success(f"✅ Profile exists!")
                st.info(f"📁 Location: {profile_dir}")
                st.info(f"📄 Files: {file_count}")
                
                # Check if it looks like a valid Chrome profile
                required_items = ['Default', 'Local State']
                has_required = [item for item in required_items if (profile_dir / item).exists()]
                
                if len(has_required) >= 1:
                    st.success(f"✅ Valid Chrome profile detected!")
                else:
                    st.warning("⚠️ Profile exists but may be incomplete. Run setup again.")
            else:
                st.error(f"❌ No profile found for @{instagram_username}")
                st.info("💡 Run the setup script to create a profile!")
        else:
            st.error("Please enter your Instagram username")

with col2:
    if st.button("🗑️ Delete Profile", use_container_width=True, type="secondary"):
        if instagram_username:
            profile_dir = Path(f'/tmp/chrome_profiles/{instagram_username}')
            if profile_dir.exists():
                import shutil
                shutil.rmtree(profile_dir)
                st.success(f"✅ Profile deleted for @{instagram_username}")
                st.rerun()
            else:
                st.info("No profile to delete")
        else:
            st.error("Please enter your Instagram username")

st.divider()

st.subheader("📚 Advanced: Manual Setup Steps")

with st.expander("🔧 View Detailed Instructions"):
    st.markdown("""
    ### Step-by-Step Manual Setup:
    
    1. **Open Terminal** in Replit
    
    2. **Run Setup Script:**
       ```bash
       python3 setup_instagram_profile.py YOUR_USERNAME
       ```
    
    3. **Browser Opens:**
       - Chrome window will appear (if not headless)
       - You'll see Instagram login page
    
    4. **Login Process:**
       - Enter your Instagram username/password
       - Complete 2FA if prompted
       - Click "Save Login Info" if asked
       - Click "Not Now" for notifications
    
    5. **Verify Login:**
       - Make sure you see your Instagram feed
       - NOT the login page
    
    6. **Confirm in Terminal:**
       - Go back to terminal
       - Press ENTER
       - Script will verify and save profile
    
    7. **Success!**
       - Profile saved to `/tmp/chrome_profiles/YOUR_USERNAME`
       - Automation will now use this profile
    
    ---
    
    ### Troubleshooting:
    
    **Problem:** Browser doesn't open
    - Make sure Chrome/Chromium is installed
    - Check terminal for error messages
    
    **Problem:** Can't see browser (headless mode)
    - Modify script to disable headless
    - Or use VNC viewer
    
    **Problem:** Profile not working in automation
    - Delete profile and setup again
    - Make sure you completed 2FA
    - Verify you saw the feed before pressing ENTER
    
    **Problem:** Instagram still asks for login
    - Session may have expired
    - Run setup script again
    - Check if IP address changed
    """)

st.divider()

st.warning("""
### ⚠️ Important Notes:

- **Sessions Expire**: Instagram sessions expire after ~90 days of inactivity
- **Different IPs**: If server IP changes, you may need to re-setup
- **2FA Required**: Complete all security challenges during setup
- **One Profile Per User**: Each Instagram account needs its own profile
- **Security**: Profile contains your session data - keep it secure!
""")

st.info("""
### 🎯 Next Steps After Setup:

1. ✅ Setup your browser profile (use this page)
2. 🔐 Go to Configuration page
3. ⚙️ Select "Cookies" login method (optional - profile alone might work!)
4. 🚀 Start automation
5. 📊 Check logs to verify success!

**Profile + Cookies = Maximum Success Rate!** 🎉
""")

st.divider()

st.success("""
### 💡 Why This Works:

Instagram checks for:
- ✅ Same device fingerprint → Profile provides this
- ✅ localStorage data → Profile includes this  
- ✅ Session cookies → Profile has everything
- ✅ Realistic browser → Chrome with full profile looks real
- ✅ Consistent behavior → Same profile = same "device"

Result: **Instagram thinks automation is just you browsing normally!** 🎭
""")
