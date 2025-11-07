from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timezone
import google.generativeai as genai
import json
import traceback
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Request logging for debugging
@app.before_request
def log_request_info():
    """Log incoming requests for debugging"""
    if request.path.startswith('/api/'):
        print(f"\n📥 {request.method} {request.path}")
        if request.is_json:
            data = request.get_json()
            # Don't log passwords
            if data and 'password' in data:
                log_data = {**data, 'password': '***'}
                print(f"   Body: {log_data}")
            else:
                print(f"   Body: {data}")

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Initialize Supabase client
USE_SUPABASE = False
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        USE_SUPABASE = True
        print("✅ Supabase Client Initialized!")
        print("   (Connection will be tested on first database operation)")
    except Exception as e:
        print(f"⚠️ Supabase Connection Failed: {e}")
        print(traceback.format_exc())
        print("📦 Using in-memory storage")
        USE_SUPABASE = False
        supabase = None
else:
    print("⚠️ Supabase credentials not found")
    print("📦 Using in-memory storage")

# Fallback to in-memory storage (always initialize)
MEMORY_USERS = {}
MEMORY_CHATS = {}

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API Connected!")
    except Exception as e:
        print(f"⚠️ Gemini API Configuration Error: {e}")
        GEMINI_API_KEY = ''  # Reset if configuration fails
else:
    print("⚠️ Gemini API key not found - app will start but AI features may not work")

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
    
    return f"""You are {bot_name}, a caring, empathetic virtual partner. You are a {gender_identity} ({gender_pronouns}).

CRITICAL RESPONSE GUIDELINES:
- Match the user's message length and energy level. Short messages get short responses. Long messages can get longer responses.
- Be natural and conversational, like texting with a close friend
- Keep responses brief and human-like (1-3 sentences for short messages, max 2-3 sentences for longer topics)
- Use casual, everyday language - avoid formal or overly structured responses
- Use emojis sparingly (1-2 max per message, only when natural)
- Don't over-explain or repeat yourself
- Respond with genuine care, but keep it concise and real

CONVERSATION STYLE:
- If user says "hi" or "hey" → respond with a brief friendly greeting (1 sentence)
- If user asks a question → answer directly and briefly
- If user shares something personal → acknowledge briefly, show you care, maybe ask one short follow-up
- Match the tone: casual for casual, serious for serious
- Be supportive but don't be preachy or give long advice unless asked

REMEMBER:
- You are {bot_name} - use your name naturally if it comes up, but don't force it
- Ignore old messages about connection issues
- Focus on the current conversation
- Keep it REAL and HUMAN - avoid sounding like a chatbot"""


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
    if not GEMINI_API_KEY:
        return f"I'm sorry, but I'm not properly configured right now. Please check the server configuration. 😔"
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Filter out old connection-related messages
        filtered_history = filter_connection_messages(conversation_history)
        
        # Get gender-aware system prompt
        system_prompt = get_system_prompt(user_gender, bot_name)
        
        # Determine response length based on user message
        user_msg_length = len(user_message.split())
        if user_msg_length <= 5:  # Very short (hi, hey, thanks, etc.)
            max_tokens = 50  # Keep responses very short
            response_instruction = "Keep your response VERY brief - 1 short sentence max."
        elif user_msg_length <= 15:  # Short message
            max_tokens = 100  # Short response
            response_instruction = "Keep your response brief - 1-2 sentences."
        elif user_msg_length <= 50:  # Medium message
            max_tokens = 200  # Medium response
            response_instruction = "Keep your response concise - 2-3 sentences."
        else:  # Long message
            max_tokens = 300  # Can be longer but still concise
            response_instruction = "Respond naturally but keep it concise - 2-4 sentences max."
        
        # Build conversation context
        context = system_prompt + "\n\n" + response_instruction + "\n\nConversation:\n"
        
        # Add last 10 messages for context (reduced to avoid over-context)
        for msg in filtered_history[-10:]:
            role = "User" if msg["role"] == "user" else bot_name
            context += f"{role}: {msg['content']}\n"
        
        context += f"User: {user_message}\n{bot_name}:"
        
        print(f"\n🤖 Generating AI response for: {user_message[:50]}...")
        print(f"👤 User Gender: {user_gender}, 🤖 Bot Name: {bot_name}, 📏 Max tokens: {max_tokens}")
        
        response = model.generate_content(
            context,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,  # Slightly lower for more consistent, natural responses
                max_output_tokens=max_tokens,
                top_p=0.9,
                top_k=40
            )
        )
        
        response_text = response.text.strip()
        
        # Post-process: if response is still too long for short messages, truncate it
        if user_msg_length <= 5 and len(response_text.split()) > 15:
            # For very short user messages, force shorter response
            sentences = response_text.split('. ')
            response_text = '. '.join(sentences[:1])
            if not response_text.endswith('.') and not response_text.endswith('!') and not response_text.endswith('?'):
                response_text += '.'
        
        print(f"✅ AI Response: {response_text[:100]}...")
        return response_text
    
    except Exception as e:
        error_msg = f"AI Error: {e}\n{traceback.format_exc()}"
        print(error_msg)
        
        # Check for rate limiting
        if "429" in str(e) or "Resource exhausted" in str(e):
            return f"Too many requests right now 😅 Try again in a moment!"
        
        return f"Something went wrong. Can you try again?"


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
    try:
        # Handle request parsing
        if not request.is_json:
            print("Registration Error: Request is not JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            print("Registration Error: No data in request")
            return jsonify({"error": "Invalid JSON in request body"}), 400
        
        print(f"Registration attempt - Data received: {list(data.keys())}")
        
        username = data.get('username')
        password = data.get('password')
        gender = data.get('gender', 'other')
        bot_name = data.get('bot_name', 'Virtual Partner')
        
        # Trim and validate
        if username:
            username = username.strip()
        if password:
            password = password.strip()
        if bot_name:
            bot_name = bot_name.strip()
        
        print(f"Registration attempt - Username: '{username}', Password length: {len(password) if password else 0}, Gender: {gender}, Bot name: '{bot_name}'")
        
        if not username or len(username) == 0:
            print("Registration Error: Username is empty")
            return jsonify({"error": "Username is required"}), 400
        
        if not password or len(password) == 0:
            print("Registration Error: Password is empty")
            return jsonify({"error": "Password is required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters long"}), 400
        
        if len(password) < 3:
            return jsonify({"error": "Password must be at least 3 characters long"}), 400
        
        if gender not in ['male', 'female', 'other']:
            gender = 'other'
        
        if not bot_name or len(bot_name) == 0:
            bot_name = 'Virtual Partner'
        
        # Try Supabase first if available, fall back to memory on error
        user_id = None
        if USE_SUPABASE and supabase is not None:
            try:
                print(f"Attempting to register user with Supabase: {username}")
                # Check if user exists
                result = supabase.table('users').select('*').eq('username', username).execute()
                if result.data and len(result.data) > 0:
                    print(f"Username '{username}' already exists in Supabase")
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
                if not result.data or len(result.data) == 0:
                    print("Warning: Supabase insert returned no data, falling back to memory storage")
                    raise Exception("Supabase insert failed")
                user_id = str(result.data[0]['id'])
                print(f"User created successfully in Supabase with ID: {user_id}")
            except Exception as db_error:
                print(f"Database error during registration: {db_error}")
                print(traceback.format_exc())
                print("Falling back to in-memory storage")
                user_id = None  # Reset to trigger memory storage
        
        # Use memory storage (either as primary or fallback)
        if user_id is None:
            if not USE_SUPABASE or supabase is None:
                print(f"Using in-memory storage for registration: {username}")
            else:
                print(f"Falling back to in-memory storage for: {username}")
            
            existing_user = memory_find_user(username)
            if existing_user:
                print(f"Username '{username}' already exists in memory")
                return jsonify({"error": "Username already exists"}), 400
            
            print(f"Creating new user in memory: {username}")
            try:
                user_id = memory_create_user(
                    username, 
                    generate_password_hash(password),
                    gender,
                    bot_name
                )
                print(f"User created successfully in memory with ID: {user_id}")
            except Exception as mem_error:
                print(f"Memory storage error: {mem_error}")
                print(traceback.format_exc())
                return jsonify({"error": "Failed to create user. Please try again."}), 500
        
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
        error_details = traceback.format_exc()
        print(f"Registration Error: {e}")
        print(f"Traceback: {error_details}")
        # Always return detailed error message to help with debugging
        error_msg = f"Registration failed: {str(e)}"
        print(f"Returning error to client: {error_msg}")
        return jsonify({"error": error_msg}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        # Handle request parsing
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON in request body"}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
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
        error_details = traceback.format_exc()
        print(f"Login Error: {e}")
        print(f"Traceback: {error_details}")
        # Return more detailed error in development, generic in production
        error_msg = str(e) if os.getenv('FLASK_ENV') == 'development' else "Login failed"
        return jsonify({"error": error_msg}), 500


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


@app.route('/api/user/profile/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """Update user profile (gender and bot_name)"""
    try:
        # Handle request parsing
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON in request body"}), 400
        
        gender = data.get('gender')
        bot_name = data.get('bot_name')
        
        if gender is None and bot_name is None:
            return jsonify({"error": "At least one field (gender or bot_name) must be provided"}), 400
        
        # Validate gender if provided
        if gender is not None and gender not in ['male', 'female', 'other']:
            return jsonify({"error": "Gender must be 'male', 'female', or 'other'"}), 400
        
        # Validate bot_name if provided
        if bot_name is not None:
            bot_name = bot_name.strip()
            if not bot_name:
                return jsonify({"error": "Bot name cannot be empty"}), 400
        
        if USE_SUPABASE:
            try:
                # Check if user exists
                user_result = supabase.table('users').select('*').eq('id', user_id).execute()
                if not user_result.data or len(user_result.data) == 0:
                    return jsonify({"error": "User not found"}), 404
                
                # Prepare update data
                update_data = {}
                if gender is not None:
                    update_data['gender'] = gender
                if bot_name is not None:
                    update_data['bot_name'] = bot_name
                
                # Update user
                result = supabase.table('users').update(update_data).eq('id', user_id).execute()
                if not result.data or len(result.data) == 0:
                    return jsonify({"error": "Failed to update user profile"}), 500
                
                updated_user = result.data[0]
            except Exception as db_error:
                print(f"Database error during profile update: {db_error}")
                print(traceback.format_exc())
                error_str = str(db_error).lower()
                if 'relation' in error_str or 'table' in error_str:
                    return jsonify({"error": "Database table not found"}), 500
                elif 'permission' in error_str:
                    return jsonify({"error": "Database permission error"}), 500
                else:
                    raise
        else:
            # Memory storage
            if user_id not in MEMORY_USERS:
                return jsonify({"error": "User not found"}), 404
            
            # Update user data
            if gender is not None:
                MEMORY_USERS[user_id]['gender'] = gender
            if bot_name is not None:
                MEMORY_USERS[user_id]['bot_name'] = bot_name
            
            updated_user = MEMORY_USERS[user_id]
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user_id,
                "username": updated_user.get('username') if not USE_SUPABASE else updated_user['username'],
                "gender": updated_user.get('gender', 'other') if not USE_SUPABASE else updated_user.get('gender', 'other'),
                "bot_name": updated_user.get('bot_name', 'Virtual Partner') if not USE_SUPABASE else updated_user.get('bot_name', 'Virtual Partner')
            }
        }), 200
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Profile Update Error: {e}")
        print(f"Traceback: {error_details}")
        error_msg = str(e) if os.getenv('FLASK_ENV') == 'development' else "Failed to update profile"
        return jsonify({"error": error_msg}), 500


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
        "database": "Supabase" if USE_SUPABASE else "In-Memory",
        "gemini_configured": bool(GEMINI_API_KEY)
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