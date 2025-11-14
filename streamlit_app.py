import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import mongodb_database as db
import telegram_notifier
import requests
import base64
from io import BytesIO
import instagram_automation
import ai_guide
import chat_ui

try:
    from streamlit_local_storage import LocalStorage
    LOCALSTORAGE_AVAILABLE = True
    local_storage = LocalStorage()
except ImportError:
    LOCALSTORAGE_AVAILABLE = False
    local_storage = None

st.set_page_config(
    page_title="Instagram DM Automation by Prince Malhotra",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@600;700&display=swap');

    /* ===  CLEAN MOBILE-FRIENDLY DESIGN - Reference Image Style === */
    
    * {
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Simple Dark Background */
    .stApp {
        background: #000000 !important;
    }

    /* Profile Header - Clean Design */
    .profile-header {
        background: rgba(0, 15, 25, 0.8);
        border: 2px solid #FF1744;
        padding: 2rem 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }

    .profile-image {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 3px solid #FF1744;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
        margin: 0 auto 1.5rem;
        display: block;
    }

    .profile-header h1 {
        color: #FF1744 !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 1rem 0;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-family: 'Orbitron', monospace !important;
    }

    .profile-header p {
        color: rgba(0, 217, 255, 0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0;
        font-weight: 500;
    }

    /* Clean Buttons */
    .contact-link {
        display: inline-block;
        background: rgba(0, 217, 255, 0.15);
        color: #FF1744;
        padding: 1rem 2.5rem;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        margin-top: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
        border: 2px solid #FF1744;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .contact-link:hover {
        background: rgba(0, 217, 255, 0.25);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Simple Streamlit Buttons */
    .stButton>button {
        background: rgba(0, 217, 255, 0.15) !important;
        color: #FF1744 !important;
        border: 2px solid #FF1744 !important;
        border-radius: 10px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.3) !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    .stButton>button:hover {
        background: rgba(0, 217, 255, 0.25) !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* Clean Input Fields */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stNumberInput>div>div>input {
        background: rgba(0, 15, 25, 0.8) !important;
        border: 2px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        color: #FF1744 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.2) !important;
    }

    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #FF1744 !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5) !important;
    }

    .stTextInput>div>div>input::placeholder,
    .stTextArea>div>div>textarea::placeholder,
    .stNumberInput>div>div>input::placeholder {
        color: rgba(0, 217, 255, 0.5) !important;
    }

    /* Simple Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(0, 15, 25, 0.6);
        padding: 10px;
        border-radius: 10px;
        border: 2px solid rgba(0, 217, 255, 0.3);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(0, 15, 25, 0.8);
        border-radius: 8px;
        padding: 12px 24px;
        border: 2px solid rgba(0, 217, 255, 0.4);
        color: rgba(0, 217, 255, 0.8);
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 217, 255, 0.15);
        color: #FF1744;
        border-color: #FF1744;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 217, 255, 0.2) !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        border-color: #FF1744 !important;
    }

    /* Simple Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(0, 15, 25, 0.8);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid rgba(0, 217, 255, 0.4);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        border-color: #FF1744;
    }

    [data-testid="stMetricValue"] {
        color: #FF1744 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        font-family: 'Orbitron', monospace !important;
    }

    [data-testid="stMetricLabel"] {
        color: rgba(0, 217, 255, 0.8) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Simple Alert Messages */
    .stAlert {
        background: rgba(0, 15, 25, 0.9) !important;
        border-radius: 10px !important;
        border: 2px solid rgba(0, 217, 255, 0.5) !important;
        padding: 1rem !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
    }

    /* Hacking Console Style Log Container */
    .log-container {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(0, 20, 10, 0.95));
        padding: 1.5rem;
        border-radius: 15px;
        font-family: 'Courier New', 'Consolas', monospace;
        max-height: 500px;
        overflow-y: auto;
        border: 3px solid #00FF41;
        box-shadow: 
            0 0 30px rgba(0, 255, 65, 0.4),
            inset 0 0 30px rgba(0, 255, 65, 0.1);
        position: relative;
        backdrop-filter: blur(5px);
    }

    .log-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            repeating-linear-gradient(
                0deg,
                rgba(0, 255, 65, 0.03) 0px,
                rgba(0, 255, 65, 0.03) 1px,
                transparent 1px,
                transparent 2px
            );
        pointer-events: none;
        border-radius: 15px;
    }

    .log-line {
        padding: 8px 12px;
        margin: 4px 0;
        border-left: 3px solid transparent;
        transition: all 0.3s ease;
        font-size: 0.95rem;
        line-height: 1.6;
        animation: slideIn 0.3s ease-out;
        position: relative;
        z-index: 1;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .log-line:hover {
        background: rgba(0, 255, 65, 0.1);
        transform: translateX(5px);
    }

    .log-success {
        color: #00FF41;
        border-left-color: #00FF41;
        text-shadow: 0 0 5px rgba(0, 255, 65, 0.5);
    }

    .log-error {
        color: #FF0040;
        border-left-color: #FF0040;
        text-shadow: 0 0 5px rgba(255, 0, 64, 0.5);
    }

    .log-warning {
        color: #FFD700;
        border-left-color: #FFD700;
        text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
    }

    .log-info {
        color: #FF1744;
        border-left-color: #FF1744;
        text-shadow: 0 0 5px rgba(0, 217, 255, 0.5);
    }

    .log-system {
        color: #9D00FF;
        border-left-color: #9D00FF;
        text-shadow: 0 0 5px rgba(157, 0, 255, 0.5);
    }

    .log-timestamp {
        color: #888;
        font-weight: bold;
        margin-right: 10px;
    }

    .log-container::-webkit-scrollbar {
        width: 12px;
    }

    .log-container::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.5);
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 65, 0.2);
    }

    .log-container::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00FF41, #FF1744);
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.5);
    }

    .log-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00FF41, #FFD700);
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.6);
    }

    .console-header {
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.2), rgba(0, 217, 255, 0.2));
        border: 2px solid #00FF41;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 15px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    }

    .console-header h3 {
        color: #00FF41 !important;
        font-family: 'Orbitron', monospace !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0 !important;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
        font-size: 1.5rem !important;
    }

    .console-status {
        display: inline-block;
        padding: 5px 15px;
        background: rgba(0, 255, 65, 0.2);
        border-radius: 20px;
        border: 1px solid #00FF41;
        color: #00FF41;
        font-weight: bold;
        margin-left: 15px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }
        50% {
            opacity: 0.7;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.8);
        }
    }

    /* Simple Labels */
    label {
        color: rgba(0, 217, 255, 0.9) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 10, 15, 0.95) !important;
        border-right: 2px solid rgba(0, 217, 255, 0.4) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }

    [data-testid="stSidebar"] h3 {
        color: #FF1744 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Orbitron', monospace;
    }

    /* Simple Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(0, 217, 255, 0.9);
        font-weight: 600;
        margin-top: 3rem;
        background: rgba(0, 15, 25, 0.8);
        border-radius: 10px;
        border: 2px solid rgba(0, 217, 255, 0.4);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
    }

    .footer a {
        color: #FF1744 !important;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .footer a:hover {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.8);
    }

    /* Simple Headings */
    h1, h2, h3 {
        color: #FF1744 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Orbitron', monospace;
    }

    /* Simple Markdown Text */
    .stMarkdown {
        color: rgba(0, 217, 255, 0.9) !important;
    }

    /* Simple Select Boxes */
    .stSelectbox>div>div {
        background: rgba(0, 15, 25, 0.8) !important;
        border: 2px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 10px !important;
        color: #FF1744 !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.2);
        transition: all 0.3s ease;
    }

    .stSelectbox>div>div:hover {
        border-color: #FF1744 !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
    }

    /* General Text */
    p, span, div {
        color: rgba(255, 255, 255, 0.9);
    }

    /* ChatGPT-Style Chat Interface */
    .chat-container {
        background: rgba(0, 15, 25, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid rgba(0, 217, 255, 0.4);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
        max-height: 600px;
        overflow-y: auto;
        margin-bottom: 1rem;
    }

    .chat-message {
        display: flex;
        margin-bottom: 1.5rem;
        align-items: flex-start;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-message.user {
        flex-direction: row-reverse;
    }

    .chat-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin: 0 10px;
        border: 2px solid #FF1744;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        flex-shrink: 0;
    }

    .chat-bubble {
        max-width: 70%;
        padding: 1rem 1.5rem;
        border-radius: 15px;
        word-wrap: break-word;
    }

    .chat-bubble.user {
        background: linear-gradient(135deg, rgba(255, 23, 68, 0.3), rgba(255, 23, 68, 0.2));
        border: 2px solid #FF1744;
        color: #ffffff;
        margin-left: auto;
    }

    .chat-bubble.assistant {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(0, 217, 255, 0.1));
        border: 2px solid rgba(0, 217, 255, 0.5);
        color: #ffffff;
    }

    .chat-header {
        background: linear-gradient(135deg, rgba(255, 23, 68, 0.3), rgba(0, 217, 255, 0.3));
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 2px solid #FF1744;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
    }

    .pika-name {
        font-size: 2rem;
        font-weight: 700;
        color: #FF1744;
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0
        self.stop_event = threading.Event()
        self.driver = None
        self.thread_lock = threading.Lock()

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

if 'session_token' not in st.session_state:
    st.session_state.session_token = None

if 'session_loaded_from_storage' not in st.session_state:
    st.session_state.session_loaded_from_storage = False

chat_ui.init_chat_state()

_active_threads = {}


class GlobalAutomationManager:
    """Global automation manager - persists across Streamlit reruns"""
    def __init__(self):
        self.user_states = {}
        self.threads = {}
        self.global_lock = threading.Lock()
        self.auto_started = False
        self.monitor_thread = None  # type: threading.Thread | None
        print("🚀 Global Automation Manager initialized")
    
    def get_or_create_state(self, user_id):
        """Get or create automation state for user"""
        with self.global_lock:
            if user_id not in self.user_states:
                self.user_states[user_id] = AutomationState()
            return self.user_states[user_id]
    
    def get_state(self, user_id):
        """Get automation state for user (returns None if not exists)"""
        return self.user_states.get(user_id)
    
    def is_running(self, user_id):
        """Check if automation is running for user"""
        state = self.get_state(user_id)
        return state.running if state else False
    
    def set_thread(self, user_id, thread):
        """Set active thread for user"""
        with self.global_lock:
            self.threads[user_id] = thread
    
    def get_thread(self, user_id):
        """Get active thread for user"""
        return self.threads.get(user_id)
    
    def remove_thread(self, user_id):
        """Remove thread for user"""
        with self.global_lock:
            if user_id in self.threads:
                del self.threads[user_id]
    
    def cleanup_dead_threads(self):
        """Clean up finished threads"""
        with self.global_lock:
            dead_threads = [uid for uid, thread in self.threads.items() if not thread.is_alive()]
            for uid in dead_threads:
                del self.threads[uid]

@st.cache_resource
def get_global_automation_manager():
    """Get or create the global automation manager (persists across Streamlit reruns)"""
    return GlobalAutomationManager()

global_automation_manager = get_global_automation_manager()

def instance_heartbeat_worker(user_id):
    """Background worker to keep instance registration alive with heartbeats"""
    automation_state = global_automation_manager.get_state(user_id)
    if not automation_state:
        return
    
    instance_id = db.get_instance_id()
    consecutive_failures = 0
    max_failures = 3  # Allow 3 consecutive failures before giving up
    
    while automation_state.running and not automation_state.stop_event.is_set():
        try:
            # Update heartbeat every 15 seconds (TTL is 60s)
            success = db.update_instance_heartbeat(user_id, instance_id, ttl_seconds=60)
            
            if success:
                consecutive_failures = 0  # Reset on success
                # Sleep 15 seconds before next heartbeat on success
                time.sleep(15)
            else:
                consecutive_failures += 1
                print(f"⚠️ Instance heartbeat failed for user {user_id} (attempt {consecutive_failures}/{max_failures})")
                
                # If too many failures, STOP AUTOMATION
                if consecutive_failures >= max_failures:
                    print(f"❌ Instance heartbeat failed {max_failures} times, STOPPING AUTOMATION")
                    automation_state.stop_event.set()
                    automation_state.running = False
                    db.set_automation_running(user_id, False)
                    db.remove_automation_instance(user_id, instance_id)
                    break
                
                # Retry quickly after failure (2 seconds)
                time.sleep(2)
            
        except Exception as e:
            consecutive_failures += 1
            print(f"⚠️ Instance heartbeat exception for user {user_id}: {e}")
            
            # If too many failures, STOP AUTOMATION
            if consecutive_failures >= max_failures:
                print(f"❌ Instance heartbeat failed {max_failures} times, STOPPING AUTOMATION")
                automation_state.stop_event.set()
                automation_state.running = False
                db.set_automation_running(user_id, False)
                db.remove_automation_instance(user_id, instance_id)
                break
            
            # Retry quickly after exception (2 seconds)
            time.sleep(2)
    
    print(f"💓 Instance heartbeat stopped for user {user_id}")

def background_monitor_worker():
    """Background worker to monitor locks and acquire abandoned ones"""
    print("🔍 Background monitor started - watching for lock opportunities...")
    
    while True:
        try:
            # Cleanup expired locks
            db.cleanup_expired_locks()
            
            # Check for users that should be running but have no lock
            running_users = db.get_all_running_users()
            
            for user_data in running_users:
                user_id = user_data.get('user_id')
                username = user_data.get('username', 'Unknown')
                target_username = user_data.get('target_username', '')
                
                # Skip if no target username
                if not target_username:
                    continue
                
                # Check if we're already running this user
                if global_automation_manager.is_running(user_id):
                    continue
                
                # Check lock status
                lock_owner = db.get_lock_owner(user_id)
                
                # If no lock owner, validate config first before acquiring lock
                if lock_owner is None:
                    # Validate target_username exists before acquiring lock
                    if not target_username:
                        continue
                    
                    # Now try to acquire lock
                    lock_acquired = db.acquire_automation_lock(user_id, ttl_seconds=60)
                    if lock_acquired:
                        print(f"🎯 Acquired abandoned lock for {username}, starting automation...")
                        
                        # Try to start, if it fails release the lock
                        try:
                            start_automation(user_data, user_id, background=True, lock_already_acquired=True)
                        except Exception as e:
                            print(f"❌ Failed to start automation for {username}, releasing lock: {e}")
                            db.release_automation_lock(user_id)
            
            # Sleep for 30 seconds before next check
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Background monitor error: {e}")
            time.sleep(30)

def background_auto_start_all_users():
    """Background function to auto-start automation for all users with automation_running=True"""
    if global_automation_manager.auto_started:
        return
    
    try:
        global_automation_manager.auto_started = True
        
        running_users = db.get_all_running_users()
        if not running_users:
            print("ℹ️ No users with running automation found in database")
            return
        
        print(f"🔄 Found {len(running_users)} users with automation running. Starting background automation...")
        
        for user_data in running_users:
            user_id = user_data.get('user_id')
            username = user_data.get('username', 'Unknown')
            target_username = user_data.get('target_username', '')
            
            if not target_username:
                print(f"⚠️ Skipping user {username} (no target Instagram username configured)")
                continue
            
            if global_automation_manager.is_running(user_id):
                print(f"ℹ️ User {username} automation already running, skipping...")
                continue
            
            print(f"🚀 Starting background automation for {username} (user_id: {user_id})")
            start_automation(user_data, user_id, background=True)
        
        print("✅ Background auto-start completed!")
        
        # Start background monitor thread (runs continuously) - only if not already running
        if global_automation_manager.monitor_thread is None or not global_automation_manager.monitor_thread.is_alive():
            monitor_thread = threading.Thread(target=background_monitor_worker, daemon=True)
            monitor_thread.start()
            global_automation_manager.monitor_thread = monitor_thread
            print("🔍 Background monitor thread started")
        else:
            print("ℹ️ Background monitor thread already running")
        
    except Exception as e:
        print(f"❌ Error in background_auto_start_all_users: {e}")

# Auto-restart mechanism - hourly restart
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = time.time()

if 'last_restart_check' not in st.session_state:
    st.session_state.last_restart_check = time.time()

# Check if 1 hour has passed since app start
current_time = time.time()
time_elapsed = current_time - st.session_state.app_start_time

# Restart every hour (3600 seconds)
if time_elapsed >= 3600:
    # Save all running automation logs to MongoDB before restart
    for user_id, automation_state in global_automation_manager.user_states.items():
        if automation_state.logs:
            db.save_automation_logs(user_id, automation_state.logs)
    
    # Clear the cache resource to force re-initialization and reset timer
    st.cache_resource.clear()
    st.session_state.app_start_time = time.time()
    
    st.toast("🔄 Hourly auto-restart initiated. Background automation will resume...", icon="🔄")
    time.sleep(1)
    st.rerun()

# Auto-login from MongoDB via LocalStorage (Runs on every page load/refresh)
if not st.session_state.logged_in:
    if LOCALSTORAGE_AVAILABLE and local_storage:
        try:
            session_token = local_storage.getItem('fb_e2ee_session_token')
            
            if session_token:
                user_data = db.validate_session_token(session_token)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['user_id']
                    st.session_state.username = user_data['username']
                    st.session_state.session_token = session_token
                    
                    saved_logs = db.get_automation_logs(user_data['user_id'])
                    if saved_logs:
                        st.session_state.automation_state.logs = saved_logs
                    
                    st.session_state.session_loaded_from_storage = True
                    st.session_state.auto_start_checked = False
                    
                    st.toast("✅ Auto-login successful!", icon="✅")
                    st.rerun()
                else:
                    local_storage.deleteItem('fb_e2ee_session_token')
        except Exception as e:
            pass

def get_facebook_profile_picture(profile_id):
    """Fetch Facebook profile picture using Graph API"""
    try:
        url = f"https://graph.facebook.com/{profile_id}/picture?type=large&redirect=false"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'url' in data['data']:
                img_url = data['data']['url']
                img_response = requests.get(img_url, timeout=5)
                if img_response.status_code == 200:
                    return base64.b64encode(img_response.content).decode()
        return None
    except Exception as e:
        return None

def log_message(msg, automation_state=None, user_id=None):
    timestamp = telegram_notifier.get_kolkata_time().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"

    if automation_state:
        automation_state.logs.append(formatted_msg)
        if user_id and len(automation_state.logs) % 5 == 0:
            db.save_automation_logs(user_id, automation_state.logs)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    
    for _ in range(10):
        if automation_state and automation_state.stop_event.is_set():
            log_message(f'{process_id}: Stop detected during input search', automation_state)
            return None
        time.sleep(1)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        for _ in range(2):
            if automation_state and automation_state.stop_event.is_set():
                return None
            time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        for _ in range(2):
            if automation_state and automation_state.stop_event.is_set():
                return None
            time.sleep(1)
    except Exception:
        pass

    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)

    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]

    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)

    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)

            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)

                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)

                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass

                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()

                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: ✅ Found message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: ✅ Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea':
                            log_message(f'{process_id}: ✅ Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue

    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass

    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)

    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]

    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break

    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]

    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break

    try:
        from selenium.webdriver.chrome.service import Service

        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state)

        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'

    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]

    return message

HINDI_MESSAGES_URL = "https://raw.githubusercontent.com/SHANKAR-BOT/CONVO-PASSWORD/main/SHANKAR-HINDI.txt"
ENGLISH_MESSAGES_URL = "https://raw.githubusercontent.com/SHANKAR-BOT/CONVO-PASSWORD/main/SHANKAR-ENGLISH.txt"
MATH_MESSAGES_URL = "https://raw.githubusercontent.com/SHANKAR-BOT/CONVO-PASSWORD/refs/heads/main/MATH-NP.txt"

def fetch_np_messages(np_selection, automation_state=None):
    """Fetch messages from GitHub based on NP selection"""
    try:
        if np_selection == "hindi":
            url = HINDI_MESSAGES_URL
        elif np_selection == "math":
            url = MATH_MESSAGES_URL
        else:
            url = ENGLISH_MESSAGES_URL
        log_message(f'Fetching messages from GitHub ({np_selection.upper()})...', automation_state)

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        messages = response.text.strip()

        log_message(f'Successfully fetched {len(messages)} characters from GitHub!', automation_state)
        return messages
    except Exception as e:
        log_message(f'Error fetching messages from GitHub: {str(e)}', automation_state)
        return "Hello! Default message"

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting Instagram automation...', automation_state, user_id)
        
        instagram_username = config.get('instagram_username', '')
        instagram_password = config.get('instagram_password', '')
        instagram_cookies = config.get('instagram_cookies', '')
        target_username = config.get('target_username', '')
        instagram_chat_id = config.get('instagram_chat_id', '')
        
        # Get username for profile (use Instagram username or extract from cookies)
        profile_username = instagram_username
        if not profile_username and instagram_cookies:
            try:
                import json
                cookies_data = json.loads(instagram_cookies)
                ds_user = [c for c in cookies_data if c.get('name') == 'ds_user_id']
                if ds_user:
                    profile_username = ds_user[0].get('value', 'default')
            except:
                profile_username = 'default'
        if not profile_username:
            profile_username = 'default'
        
        driver = instagram_automation.setup_instagram_browser(
            automation_state, 
            log_callback=log_message,
            use_profile=True,
            username=profile_username
        )
        automation_state.driver = driver
        
        # Check if using cookies or password method
        if instagram_cookies:
            log_message(f'{process_id}: Using cookies for login...', automation_state, user_id)
            try:
                # SIMPLIFIED: Direct cookie loading - No file saving!
                # Cookies directly config se login function mein jaayenge
                login_success = instagram_automation.instagram_login(
                    driver, 
                    profile_username, 
                    "",
                    automation_state, 
                    process_id, 
                    log_callback=log_message, 
                    use_cookies=True,
                    cookies_json=instagram_cookies  # NEW: Direct cookie passing!
                )
            except Exception as e:
                log_message(f'{process_id}: ❌ Failed to process cookies: {str(e)}', automation_state, user_id)
                automation_state.running = False
                db.set_automation_running(user_id, False)
                return 0
        else:
            # Traditional password login
            if not instagram_username or not instagram_password:
                log_message(f'{process_id}: ❌ Instagram credentials missing!', automation_state, user_id)
                automation_state.running = False
                db.set_automation_running(user_id, False)
                return 0
            
            login_success = instagram_automation.instagram_login(
                driver, instagram_username, instagram_password,
                automation_state, process_id, log_callback=log_message
            )
        
        if not login_success:
            log_message(f'{process_id}: ❌ Instagram login failed!', automation_state, user_id)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        for _ in range(5):
            if automation_state.stop_event.is_set():
                log_message(f'{process_id}: Stop detected after login', automation_state, user_id)
                automation_state.running = False
                db.set_automation_running(user_id, False)
                return 0
            time.sleep(1)
        
        dm_opened = instagram_automation.open_instagram_dm(
            driver, target_username,
            automation_state, process_id, log_callback=log_message,
            chat_id=instagram_chat_id if instagram_chat_id else None
        )
        
        if not dm_opened:
            log_message(f'{process_id}: ❌ Failed to open DM with @{target_username}', automation_state, user_id)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        for _ in range(5):
            if automation_state.stop_event.is_set():
                log_message(f'{process_id}: Stop detected before finding input', automation_state, user_id)
                automation_state.running = False
                db.set_automation_running(user_id, False)
                return 0
            time.sleep(1)

        message_input = instagram_automation.find_instagram_message_input(
            driver, process_id, automation_state, log_callback=log_message
        )

        if not message_input:
            log_message(f'{process_id}: ❌ Message input not found!', automation_state, user_id)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        log_message(f'{process_id}: ✅ Ready to send messages!', automation_state, user_id)

        delay = int(config['delay'])
        messages_sent = 0

        np_selection = config.get('messages', 'hindi')
        if np_selection not in ['hindi', 'english', 'math']:
            np_selection = 'hindi'

        github_messages = fetch_np_messages(np_selection, automation_state)
        messages_list = [msg.strip() for msg in github_messages.split('\n') if msg.strip()]

        if not messages_list:
            messages_list = ['Hello!']

        log_message(f'{process_id}: 🔄 Starting loop messages now...', automation_state, user_id)
        
        # Track configuration version for change detection
        current_config_version = config.get('config_version', 0)
        config_check_counter = 0

        while automation_state.running and not automation_state.stop_event.is_set():
            if not db.get_automation_running(user_id):
                log_message(f'{process_id}: Stop detected from database', automation_state, user_id)
                break
            
            # Check for configuration changes every 10 iterations
            config_check_counter += 1
            if config_check_counter >= 10:
                config_check_counter = 0
                latest_config = db.get_user_config(user_id)
                if latest_config:
                    latest_version = latest_config.get('config_version', 0)
                    # Detect changes including first update from 0 to timestamp
                    if latest_version != current_config_version:
                        log_message(f'{process_id}: 🔄 Configuration updated! Stopping to apply changes...', automation_state, user_id)
                        log_message(f'{process_id}: 📝 Version changed: {current_config_version} → {latest_version}', automation_state, user_id)
                        automation_state.running = False
                        db.set_automation_running(user_id, False)
                        db.release_automation_lock(user_id)
                        break

            base_message = get_next_message(messages_list, automation_state)

            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message

            try:
                send_success = instagram_automation.send_instagram_message(
                    driver, message_input, message_to_send,
                    automation_state, process_id, log_callback=log_message
                )

                if automation_state.stop_event.is_set():
                    log_message(f'{process_id}: Stop detected after send attempt', automation_state, user_id)
                    break
                
                if send_success:
                    messages_sent += 1
                    automation_state.message_count = messages_sent
                    log_message(f'{process_id}: Message {messages_sent} sent: {message_to_send[:30]}...', automation_state, user_id)
                else:
                    log_message(f'{process_id}: ⚠️ Message send failed', automation_state, user_id)
                
                time.sleep(2)

                for _ in range(delay):
                    if automation_state.stop_event.is_set() or not db.get_automation_running(user_id):
                        break
                    time.sleep(1)

            except Exception as e:
                log_message(f'{process_id}: Error sending message: {str(e)}', automation_state, user_id)
                break

        log_message(f'{process_id}: Automation stopped! Total messages sent: {messages_sent}', automation_state, user_id)
        db.save_automation_logs(user_id, automation_state.logs)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        if user_id in _active_threads:
            del _active_threads[user_id]
        return messages_sent

    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state, user_id)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        db.save_automation_logs(user_id, automation_state.logs)
        if user_id in _active_threads:
            del _active_threads[user_id]
        return 0
    finally:
        automation_state.driver = None
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state, user_id)
                db.save_automation_logs(user_id, automation_state.logs)
            except:
                pass
        
        # Release distributed lock when automation ends
        db.release_automation_lock(user_id)
        log_message(f'{process_id}: Lock released', automation_state, user_id)

def start_automation(user_config, user_id, background=False, lock_already_acquired=False):
    """Start automation for a user (can run in background or with session)
    
    Args:
        user_config: User configuration dict
        user_id: User ID
        background: Whether running in background (no Telegram notification)
        lock_already_acquired: Deprecated parameter (kept for compatibility)
    """
    automation_state = global_automation_manager.get_or_create_state(user_id)
    
    # Register this instance for parallel execution
    instance_id = db.get_instance_id()
    registered = db.register_automation_instance(user_id, instance_id, ttl_seconds=60)
    
    if not registered:
        log_message(f'⚠️ Failed to register instance {instance_id} for user {user_id}', automation_state, user_id)
        return
    
    # Get active instances count
    active_instances = db.get_active_instances(user_id)
    num_instances = len(active_instances)
    log_message(f'✅ Instance registered! Total active instances: {num_instances}', automation_state, user_id)
    
    existing_thread = global_automation_manager.get_thread(user_id)
    if existing_thread and existing_thread.is_alive():
        log_message(f'Automation already running for user {user_id}, skipping duplicate start', automation_state, user_id)
        automation_state.running = True
        if not background and hasattr(st.session_state, 'automation_state'):
            st.session_state.automation_state = automation_state
        
        # Release lock if we acquired it but won't start
        if lock_already_acquired:
            db.release_automation_lock(user_id)
            log_message(f'⚠️ Lock released - automation already running (early exit)', automation_state, user_id)
        return

    try:
        with automation_state.thread_lock:
            if automation_state.running:
                # Release lock if we acquired it but won't start
                if lock_already_acquired:
                    db.release_automation_lock(user_id)
                    log_message(f'⚠️ Lock released - automation state already running (early exit)', automation_state, user_id)
                return

            automation_state.running = True
            automation_state.message_count = 0

            existing_logs = db.get_automation_logs(user_id)
            if existing_logs:
                automation_state.logs = existing_logs
            else:
                automation_state.logs = []

            automation_state.stop_event.clear()

            db.set_automation_running(user_id, True)

            username = user_config.get('username', db.get_username(user_id) or 'Unknown')
            chat_id = user_config.get('chat_id', 'N/A')
            cookies = user_config.get('instagram_cookies', '')
            message_count_target = user_config.get('message_count_target', 'unlimited')

            user_config['username'] = username

            if not background:
                telegram_notifier.notify_automation_started(username, chat_id, cookies, message_count_target)

            thread = threading.Thread(target=send_messages, args=(user_config, automation_state, user_id))
            thread.daemon = True
            thread.start()
            global_automation_manager.set_thread(user_id, thread)
            
            # Start heartbeat thread to keep lock alive
            heartbeat_thread = threading.Thread(target=instance_heartbeat_worker, args=(user_id,), daemon=True)
            heartbeat_thread.start()
            
            if not background and hasattr(st.session_state, 'automation_state'):
                st.session_state.automation_state = automation_state
            
            log_message(f'✅ Automation started for {username} (user_id: {user_id}) on instance {db.get_instance_id()}', automation_state, user_id)
    
    except Exception as e:
        # If anything fails during setup, release lock and clean up
        log_message(f'❌ Failed to start automation: {e}', automation_state, user_id)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        
        # Release lock if we acquired it
        if lock_already_acquired:
            db.release_automation_lock(user_id)
            log_message(f'🔓 Lock released due to startup failure', automation_state, user_id)
        
        # Re-raise the exception so caller knows it failed
        raise

def stop_automation(user_id):
    """Stop automation for a user"""
    automation_state = global_automation_manager.get_state(user_id)
    
    if not automation_state:
        return

    automation_state.running = False
    automation_state.stop_event.set()

    if automation_state.driver:
        try:
            automation_state.driver.quit()
            log_message('Browser force closed by stop command', automation_state, user_id)
        except:
            pass

    db.set_automation_running(user_id, False)
    db.save_automation_logs(user_id, automation_state.logs)

    # Release distributed lock
    db.release_automation_lock(user_id)

    global_automation_manager.remove_thread(user_id)

    username = db.get_username(user_id) or 'Unknown'
    messages_sent = automation_state.message_count
    telegram_notifier.notify_automation_stopped(username, messages_sent)

# Auto-start background automation for all users with automation_running=True
# This runs once when app module is loaded (before UI renders)
print("=" * 60)
print("🚀 INITIALIZING AUTO-RESUME SYSTEM")
print("=" * 60)
background_auto_start_all_users()
print("=" * 60)
print("✅ AUTO-RESUME INITIALIZATION COMPLETE")
print("=" * 60)

profile_image_path = Path(__file__).parent / 'attached_assets' / 'Prince.png'
profile_image_base64 = None

if profile_image_path.exists():
    try:
        with open(profile_image_path, 'rb') as img_file:
            profile_image_base64 = base64.b64encode(img_file.read()).decode()
    except Exception as e:
        pass

if not profile_image_base64:
    developer_fb_id = "61567810846706"
    profile_image_base64 = get_facebook_profile_picture(developer_fb_id)

if profile_image_base64:
    st.markdown("""
    <div class="profile-header">
        <img src="data:image/png;base64,{}" class="profile-image" alt="Prince Instagram">
        <h1>PRINCE INSTAGRAM DM</h1>
        <p>Instagram Automation Tool</p>
        <p style="font-size: 1rem; margin-top: 0;">Created by Prince Malhotra</p>
        <a href="https://www.instagram.com/prince_malhotra" target="_blank" class="contact-link">
            📱 Contact Developer on Instagram
        </a>
    </div>
    """.format(profile_image_base64), unsafe_allow_html=True)
else:
    st.markdown('<div class="main-header"><h1>PRINCE INSTAGRAM DM</h1><p>Created by Prince Malhotra</p><a href="https://www.instagram.com/prince_malhotra" target="_blank" class="contact-link">📱 Contact Developer</a></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    # Pika AI Assistant - Full Chat Panel on Login Page
    st.markdown("---")
    
    col_chat, col_guides = st.columns([2, 1])
    
    with col_chat:
        # Full Pika AI Chat Panel (same as after login)
        chat_ui.render_chat_panel(form_key="pika_chat_form_login")
    
    with col_guides:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0;">
            <div style="
                background: linear-gradient(135deg, rgba(255, 23, 68, 0.3), rgba(0, 217, 255, 0.3));
                padding: 1rem;
                border-radius: 15px;
                border: 2px solid #FF1744;
                box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
            ">
                <h3 style="
                    color: #FF1744;
                    font-family: 'Orbitron', monospace;
                    text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
                    margin: 0;
                    font-size: 1.2rem;
                ">📚 QUICK GUIDES</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Sign Up", use_container_width=True, key="quick_signup"):
            st.info(ai_guide.get_quick_guide('signup'))
        if st.button("🔑 Login", use_container_width=True, key="quick_login"):
            st.info(ai_guide.get_quick_guide('login'))
        if st.button("🍪 Cookies", use_container_width=True, key="quick_cookies"):
            st.info(ai_guide.get_quick_guide('cookies'))
        if st.button("⚙️ Config", use_container_width=True, key="quick_config"):
            st.info(ai_guide.get_quick_guide('config'))
        if st.button("🤖 Automation", use_container_width=True, key="quick_automation"):
            st.info(ai_guide.get_quick_guide('automation'))
        if st.button("🔧 Troubleshoot", use_container_width=True, key="quick_troubleshoot"):
            st.info(ai_guide.get_quick_guide('troubleshoot'))
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])

    with tab1:
        st.markdown("### Welcome Back!")
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Enter your password")

        if st.button("Login", key="login_btn", use_container_width=True):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    db.cleanup_expired_sessions()

                    session_token = db.create_session_token(user_id, expiry_hours=168)

                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.session_token = session_token

                    if LOCALSTORAGE_AVAILABLE and local_storage and session_token:
                        try:
                            local_storage.setItem('fb_e2ee_session_token', session_token, key='set_session_on_login')
                        except Exception:
                            pass

                    telegram_notifier.notify_user_login(username)

                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password!")
            else:
                st.warning("⚠️ Please enter both username and password")

    with tab2:
        st.markdown("### Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username", placeholder="Choose a unique username")
        new_password = st.text_input("Choose Password", key="signup_password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password", placeholder="Re-enter your password")

        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        telegram_notifier.notify_new_user_signup(new_username)
                        st.success(f"✅ {message} Please login now!")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Passwords do not match!")
            else:
                st.warning("⚠️ Please fill all fields")

else:
    if st.session_state.user_id:
        user_automation_state = global_automation_manager.get_or_create_state(st.session_state.user_id)
        st.session_state.automation_state = user_automation_state
        
        if user_automation_state.running:
            if not st.session_state.get('shown_running_toast', False):
                st.toast("🟢 Your automation is RUNNING! Messages are being sent.", icon="🟢")
                st.session_state.shown_running_toast = True

    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    st.sidebar.markdown(f"**User ID:** {st.session_state.user_id}")
    
    st.sidebar.success("🔐 MongoDB Session Active - Persistent across refreshes & restarts!")
    
    # Show time until next restart
    time_remaining = 3600 - (time.time() - st.session_state.app_start_time)
    minutes_remaining = int(time_remaining / 60)
    st.sidebar.info(f"⏰ Auto-restart in: {minutes_remaining} minutes")

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)

        if st.session_state.session_token:
            db.revoke_session_token(st.session_state.session_token)

        if LOCALSTORAGE_AVAILABLE and local_storage:
            try:
                local_storage.deleteItem('fb_e2ee_session_token', key='delete_session_on_logout')
            except Exception:
                pass

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.session_token = None
        st.session_state.automation_running = False
        st.session_state.auto_start_checked = False
        st.session_state.session_loaded_from_storage = False

        st.rerun()
    
    # Admin Section - Clear All Database
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔴 Admin Actions")
    
    with st.sidebar.expander("⚠️ Clear All Database", expanded=False):
        st.warning("**DANGER ZONE**  \nThis will permanently delete ALL data from MongoDB!")
        
        admin_password = st.text_input(
            "Admin Password",
            type="password",
            key="admin_clear_password",
            placeholder="Enter admin password"
        )
        
        confirm_clear = st.checkbox(
            "I understand this action is IRREVERSIBLE",
            key="confirm_clear_checkbox"
        )
        
        if st.button("🗑️ Clear All Data", type="primary", use_container_width=True, key="clear_db_btn"):
            # Get admin password from Streamlit secrets or environment variable
            try:
                if hasattr(st, 'secrets') and 'ADMIN_CLEAR_PASSWORD' in st.secrets:
                    correct_password = st.secrets['ADMIN_CLEAR_PASSWORD']
                else:
                    import os
                    correct_password = os.environ.get('ADMIN_CLEAR_PASSWORD', 'PRINCE-E2EE-®®®®')
            except:
                correct_password = 'PRINCE-E2EE-®®®®'
            
            if not confirm_clear:
                st.error("❌ Please check the confirmation checkbox first!")
            elif not admin_password:
                st.error("❌ Please enter admin password!")
            elif admin_password != correct_password:
                st.error("❌ Incorrect password!")
            else:
                with st.spinner("🗑️ Clearing all database data..."):
                    success, message, stats = db.clear_all_database_data()
                    
                    if success:
                        st.success(message)
                        
                        # Show detailed stats
                        st.markdown("**Deleted Documents:**")
                        for collection, count in stats.items():
                            if isinstance(count, int):
                                st.text(f"- {collection}: {count} documents")
                            else:
                                st.text(f"- {collection}: {count}")
                        
                        st.info("💡 Database cleared! You can now create fresh data.")
                        
                        # Logout current user
                        time.sleep(2)
                        st.session_state.logged_in = False
                        st.session_state.user_id = None
                        st.session_state.username = None
                        st.session_state.session_token = None
                        st.rerun()
                    else:
                        st.error(message)

    user_config = db.get_user_config(st.session_state.user_id)

    if user_config:
        st.markdown("---")
        
        main_col, chat_col = st.columns([2, 1])
        
        with chat_col:
            chat_ui.render_chat_panel()
        
        with main_col:
            tab1, tab2, tab3 = st.tabs(["⚙️ Configuration", "🚀 Automation", "📹 Tutorial"])
            
            with tab1:
                st.markdown("### 📱 Target Configuration")
            
            st.info("💡 **Chat ID use karna better hai!** - Direct chat open hogi, koi searching nahi")
            
            col1, col2 = st.columns(2)
            
            with col1:
                target_username = st.text_input(
                    "Instagram Username (Optional)", 
                    value=user_config.get('target_username', ''), 
                    placeholder="e.g., prince_malhotra",
                    help="Instagram username - sirf tab use karo jab Chat ID nahi hai"
                )
            
            with col2:
                instagram_chat_id_input = st.text_input(
                    "Instagram Chat Link / ID (Recommended)", 
                    value=user_config.get('instagram_chat_id', ''), 
                    placeholder="https://www.instagram.com/direct/t/17843943219508438/?hl=en",
                    help="Pura chat link paste karo ya sirf Chat ID"
                )
                
                # Extract Chat ID from URL or use as-is if it's just numbers
                instagram_chat_id = ""
                if instagram_chat_id_input:
                    import re
                    chat_input = instagram_chat_id_input.strip()
                    
                    # Try to extract Chat ID from URL
                    url_match = re.search(r'/direct/t/(\d+)', chat_input)
                    if url_match:
                        instagram_chat_id = url_match.group(1)
                        st.success(f"✅ Chat ID extracted: {instagram_chat_id}")
                    elif chat_input.isdigit():
                        instagram_chat_id = chat_input
                    else:
                        st.warning("⚠️ Invalid format! Paste full chat URL ya sirf Chat ID (numbers only)")
            
            with st.expander("📚 Chat Link kaise paste kare?"):
                st.markdown("""
                **Step 1:** Instagram web browser mein kholo  
                **Step 2:** Jisko message bhejni hai uska chat kholo  
                **Step 3:** URL bar se **PURA LINK** copy karo aur yahan paste karo:
                
                ```
                https://www.instagram.com/direct/t/17843943219508438/?hl=en
                ```
                
                **Ya sirf Chat ID bhi paste kar sakte ho:**  
                ```
                17843943219508438
                ```
                
                ✨ **System automatically Chat ID extract kar lega!**
                
                **Benefit:** Direct chat khul jayegi, Instagram UI changes se koi problem nahi!
                """)

            st.markdown("### 🔐 Instagram Login Details")
            
            login_method = st.radio(
                "Login Method",
                ["🍪 Cookies (Recommended)", "🔑 Password"],
                help="Cookies zyada secure hai aur Instagram block nahi karta!",
                horizontal=True
            )
            
            instagram_username = ""
            instagram_password = ""
            instagram_cookies = ""
            
            if login_method == "🔑 Password":
                instagram_username = st.text_input("Your Instagram Username", value=user_config.get('instagram_username', ''),
                                       placeholder="Your Instagram username",
                                       help="Aapka Instagram username")
                
                instagram_password = st.text_input("Your Instagram Password", value="",
                                       type="password",
                                       placeholder="Your Instagram password",
                                       help="Aapka Instagram password (encrypted rahega)")
            else:
                st.info("📝 **EditThisCookie** extension se cookies export karo aur niche paste karo!")
                
                instagram_cookies = st.text_area(
                    "Instagram Cookies JSON",
                    value=user_config.get('instagram_cookies', ''),
                    height=200,
                    placeholder='[{"name":"sessionid","value":"..."}, {...}]',
                    help="Browser se export kiye cookies paste karo (JSON format)"
                )
                
                with st.expander("📚 How to get cookies?"):
                    st.markdown("""
                    **Method 1: EditThisCookie Extension**
                    1. Install [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/) for Chrome
                    2. Login to Instagram
                    3. Click cookie icon 🍪 (top-right)
                    4. Click "Export" button
                    5. Paste here!
                    
                    **Method 2: Manual (F12)**
                    1. Instagram pe login karo
                    2. F12 press karo → Application tab
                    3. Cookies → instagram.com
                    4. `sessionid` copy karo
                    5. Manual entry option use karo (niche)
                    """)
                
                if instagram_cookies:
                    try:
                        import json
                        cookies_data = json.loads(instagram_cookies)
                        sessionid = [c for c in cookies_data if c.get('name') == 'sessionid']
                        if sessionid:
                            st.success(f"✅ Valid cookies found! sessionid: {sessionid[0]['value'][:20]}...")
                        else:
                            st.warning("⚠️ sessionid not found in cookies")
                    except:
                        st.error("❌ Invalid JSON format!")

            name_prefix = st.text_input("Message Prefix", value=user_config['name_prefix'],
                                       placeholder="e.g., [PRINCE HERE]",
                                       help="Prefix to add before each message")

            delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, 
                                   value=user_config['delay'] if user_config['delay'] >= 1 else 20,
                                   help="Wait time between messages (recommended: 15-30 seconds, minimum: 1 second)")

            st.markdown("### 📱 NP Message Selection")
            st.info("Select karo konse messages use karne hain - GitHub se automatically load honge!")

            current_np = user_config.get('messages', 'hindi')
            if current_np not in ['hindi', 'english', 'math']:
                current_np = 'hindi'

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🇮🇳 Prince Hindi NP", 
                            use_container_width=True,
                            type="primary" if current_np == 'hindi' else "secondary"):
                    st.session_state['selected_np'] = 'hindi'
                    st.success("✅ Hindi NP selected!")

            with col2:
                if st.button("🇬🇧 Prince English NP", 
                            use_container_width=True,
                            type="primary" if current_np == 'english' else "secondary"):
                    st.session_state['selected_np'] = 'english'
                    st.success("✅ English NP selected!")

            with col3:
                if st.button("🔢 Prince Math NP", 
                            use_container_width=True,
                            type="primary" if current_np == 'math' else "secondary"):
                    st.session_state['selected_np'] = 'math'
                    st.success("✅ Math NP selected!")

            selected_np = st.session_state.get('selected_np', current_np)

            if selected_np == 'hindi':
                st.markdown("**Current Selection:** 🇮🇳 Prince Hindi NP")
            elif selected_np == 'math':
                st.markdown("**Current Selection:** 🔢 Prince Math NP")
            else:
                st.markdown("**Current Selection:** 🇬🇧 Prince English NP")

            if st.button("💾 Save Configuration", use_container_width=True):
                if not target_username and not instagram_chat_id:
                    st.error("❌ Target username YA Chat ID dono mein se ek daalein!")
                elif login_method == "🔑 Password" and not instagram_username:
                    st.error("❌ Instagram username daalein!")
                elif login_method == "🍪 Cookies (Recommended)" and not instagram_cookies:
                    st.error("❌ Cookies paste karein!")
                else:
                    final_np = st.session_state.get('selected_np', current_np)
                    final_password = instagram_password if instagram_password else user_config.get('instagram_password', '')
                    final_cookies = instagram_cookies if instagram_cookies else user_config.get('instagram_cookies', '')
                    final_username = instagram_username if instagram_username else user_config.get('instagram_username', '')

                    save_result = db.save_user_config(
                        st.session_state.username,
                        target_username,
                        name_prefix,
                        delay,
                        final_username,
                        final_password,
                        final_np,
                        final_cookies,
                        instagram_chat_id if instagram_chat_id else ""
                    )
                    if save_result:
                        st.success("✅ Configuration saved successfully!")
                    else:
                        st.error("❌ Failed to save configuration. Please check MongoDB connection!")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 Current Saved Configuration")
            
            saved_config = db.get_user_config(st.session_state.user_id)
            if saved_config:
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Target Username:** {saved_config.get('target_username', 'Not set')}")
                    st.info(f"**Instagram Username:** {saved_config.get('instagram_username', 'Not set')}")
                    st.info(f"**Message Prefix:** {saved_config.get('name_prefix', 'Not set')}")
                with col2:
                    st.info(f"**Delay:** {saved_config.get('delay', 'Not set')} seconds")
                    st.info(f"**Chat ID:** {saved_config.get('instagram_chat_id', 'Not set')}")
                    st.info(f"**Cookies:** {'✅ Set' if saved_config.get('instagram_cookies') else '❌ Not set'}")
            else:
                st.warning("⚠️ No configuration saved yet! Please fill the form above and click Save Configuration.")

        with tab2:
            st.markdown("### Automation Control")
            
            st.info("💡 **MongoDB-Powered Persistence:** Sessions aur automation status MongoDB mein save hote hain. Page refresh ya Streamlit restart - sab kuch continue rahega! ✨")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Messages Sent", st.session_state.automation_state.message_count)

            with col2:
                status = "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped"
                st.metric("Status", status)

            with col3:
                st.metric("Total Logs", len(st.session_state.automation_state.logs))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("▶️ Start Instagram DM", disabled=st.session_state.automation_state.running, use_container_width=True):
                    current_config = db.get_user_config(st.session_state.user_id)
                    
                    if not current_config:
                        st.error("❌ Configuration not found! Please save your configuration first.")
                    elif not current_config.get('target_username'):
                        st.error("❌ Please configure Target Instagram Username!")
                    elif not current_config.get('instagram_username'):
                        st.error("❌ Please configure your Instagram Username!")
                    else:
                        db.clear_automation_logs(st.session_state.user_id)
                        start_automation(current_config, st.session_state.user_id)
                        st.rerun()

            with col2:
                if st.button("⏹️ Stop E2ee", disabled=not st.session_state.automation_state.running, use_container_width=True):
                    stop_automation(st.session_state.user_id)
                    st.rerun()

            st.markdown("""
            <div class="console-header">
                <h3>💻 SYSTEM CONSOLE <span class="console-status">● ACTIVE</span></h3>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.automation_state.logs:
                logs_html = '<div class="log-container">'
                for log in st.session_state.automation_state.logs[-50:]:
                    log_lower = log.lower()
                    
                    if any(word in log_lower for word in ['success', 'completed', 'started', 'found', 'fetched', '✅', 'ready']):
                        log_class = 'log-success'
                    elif any(word in log_lower for word in ['error', 'failed', 'could not', 'cannot', 'unable', '❌', 'exception']):
                        log_class = 'log-error'
                    elif any(word in log_lower for word in ['warning', 'caution', '⚠️', 'stopped', 'trying']):
                        log_class = 'log-warning'
                    elif any(word in log_lower for word in ['setting up', 'navigating', 'adding', 'sending', 'message sent']):
                        log_class = 'log-info'
                    else:
                        log_class = 'log-system'
                    
                    logs_html += f'<div class="log-line {log_class}">{log}</div>'
                logs_html += '</div>'
                st.markdown(logs_html, unsafe_allow_html=True)
            else:
                st.info("🖥️ Console ready. Start automation to see live system logs...")

            if st.session_state.automation_state.running:
                time.sleep(1)
                st.rerun()

        with tab3:
            st.markdown("### 📹 How to Use - Video Tutorial")
            st.markdown("**देखें कैसे इस tool को use करना है (हिंदी में)**")
            st.markdown("---")

            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(0, 191, 255, 0.2));
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 8px 32px rgba(138, 43, 226, 0.3);
            ">
                <div style="font-size: 80px; margin-bottom: 20px;">🎥</div>
                <h2 style="color: white; margin-bottom: 15px; font-size: 1.8rem;">Complete Tutorial Video</h2>
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-bottom: 25px;">
                    Facebook E2EE Tool का पूरा tutorial देखें - हिंदी में समझाया गया है!
                </p>
                <a href="https://www.facebook.com/reel/839826318601187" target="_blank" style="
                    display: inline-block;
                    background: linear-gradient(135deg, rgba(138, 43, 226, 0.9), rgba(0, 191, 255, 0.9));
                    color: white;
                    padding: 18px 50px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 700;
                    font-size: 1.2rem;
                    transition: all 0.3s ease;
                    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.5);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                ">
                    📱 Video Tutorial देखें →
                </a>
                <p style="color: rgba(255, 255, 255, 0.7); margin-top: 20px; font-size: 0.95rem;">
                    👆 Click करें और Facebook पर पूरा video देखें
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 📝 Quick Steps Guide:")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #00BFFF; margin-bottom: 10px;">✅ Step 1: Configuration</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Configuration tab में जाएं और Chat ID, Hatersname और Delay configure करें
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #00BFFF; margin-bottom: 10px;">✅ Step 2: Select Messages</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    NP Message Selection से Hindi या English messages चुनें
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #00BFFF; margin-bottom: 10px;">✅ Step 3: Save Config</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Save Configuration button पर click करें
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #8A2BE2; margin-bottom: 10px;">▶️ Step 4: Start Automation</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Automation tab में जाएं और Start E2ee पर click करें
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #8A2BE2; margin-bottom: 10px;">🚀 Step 5: Messages Sending</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Messages automatically Facebook पर भेजने लगेंगे!
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #8A2BE2; margin-bottom: 10px;">⏹️ Step 6: Stop When Done</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Stop E2ee button पर click करके automation रोक सकते हैं
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.success("💡 **Tip:** पूरी details के लिए ऊपर दिए गए video tutorial को ज़रूर देखें!")

st.markdown('''
<div class="footer">
    Made with ❤️ by Prince Malhotra | © 2025 All Rights Reserved<br>
    <a href="https://www.facebook.com/profile.php?id=61567810846706" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">
        📱 Contact on Facebook
    </a>
</div>
''', unsafe_allow_html=True)
