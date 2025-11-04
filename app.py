# backend/app.py (Final Stable Structure)

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
# NOTE: Removed problematic google/genai imports that caused the crash.


load_dotenv()

# 1. Define the Flask App instance
app = Flask(__name__)
CORS(app) 

# 2. Initialize the AI Model
model = DualPersonalityModel()
AI_PROFILES = None 

# --- API Endpoints (The code remains stable here) ---

# ... (all endpoints: status, login, register, train_model are placed here) ...

@app.route('/api/auth/register', methods=['POST'])
def register():
    # ... (Registration logic remains the same)
    pass # [For brevity, assume the registration function is here]

@app.route('/api/chat/<user_id>', methods=['POST'])
def chat(user_id):
    """Handles message receipt and LLM response generation."""
    
    # ... (User lookup and saving message remains stable) ...
    
    # 3. Generate Response (LLM is called here)
    # The actual LLM logic will now be handled inside personality_model.py
    ai_response = model.generate_response(user_id, target_partner_id, history, user_input)
    
    # ... (saving response and returning JSON remains stable) ...
    pass # [For brevity, assume the chat function is here]


if __name__ == '__main__':
    print("Running Flask App locally...")
    app.run(debug=True, port=8000)