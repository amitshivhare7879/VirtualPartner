import re
from collections import Counter
import emoji

# --- Configuration based on identified chat data ---
KEY_PATTERNS = {
    'A': {
        'gender': 'Male', 
        'role': 'Guider/Caretaker',
        'keywords': ['khana kha', 'beta', 'dawai', 'kahan ho'],
        'insults': ['Chudial', 'Champa'],
        'pet_names': ['Accha baacha', 'My love']
    },
    'B': {
        'gender': 'Female', 
        'role': 'Emotive/Contrarian',
        'keywords': ['sar dukhra', 'nind ni aari', 'kya karu', 'aaj ni'],
        'insults': ['gadhi', 'kutaa'], # Embraced by Ritu
        'pet_names': ['baby', 'shona', 'jaanu']
    }
}

class DualPersonalityModel:
    def __init__(self, key_patterns=KEY_PATTERNS):
        self.profiles = {'A': {}, 'B': {}}
        self.key_patterns = key_patterns

    def extract_patterns(self, parsed_messages: list):
        """
        Pattern Recognition: Analyzes parsed messages to build personality profiles.
        """
        all_messages = {'A': [], 'B': []}
        all_emojis = {'A': [], 'B': []}
        
        for msg in parsed_messages:
            sender_id = msg['sender']
            content = msg['content'].lower()
            all_messages[sender_id].append(content)
            
            # Extract Emojis
            for char in content:
                if emoji.is_emoji(char):
                    all_emojis[sender_id].append(char)

        for person_id in ['A', 'B']:
            messages = all_messages[person_id]
            
            # 1. Language Style (Word Frequencies)
            words = re.findall(r'\b\w+\b', ' '.join(messages))
            most_common_words = Counter(words).most_common(50)
            
            # 2. Emoji/Emoticon Usage
            top_emojis = Counter(all_emojis[person_id]).most_common(10)
            
            # 3. Message Length (Approximate)
            avg_len = sum(len(m) for m in messages) / len(messages) if messages else 0
            
            self.profiles[person_id] = {
                'gender': self.key_patterns[person_id]['gender'],
                'role': self.key_patterns[person_id]['role'],
                'avg_msg_length': round(avg_len),
                'top_words': most_common_words,
                'top_emojis': top_emojis,
                'slang_list': self.key_patterns[person_id]['keywords'] + self.key_patterns[person_id]['insults'],
                'message_count': len(messages)
            }
        
        return self.profiles

    # --- Adaptive Learning & Context Memory Placeholder ---
    def generate_response(self, user_id, target_partner_id, conversation_history, user_input):
        """
        Generates a response using the learned personality profile and context memory.
        
        This is where the LLM integration logic would go (e.g., OpenAI, Gemini API call).
        The prompt is dynamically built to include the profile:
        
        PROMPT = f"You are a chatbot named {self.profiles[target_partner_id]['role']} with the personality of 
        Person {target_partner_id}. You use slang like: {self.profiles[target_partner_id]['slang_list'][:3]} 
        and frequently use these emojis: {self.profiles[target_partner_id]['top_emojis'][:3]}. 
        The current conversation history is: {conversation_history}. Respond to: {user_input}"
        """
        profile = self.profiles.get(target_partner_id, {})
        if not profile:
            return "Error: Personality profile not yet trained."

        # Simple Rule-Based Response (to illustrate core features without a full LLM)
        if 'khana' in user_input.lower() and target_partner_id == 'A':
            return "Khana kha liya beta? Davai li kya? 💜" # Amit's Caretaker style

        if 'kya hua' in user_input.lower() and target_partner_id == 'B':
            return f"Sar dukhra yaar. Tu bas {profile['top_emojis'][0][0]} bol deta hai. 🙄" # Ritu's Emotive style
            
        return f"Hello, I am the AI trained on Person {target_partner_id}'s style. My average message length is {profile['avg_msg_length']} characters. I need an LLM to generate a real response!"