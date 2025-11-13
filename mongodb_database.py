"""
MongoDB Database Module
सभी user data, configurations, sessions और logs को MongoDB में store करता है
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from pathlib import Path
import secrets
import os
import certifi
import ssl

# MongoDB Configuration
# Priority: Streamlit secrets > Environment variable > mongodb_config.py
try:
    import streamlit as st
    # Streamlit secrets से पढ़ने की कोशिश (Streamlit Cloud deployment के लिए)
    if hasattr(st, 'secrets') and 'MONGODB_URI' in st.secrets:
        MONGODB_URI = st.secrets['MONGODB_URI']
        DATABASE_NAME = "instagram_automation_db"
        USERS_COLLECTION = "users"
        USER_CONFIGS_COLLECTION = "user_configs"
        USER_SESSIONS_COLLECTION = "user_sessions"
        AUTOMATION_LOGS_COLLECTION = "automation_logs"
        AUTOMATION_LOCKS_COLLECTION = "automation_locks"
        AUTOMATION_INSTANCES_COLLECTION = "automation_instances"
        USER_MESSAGE_INDEX_COLLECTION = "user_message_index"
    else:
        raise ImportError("Streamlit secrets not available")
except (ImportError, FileNotFoundError):
    # Fallback: Environment variable या mongodb_config.py
    try:
        from mongodb_config import MONGODB_URI, DATABASE_NAME
        from mongodb_config import USERS_COLLECTION, USER_CONFIGS_COLLECTION
        from mongodb_config import USER_SESSIONS_COLLECTION, AUTOMATION_LOGS_COLLECTION, AUTOMATION_LOCKS_COLLECTION
        from mongodb_config import AUTOMATION_INSTANCES_COLLECTION, USER_MESSAGE_INDEX_COLLECTION
    except ImportError:
        # Final fallback: Environment variable
        MONGODB_URI = os.environ.get('MONGODB_URI', 'your_mongodb_connection_string_here')
        DATABASE_NAME = "instagram_automation_db"
        USERS_COLLECTION = "users"
        USER_CONFIGS_COLLECTION = "user_configs"
        USER_SESSIONS_COLLECTION = "user_sessions"
        AUTOMATION_LOGS_COLLECTION = "automation_logs"
        AUTOMATION_LOCKS_COLLECTION = "automation_locks"
        AUTOMATION_INSTANCES_COLLECTION = "automation_instances"
        USER_MESSAGE_INDEX_COLLECTION = "user_message_index"

# Encryption Key Management
ENCRYPTION_KEY_FILE = Path(__file__).parent / '.encryption_key'

def get_encryption_key():
    """
    Get encryption key for password storage
    Priority: Streamlit Secrets > Environment Variable > Local File
    
    For multi-deployment setup (3 Streamlit instances sharing MongoDB):
    - Set ENCRYPTION_KEY in Streamlit secrets for all 3 deployments
    - Use the SAME key across all deployments for password sharing
    """
    # Priority 1: Streamlit Secrets (for Streamlit Cloud deployments)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ENCRYPTION_KEY' in st.secrets:
            key = st.secrets['ENCRYPTION_KEY']
            # Convert string to bytes if needed
            if isinstance(key, str):
                key = key.encode('utf-8')
            print("🔐 Using shared encryption key from Streamlit Secrets")
            return key
    except (ImportError, Exception):
        pass
    
    # Priority 2: Environment Variable (for other deployments)
    env_key = os.environ.get('ENCRYPTION_KEY')
    if env_key:
        if isinstance(env_key, str):
            env_key = env_key.encode('utf-8')
        print("🔐 Using shared encryption key from Environment Variable")
        return env_key
    
    # Priority 3: Local file (for development only)
    if ENCRYPTION_KEY_FILE.exists():
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            print("⚠️ Using local encryption key (development mode)")
            print("💡 For production: Set ENCRYPTION_KEY in Streamlit Secrets or Environment")
            return f.read()
    else:
        # Generate new key for local development
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        print("🔑 Generated new encryption key (development mode)")
        print(f"📋 Key (base64): {key.decode('utf-8')}")
        print("💡 Copy this key to ENCRYPTION_KEY secret in all Streamlit deployments!")
        return key

ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# MongoDB Client
_client = None
_db = None

def get_mongodb_client():
    """MongoDB client connection singleton"""
    global _client, _db
    if _client is None:
        try:
            # Try multiple connection approaches with longer timeout for SSL
            connection_params = {
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 5000,
                'socketTimeoutMS': 5000,
                'tls': True,
                'tlsCAFile': certifi.where()
            }
            
            _client = MongoClient(MONGODB_URI, **connection_params)
            # Test connection
            _client.admin.command('ping')
            _db = _client[DATABASE_NAME]
            print("✅ MongoDB connected successfully!")
            print("💡 All signup/login data will now be stored in MongoDB Atlas")
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("\n⚠️  IMPORTANT: MongoDB Atlas IP Whitelisting Required!")
            print("📋 Please follow these steps:")
            print("1. Go to https://cloud.mongodb.com")
            print("2. Select your project and cluster")
            print("3. Click on 'Network Access' in the left sidebar")
            print("4. Click 'Add IP Address'")
            print("5. Select 'Allow Access From Anywhere' (0.0.0.0/0)")
            print("6. Click 'Confirm' and wait 1-2 minutes")
            print("\n💡 After whitelisting, restart the app to connect to MongoDB\n")
            return None
        except Exception as e:
            print(f"❌ MongoDB error: {e}")
            print("💡 App will continue to work, but MongoDB features will be unavailable")
            return None
    
    return _db

def init_db():
    """Initialize MongoDB collections with indexes"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        # Users collection indexes
        db[USERS_COLLECTION].create_index([("username", ASCENDING)], unique=True)
        
        # User configs collection indexes
        db[USER_CONFIGS_COLLECTION].create_index([("user_id", ASCENDING)])
        
        # User sessions collection indexes
        db[USER_SESSIONS_COLLECTION].create_index([("token_hash", ASCENDING)], unique=True)
        db[USER_SESSIONS_COLLECTION].create_index([("user_id", ASCENDING)])
        db[USER_SESSIONS_COLLECTION].create_index([("expires_at", ASCENDING)])
        
        # Automation logs collection indexes
        db[AUTOMATION_LOGS_COLLECTION].create_index([("user_id", ASCENDING)])
        db[AUTOMATION_LOGS_COLLECTION].create_index([("timestamp", DESCENDING)])
        
        # Automation locks collection indexes
        db[AUTOMATION_LOCKS_COLLECTION].create_index([("user_id", ASCENDING)], unique=True)
        db[AUTOMATION_LOCKS_COLLECTION].create_index([("heartbeat_at", ASCENDING)])
        db[AUTOMATION_LOCKS_COLLECTION].create_index([("instance_id", ASCENDING)])
        
        # Automation instances collection indexes (for parallel execution)
        db[AUTOMATION_INSTANCES_COLLECTION].create_index([("user_id", ASCENDING)])
        db[AUTOMATION_INSTANCES_COLLECTION].create_index([("instance_id", ASCENDING)])
        db[AUTOMATION_INSTANCES_COLLECTION].create_index([("heartbeat_at", ASCENDING)])
        db[AUTOMATION_INSTANCES_COLLECTION].create_index([("user_id", ASCENDING), ("instance_id", ASCENDING)], unique=True)
        
        # User message index collection indexes (for message distribution)
        db[USER_MESSAGE_INDEX_COLLECTION].create_index([("user_id", ASCENDING)], unique=True)
        
        print("✅ MongoDB collections initialized with indexes")
        return True
    except Exception as e:
        print(f"❌ MongoDB initialization error: {e}")
        return False

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def hash_token(token):
    """Hash session token using SHA-256"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_user(username, password):
    """Create new user"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False, "MongoDB not connected. Please setup IP whitelisting in MongoDB Atlas."
        
        password_hash = hash_password(password)
        
        user_doc = {
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }
        
        result = db[USERS_COLLECTION].insert_one(user_doc)
        user_id = result.inserted_id
        
        # Initialize empty config for user
        config_doc = {
            "user_id": str(user_id),
            "target_username": "",
            "name_prefix": "",
            "delay": 30,
            "instagram_username": "",
            "instagram_password_encrypted": "",
            "messages": "",
            "automation_running": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db[USER_CONFIGS_COLLECTION].insert_one(config_doc)
        
        print(f"✅ User created: {username}")
        return True, "Account created successfully!"
    except DuplicateKeyError:
        print(f"⚠️ Username already exists: {username}")
        return False, "Username already exists!"
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False, f"Error: {str(e)}"

def verify_user(username, password):
    """Verify user credentials"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        
        password_hash = hash_password(password)
        
        user = db[USERS_COLLECTION].find_one({
            "username": username,
            "password_hash": password_hash
        })
        
        if user:
            return str(user["_id"])
        return None
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        return None

def get_user_id(username):
    """Get user ID from username"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        user = db[USERS_COLLECTION].find_one({"username": username})
        return str(user["_id"]) if user else None
    except Exception as e:
        print(f"❌ Error getting user ID: {e}")
        return None

def create_session(username):
    """Create session token for user"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        user_id = get_user_id(username)
        if not user_id:
            return None
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        
        # 7 days expiry
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        session_doc = {
            "token_hash": token_hash,
            "user_id": user_id,
            "issued_at": datetime.utcnow(),
            "expires_at": expires_at,
            "revoked": 0
        }
        
        db[USER_SESSIONS_COLLECTION].insert_one(session_doc)
        print(f"✅ Session created for user: {username}")
        return token
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None

def verify_session(token):
    """Verify session token and return username"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        token_hash = hash_token(token)
        
        session = db[USER_SESSIONS_COLLECTION].find_one({
            "token_hash": token_hash,
            "revoked": 0,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            return None
        
        user = db[USERS_COLLECTION].find_one({"_id": session["user_id"]})
        return user["username"] if user else None
    except Exception as e:
        print(f"❌ Error verifying session: {e}")
        return None

def revoke_session(token):
    """Revoke (logout) session token"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        token_hash = hash_token(token)
        
        db[USER_SESSIONS_COLLECTION].update_one(
            {"token_hash": token_hash},
            {"$set": {"revoked": 1}}
        )
        print("✅ Session revoked")
        return True
    except Exception as e:
        print(f"❌ Error revoking session: {e}")
        return False

def revoke_session_token(token):
    """Revoke (logout) session token - alias for compatibility"""
    return revoke_session(token)

def save_user_config(username, target_username, name_prefix, delay, instagram_username, instagram_password, messages, instagram_cookies="", instagram_chat_id=""):
    """Save user configuration"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        user_id = get_user_id(username)
        if not user_id:
            return False
        
        # Encrypt Instagram password
        password_encrypted = cipher_suite.encrypt(instagram_password.encode()).decode() if instagram_password else ""
        
        # Configuration version for change detection
        config_version = datetime.utcnow().timestamp()
        
        update_doc = {
            "target_username": target_username,
            "instagram_chat_id": instagram_chat_id,
            "name_prefix": name_prefix,
            "delay": delay,
            "instagram_username": instagram_username,
            "instagram_password_encrypted": password_encrypted,
            "instagram_cookies": instagram_cookies,
            "messages": messages,
            "config_version": config_version,
            "updated_at": datetime.utcnow()
        }
        
        db[USER_CONFIGS_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": update_doc},
            upsert=True
        )
        
        print(f"✅ Config saved for user: {username}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def get_user_config(user_id_or_username):
    """Get user configuration by user_id or username"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        
        # Check if it's a user_id (ObjectId format) or username
        user_id = user_id_or_username
        if isinstance(user_id_or_username, str) and len(user_id_or_username) < 24:
            # Likely a username, convert to user_id
            user_id = get_user_id(user_id_or_username)
            if not user_id:
                return None
        
        config = db[USER_CONFIGS_COLLECTION].find_one({"user_id": str(user_id)})
        if not config:
            return None
        
        # Decrypt Instagram password
        password_decrypted = ""
        if config.get("instagram_password_encrypted"):
            try:
                password_decrypted = cipher_suite.decrypt(config["instagram_password_encrypted"].encode()).decode()
            except Exception:
                password_decrypted = ""
        
        return {
            "target_username": config.get("target_username", ""),
            "instagram_chat_id": config.get("instagram_chat_id", ""),
            "name_prefix": config.get("name_prefix", ""),
            "delay": config.get("delay", 30),
            "instagram_username": config.get("instagram_username", ""),
            "instagram_password": password_decrypted,
            "instagram_cookies": config.get("instagram_cookies", ""),
            "messages": config.get("messages", ""),
            "automation_running": config.get("automation_running", 0),
            "config_version": config.get("config_version", 0)
        }
    except Exception as e:
        print(f"❌ Error getting config: {e}")
        return None

def set_automation_status(username, status):
    """Set automation running status (0 or 1)"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        user_id = get_user_id(username)
        if not user_id:
            return False
        
        db[USER_CONFIGS_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": {"automation_running": status, "updated_at": datetime.utcnow()}}
        )
        
        print(f"✅ Automation status set to {status} for user: {username}")
        return True
    except Exception as e:
        print(f"❌ Error setting automation status: {e}")
        return False

def set_automation_running(user_id, status):
    """Set automation running status by user_id (0 or 1)"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        db[USER_CONFIGS_COLLECTION].update_one(
            {"user_id": str(user_id)},
            {"$set": {"automation_running": status, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        print(f"✅ Automation status set to {status} for user_id: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error setting automation status: {e}")
        return False

def get_automation_running(user_id):
    """Get automation running status by user_id"""
    try:
        db = get_mongodb_client()
        if db is None:
            return 0
        
        config = db[USER_CONFIGS_COLLECTION].find_one({"user_id": str(user_id)})
        if config:
            return config.get("automation_running", 0)
        return 0
    except Exception as e:
        print(f"❌ Error getting automation status: {e}")
        return 0

def get_username(user_id):
    """Get username from user_id"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        
        from bson import ObjectId
        user = db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
        return user["username"] if user else None
    except Exception as e:
        print(f"❌ Error getting username: {e}")
        return None

def get_all_running_users():
    """Get all users with automation_running=True"""
    try:
        db = get_mongodb_client()
        if db is None:
            return []
        
        # Check for both True (boolean) and 1 (integer) for compatibility
        configs = db[USER_CONFIGS_COLLECTION].find({"automation_running": {"$in": [True, 1]}})
        
        running_users = []
        for config in configs:
            user_id = config.get('user_id')
            username = get_username(user_id)
            
            password_encrypted = config.get('instagram_password_encrypted', '')
            password_decrypted = ''
            if password_encrypted:
                try:
                    password_decrypted = cipher_suite.decrypt(password_encrypted.encode()).decode()
                except:
                    pass
            
            user_data = {
                'user_id': user_id,
                'username': username,
                'target_username': config.get('target_username', ''),
                'name_prefix': config.get('name_prefix', ''),
                'delay': config.get('delay', 30),
                'instagram_username': config.get('instagram_username', ''),
                'instagram_password': password_decrypted,
                'instagram_cookies': config.get('instagram_cookies', ''),
                'instagram_chat_id': config.get('instagram_chat_id', ''),
                'messages': config.get('messages', 'hindi'),
                'config_version': config.get('config_version', 0)
            }
            running_users.append(user_data)
        
        print(f"✅ Found {len(running_users)} users with automation running")
        return running_users
    except Exception as e:
        print(f"❌ Error getting running users: {e}")
        return []

def validate_session_token(token):
    """Validate session token and return user data"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        token_hash = hash_token(token)
        
        session = db[USER_SESSIONS_COLLECTION].find_one({
            "token_hash": token_hash,
            "revoked": 0,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            return None
        
        user_id = session["user_id"]
        user = db[USERS_COLLECTION].find_one({"_id": user_id})
        
        if user:
            return {
                "user_id": user_id,
                "username": user["username"]
            }
        return None
    except Exception as e:
        print(f"❌ Error validating session: {e}")
        return None

def create_session_token(user_id, expiry_hours=168):
    """Create session token for user by user_id"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        
        # expiry_hours days expiry
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        session_doc = {
            "token_hash": token_hash,
            "user_id": user_id,
            "issued_at": datetime.utcnow(),
            "expires_at": expires_at,
            "revoked": 0
        }
        
        db[USER_SESSIONS_COLLECTION].insert_one(session_doc)
        print(f"✅ Session created for user_id: {user_id}")
        return token
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None

def cleanup_expired_sessions():
    """Remove expired and revoked sessions from database"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        result = db[USER_SESSIONS_COLLECTION].delete_many({
            "$or": [
                {"expires_at": {"$lt": datetime.utcnow()}},
                {"revoked": 1}
            ]
        })
        
        print(f"✅ Cleaned up {result.deleted_count} expired/revoked sessions")
        return True
    except Exception as e:
        print(f"❌ Error cleaning up sessions: {e}")
        return False

def get_automation_logs(user_id):
    """Get automation logs by user_id (returns as list of strings)"""
    try:
        db = get_mongodb_client()
        if db is None:
            return []
        
        # Find the most recent logs document for this user
        logs_doc = db[AUTOMATION_LOGS_COLLECTION].find_one(
            {"user_id": str(user_id)},
            sort=[("updated_at", DESCENDING)]
        )
        
        if logs_doc and "logs" in logs_doc:
            return logs_doc["logs"]
        return []
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return []

def save_automation_logs(user_id, logs):
    """Save automation logs array for user_id"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        log_doc = {
            "user_id": str(user_id),
            "logs": logs,
            "updated_at": datetime.utcnow()
        }
        
        # Update or insert logs document
        db[AUTOMATION_LOGS_COLLECTION].update_one(
            {"user_id": str(user_id)},
            {"$set": log_doc},
            upsert=True
        )
        
        print(f"✅ Logs saved for user_id: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error saving logs: {e}")
        return False

def clear_automation_logs(user_id):
    """Clear all automation logs for user_id"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        db[AUTOMATION_LOGS_COLLECTION].delete_many({"user_id": str(user_id)})
        
        print(f"✅ Logs cleared for user_id: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error clearing logs: {e}")
        return False

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages, fb_profile_id=""):
    """Update user configuration by user_id"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        # Encrypt cookies
        cookies_encrypted = cipher_suite.encrypt(cookies.encode()).decode() if cookies else ""
        
        update_doc = {
            "chat_id": chat_id,
            "name_prefix": name_prefix,
            "delay": delay,
            "cookies_encrypted": cookies_encrypted,
            "messages": messages,
            "fb_profile_id": fb_profile_id,
            "updated_at": datetime.utcnow()
        }
        
        db[USER_CONFIGS_COLLECTION].update_one(
            {"user_id": str(user_id)},
            {"$set": update_doc},
            upsert=True
        )
        
        print(f"✅ Config updated for user_id: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

# ========================================
# DISTRIBUTED LOCKING SYSTEM
# Multiple Streamlit instances coordination
# ========================================

_INSTANCE_ID = None
_INSTANCE_ID_FILE = Path(__file__).parent / '.instance_id'

def get_instance_id():
    """Get or generate unique instance ID for this deployment"""
    global _INSTANCE_ID
    if _INSTANCE_ID is not None:
        return _INSTANCE_ID
    
    # Try to load from file first
    if _INSTANCE_ID_FILE.exists():
        try:
            with open(_INSTANCE_ID_FILE, 'r') as f:
                _INSTANCE_ID = f.read().strip()
                return _INSTANCE_ID
        except:
            pass
    
    # Generate new instance ID
    _INSTANCE_ID = secrets.token_hex(8)
    
    # Save to file
    try:
        with open(_INSTANCE_ID_FILE, 'w') as f:
            f.write(_INSTANCE_ID)
    except:
        pass
    
    return _INSTANCE_ID

def acquire_automation_lock(user_id, instance_id=None, ttl_seconds=20):
    """
    Acquire distributed lock for automation.
    Returns True if lock acquired, False otherwise.
    TTL aligned with failover system (20 seconds, refreshed by heartbeat)
    """
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(seconds=ttl_seconds)
        
        lock_doc = {
            "user_id": str(user_id),
            "instance_id": instance_id,
            "acquired_at": current_time,
            "heartbeat_at": current_time,
            "expires_at": expires_at
        }
        
        # Try to insert lock (will fail if lock already exists)
        try:
            db[AUTOMATION_LOCKS_COLLECTION].insert_one(lock_doc)
            print(f"🔒 Lock acquired for user {user_id} by instance {instance_id}")
            return True
        except DuplicateKeyError:
            # Lock exists, check if it's expired or owned by us
            existing_lock = db[AUTOMATION_LOCKS_COLLECTION].find_one({"user_id": str(user_id)})
            
            if existing_lock:
                # If lock expired, try to acquire it
                if existing_lock['expires_at'] < current_time:
                    result = db[AUTOMATION_LOCKS_COLLECTION].update_one(
                        {
                            "user_id": str(user_id),
                            "expires_at": {"$lt": current_time}
                        },
                        {"$set": lock_doc}
                    )
                    if result.modified_count > 0:
                        print(f"🔒 Acquired expired lock for user {user_id} by instance {instance_id}")
                        return True
                
                # If we already own the lock, just update heartbeat
                if existing_lock.get('instance_id') == instance_id:
                    update_lock_heartbeat(user_id, instance_id, ttl_seconds)
                    return True
            
            return False
    except Exception as e:
        print(f"❌ Error acquiring lock: {e}")
        return False

def release_automation_lock(user_id, instance_id=None):
    """Release distributed lock for automation"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        # Only release if we own the lock
        result = db[AUTOMATION_LOCKS_COLLECTION].delete_one({
            "user_id": str(user_id),
            "instance_id": instance_id
        })
        
        if result.deleted_count > 0:
            print(f"🔓 Lock released for user {user_id} by instance {instance_id}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error releasing lock: {e}")
        return False

def update_lock_heartbeat(user_id, instance_id=None, ttl_seconds=20):
    """Update lock heartbeat to keep it alive"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(seconds=ttl_seconds)
        
        result = db[AUTOMATION_LOCKS_COLLECTION].update_one(
            {
                "user_id": str(user_id),
                "instance_id": instance_id
            },
            {
                "$set": {
                    "heartbeat_at": current_time,
                    "expires_at": expires_at
                }
            }
        )
        
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Error updating heartbeat: {e}")
        return False

def get_lock_owner(user_id):
    """Get the instance_id that owns the lock for this user"""
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        
        lock = db[AUTOMATION_LOCKS_COLLECTION].find_one({"user_id": str(user_id)})
        
        if lock:
            # Check if lock is expired
            if lock['expires_at'] < datetime.utcnow():
                return None
            return lock.get('instance_id')
        return None
    except Exception as e:
        print(f"❌ Error getting lock owner: {e}")
        return None

def check_if_lock_owned(user_id, instance_id=None):
    """Check if we own the lock for this user"""
    if instance_id is None:
        instance_id = get_instance_id()
    
    owner = get_lock_owner(user_id)
    return owner == instance_id

def cleanup_expired_locks():
    """Remove expired locks from database"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        result = db[AUTOMATION_LOCKS_COLLECTION].delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        if result.deleted_count > 0:
            print(f"🧹 Cleaned up {result.deleted_count} expired locks")
        return True
    except Exception as e:
        print(f"❌ Error cleaning up locks: {e}")
        return False

def get_all_locks():
    """Get all active locks (for monitoring/debugging)"""
    try:
        db = get_mongodb_client()
        if db is None:
            return []
        
        locks = db[AUTOMATION_LOCKS_COLLECTION].find({
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        return list(locks)
    except Exception as e:
        print(f"❌ Error getting locks: {e}")
        return []

# ========================================
# PARALLEL EXECUTION SYSTEM
# Multiple instances running simultaneously
# ========================================

def register_automation_instance(user_id, instance_id=None, ttl_seconds=60):
    """
    Register this instance as active for parallel execution.
    Returns True if registered successfully.
    """
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(seconds=ttl_seconds)
        
        instance_doc = {
            "user_id": str(user_id),
            "instance_id": instance_id,
            "registered_at": current_time,
            "heartbeat_at": current_time,
            "expires_at": expires_at
        }
        
        # Upsert: update if exists, insert if not
        db[AUTOMATION_INSTANCES_COLLECTION].update_one(
            {"user_id": str(user_id), "instance_id": instance_id},
            {"$set": instance_doc},
            upsert=True
        )
        
        print(f"✅ Instance {instance_id} registered for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error registering instance: {e}")
        return False

def update_instance_heartbeat(user_id, instance_id=None, ttl_seconds=60):
    """Update instance heartbeat to keep it alive"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(seconds=ttl_seconds)
        
        result = db[AUTOMATION_INSTANCES_COLLECTION].update_one(
            {
                "user_id": str(user_id),
                "instance_id": instance_id
            },
            {
                "$set": {
                    "heartbeat_at": current_time,
                    "expires_at": expires_at
                }
            }
        )
        
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Error updating instance heartbeat: {e}")
        return False

def get_active_instances(user_id):
    """Get all active instances for a user"""
    try:
        db = get_mongodb_client()
        if db is None:
            return []
        
        # Clean up expired instances first
        cleanup_expired_instances()
        
        instances = db[AUTOMATION_INSTANCES_COLLECTION].find({
            "user_id": str(user_id),
            "expires_at": {"$gt": datetime.utcnow()}
        }).sort("registered_at", ASCENDING)
        
        return list(instances)
    except Exception as e:
        print(f"❌ Error getting active instances: {e}")
        return []

def remove_automation_instance(user_id, instance_id=None):
    """Remove instance registration"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        result = db[AUTOMATION_INSTANCES_COLLECTION].delete_one({
            "user_id": str(user_id),
            "instance_id": instance_id
        })
        
        if result.deleted_count > 0:
            print(f"🗑️ Instance {instance_id} removed for user {user_id}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error removing instance: {e}")
        return False

def cleanup_expired_instances():
    """Remove expired instance registrations"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        result = db[AUTOMATION_INSTANCES_COLLECTION].delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        if result.deleted_count > 0:
            print(f"🧹 Cleaned up {result.deleted_count} expired instances")
        return True
    except Exception as e:
        print(f"❌ Error cleaning up instances: {e}")
        return False

def get_instance_shard(user_id, instance_id, total_messages):
    """
    Calculate which messages this instance should send.
    Returns (start_index, step) for modulo-based distribution.
    
    Example: If 3 instances are active:
    - Instance 0: sends messages 0, 3, 6, 9, ...
    - Instance 1: sends messages 1, 4, 7, 10, ...
    - Instance 2: sends messages 2, 5, 8, 11, ...
    """
    try:
        active_instances = get_active_instances(user_id)
        if not active_instances:
            return (0, 1)  # Single instance, send all messages
        
        # Sort instances by registration time to get consistent shard assignment
        instance_ids = sorted([inst['instance_id'] for inst in active_instances])
        
        try:
            shard_index = instance_ids.index(instance_id)
        except ValueError:
            shard_index = 0
        
        num_instances = len(instance_ids)
        
        print(f"📊 Instance {instance_id} assigned shard {shard_index}/{num_instances}")
        return (shard_index, num_instances)
    except Exception as e:
        print(f"❌ Error calculating shard: {e}")
        return (0, 1)

def get_next_message_index_atomic(user_id, instance_id, total_messages):
    """
    Atomically get and increment the next message index for this instance's shard.
    Uses MongoDB's findOneAndUpdate for atomic operation to prevent duplicates.
    
    Returns: message_index or None if this instance shouldn't send (another shard's turn)
    """
    try:
        db = get_mongodb_client()
        if db is None:
            return None
        
        # Get this instance's shard assignment
        shard_start, shard_step = get_instance_shard(user_id, instance_id, total_messages)
        
        # Atomically increment the global counter
        result = db[USER_MESSAGE_INDEX_COLLECTION].find_one_and_update(
            {"user_id": str(user_id)},
            {"$inc": {"global_index": 1}},
            upsert=True,
            return_document=True
        )
        
        if not result:
            return None
        
        global_index = result.get('global_index', 0)
        
        # Calculate message index based on shard
        # This ensures each instance sends different messages
        message_index = (shard_start + (global_index // shard_step) * shard_step) % total_messages
        
        return message_index
    except Exception as e:
        print(f"❌ Error getting message index: {e}")
        return None

def reset_message_index(user_id):
    """Reset the message index counter for a user"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        db[USER_MESSAGE_INDEX_COLLECTION].delete_one({"user_id": str(user_id)})
        print(f"🔄 Message index reset for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error resetting message index: {e}")
        return False

# ========================================
# GLOBAL INSTANCE HEARTBEAT SYSTEM
# For automatic failover detection
# ========================================

GLOBAL_INSTANCE_HEARTBEATS_COLLECTION = 'global_instance_heartbeats'

def register_global_instance_heartbeat(instance_id=None, role='secondary', ttl_seconds=20):
    """
    Register global heartbeat for this instance
    Role can be 'primary' or 'secondary'
    TTL aligned with failover detection (20 seconds)
    """
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(seconds=ttl_seconds)
        
        heartbeat_doc = {
            "instance_id": instance_id,
            "role": role,
            "heartbeat_at": current_time,
            "expires_at": expires_at,
            "is_active": True
        }
        
        db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].update_one(
            {"instance_id": instance_id},
            {"$set": heartbeat_doc},
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"❌ Error registering global heartbeat: {e}")
        return False

def update_global_instance_heartbeat(instance_id=None, ttl_seconds=20):
    """Update global heartbeat to keep instance alive"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(seconds=ttl_seconds)
        
        result = db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].update_one(
            {"instance_id": instance_id},
            {
                "$set": {
                    "heartbeat_at": current_time,
                    "expires_at": expires_at,
                    "is_active": True
                }
            }
        )
        
        return result.modified_count > 0
    except Exception as e:
        return False

def get_all_global_instances():
    """Get all active instances from global heartbeat collection"""
    try:
        db = get_mongodb_client()
        if db is None:
            return []
        
        # Clean up expired first
        db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        instances = db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].find({
            "expires_at": {"$gt": datetime.utcnow()},
            "is_active": True
        }).sort("heartbeat_at", DESCENDING)
        
        return list(instances)
    except Exception as e:
        return []

def check_primary_instance_alive(current_instance_id):
    """
    Check if a primary instance is alive (not us)
    Returns True if another instance with primary role is sending heartbeats
    """
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        # Look for primary instances (not us) with recent heartbeat
        cutoff_time = datetime.utcnow() - timedelta(seconds=15)  # 15 second timeout
        
        primary = db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].find_one({
            "role": "primary",
            "instance_id": {"$ne": current_instance_id},
            "heartbeat_at": {"$gte": cutoff_time},
            "is_active": True
        })
        
        return primary is not None
    except Exception as e:
        return False

def set_instance_role(instance_id, role):
    """Set instance role (primary or secondary)"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        result = db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].update_one(
            {"instance_id": instance_id},
            {"$set": {"role": role}},
            upsert=False
        )
        
        return result.modified_count > 0
    except Exception as e:
        return False

def deactivate_global_instance(instance_id=None):
    """Mark instance as inactive"""
    try:
        db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        result = db[GLOBAL_INSTANCE_HEARTBEATS_COLLECTION].update_one(
            {"instance_id": instance_id},
            {"$set": {"is_active": False}}
        )
        
        return result.modified_count > 0
    except Exception as e:
        return False

def clear_all_database_data():
    """
    ⚠️ DANGER: Clears all data from MongoDB database
    This will delete all users, configurations, sessions, logs, locks, and instances
    Use with extreme caution - this action is IRREVERSIBLE!
    
    Returns: (success: bool, message: str, stats: dict)
    """
    try:
        db = get_mongodb_client()
        if db is None:
            return False, "❌ MongoDB connection failed", {}
        
        stats = {}
        collections = [
            USERS_COLLECTION,
            USER_CONFIGS_COLLECTION,
            USER_SESSIONS_COLLECTION,
            AUTOMATION_LOGS_COLLECTION,
            AUTOMATION_LOCKS_COLLECTION,
            AUTOMATION_INSTANCES_COLLECTION,
            USER_MESSAGE_INDEX_COLLECTION,
            GLOBAL_INSTANCE_HEARTBEATS_COLLECTION
        ]
        
        for collection_name in collections:
            try:
                result = db[collection_name].delete_many({})
                stats[collection_name] = result.deleted_count
            except Exception as e:
                stats[collection_name] = f"Error: {str(e)}"
        
        total_deleted = sum([v for v in stats.values() if isinstance(v, int)])
        
        return True, f"✅ Successfully cleared {total_deleted} documents from database", stats
    
    except Exception as e:
        return False, f"❌ Error clearing database: {str(e)}", {}

# Initialize database on import
if __name__ != "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"⚠️ MongoDB auto-initialization skipped: {e}")
        print("💡 MongoDB will be initialized on first use")
