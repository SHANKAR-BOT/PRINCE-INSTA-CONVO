import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import chat_ui

st.set_page_config(page_title="Instagram Graph API", page_icon="📱")

chat_ui.init_chat_state()

st.title("📱 Instagram Graph API Integration")

main_col, chat_col = st.columns([2, 1])

with chat_col:
    chat_ui.render_chat_panel()

with main_col:
    st.markdown("""
    ### Official Instagram Messaging API

Instagram ka **official API** use karke messages send kar sakte ho - **completely legal and safe**! 🎯

**Vs Browser Automation:**
| Feature | Browser Automation | Instagram API |
|---------|-------------------|---------------|
| **Legality** | ⚠️ Gray area | ✅ Official & Legal |
| **Blocking Risk** | 🔴 High | 🟢 None |
| **Reliability** | ⚠️ Can break anytime | ✅ Stable |
| **Rate Limits** | ❌ Unpredictable | ✅ Clear limits |
| **Setup** | 🟢 Easy | ⚠️ Complex |
| **Cost** | 🟢 Free | ⚠️ May have costs |
""")

st.divider()

st.info("⚠️ **Important**: Instagram Graph API is still in development for this app. Below are instructions for future implementation.")

st.divider()

st.subheader("📋 Prerequisites")

st.markdown("""
To use Instagram Graph API, you need:

1. **Instagram Business Account**
   - Convert your personal account to Business
   - Link it to a Facebook Page

2. **Facebook Developer Account**
   - Sign up at [developers.facebook.com](https://developers.facebook.com)
   - Create a new App
   - Add Instagram Graph API

3. **API Access Token**
   - Generate a long-lived access token
   - Configure permissions (instagram_basic, instagram_manage_messages)

4. **Webhook Setup**
   - For receiving messages
   - Requires public URL (Replit provides this!)
""")

st.divider()

st.subheader("🔧 Setup Steps (Coming Soon)")

with st.expander("📚 View Detailed Setup Guide"):
    st.markdown("""
    ### Step 1: Convert to Business Account
    
    1. Open Instagram app on phone
    2. Go to Settings → Account
    3. Switch to Professional Account
    4. Choose "Business"
    5. Connect to a Facebook Page (create one if needed)
    
    ---
    
    ### Step 2: Create Facebook App
    
    1. Go to [developers.facebook.com](https://developers.facebook.com)
    2. Click "My Apps" → "Create App"
    3. Choose "Business" type
    4. Fill in app details:
       - App Name: "Instagram DM Bot"
       - Contact Email: your email
    5. Click "Create App"
    
    ---
    
    ### Step 3: Add Instagram Graph API
    
    1. In your Facebook App dashboard
    2. Click "Add Product"
    3. Find "Instagram" → Click "Set Up"
    4. Follow the configuration wizard
    5. Add Instagram Business Account
    
    ---
    
    ### Step 4: Generate Access Token
    
    1. Go to Graph API Explorer
    2. Select your App
    3. Add permissions:
       - `instagram_basic`
       - `instagram_manage_messages`
       - `pages_read_engagement`
    4. Click "Generate Access Token"
    5. Save the token securely!
    
    **Make it long-lived:**
    ```bash
    curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?
        grant_type=fb_exchange_token&
        client_id={app-id}&
        client_secret={app-secret}&
        fb_exchange_token={short-lived-token}"
    ```
    
    ---
    
    ### Step 5: Configure Webhooks
    
    1. In Facebook App → Products → Webhooks
    2. Subscribe to Instagram
    3. Add Callback URL: `https://your-repl.repl.co/webhook`
    4. Set Verify Token: `your_secret_token`
    5. Subscribe to `messages` field
    
    ---
    
    ### Step 6: Send Test Message
    
    ```python
    import requests
    
    access_token = "YOUR_ACCESS_TOKEN"
    instagram_account_id = "YOUR_IG_ACCOUNT_ID"
    recipient_id = "RECIPIENT_IG_USER_ID"
    
    url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/messages"
    
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": "Hello from Instagram API!"},
        "access_token": access_token
    }
    
    response = requests.post(url, json=data)
    print(response.json())
    ```
    """)

st.divider()

st.subheader("💡 API Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **✅ What You CAN Do:**
    - Send/receive messages
    - Media messages (images, videos)
    - Quick replies
    - Message templates
    - Read receipts
    - Webhook notifications
    """)

with col2:
    st.markdown("""
    **❌ What You CAN'T Do:**
    - Send to users who haven't messaged first
    - Automated outreach
    - Mass messaging
    - Promotional content (in some cases)
    - Voice/video calls
    """)

st.divider()

st.subheader("📊 Rate Limits")

st.warning("""
### Instagram Graph API Rate Limits:

- **Default**: 200 requests per hour per user
- **Messaging**: 1000 messages per day per user
- **Burst**: Max 10 requests per second

**Note**: These limits are per Instagram account, not per app!
""")

st.divider()

st.subheader("💰 Pricing")

st.info("""
### Instagram Graph API Pricing:

**Good News**: The API itself is **FREE**! 🎉

**But consider:**
- Facebook/Instagram Business account (Free)
- Server hosting costs (Replit covers this!)
- Potential costs for premium features
- Time investment for setup and maintenance

**Bottom Line**: Much cheaper than getting banned! 😅
""")

st.divider()

st.subheader("🔮 Future Implementation")

st.markdown("""
This app will soon support Instagram Graph API! Here's what's planned:

1. ✅ One-click API setup wizard
2. ✅ Automatic token refresh
3. ✅ Webhook handling
4. ✅ Message sending interface
5. ✅ Analytics dashboard
6. ✅ Fallback to browser automation

**Timeline**: Coming in next update! 🚀
""")

st.divider()

st.success("""
### 🎯 Recommendation:

**For now**: Use browser automation with persistent profile (works great!)

**For production**: Setup Instagram Graph API (more reliable, won't get banned)

**Best approach**: Have both options available! 💪

Use the **Profile Setup** page to get browser automation working immediately,  
then setup Graph API later for production use!
""")

st.divider()

st.markdown("""
### 📚 Resources:

- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api/)
- [Messenger Platform Overview](https://developers.facebook.com/docs/messenger-platform)
- [Instagram Business API](https://developers.facebook.com/docs/instagram-api/guides/messaging)
- [Rate Limits Guide](https://developers.facebook.com/docs/graph-api/overview/rate-limiting)

---

**Questions?** Contact developer at [@prince_malhotra](https://instagram.com/prince_malhotra)
""")
