# 📸 PRINCE INSTAGRAM DM - Instagram Automation Tool

A powerful Streamlit-based Instagram DM automation tool with secure credential management.

Created by **Prince Malhotra**

## 🌟 Features

- 🔐 **Secure Authentication** - MongoDB-based user management with session tokens
- 📸 **Instagram DM** - Automated Instagram Direct Messages
- 🤖 **Automated Messages** - Send messages automatically with custom delays
- 📊 **Real-time Logs** - Live monitoring of automation status
- 🔄 **Auto-Resume** - Automatically resumes automation after app restarts
- 💾 **Persistent Storage** - MongoDB Atlas for reliable data storage
- 🔒 **Encrypted Credentials** - Your Instagram password is encrypted and secure
- 🛡️ **Health Monitoring** - Auto-restart on crashes (Replit only)

## 🚀 Streamlit Cloud Deployment

### Prerequisites

1. MongoDB Atlas account with a cluster setup
2. Instagram account credentials
3. Telegram Bot Token (optional, for notifications)

### Environment Variables

Add these secrets in Streamlit Cloud dashboard:

```
MONGODB_URI=your_mongodb_connection_string
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ADMIN_ID=your_telegram_chat_id
```

### Deployment Steps

1. **Fork or Clone** this repository
2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```
3. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `streamlit_app.py`
   - Add secrets in "Advanced settings"
   - Click "Deploy"

### MongoDB Setup

1. Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a database user
3. Whitelist IP: `0.0.0.0/0` (Allow from anywhere)
4. Get connection string
5. Add to Streamlit secrets

## 📦 Requirements

All dependencies are listed in `requirements.txt`:
- streamlit
- selenium
- pymongo
- requests
- bcrypt
- pytz
- And more...

## 🔧 Local Development

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 5000
```

## 📱 Usage

1. **Sign Up** - Create your account
2. **Configure** - Add Target Instagram Username, Your Instagram credentials, Message prefix
3. **Start Automation** - Begin sending Instagram DMs
4. **Monitor** - Watch real-time logs
5. **Stop** - Stop automation anytime

## 🛡️ Security

- Passwords are hashed with SHA-256
- Session tokens with expiry
- MongoDB Atlas encryption at rest
- Instagram credentials encrypted with Fernet encryption

## 📞 Support

Created by **Prince Malhotra**

[Contact Developer on Instagram](https://www.instagram.com/prince_malhotra)

## ⚠️ Disclaimer

This tool is for educational purposes. Use responsibly and in accordance with Instagram's Terms of Service.

## 📝 License

Private - All rights reserved
