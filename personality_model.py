# backend/personality_model.py (FINAL STABLE GENERIC LLM CORE)

import os
import requests
import json

# --- CONFIGURATION: Single Generic Persona for Reliability ---
KEY_PATTERNS = {
    # We maintain 'A' and 'B' for gender mapping compatibility, but the style is unified.
    'A': {
        'gender': 'Male', 
        'role': 'Generic Chatbot',
        'style': "You are a helpful and friendly conversational assistant. Your goal is to engage the user, remember previous messages, and provide thoughtful, unique responses. Do not use slang or specific character traits.",
    },
    'B': {
        'gender': 'Female', 
        'role': 'Generic Chatbot',
        'style': "You are a helpful and friendly conversational assistant. Your goal is to engage the user, remember previous messages, and provide thoughtful, unique responses. Do not use slang or specific character traits.",
    }
}

# CRITICAL: This placeholder URL must be replaced with a live LLM endpoint
LLM_ENDPOINT_URL = "https://YOUR-STABLE-LLM-API-ENDPOINT-HERE" 

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns
        self.api_key = os.environ.get("GEMINI_API_KEY") 

    def extract_patterns(self, parsed_messages: list):
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        
        # --- Authentication Check ---
        if not self.api_key:
            return "Server Error: LLM API Key is missing from Render Environment Variables. Cannot generate dynamic response."

        # 1. Build the LLM Prompt with Context Memory
        profile = self.profiles.get(target_partner_id, {})
        system_prompt = f"System: {profile['style']}. Use the provided history to maintain context."
        
        # Prepare history for LLM (Focusing on contents)
        context_messages = [f"{msg['sender']}: {msg['content']}" for msg in conversation_history[-5:]]
        full_prompt = f"{system_prompt}\n---History---\n{'\n'.join(context_messages)}\n---User: {user_input}"

        # 2. Build the Payload for the External API (Adjust based on your final LLM choice)
        payload = {
            "prompt": full_prompt,
            "max_tokens": 150
        }

        # 3. CRITICAL: Stable API Call with Requests
        try:
            response = requests.post(
                LLM_ENDPOINT_URL, 
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=30 
            )
            response.raise_for_status() # Raise exception for 4xx or 5xx status codes

            # Assuming the external API returns the text in a predictable field
            # You will need to inspect the response structure and adjust the line below
            # For stability, we assume it returns { "text": "..." }
            return response.json().get('text', 'I hit a technical snag, yaar. Try again!')

        except requests.exceptions.RequestException as e:
            print(f"External API Error: {e}")
            return "I'm having technical difficulty connecting to my brain right now. Try again in a moment!"