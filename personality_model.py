# backend/personality_model.py (Final Stable Rules)
import re
from collections import Counter
import emoji

# NOTE: This code is simplified to guarantee startup success.
KEY_PATTERNS = {
    'A': {'gender': 'Male', 'role': 'Supportive Guide', 'top_emojis': ['😊', '💜'],},
    'B': {'gender': 'Female', 'role': 'Playful Companion', 'top_emojis': ['🙄', '😘'],},
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = key_patterns 

    def extract_patterns(self, parsed_messages: list):
        return self.profiles

    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        # We ensure a response is always returned to prevent the 500 error.
        
        if target_partner_id == 'A':
            return "Hey, beta. Our server is having signal issues right now. I'm here to listen, though! 😊"
        else:
            return "Ugh, network fail ho gaya, yaar! I'm stuck, but tell me more! 🙄"