# backend/database.py

from pymongo import MongoClient
import os
from datetime import datetime
import uuid 

# --- Global Client Initialization for Connection Pooling ---
CLIENT = None 

def get_db():
    """
    Establishes and returns a connection to the MongoDB database.
    This function initializes the connection client once (globally).
    """
    global CLIENT
    
    # If the client is already connected, return the database instance immediately
    if CLIENT is not None:
        return CLIENT['VirtualPartnerDB']
        
    # 1. Get connection string from environment variables
    MONGO_URI = os.environ.get('MONGO_URI')
    if not MONGO_URI:
        raise EnvironmentError("MONGO_URI environment variable not set.")
    
    # 2. Connect to the Atlas cluster (5-second timeout for cloud stability)
    CLIENT = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) 
    
    # 3. Return the specific database instance
    return CLIENT['VirtualPartnerDB']

def create_user(user_data):
    """Saves a new user profile during registration."""
    db = get_db()
    
    if 'user_id' not in user_data:
        user_data['user_id'] = str(uuid.uuid4())
        
    user_data['created_at'] = datetime.utcnow()
    db.users.insert_one(user_data)
    return user_data

def get_user_and_history(user_id):
    """Retrieves a user's profile and their complete chat history for session persistence."""
    db = get_db()
    
    user = db.users.find_one({'user_id': user_id})
    history = list(db.chats.find({'user_id': user_id}).sort('timestamp', 1))
    
    return user, history

def save_chat_message(user_id, sender, content):
    """Saves a chat message for conversation history and adaptive learning."""
    db = get_db()
    
    message = {
        'user_id': user_id,
        'sender': sender, # 'user' or 'partner'
        'content': content,
        'timestamp': datetime.utcnow()
    }
    db.chats.insert_one(message)
    return message