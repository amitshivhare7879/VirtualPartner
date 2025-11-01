# backend/app.py (KEY MODIFICATIONS)
# ... (imports) ...
from backend.database import get_db, create_user, get_user_and_history, save_chat_message
from datetime import datetime
import uuid # For generating unique user IDs
from flask_cors import CORS # Crucial for free-tier deployment (Frontend needs to talk to Backend)

# ... (load_dotenv, app = Flask(__name__), model = DualPersonalityModel())
CORS(app) # Enable CORS for frontend communication

# --- Training Endpoint (Updated to use your provided files) ---
@app.route('/api/train_model', methods=['POST'])
def train_model():
    # This endpoint is run ONCE by you, the developer, to train the core model 
    # using the provided four chat files.
    # NOTE: This requires replacing the placeholder data in the last response 
    # with the actual content of the four files when you run this locally/on your server.
    # For simplicity, we assume success for the API demo:
    # (This is where the model.extract_patterns(parsed_data) call happens)
    # Global AI_PROFILES is set here.
    # AI_PROFILES = model.extract_patterns(parsed_data)

    # Once trained, store the resulting personality profiles in the database
    # db = get_db()
    # db.ai_profiles.update_one({}, {"$set": AI_PROFILES}, upsert=True)

    # ... (rest of the success response)
    return jsonify({"message": "Core model trained and stored."}), 200

# --- User Flow: Login/Signup & Session Persistence ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    # 1. Check for existing user (Simulated)
    # user = db.users.find_one({'email': data['email'], 'password': data['password']})
    user, history = get_user_and_history(data.get('user_id')) # Simplified by looking for an ID

    if user:
        # Returning User: Continue previous chat
        partner_name = user['partner_name']

    else:
        # New User: Requires Onboarding
        return jsonify({"needs_onboarding": True}), 200

    return jsonify({
        "success": True, 
        "user_id": user['user_id'], 
        "partner_name": partner_name,
        "chat_history": history
    }), 200

# --- Onboarding Flow: Gender, Name Partner ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    user_id = str(uuid.uuid4()) # Generate unique ID

    # Choose gender -> Bot is opposite gender partner
    user_gender = data.get('user_gender')
    partner_gender = 'Female' if user_gender == 'Male' else 'Male'

    # Let user name their virtual partner
    partner_name = data.get('partner_name')

    new_user = {
        'user_id': user_id,
        'email': data.get('email'), # Login/Signup
        'password': data.get('password'),
        'user_gender': user_gender,
        'partner_gender': partner_gender,
        'partner_name': partner_name
    }

    # Save user to DB and provide initial message
    create_user(new_user)
    save_chat_message(user_id, 'partner', f"Hi {partner_name}!")

    return jsonify({"success": True, "user_id": user_id, "partner_name": partner_name, "chat_history": []}), 201

# --- Chat Interface (Updated) ---
@app.route('/api/chat/<user_id>', methods=['POST'])
def chat(user_id):
    # ... (Same chat logic as before, but using database.py for history/persistence) ...
    # (Save user input and AI response using save_chat_message)
    # (LLM integration/model.generate_response logic remains the same)
    # ...

    data = request.json
    user_input = data.get('message')

    # 1. Get User Details
    user, _ = get_user_and_history(user_id)
    if not user:
         return jsonify({"message": "User not found."}), 404

    # 2. Save User Message
    save_chat_message(user_id, 'user', user_input)

    # 3. Get AI Profile (A=Male, B=Female based on your training data)
    # Determine target_partner_id based on the user's selected partner_gender
    target_partner_id = 'A' if user['partner_gender'] == 'Male' else 'B'

    # 4. Generate Response (LLM/Rule-based logic)
    # NOTE: You MUST load AI_PROFILES from the database here 
    # (This is the adaptive learning/context memory step)

    # For this step, we'll use the rule-based example from the previous response:
    ai_response = model.generate_response(user_id, target_partner_id, [], user_input)

    # 5. Save AI Response (Adaptive Learning)
    save_chat_message(user_id, 'partner', ai_response)

    return jsonify({
        "message": ai_response,
        "sender": "virtual_partner",
    })