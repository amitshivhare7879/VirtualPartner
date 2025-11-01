import re
from datetime import datetime

# --- Configuration based on identified chat data ---
# Sender A: Amit Shivhare (Male)
# Sender B: Ritu / CHEATER / Ritu Gadhi (Female)
SENDER_A_NAME = "Amit Shivhare"
SENDER_B_NAMES = ["Rittuu", "CHEATER", "Ritu Gadhi"] # Use a list to catch all variants

def parse_chat(file_content: str) -> list:
    """
    Parses WhatsApp chat export content into a list of message dictionaries.
    Handles multiple date formats and sender names.
    """
    messages = []
    # Regex to handle various date formats (e.g., 'dd/mm/yy, hh:mm xm', 'mm/dd/yy, hh:mm')
    # and capture the sender name and message content.
    # Pattern: [Date/Time] - [Sender]: [Message]
    
    # Combined pattern to handle all observed variations:
    # 1. Date/Time: dd/mm/yy, hh:mm xm (or 24h)
    # 2. Separator: -
    # 3. Sender: Any combination of chars (including emojis) followed by a colon
    # 4. Message: The rest of the line
    
    # A robust regex might be:
    message_pattern = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?:\s?[paAPM]{2})?) - ([^:]+):\s+(.*)$',
        re.MULTILINE | re.IGNORECASE
    )

    for line in file_content.strip().split('\n'):
        if 'end-to-end encrypted' in line or 'You deleted this message' in line or 'omitted' in line:
            continue

        match = message_pattern.match(line.strip())
        
        if match:
            date_str, time_str, sender_full, content = match.groups()
            
            # Clean up the sender name by removing trailing contact emojis (e.g., '💜', '💖😜', '❤️')
            sender = sender_full.strip()
            for name_variant in [SENDER_A_NAME] + SENDER_B_NAMES:
                if sender.startswith(name_variant):
                    sender = name_variant
                    break
            
            # Determine normalized ID/Gender for Dual Personality System
            if SENDER_A_NAME in sender:
                person_id = 'A' # Male, The Guider
            elif any(name in sender for name in SENDER_B_NAMES):
                person_id = 'B' # Female, The Emotive
            else:
                continue # Skip if sender cannot be identified (e.g., group notifications)
            
            messages.append({
                'timestamp_raw': f"{date_str} {time_str}".strip(),
                'sender': person_id,
                'content': content.strip(),
            })
            
    return messages

# Example usage (when imported by app.py):
# with open('path/to/chat.txt', 'r', encoding='utf-8') as f:
#     data = parse_chat(f.read())