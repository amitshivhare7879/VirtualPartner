# backend/database.py

from pymongo import MongoClient
import os
from datetime import datetime
import uuid # Used for generating unique user IDs in register endpoint

def get_db():
    """
    Establishes and returns a connection to the MongoDB database.
    MONGO_URI is expected to be set as an environment variable by Render.
    """
    # 1. Get connection string from environment variables
    MONGO_URI = os.environ.get('MONGO_URI')
    if not MONGO_URI:
        raise EnvironmentError("MONGO_URI environment variable not set.")
    
    # 2. Connect to the Atlas cluster
    client = MongoClient(MONGO_URI)
    
    # 3. Use 'VirtualPartnerDB' as the specific database name inside the cluster
    db = client['VirtualPartnerDB'] 
    return db

def create_user(user_data):
    """
    Saves a new user profile during the onboarding/registration process.
    """
    db = get_db()
    
    # Ensure user_id is unique before insertion
    if 'user_id' not in user_data:
        user_data['user_id'] = str(uuid.uuid4())
        
    user_data['created_at'] = datetime.utcnow()
    # The 'users' collection stores user profile data
    db.users.insert_one(user_data)
    return user_data

def get_user_and_history(user_id):
    """
    Retrieves a user's profile and their complete chat history for session persistence.
    """
    db = get_db()
    
    # Find the user profile
    user = db.users.find_one({'user_id': user_id})
    
    # Retrieve the chat history, sorted chronologically
    history = list(db.chats.find({'user_id': user_id}).sort('timestamp', 1))
    
    return user, history

def save_chat_message(user_id, sender, content):
    """
    Saves a chat message (from user or AI partner) for conversation history and adaptive learning.
    """
    db = get_db()
    
    message = {
        'user_id': user_id,
        'sender': sender, # 'user' or 'partner'
        'content': content,
        'timestamp': datetime.utcnow()
    }
    # The 'chats' collection stores the conversation history
    db.chats.insert_one(message)
    return message