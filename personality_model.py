# backend/personality_model.py (FINAL DYNAMIC FIX)

import os
# Import LLM components conditionally (Ensures file loads even if library is missing)
try:
    from google import genai
    from google.genai import types
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    class MockClient: # Mock client to prevent NameErrors
        def __init__(self): pass
        def models(self): return self
        def generate_content(self, model, contents, config): return type('', (object,), {'text': 'LLM ERROR: API key or dependency missing.'})()

# --- CONFIGURATION: Personalities remain the same ---
KEY_PATTERNS = {
    'A': {'gender': 'Male', 'role': 'Supportive Guide', 'style': "Your tone is empathetic, protective, and uses 'beta' and 'accha baacha' slang. Your responses must be unique and highly variable."},
    'B': {'gender': 'Female', 'role': 'Playful Companion', 'style': "Your tone is playful, uses expressive emojis and Hinglish slang like 'yaar' and 'okkk'. Always maintain high energy and curiosity."},
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 
        self._client = None # Client is initialized lazily

    def _get_llm_client(self):
        """Initializes the LLM client only when the API key is verified."""
        if self._client is None and LLM_AVAILABLE:
            if os.environ.get("GEMINI_API_KEY"):
                try:
                    self._client = genai.Client()
                except Exception as e:
                    print(f"LLM Client initialization failed: {e}")
                    return None
            else:
                # If key is missing, use MockClient to prevent crash
                return MockClient()
        return self._client if self._client else MockClient()

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        
        client = self._get_llm_client()
        
        # --- Fallback if Client Fails (Will only happen if API key is missing) ---
        if isinstance(client, MockClient):
            if "LLM ERROR" in client.models().generate_content(None,None,None).text:
                if target_partner_id == 'A':
                    return "Our intelligent service is offline right now. I can only manage simple replies. (Error: Missing API Key) 😥"
                else:
                    return "Ugh, my brain is fried! I can't think of a unique answer yet! (Error: Missing API Key) 😩"

        # --- LLM Call (Dynamic Response Generation) ---
        profile = self.profiles.get(target_partner_id, {})
        system_prompt = f"You are a virtual partner. Your persona is: {profile['style']}. Never give the same response twice."
        
        chat_history = []
        for msg in conversation_history[-10:]:
            role = "user" if msg['sender'] == 'user' else "model"
            chat_history.append(types.Content(role=role, parts=[types.Part.from_text(msg['content'])])) 
        chat_history.append(types.Content(role="user", parts=[types.Part.from_text(user_input)]))

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=chat_history,
                config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.9),
            )
            return response.text
        
        except Exception as e:
            return "I hit a temporary limit. Can you rephrase that? I want to hear it!"