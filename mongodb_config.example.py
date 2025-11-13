# MongoDB Configuration File (EXAMPLE)
# Copy this file to mongodb_config.py and update with your actual credentials

# MongoDB Connection String
# Get this from MongoDB Atlas:
# 1. Go to https://cloud.mongodb.com
# 2. Click "Connect" on your cluster
# 3. Choose "Connect your application"
# 4. Copy the connection string and replace the values below

MONGODB_URI = "mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/facebook_automation_db?retryWrites=true&w=majority&appName=Cluster0"

# Database Name
DATABASE_NAME = "facebook_automation_db"

# Collections Names
USERS_COLLECTION = "users"
USER_CONFIGS_COLLECTION = "user_configs"
USER_SESSIONS_COLLECTION = "user_sessions"
AUTOMATION_LOGS_COLLECTION = "automation_logs"
AUTOMATION_LOCKS_COLLECTION = "automation_locks"
AUTOMATION_INSTANCES_COLLECTION = "automation_instances"
USER_MESSAGE_INDEX_COLLECTION = "user_message_index"
