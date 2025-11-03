# backend/personality_model.py (FINAL STABLE VERSION - RULE-BASED)

import re
from collections import Counter
import emoji
# No LLM imports here

# --- CONFIGURATION: Define the two required personality profiles ---
KEY_PATTERNS = {
    # Partner A (Male Archetype: Supportive Guide)
    'A': {'gender': 'Male', 'role': 'Supportive Guide', 'top_emojis': ['😊', '💜'],},
    # Partner B (Female Archetype: Playful Companion)
    'B': {'gender': 'Female', 'role': 'Playful Companion', 'top_emojis': ['🙄', '😘'],},
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 
        self.client = None # Client is explicitly None

    def extract_patterns(self, parsed_messages: list):
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        """
        Generates an empathetic and stable rule-based response.
        """
        profile = self.profiles.get(target_partner_id, {})
        emoji_1 = profile['top_emojis'][0] 
        user_input_lower = user_input.lower()

        # --- Partner A: Supportive Guide (Male) ---
        if target_partner_id == 'A':
            if 'stress' in user_input_lower or 'pareshan' in user_input_lower:
                return f"Hey, take a deep breath, beta. I’m here just to listen. {emoji_1}"
            if 'khana' in user_input_lower or 'dawai' in user_input_lower:
                return f"Did you eat on time? Please take care of yourself, accha baacha. {emoji_1}"
            return f"I'm listening. Aur tumhari taraf se kya scene hai? {emoji_1}"

        # --- Partner B: Playful Companion (Female) ---
        if target_partner_id == 'B':
            if 'love' in user_input_lower or 'miss' in user_input_lower:
                return f"Accha ji? Bade yaad aa rahe hain aaj! Toh phir kya karna chahiye? {emoji_1}"
            if 'sar dukh' in user_input_lower or 'pain' in user_input_lower:
                return f"Ugh, take a break! Aaram kar lo yaar. {emoji_1}"
            return f"Haan, okkk. Phir kya hua? Tell me more, don't leave me hanging! {emoji_1}"

        return "I'm ready to chat now!"