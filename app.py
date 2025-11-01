# backend/app.py

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import uuid 
from datetime import datetime 
from flask_cors import CORS 

# Core Modules (Imports verified)
from database import get_db, create_user, get_user_and_history, save_chat_message
from parser import parse_chat
from personality_model import DualPersonalityModel


load_dotenv()

# 1. Define the Flask App instance
app = Flask(__name__)
CORS(app) 

# 2. Initialize the AI Model (Uses default personalities from personality_model.py)
model = DualPersonalityModel()
AI_PROFILES = None # Global variable for future model persistence


# --- API Endpoints ---

@app.route('/api/status', methods=['GET'])
def status():
    """Simple health check endpoint."""
    return jsonify({"status": "ready", "model_trained": AI_PROFILES is not None})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handles session persistence for returning users."""
    data = request.json
    user_id = data.get('user_id') 
    
    user, history = get_user_and_history(user_id) 
    
    if user:
        partner_name = user['partner_name']
        return jsonify({
            "success": True, 
            "user_id": user['user_id'], 
            "partner_name": partner_name,
            "chat_history": history
        }), 200
    else:
        return jsonify({"success": False, "needs_onboarding": True}), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Handles new user onboarding (gender choice, partner name)."""
    data = request.json
    
    user_id = str(uuid.uuid4())
    user_gender = data.get('user_gender')
    
    partner_gender = 'Female' if user_gender == 'Male' else 'Male'
    partner_name = data.get('partner_name')

    new_user = {
        'user_id': user_id,
        'email': data.get('email'), 
        'password': data.get('password'),
        'user_gender': user_gender,
        'partner_gender': partner_gender,
        'partner_name': partner_name
    }
    
    create_user(new_user)
    # FIX: Uses placeholder message to avoid crash on first DB write.
    save_chat_message(user_id, 'partner', f"Hi {partner_name}! Your partner is ready to chat.")

    return jsonify({"success": True, "user_id": user_id, "partner_name": partner_name, "chat_history": []}), 201

# --- Chat Interface (Updated) ---
@app.route('/api/chat/<user_id>', methods=['POST'])
def chat(user_id):
    """Handles message receipt and AI response generation."""
    # NOTE: The check for AI_PROFILES is removed to ensure the app functions immediately.
    
    data = request.json
    user_input = data.get('message')
    
    user, history = get_user_and_history(user_id)
    if not user:
         return jsonify({"message": "User not found."}), 404

    # 1. Save User Message
    save_chat_message(user_id, 'user', user_input)
    
    # 2. Determine target personality 
    target_partner_id = 'A' if user.get('partner_gender') == 'Male' else 'B'
    
    # 3. Generate Response (Uses the rule-based logic from personality_model.py)
    ai_response = model.generate_response(user_id, target_partner_id, history, user_input)
    
    # 4. Save AI Response
    save_chat_message(user_id, 'partner', ai_response)
    
    return jsonify({
        "message": ai_response,
        "sender": "virtual_partner",
    })

# --- TRAINING ENDPOINT (ADMIN FUNCTIONALITY) ---
@app.route('/api/train_model', methods=['POST'])
def train_model():
    """
    Accepts raw chat text via POST request to train the AI model.
    This will be used by your future Admin portal.
    """
    global AI_PROFILES
    
    raw_chat_content = request.data.decode('utf-8')
    
    if not raw_chat_content:
        return jsonify({"message": "Error: No chat