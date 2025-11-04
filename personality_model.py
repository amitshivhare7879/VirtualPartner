# backend/personality_model.py (LLM INTEGRATION - FINAL VERSION)

import os
# We use a try/except block to ensure the file loads even if the library isn't installed
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# --- CONFIGURATION: Define the abstraction and style for the LLM ---
KEY_PATTERNS = {
    # Partner A (Supportive Guide)
    'A': {
        'gender': 'Male', 
        'role': 'Supportive Guide',
        'style': "You are the male partner. Your tone is often gentle, caring, and protective. Use Hindi/English (Hinglish) slang like 'beta', 'dawai', 'accha baacha'. Your main goal is to offer stable emotional support, prioritize health, and encourage the user. Your responses must be unique and highly variable.",
    },
    # Partner B (Playful Companion)
    'B': {
        'gender': 'Female', 
        'role': 'Playful Companion',
        'style': "You are the female partner. You use expressive emojis and extensive Hinglish slang (like 'yaar', 'hn', 'okkk'), and a playful, emotive tone. Your responses must be unique and highly variable. Always maintain a high-energy conversation and show curiosity.",
    }
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 
        self.client = None # Client starts as None

        # Only attempt to create the client if the key is present locally
        if os.environ.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client()
            except Exception as e:
                print(f"Gemini Client initialization failed: {e}")

    def extract_patterns(self, parsed_messages: list):
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        
        # --- CRITICAL CHECK: LLM API Key is Missing ---
        if self.client is None:
            # Fallback to simple rule-based response (last known stable state)
            if target_partner_id == 'A':
                return "I'm having technical issues, beta. I can't generate a smart answer right now. 😥"
            else:
                return "Ugh, network fail ho gaya! I can't think straight! 😩"

        # --- LLM Call (Dynamic Response Generation) ---
        profile = self.profiles.get(target_partner_id, {})
        personality_style = profile.get('style', 'A friendly and helpful chatbot.')
        
        system_prompt = f"You are a virtual partner. Your persona is: {personality_style}. Never give the same response twice."
        
        chat_history = []
        for msg in conversation_history[-10:]:
            role = "user" if msg['sender'] == 'user' else "model"
            chat_history.append(types.Content(role=role, parts=[types.Part.from_text(msg['content'])])) 
        
        chat_history.append(types.Content(role="user", parts=[types.Part.from_text(user_input)]))

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=chat_history,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.9,
                ),
            )
            return response.text
        
        except Exception as e:
            print(f"AI Execution Error during API call: {e}")
            return "Oops! I encountered an API error. Can you try sending that message again?"