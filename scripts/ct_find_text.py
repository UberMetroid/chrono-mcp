#!/usr/bin/env python3
"""
Chrono Trigger ROM - Text Finder
Uses a different approach - look for the encoding directly
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

# Chrono Trigger uses Shift-JIS like encoding for Japanese
# But for US version, it uses a modified encoding
# Let's find the actual text by looking at common strings

# Known: CT uses a 1-byte encoding where:
# 0x20-0x5A = A-Z, 0x61-0x7A = a-z, 0x30-0x39 = 0-9
# Special chars for accents

def find_potential_text(data, min_length=15):
    """Find potential text sequences"""
    results = []
    i = 0
    
    while i < len(data) - min_length:
        # Look for sequences of "text-like" bytes
        seq_start = i
        consecutive = 0
        
        while i < len(data):
            b = data[i]
            
            # Acceptable: A-Z, a-z, 0-9, space, common punctuation
            if (0x40 <= b <= 0x5A or   # A-Z
                0x60 <= b <= 0x7A or    # a-z
                0x30 <= b <= 0x39 or    # 0-9
                b in [0x20, 0x2E, 0x2C, 0x27, 0x22, 0x3A, 0x3F, 0x21]):  # space . , ' " : ? !
                consecutive += 1
            else:
                break
            i += 1
        
        if consecutive >= min_length:
            text = bytes(data[seq_start:i]).decode('ascii', errors='replace')
            results.append((seq_start, text))
        
        i += 1
    
    return results

def find_game_strings():
    data = read_rom()
    
    print("=== CHRONO TRIGGER ROM ANALYSIS ===\n")
    
    # Find ALL printable sequences
    print("--- Looking for readable text ---")
    all_text = find_potential_text(data, min_length=10)
    
    # Filter for game-related words
    keywords = [
        'CHRONO', 'TRIGGER', 'TIME', 'GATE', 'KING', 'QUEEN', 'PRINCE',
        'MAGIC', 'ATTACK', 'DEFEND', 'ITEM', 'EQUIP', 'SAVE', 'LOAD',
        'HP', 'MP', 'LVL', 'EXP', 'GOLD', 'NAME', 'STATUS', 'MENU',
        'START', 'SELECT', 'BATTLE', 'VICTORY', 'DEFEAT', 'RUN',
        'LUCCA', 'MARLE', 'FROG', 'ROBO', 'AYLA', 'MAGUS', 'ZEAL',
        'EARTH', 'FIRE', 'WATER', 'WIND', 'ICE', 'THUNDER', 'LIGHT',
        'DARK', 'SWORD', 'SHIELD', 'HELMET', 'ARMOR', 'ACCESSORY'
    ]
    
    print("\n--- Game-related strings ---")
    found = set()
    for offset, text in all_text:
        upper = text.upper()
        for kw in keywords:
            if kw in upper and len(text) >= len(kw) + 2:
                if (offset, text) not in found:
                    found.add((offset, text))
                    print(f"  {hex(offset)}: {text[:60]}")
    
    # Now let's find the message box format
    print("\n--- Message box patterns ---")
    # Look for the "window" drawing characters
    # In SNES, these are typically at specific offsets
    
    # Look at the very start of the ROM (after header)
    print(f"\nFirst 100 bytes at 0x10000:")
    chunk = data[0x10000:0x10064]
    print(' '.join(f'{b:02X}' for b in chunk))
    
    # Look for text at known locations (from other CT research)
    # The script is typically at around 0x120000 in HiROM
    print("\n--- Examining potential script area (0x120000) ---")
    chunk = data[0x120000:0x120100]
    # Try to interpret as text
    text = ''
    for b in chunk:
        if 0x20 <= b <= 0x7E:
            text += chr(b)
        elif b == 0x00:
            text += '.'
        else:
            text += f'[{b:02X}]'
    print(text)

    # Search for specific known strings
    print("\n--- Searching for known strings ---")
    search_terms = [
        b'CRONO', b'LUCCA', b'MARLE', b'FROG', b'ROBO', b'AYLA', b'MAGUS',
        b'TRIGGER', b'ZEAL', b'KING', b'QUEEN'
    ]
    
    for term in search_terms:
        pos = data.find(term)
        if pos != -1:
            print(f"  Found '{term.decode()}': {hex(pos)}")
            # Show context
            ctx = data[pos:pos+32]
            readable = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in ctx)
            print(f"    Context: {readable}")

    # The battle messages are usually uncompressed
    print("\n--- Looking for battle messages ---")
    battle_terms = [b'VICTORY', b'DEFEAT', b'RUN', b'ATTACK', b'MAGIC', b'ITEM']
    for term in battle_terms:
        pos = data.find(term)
        if pos != -1:
            print(f"  {term.decode()}: {hex(pos)}")

if __name__ == "__main__":
    find_game_strings()
