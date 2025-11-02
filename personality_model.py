# backend/personality_model.py (FINAL, ROBUST VERSION)

import os
from google import genai
from google.genai import types

# --- Configuration: Base Personality Definitions (Abstracted) ---
KEY_PATTERNS = {
    # Partner A (Male Archetype)
    'A': {
        'gender': 'Male', 
        'role': 'Supportive Guide',
        'style': "You are the male partner. Your tone is often gentle, caring, and protective. Use Hindi/English (Hinglish) slang like 'beta', 'dawai', 'accha baacha'. Be empathetic. DO NOT use generic AI language.",
    },
    # Partner B (Female Archetype)
    'B': {
        'gender': 'Female', 
        'role': 'Playful Companion',
        'style': "You use expressive emojis and extensive Hinglish slang (like 'yaar', 'hn', 'okkk'), and a playful, emotive tone. Always ask follow-up questions. DO NOT use generic AI language.",
    }
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 
        self.client = None # Client starts as None

        # DELAYED, CONDITIONAL CLIENT INITIALIZATION
        if os.environ.get("GEMINI_API_KEY"):
            try:
                # Client is only created if the key exists in the environment
                self.client = genai.Client()
            except Exception as e:
                # Log any failure during creation but let the server start
                print(f"Gemini Client creation failed at startup: {e}")
        else:
            print("WARNING: GEMINI_API_KEY environment variable is missing. AI responses will be disabled.")


    def extract_patterns(self, parsed_messages: list):
        """Placeholder for future advanced pattern extraction."""
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        """
        Generates an LLM response or a deterministic fallback response.
        """
        # --- Check 1: Fallback if Client is Missing ---
        if self.client is None:
            # Fallback (deterministic response based on partner)
            if target_partner_id == 'A':
                return "Our connection is down right now, beta. Try again later. 😊"
            else:
                return "Ugh, my signal is totally gone, yaar! 😭"

        # --- Check 2: LLM Call ---
        profile = self.profiles.get(target_partner_id, {})
        personality_style = profile.get('style', 'A friendly and helpful chatbot.')
        
        system_prompt = f"You are a virtual partner. Your persona is: {personality_style}."
        
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
                    temperature=0.8,
                ),
            )
            return response.text
        
        except Exception as e:
            # Fallback for API execution errors (e.g., rate limit)
            print(f"AI Execution Error: {e}")
            return "Oops! I hit a limit. Can you rephrase that? I still want to talk to you!"