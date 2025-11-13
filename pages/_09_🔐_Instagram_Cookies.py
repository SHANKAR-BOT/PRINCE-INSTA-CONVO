import streamlit as st
import pickle
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import chat_ui

st.set_page_config(page_title="Instagram Cookies Setup", page_icon="🔐")

chat_ui.init_chat_state()

st.title("🔐 Instagram Cookie Setup")

main_col, chat_col = st.columns([2, 1])

with chat_col:
    chat_ui.render_chat_panel()


main_col, chat_col = st.columns([2, 1])

with chat_col:
    chat_ui.render_chat_panel()

with main_col:
    render_main_content()
def render_main_content():
    st.markdown("""
    ### Why do we need cookies?

Instagram blocks automation tools very aggressively. To bypass this, we use **session cookies** from your real browser login.

This way, Instagram thinks the automation is from your regular logged-in session! 🎭
""")
    
        ### Why do we need cookies?

    Instagram blocks automation tools very aggressively. To bypass this, we use **session cookies** from your real browser login.

    This way, Instagram thinks the automation is from your regular logged-in session! 🎭
    """)

    st.divider()

    st.markdown("""
    ### 📝 How to get your Instagram cookies:

    1. **Open Instagram** in your browser (Chrome/Firefox)
    2. **Login** to your account
    3. **Open Developer Tools**:
       - Chrome: Press `F12` or `Right Click` → `Inspect`
       - Firefox: Press `F12`
    4. **Go to Application/Storage tab**
    5. **Click on Cookies** → `https://www.instagram.com`
    6. **Find these important cookies**:
       - `sessionid` (most important!)
       - `csrftoken`
       - `ds_user_id`
    7. **Copy the cookie values** and paste below

    ---
    """)

    st.info("💡 **Pro Tip**: Only `sessionid` is essential for basic automation. The others help make it more reliable.")

    st.divider()

    st.subheader("🎯 Method 1: Upload Cookies JSON (Recommended)")

    st.markdown("""
    **Using EditThisCookie Chrome Extension:**
    1. Install [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/) extension
    2. Login to Instagram
    3. Click the cookie icon
    4. Click "Export" (bottom right)
    5. Paste the exported JSON below
    """)

    uploaded_file = st.file_uploader("Or upload cookies.json file", type=['json', 'txt'])

    cookies_json = st.text_area(
        "Paste exported cookies JSON here:",
        height=200,
        placeholder='[{"name":"sessionid","value":"..."}, {...}]'
    )

    instagram_username = st.text_input("Your Instagram Username", placeholder="your_username")

    if st.button("💾 Save Cookies", type="primary"):
        if not instagram_username:
            st.error("❌ Please enter your Instagram username!")
        elif not cookies_json and not uploaded_file:
            st.error("❌ Please paste cookies JSON or upload a file!")
        else:
            try:
                if uploaded_file:
                    cookies_data = json.load(uploaded_file)
                else:
                    cookies_data = json.loads(cookies_json)
            
                cookies_dir = Path('/tmp/instagram_cookies')
                cookies_dir.mkdir(exist_ok=True)
                cookies_path = cookies_dir / f"{instagram_username}_cookies.pkl"
            
                with open(cookies_path, 'wb') as f:
                    pickle.dump(cookies_data, f)
            
                st.success(f"✅ Cookies saved successfully for @{instagram_username}!")
                st.success(f"📁 Saved to: {cookies_path}")
                st.balloons()
            
                st.info("🚀 Now you can start automation and it will use these cookies!")
            
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format! Please check and try again.")
            except Exception as e:
                st.error(f"❌ Error saving cookies: {str(e)}")

    st.divider()

    st.subheader("🎯 Method 2: Manual Cookie Entry")

    with st.form("manual_cookies"):
        st.markdown("Enter cookies manually:")
    
        sessionid = st.text_input("sessionid (Required)", type="password")
        csrftoken = st.text_input("csrftoken (Optional)", type="password")
        ds_user_id = st.text_input("ds_user_id (Optional)", type="password")
        username_manual = st.text_input("Instagram Username")
    
        submit = st.form_submit_button("💾 Save Cookies")
    
        if submit:
            if not username_manual or not sessionid:
                st.error("❌ Username and sessionid are required!")
            else:
                try:
                    cookies = []
                
                    cookies.append({
                        "name": "sessionid",
                        "value": sessionid,
                        "domain": ".instagram.com",
                        "path": "/",
                        "secure": True,
                        "httpOnly": True
                    })
                
                    if csrftoken:
                        cookies.append({
                            "name": "csrftoken",
                            "value": csrftoken,
                            "domain": ".instagram.com",
                            "path": "/",
                            "secure": True
                        })
                
                    if ds_user_id:
                        cookies.append({
                            "name": "ds_user_id",
                            "value": ds_user_id,
                            "domain": ".instagram.com",
                            "path": "/",
                            "secure": True
                        })
                
                    cookies_dir = Path('/tmp/instagram_cookies')
                    cookies_dir.mkdir(exist_ok=True)
                    cookies_path = cookies_dir / f"{username_manual}_cookies.pkl"
                
                    with open(cookies_path, 'wb') as f:
                        pickle.dump(cookies, f)
                
                    st.success(f"✅ Cookies saved for @{username_manual}!")
                    st.balloons()
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.divider()

    st.subheader("📋 Saved Cookies")

    cookies_dir = Path('/tmp/instagram_cookies')
    if cookies_dir.exists():
        cookie_files = list(cookies_dir.glob("*_cookies.pkl"))
    
        if cookie_files:
            st.success(f"Found {len(cookie_files)} saved cookie file(s)")
        
            for cookie_file in cookie_files:
                username = cookie_file.stem.replace("_cookies", "")
                col1, col2 = st.columns([3, 1])
            
                with col1:
                    st.text(f"👤 @{username}")
            
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{username}"):
                        cookie_file.unlink()
                        st.rerun()
        else:
            st.info("No saved cookies yet")
    else:
        st.info("No saved cookies yet")

    st.divider()

    st.warning("""
    ### ⚠️ Security Notes:
    - Cookies are stored temporarily on this server
    - Never share your cookies with anyone
    - Cookies expire after some time (usually 90 days)
    - If automation stops working, refresh your cookies
    """)

    st.info("""
    ### 🔄 Alternative: Instagram Graph API
    For production apps, consider using **Instagram Graph API** (official API):
    - More reliable and stable
    - No risk of being blocked
    - Requires Facebook Business account
    - Has rate limits but official support
    """)
