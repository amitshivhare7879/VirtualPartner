# backend/parser.py (ABSTRACTED)

import re
from datetime import datetime

# --- Configuration for Sender Mapping (Abstracted from original chats) ---
# NOTE: These names must be modified manually if the user uploads files with different sender names.
SENDER_MALE_VARIANTS = ["Amit Shivhare", "AMIT Shivhare", "Amit Shivhare😍"] # Based on original data
SENDER_FEMALE_VARIANTS = ["Rittuu", "CHEATER", "Ritu Gadhi", "Rittuu Baacha"] # Based on original data

def parse_chat(file_content: str) -> list:
    """
    Parses WhatsApp chat export content into a list of message dictionaries.
    Assigns normalized IDs 'A' (Male) or 'B' (Female) based on variants.
    """
    messages = []
    # Combined regex pattern to capture Date, Time, Sender Name, and Message Content
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
            
            sender = sender_full.strip()
            person_id = None
            
            # --- Determine normalized ID based on observed variants ---
            if any(name in sender for name in SENDER_MALE_VARIANTS):
                person_id = 'A' # Male Archetype
            elif any(name in sender for name in SENDER_FEMALE_VARIANTS):
                person_id = 'B' # Female Archetype
            else:
                continue # Skip if sender cannot be identified
            
            messages.append({
                'timestamp_raw': f"{date_str} {time_str}".strip(),
                'sender': person_id,
                'content': content.strip(),
            })
            
    return messages