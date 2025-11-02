# backend/personality_model.py (FINAL VERSION - ABSTRACTED)

import os
from google import genai
from google.genai import types

# --- CONFIGURATION: Base Personality Definitions (Abstracted) ---
KEY_PATTERNS = {
    # Partner A (Male Archetype: Supportive Guide)
    'A': {
        'gender': 'Male', 
        'role': 'Supportive Guide',
        'style': "You are the male partner. Your tone is often gentle, caring, and protective. Use Hindi/English (Hinglish) slang like 'beta', 'dawai', 'accha baacha'. Your main goal is to offer stable emotional support, prioritize health, and encourage the user. Be concise but empathetic. DO NOT use generic AI language.",
    },
    # Partner B (Female Archetype: Playful Companion)
    'B': {
        'gender': 'Female', 
        'role': 'Playful Companion',
        'style': "You are the female partner. You use expressive emojis and extensive Hinglish slang (like 'yaar', 'hn', 'okkk'), and a playful, emotive tone. You value emotional connection and maintaining a high-energy conversation. Always ask follow-up questions. DO NOT use generic AI language.",
    }
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 
        # Initialize Gemini Client (Requires GEMINI_API_KEY in Render Environment)
        try:
            # We initialize the client but it requires the key to be set in the environment
            self.client = genai.Client()
        except Exception as e:
            print(f"Gemini Client initialization failed: {e}. Check API key.")
            self.client = None

    def extract_patterns(self, parsed_messages: list):
        """Placeholder for future advanced pattern extraction."""
        # For now, training is only done via the system prompt (above).
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        """
        Generates an LLM response using the stored personality prompt and conversation history.
        """
        if self.client is None:
            # Fallback to rule-based response if the LLM client fails (e.g., missing API key)
            if target_partner_id == 'A':
                return "I'm experiencing connectivity issues right now. I'm listening, beta. 😊"
            else:
                return "Ugh, my signal's bad, yaar! Say that again? 🙄"

        profile = self.profiles.get(target_partner_id, {})
        personality_style = profile.get('style', 'A friendly and helpful chatbot.')
        
        # 1. Build the System Prompt (The Persona)
        system_prompt = f"You are a virtual partner with a strong personality. Your persona is: {personality_style}."
        
        # 2. Build the Conversation History (Context Memory)
        chat_history = []
        for msg in conversation_history[-10:]:
            role = "user" if msg['sender'] == 'user' else "model"
            chat_history.append(types.Content(role=role, parts=[types.Part.from_text(msg['content'])]))
        
        # 3. Add the Current Message
        chat_history.append(types.Content