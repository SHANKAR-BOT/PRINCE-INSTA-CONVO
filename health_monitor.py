#!/usr/bin/env python3
"""
Enhanced Health Monitor + Auto-Failover System
- Monitors Streamlit health
- Handles distributed automation auto-resume
- Primary-Secondary failover with automatic handback
"""
import time
import requests
import subprocess
import sys
import threading
from datetime import datetime

# Import MongoDB database for auto-resume functionality
try:
    import mongodb_database as db
    MONGODB_AVAILABLE = True
except Exception as e:
    print(f"⚠️  MongoDB import failed: {e}")
    MONGODB_AVAILABLE = False

STREAMLIT_URL = "http://0.0.0.0:5000"
CHECK_INTERVAL = 300  # Health check every 5 minutes
AUTO_RESUME_INTERVAL = 3  # Auto-resume check every 3 seconds (fast takeover)
HEARTBEAT_INTERVAL = 5  # Global heartbeat every 5 seconds
HEARTBEAT_TIMEOUT = 15  # Primary considered dead after 15 seconds
MAX_FAILURES = 3
RESTART_COOLDOWN = 60

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check_streamlit_health():
    try:
        response = requests.get(STREAMLIT_URL, timeout=10)
        if response.status_code == 200:
            return True, "OK"
        else:
            return False, f"Status code: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, f"Error: {str(e)}"

def restart_streamlit():
    try:
        print(f"[{get_timestamp()}] 🔄 Attempting to restart Streamlit...")
        
        subprocess.run(["pkill", "-f", "streamlit"], check=False)
        time.sleep(5)
        
        print(f"[{get_timestamp()}] ✅ Streamlit restart signal sent")
        return True
    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Restart failed: {str(e)}")
        return False

def global_heartbeat_worker():
    """
    Background worker that sends global heartbeat for this instance
    Announces: "I'm alive and acting as primary/secondary"
    """
    if not MONGODB_AVAILABLE:
        return
    
    instance_id = db.get_instance_id()
    
    # Register as secondary initially
    db.register_global_instance_heartbeat(instance_id, role='secondary', ttl_seconds=20)
    
    print(f"[{get_timestamp()}] 💓 Global heartbeat worker started")
    print(f"[{get_timestamp()}] 🆔 Instance ID: {instance_id}")
    print(f"[{get_timestamp()}] 📡 Sending heartbeat every {HEARTBEAT_INTERVAL} seconds")
    print("-" * 70)
    
    while True:
        try:
            # Get all users we're actively handling
            running_users = db.get_all_running_users()
            
            # Check if we own any locks (are we acting as primary?)
            is_primary = False
            for user_data in running_users:
                user_id = user_data.get('user_id')
                lock_owner = db.get_lock_owner(user_id)
                
                if lock_owner == instance_id:
                    is_primary = True
                    break
            
            # Update role and heartbeat
            role = 'primary' if is_primary else 'secondary'
            db.register_global_instance_heartbeat(instance_id, role=role, ttl_seconds=20)
            
            time.sleep(HEARTBEAT_INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n[{get_timestamp()}] 🛑 Global heartbeat worker stopped")
            db.deactivate_global_instance(instance_id)
            break
        except Exception as e:
            time.sleep(HEARTBEAT_INTERVAL)

def auto_resume_worker():
    """
    Enhanced auto-resume worker with primary-secondary failover
    - Detects abandoned automations (no lock)
    - INSTANT TAKEOVER when primary fails
    - AUTOMATIC HANDBACK when primary returns
    """
    if not MONGODB_AVAILABLE:
        print(f"[{get_timestamp()}] ⚠️  Auto-resume worker disabled (MongoDB not available)")
        return
    
    print(f"[{get_timestamp()}] 🔄 Enhanced auto-resume worker started")
    print(f"[{get_timestamp()}] 📍 Monitoring every {AUTO_RESUME_INTERVAL} seconds")
    print(f"[{get_timestamp()}] ⚡ Instant takeover enabled")
    print(f"[{get_timestamp()}] 🔄 Automatic handback enabled")
    print("-" * 70)
    
    instance_id = db.get_instance_id()
    print(f"[{get_timestamp()}] 🆔 This instance ID: {instance_id}")
    
    resumed_users = set()  # Track users we've already tried to resume
    active_takeovers = {}  # Track users we're actively handling
    config_versions = {}  # Track configuration versions for change detection
    
    while True:
        try:
            # Cleanup expired locks
            db.cleanup_expired_locks()
            
            # Get all users that should be running
            running_users = db.get_all_running_users()
            
            if not running_users:
                if active_takeovers:
                    print(f"[{get_timestamp()}] ℹ️  No more running automations")
                    active_takeovers.clear()
                time.sleep(AUTO_RESUME_INTERVAL)
                continue
            
            for user_data in running_users:
                user_id = user_data.get('user_id')
                username = user_data.get('username', 'Unknown')
                target_username = user_data.get('target_username', '')
                
                # DEBUG: Log user being checked
                print(f"[{get_timestamp()}] 🔍 Checking user: {username} (target: {'✅' if target_username else '❌'})")
                
                # Skip if no target_username configured
                if not target_username:
                    print(f"[{get_timestamp()}] ⚠️  Skipping {username}: No target_username configured")
                    continue
                
                # Check lock status
                lock_owner = db.get_lock_owner(user_id)
                print(f"[{get_timestamp()}] 🔐 Lock owner for {username}: {lock_owner if lock_owner else 'NONE (PRIMARY FAILED!)'}")
                
                # CASE 1: NO LOCK - Primary failed/crashed
                if lock_owner is None:
                    # Skip if we already tried to resume this user
                    if user_id in resumed_users:
                        continue
                    
                    print()
                    print("!" * 70)
                    print(f"[{get_timestamp()}] 🚨 PRIMARY FAILURE DETECTED!")
                    print(f"[{get_timestamp()}] 👤 User: {username}")
                    print("!" * 70)
                    print(f"[{get_timestamp()}] 🔒 Attempting INSTANT TAKEOVER...")
                    
                    lock_acquired = db.acquire_automation_lock(user_id, ttl_seconds=20)
                    
                    if lock_acquired:
                        print(f"[{get_timestamp()}] ✅ TAKEOVER SUCCESSFUL!")
                        print(f"[{get_timestamp()}] 🚀 Now handling messages for {username}")
                        print(f"[{get_timestamp()}] 💓 Heartbeat active")
                        print("!" * 70)
                        print()
                        
                        # Mark takeover
                        resumed_users.add(user_id)
                        active_takeovers[user_id] = username
                        
                        # Trigger Streamlit to resume
                        try:
                            requests.get(STREAMLIT_URL, timeout=5)
                        except:
                            pass
                    else:
                        print(f"[{get_timestamp()}] ⚠️  Lock acquisition failed")
                
                # CASE 2: WE OWN THE LOCK - Check if primary returned or config changed
                elif lock_owner == instance_id:
                    # Check for configuration changes
                    current_config = db.get_user_config(user_id)
                    if current_config:
                        current_version = current_config.get('config_version', 0)
                        known_version = config_versions.get(user_id, None)
                        
                        # Configuration changed - trigger restart
                        # Skip detection only on first check (when known_version is None)
                        if known_version is not None and current_version != known_version:
                            print()
                            print("!" * 70)
                            print(f"[{get_timestamp()}] 🔄 CONFIGURATION CHANGED!")
                            print(f"[{get_timestamp()}] 👤 User: {username}")
                            print(f"[{get_timestamp()}] 📝 Old version: {known_version}")
                            print(f"[{get_timestamp()}] 📝 New version: {current_version}")
                            print(f"[{get_timestamp()}] 🔄 Releasing lock to trigger restart...")
                            print("!" * 70)
                            
                            # Release lock to allow restart with new config
                            db.release_automation_lock(user_id)
                            
                            # Remove from tracking so it can be picked up again
                            resumed_users.discard(user_id)
                            active_takeovers.pop(user_id, None)
                            config_versions.pop(user_id, None)
                            
                            print(f"[{get_timestamp()}] ✅ Lock released - will restart with new config")
                            print()
                            continue
                        
                        # Store current version
                        config_versions[user_id] = current_version
                    
                    # We're acting as primary, check if original primary came back
                    if db.check_primary_instance_alive(instance_id):
                        print()
                        print("!" * 70)
                        print(f"[{get_timestamp()}] 🔵 PRIMARY RETURNED ONLINE!")
                        print(f"[{get_timestamp()}] 👤 User: {username}")
                        print(f"[{get_timestamp()}] 🤝 AUTOMATIC HANDBACK starting...")
                        print("!" * 70)
                        
                        # Release lock so primary can take over
                        db.release_automation_lock(user_id)
                        
                        # Remove from our tracking
                        resumed_users.discard(user_id)
                        active_takeovers.pop(user_id, None)
                        config_versions.pop(user_id, None)
                        
                        print(f"[{get_timestamp()}] ✅ Lock released")
                        print(f"[{get_timestamp()}] 🟡 Back to STANDBY mode")
                        print()
                    else:
                        # Keep heartbeat alive
                        db.update_lock_heartbeat(user_id, ttl_seconds=20)
                
                # CASE 3: ANOTHER INSTANCE owns lock - Just monitor
                else:
                    # Another instance is handling it
                    if user_id in active_takeovers:
                        print(f"[{get_timestamp()}] ℹ️  {username}: Handed back to {lock_owner}")
                        active_takeovers.pop(user_id, None)
            
            time.sleep(AUTO_RESUME_INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n[{get_timestamp()}] 🛑 Auto-resume worker stopped")
            # Release all locks we hold
            for user_id in list(active_takeovers.keys()):
                try:
                    db.release_automation_lock(user_id)
                except:
                    pass
            break
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ Auto-resume error: {str(e)}")
            time.sleep(AUTO_RESUME_INTERVAL)

def main():
    print("=" * 70)
    print(f"[{get_timestamp()}] 🚀 ENHANCED HEALTH MONITOR + AUTO-FAILOVER SYSTEM")
    print("=" * 70)
    print(f"[{get_timestamp()}] 📍 Monitoring URL: {STREAMLIT_URL}")
    print(f"[{get_timestamp()}] ⏱️  Health check interval: {CHECK_INTERVAL} seconds")
    print(f"[{get_timestamp()}] 🔄 Auto-resume check interval: {AUTO_RESUME_INTERVAL} seconds")
    print(f"[{get_timestamp()}] 💓 Global heartbeat interval: {HEARTBEAT_INTERVAL} seconds")
    print(f"[{get_timestamp()}] ⏰ Heartbeat timeout: {HEARTBEAT_TIMEOUT} seconds")
    print(f"[{get_timestamp()}] 🔁 Max failures before restart: {MAX_FAILURES}")
    print("=" * 70)
    
    # Start background workers
    if MONGODB_AVAILABLE:
        # Start global heartbeat worker
        heartbeat_thread = threading.Thread(target=global_heartbeat_worker, daemon=True)
        heartbeat_thread.start()
        print(f"[{get_timestamp()}] ✅ Global heartbeat worker started")
        
        # Start auto-resume worker
        resume_thread = threading.Thread(target=auto_resume_worker, daemon=True)
        resume_thread.start()
        print(f"[{get_timestamp()}] ✅ Auto-resume worker started (with failover)")
    else:
        print(f"[{get_timestamp()}] ⚠️  Failover disabled (MongoDB not available)")
    
    print("-" * 70)
    
    consecutive_failures = 0
    last_restart_time = 0
    
    while True:
        try:
            is_healthy, status = check_streamlit_health()
            
            if is_healthy:
                if consecutive_failures > 0:
                    print(f"[{get_timestamp()}] ✅ Streamlit recovered! Status: {status}")
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                print(f"[{get_timestamp()}] ⚠️  Health check failed ({consecutive_failures}/{MAX_FAILURES}): {status}")
                
                if consecutive_failures >= MAX_FAILURES:
                    current_time = time.time()
                    time_since_last_restart = current_time - last_restart_time
                    
                    if time_since_last_restart > RESTART_COOLDOWN:
                        print(f"[{get_timestamp()}] 🚨 Streamlit appears to be down! Auto-restarting...")
                        
                        if restart_streamlit():
                            last_restart_time = current_time
                            consecutive_failures = 0
                            print(f"[{get_timestamp()}] ⏳ Waiting {RESTART_COOLDOWN}s for Streamlit to start...")
                            time.sleep(RESTART_COOLDOWN)
                        else:
                            print(f"[{get_timestamp()}] ❌ Restart failed, will retry on next check")
                    else:
                        wait_time = int(RESTART_COOLDOWN - time_since_last_restart)
                        print(f"[{get_timestamp()}] ⏸️  In cooldown period, waiting {wait_time}s before next restart")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n[{get_timestamp()}] 🛑 Health monitor stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ Monitor error: {str(e)}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
