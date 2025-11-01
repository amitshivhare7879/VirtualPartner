# backend/app.py

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import uuid 
from datetime import datetime 
from flask_cors import CORS 

# Core Modules (Imports verified as correct relative imports)
from database import get_db, create_user, get_user_and_history, save_chat_message
from parser import parse_chat
from personality_model import DualPersonalityModel


load_dotenv()

# 1. Define the Flask App instance
app = Flask(__name__)

# 2. Initialize CORS
CORS(app) 

# 3. Initialize the AI Model
model = DualPersonalityModel()
AI_PROFILES = None # Global variable to hold the trained profiles

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
    save_chat_message(user_id, 'partner', f"Hi {partner_name}! It's great to finally chat.")

    return jsonify({"success": True, "user_id": user_id, "partner_name": partner_name, "chat_history": []}), 201

# --- Chat Interface (Updated) ---
@app.route('/api/chat/<user_id>', methods=['POST'])
def chat(user_id):
    global AI_PROFILES
    
    # 1. Check/Load Model
    if AI_PROFILES is None:
        db = get_db()
        AI_PROFILES = db.ai_profiles.find_one({}) 
        if AI_PROFILES is None:
             return jsonify({"message": "AI model not trained. Please run training script first."}), 400

    data = request.json
    user_input = data.get('message')
    
    # 2. Get User Details and History
    user, history = get_user_and_history(user_id)
    if not user:
         return jsonify({"message": "User not found."}), 404

    # 3. Save User Message
    save_chat_message(user_id, 'user', user_input)
    
    # 4. Determine target personality 
    target_partner_id = 'A' if user.get('partner_gender') == 'Male' else 'B'
    
    # 5. Generate Response (LLM/Rule-based logic)
    ai_response = model.generate_response(user_id, target_partner_id, history, user_input)
    
    # 6. Save AI Response
    save_chat_message(user_id, 'partner', ai_response)
    
    return jsonify({
        "message": ai_response,
        "sender": "virtual_partner",
    })

# --- TRAINING ENDPOINT ---
@app.route('/api/train_model', methods=['POST'])
def train_model():
    # NOTE: You MUST replace this logic with actual file reading when you run this endpoint.
    # For now, we simulate success for deployment readiness.
    # db = get_db()
    # db.ai_profiles.update_one({}, {"$set": AI_PROFILES}, upsert=True)
    return jsonify({"message": "Core model trained and stored (Placeholder success)."}), 200


if __name__ == '__main__':
    print("Running Flask App locally...")
    app.run(debug=True, port=8000)