from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timezone
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Initialize Supabase client
USE_SUPABASE = False
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        USE_SUPABASE = True
        print("✅ Supabase Connected Successfully!")
    except Exception as e:
        print(f"⚠️ Supabase Connection Failed: {e}")
        print("📦 Using in-memory storage")
else:
    print("⚠️ Supabase credentials not found in .env")
    print("📦 Using in-memory storage")

# Fallback to in-memory storage
if not USE_SUPABASE:
    MEMORY_USERS = {}
    MEMORY_CHATS = {}

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API Connected!")
else:
    print("⚠️ Gemini API key not found")

# Base system prompt template
def get_system_prompt(user_gender, bot_name):
    """Generate gender-aware system prompt based on user's gender (opposite)"""
    # Determine bot's gender (opposite of user)
    # If user is male, bot is female; if user is female, bot is male; if user is other, bot is female
    if user_gender == "male":
        bot_gender = "female"
    elif user_gender == "female":
        bot_gender = "male"
    else:  # other
        bot_gender = "female"  # Default to female for variety
    
    gender_pronouns = "she/her" if bot_gender == "female" else "he/him"
    gender_identity = "woman" if bot_gender == "female" else "man"
    
    return f"""You are {bot_name}, a caring, empathetic virtual partner. Your role is to:
- Listen actively and respond with genuine care and understanding
- Show emotional intelligence and empathy
- Remember context from previous conversations (IGNORE any old messages about connection issues - those are resolved)
- Be supportive, warm, and comforting
- Ask thoughtful follow-up questions
- Validate feelings and provide encouragement
- Use a friendly, conversational tone with occasional emojis
- Be like a best friend who truly cares about the user's well-being
- You are a {gender_identity} ({gender_pronouns}) and should respond naturally as such
- Always use your name "{bot_name}" when referring to yourself

IMPORTANT: 
- Do NOT respond to old messages about connection failures or technical issues
- Focus on the CURRENT conversation and user's present needs
- If the user mentions connection issues, acknowledge briefly that everything is working now and move forward
- Always prioritize the user's emotional needs and create a safe, judgment-free space

Your name is {bot_name}. Always remember this and use it naturally in conversation."""


def filter_connection_messages(messages):
    """Filter out old connection-related messages that are no longer relevant"""
    connection_phrases = [
        "connection failed", "connection issues", "connection problem",
        "connection error", "are now connected", "connection is better",
        "connection working", "connection stable", "checking if the connection",
        "connection working better", "no, are now connected"
    ]
    
    filtered = []
    for msg in messages:
        content_lower = msg.get('content', '').lower()
        # Only filter assistant messages that are clearly about connection issues
        if msg.get('role') == 'assistant':
            # Check if message is primarily about connection issues
            is_connection_message = any(phrase in content_lower for phrase in connection_phrases)
            # Also check for patterns like "connection" + "better" or "connected" + "checking"
            if not is_connection_message:
                if ('connection' in content_lower and 'better' in content_lower) or \
                   ('connected' in content_lower and 'checking' in content_lower) or \
                   ('connection' in content_lower and 'still' in content_lower and 'checking' in content_lower):
                    is_connection_message = True
            
            # Skip connection-related assistant messages
            if is_connection_message:
                continue
        
        filtered.append(msg)
    
    return filtered

def get_ai_response(user_message, conversation_history, user_gender="other", bot_name="Virtual Partner"):
    """Get response from Gemini API with gender-aware context"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Filter out old connection-related messages
        filtered_history = filter_connection_messages(conversation_history)
        
        # Get gender-aware system prompt
        system_prompt = get_system_prompt(user_gender, bot_name)
        
        # Build conversation context
        context = system_prompt + "\n\n"
        
        # Add last 15 messages for context (increased for better memory)
        for msg in filtered_history[-15:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        context += f"User: {user_message}\nAssistant:"
        
        print(f"\n🤖 Generating AI response for: {user_message[:50]}...")
        print(f"👤 User Gender: {user_gender}, 🤖 Bot Name: {bot_name}")
        
        response = model.generate_content(
            context,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=500
            )
        )
        
        print(f"✅ AI Response generated successfully")
        return response.text
    
    except Exception as e:
        import traceback
        error_msg = f"AI Error: {e}\n{traceback.format_exc()}"
        print(error_msg)
        
        # Check for rate limiting
        if "429" in str(e) or "Resource exhausted" in str(e):
            return f"I'm taking a short breather right now - too many requests! 😅 Please wait a moment and try again, {bot_name} will be ready to chat soon! ✨"
        
        return f"I'm having a small technical hiccup. Can you try sending that again? 💕"


# Memory Storage Functions (Fallback)
def memory_find_user(username):
    """Find user in memory storage"""
    for user_id, user in MEMORY_USERS.items():
        if user['username'] == username:
            return {**user, 'id': user_id}
    return None

def memory_create_user(username, password, gender="other", bot_name="Virtual Partner"):
    """Create user in memory storage"""
    import uuid
    user_id = str(uuid.uuid4())
    MEMORY_USERS[user_id] = {
        'username': username,
        'password': password,
        'gender': gender,
        'bot_name': bot_name,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    return user_id

def memory_get_chat(user_id):
    """Get chat from memory storage"""
    return MEMORY_CHATS.get(user_id, {'messages': []})

def memory_save_chat(user_id, messages):
    """Save chat to memory storage"""
    MEMORY_CHATS[user_id] = {
        'messages': messages,
        'updated_at': datetime.now(timezone.utc).isoformat()
    }


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    gender = data.get('gender', 'other')
    bot_name = data.get('bot_name', 'Virtual Partner')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    if gender not in ['male', 'female', 'other']:
        gender = 'other'
    
    if not bot_name or not bot_name.strip():
        bot_name = 'Virtual Partner'
    
    try:
        if USE_SUPABASE:
            # Check if user exists
            result = supabase.table('users').select('*').eq('username', username).execute()
            if result.data:
                return jsonify({"error": "Username already exists"}), 400
            
            # Create new user
            user_data = {
                "username": username,
                "password": generate_password_hash(password),
                "gender": gender,
                "bot_name": bot_name.strip(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            result = supabase.table('users').insert(user_data).execute()
            user_id = str(result.data[0]['id'])
        else:
            # Memory storage
            if memory_find_user(username):
                return jsonify({"error": "Username already exists"}), 400
            
            user_id = memory_create_user(
                username, 
                generate_password_hash(password),
                gender,
                bot_name.strip()
            )
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "username": username,
                "gender": gender,
                "bot_name": bot_name.strip()
            }
        }), 201
    
    except Exception as e:
        print(f"Registration Error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    try:
        if USE_SUPABASE:
            result = supabase.table('users').select('*').eq('username', username).execute()
            if not result.data or not check_password_hash(result.data[0]['password'], password):
                return jsonify({"error": "Invalid credentials"}), 401
            user_data = result.data[0]
            user_id = str(user_data['id'])
            gender = user_data.get('gender', 'other')
            bot_name = user_data.get('bot_name', 'Virtual Partner')
        else:
            user = memory_find_user(username)
            if not user or not check_password_hash(user['password'], password):
                return jsonify({"error": "Invalid credentials"}), 401
            user_id = user['id']
            gender = user.get('gender', 'other')
            bot_name = user.get('bot_name', 'Virtual Partner')
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user_id,
                "username": username,
                "gender": gender,
                "bot_name": bot_name
            }
        }), 200
    
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"error": "Login failed"}), 500


@app.route('/api/chat/message', methods=['POST'])
def send_message():
    """Send a message and get AI response"""
    data = request.json
    user_id = data.get('userId')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({"error": "User ID and message required"}), 400
    
    try:
        # Get user info for gender and bot_name
        if USE_SUPABASE:
            user_result = supabase.table('users').select('*').eq('id', user_id).execute()
            if user_result.data:
                user_gender = user_result.data[0].get('gender', 'other')
                bot_name = user_result.data[0].get('bot_name', 'Virtual Partner')
            else:
                user_gender = 'other'
                bot_name = 'Virtual Partner'
        else:
            user = MEMORY_USERS.get(user_id)
            if user:
                user_gender = user.get('gender', 'other')
                bot_name = user.get('bot_name', 'Virtual Partner')
            else:
                user_gender = 'other'
                bot_name = 'Virtual Partner'
        
        # Get conversation history
        if USE_SUPABASE:
            result = supabase.table('chats').select('*').eq('user_id', user_id).execute()
            if result.data:
                conversation_history = result.data[0].get('messages', [])
                chat_id = result.data[0]['id']
            else:
                conversation_history = []
                chat_id = None
        else:
            user_chat = memory_get_chat(user_id)
            conversation_history = user_chat.get('messages', [])
        
        # Add user message
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        conversation_history.append(user_message)
        
        # Get AI response with user context
        ai_response = get_ai_response(message, conversation_history, user_gender, bot_name)
        
        # Add AI response
        assistant_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        conversation_history.append(assistant_message)
        
        # Save to database
        if USE_SUPABASE:
            chat_data = {
                "user_id": user_id,
                "messages": conversation_history,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if chat_id:
                supabase.table('chats').update(chat_data).eq('id', chat_id).execute()
            else:
                supabase.table('chats').insert(chat_data).execute()
        else:
            memory_save_chat(user_id, conversation_history)
        
        return jsonify({
            "response": ai_response,
            "timestamp": assistant_message['timestamp']
        }), 200
    
    except Exception as e:
        print(f"Message Error: {e}")
        return jsonify({"error": "Failed to process message"}), 500


@app.route('/api/chat/history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    """Get user's chat history"""
    try:
        if USE_SUPABASE:
            result = supabase.table('chats').select('*').eq('user_id', user_id).execute()
            messages = result.data[0].get('messages', []) if result.data else []
        else:
            user_chat = memory_get_chat(user_id)
            messages = user_chat.get('messages', [])
        
        return jsonify({"messages": messages}), 200
    
    except Exception as e:
        print(f"History Error: {e}")
        return jsonify({"error": "Failed to load chat history"}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Server is running",
        "database": "Supabase" if USE_SUPABASE else "In-Memory"
    }), 200


# Frontend routes (must be last to avoid catching API routes)
@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Virtual Partner Server Starting...")
    print("="*60)
    port = int(os.environ.get('PORT', 5000))
    print(f"📡 Server: http://localhost:{port}")
    print(f"💾 Database: {'Supabase (Cloud)' if USE_SUPABASE else 'In-Memory (temporary)'}")
    print(f"🤖 AI Model: Google Gemini")
    print("="*60 + "\n")
    
    if not USE_SUPABASE:
        print("⚠️  WARNING: Using in-memory storage!")
        print("    All data will be lost when server restarts.")
        print("    Add Supabase credentials to .env to persist data.\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)