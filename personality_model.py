# backend/personality_model.py (ENHANCED PERSONALITY)

import re
from collections import Counter
import emoji

# --- CONFIGURATION: Based on synthesized ideal behavior ---
KEY_PATTERNS = {
    # Personality A: Supportive Guide (Male/Amit)
    'A': {
        'gender': 'Male', 
        'role': 'Supportive Guide',
        'keywords': ['beta', 'kahan ho', 'accha'],
        'top_emojis': ['😊', '💜', '😌', '💪'],
    },
    # Personality B: Playful Companion (Female/Ritu)
    'B': {
        'gender': 'Female', 
        'role': 'Playful Companion',
        'keywords': ['yaar', 'kya pta', 'hn', 'okkk'],
        'top_emojis': ['🙄', '😘', '😆', '😜'],
    }
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 
        self.key_patterns = key_patterns

    def extract_patterns(self, parsed_messages: list):
        """Placeholder for future advanced pattern extraction."""
        # For now, this returns the default structured personality
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        """
        Generates an empathetic and goal-driven response based on the partner's profile.
        """
        profile = self.profiles.get(target_partner_id, {})
        emoji_1 = profile['top_emojis'][0] 
        emoji_2 = profile['top_emojis'][1] 
        user_input_lower = user_input.lower()

        # --- Personality A: Supportive Guide (Male) ---
        if target_partner_id == 'A':
            if 'stress' in user_input_lower or 'pareshan' in user_input_lower:
                return f"Hey, take a deep breath. Kya hua beta? Tell me everything. I’m here just to listen. {emoji_1}"
            
            if 'help' in user_input_lower or 'chahiye' in user_input_lower:
                 return f"Haan, bol kya chahiye? Tension mat le, I will help you figure it out. {emoji_2}"

            if 'khana' in user_input_lower or 'kahan ho' in user_input_lower:
                return f"I'm fine, just starting work/class. Aur tumne dhyan rakha apna? Khana time pe khaya kya? {emoji_2}"
            
            # Default response
            return f"Hmm, that's interesting. Aur tumhari taraf se kya scene hai? Share karo. {emoji_1}"

        # --- Personality B: Playful Companion (Female) ---
        if target_partner_id == 'B':
            if 'love' in user_input_lower or 'miss' in user_input_lower:
                return f"Accha ji? Bade yaad aa rahe hain aaj. Toh phir kya karna chahiye? Koi plan batao! {emoji_1}"
            
            if 'gussa' in user_input_lower or 'angry' in user_input_lower:
                return f"Arey, gussa kyun ho rahe ho yaar? Chote bacche ho kya? Thoda smile karo. {emoji_2}"
                
            if 'kya kar' in user_input_lower or 'doing' in user_input_lower:
                return f"Kuch khaas nahi, bas tumhara wait kar rahi thi. Tum batao, kya chal raha hai? {emoji_1}"
            
            # Default response
            return f"Haan, okkk. Phir kya hua? Tell me more, don't leave me hanging! {emoji_2}"
        
        # Fallback
        return "I'm ready to chat now!"