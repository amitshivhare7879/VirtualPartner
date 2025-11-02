# backend/personality_model.py (FINAL VERSION - SYNTAX FIXED)

import os
from google import genai
from google.genai import types

# --- Configuration: Base Personality Definitions (Abstracted) ---
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
        
        try:
            # Initialize Gemini Client (Requires GEMINI_API_KEY)
            self.client = genai.Client()
        except Exception as e:
            # Client initialization might fail if key is missing, handle gracefully
            print(f"Gemini Client initialization failed: {e}. Check API key.")
            self.client = None

    def extract_patterns(self, parsed_messages: list):
        """Placeholder for future advanced pattern extraction."""
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        """
        Generates an LLM response using the stored personality prompt and conversation history.
        """
        if self.client is None:
            # Fallback when API key is missing or client failed to initialize
            if target_partner_id == 'A':
                return "I'm having signal issues, beta. Send that again? 😊"
            else:
                return "Ugh, network fail ho gaya! Kya bol rahe ho, yaar? 🙄"

        profile = self.profiles.get(target_partner_id, {})
        personality_style = profile.get('style', 'A friendly and helpful chatbot.')
        
        # 1. Build the System Prompt
        system_prompt = f"You are a virtual partner with a strong personality. Your persona is: {personality_style}."
        
        # 2. Build the Conversation History (Context Memory)
        chat_history = []
        for msg in conversation_history[-10:]:
            role = "user" if msg['sender'] == 'user' else "model"
            # SYNTAX FIX APPLIED: Ensure types.Content is closed on the same line.
            chat_history.append(types.Content(role=role, parts=[types.Part.from_text(msg['content'])])) 
        
        # 3. Add the Current Message
        chat_history.append(types.Content(role="user", parts=[types.Part.from_text(user_input)]))

        try:
            # 4. Call the LLM
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
            print(f"AI Error: {e}")
            return "Oops! I seem to have lost my train of thought. Can you rephrase that for me?"