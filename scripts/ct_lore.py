#!/usr/bin/env python3
"""
Chrono Trigger - Deep Text Analysis
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

# Chrono Trigger / Square game text encoding
# Based on standard Shift-JIS / Katakana hybrid
ENCODING_TABLE = {
    0x20: ' ', 0x21: '!', 0x22: '"', 0x23: '#', 0x24: '$', 0x25: '%', 0x26: '&', 0x27: "'",
    0x28: '(', 0x29: ')', 0x2A: '*', 0x2B: '+', 0x2C: ',', 0x2D: '-', 0x2E: '.', 0x2F: '/',
    0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4', 0x35: '5', 0x36: '6', 0x37: '7',
    0x38: '8', 0x39: '9', 0x3A: ':', 0x3B: ';', 0x3C: '<', 0x3D: '=', 0x3E: '>', 0x3F: '?',
    0x40: '@', 0x41: 'A', 0x42: 'B', 0x43: 'C', 0x44: 'D', 0x45: 'E', 0x46: 'F', 0x47: 'G',
    0x48: 'H', 0x49: 'I', 0x4A: 'J', 0x4B: 'K', 0x4C: 'L', 0x4D: 'M', 0x4E: 'N', 0x4F: 'O',
    0x50: 'P', 0x51: 'Q', 0x52: 'R', 0x53: 'S', 0x54: 'T', 0x55: 'U', 0x56: 'V', 0x57: 'W',
    0x58: 'X', 0x59: 'Y', 0x5A: 'Z', 0x5B: '[', 0x5C: '¥', 0x5D: ']', 0x5E: '^', 0x5F: '_',
    0x60: '`', 0x61: 'a', 0x62: 'b', 0x63: 'c', 0x64: 'd', 0x65: 'e', 0x66: 'f', 0x67: 'g',
    0x68: 'h', 0x69: 'i', 0x6A: 'j', 0x6B: 'k', 0x6C: 'l', 0x6D: 'm', 0x6E: 'n', 0x6F: 'o',
    0x70: 'p', 0x71: 'q', 0x72: 'r', 0x73: 's', 0x74: 't', 0x75: 'u', 0x76: 'v', 0x77: 'w',
    0x78: 'x', 0x79: 'y', 0x7A: 'z', 0x7B: '{', 0x7C: '|', 0x7D: '}', 0x7E: '~',
    
    # Extended Katakana area (0x80-0x9F)
    0x82: 'A', 0x83: 'I', 0x84: 'U', 0x85: 'E', 0x86: 'O',  # Vowels with dakuten
    0x89: 'K', 0x8A: 'G', 0x8B: 'K', 0x8C: 'S', 0x8D: 'Z', 0x8E: 'T', 0x8F: 'D',
    0x90: 'N', 0x91: 'H', 0x92: 'B', 0x93: 'P', 0x94: 'M',
    
    # Common special codes
    0xEE: '?', 0xEF: '?', 0xF0: '?', 0xF1: '?', 0xF2: '?', 0xF3: '?', 0xF4: '?', 0xF5: '?',
}

def decode_text(data, offset, max_len=100):
    """Decode text at offset using CT encoding"""
    result = []
    i = 0
    while i < max_len:
        b = data[offset + i]
        if b == 0x00:
            break
        elif b == 0xFF:
            break
        elif b in ENCODING_TABLE:
            result.append(ENCODING_TABLE[b])
        else:
            result.append('?')
        i += 1
    return ''.join(result)

def find_encoded_strings():
    data = read_rom()
    
    # Let's look at the area around the found "BATTLE PLAN"
    print("=== CHRONO TRIGGER LORE EXPLORATION ===\n")
    
    # Look at the battle program area
    print("--- Battle Program Area (0x115000) ---")
    for offset in range(0x115000, 0x116000, 32):
        chunk = data[offset:offset+32]
        # Check how many readable bytes
        readable = sum(1 for b in chunk if (0x20 <= b <= 0x7E or b >= 0xA0))
        if readable > 20:
            decoded = decode_text(data, offset, 32)
            if any(c != '?' for c in decoded):
                print(f"  {hex(offset)}: {decoded}")
    
    # Search for character names using encoded form
    # "CRONO" in CT encoding
    print("\n--- Searching for Character Names ---")
    # CT US uses shifted encoding - let's try finding strings by looking for readable blocks
    # at known script locations
    
    # The main script in HiROM is typically in the 0x100000-0x200000 range
    print("\n--- Main Script Area Search ---")
    
    # Look for sequences of readable text
    for offset in range(0x200000, 0x300000, 0x100):
        chunk = data[offset:offset+64]
        # Count "good" bytes
        good = sum(1 for b in chunk if (0x30 <= b <= 0x39 or 0x41 <= b <= 0x5A or 0x61 <= b <= 0x7A))
        if good > 40:
            decoded = decode_text(data, offset, 64)
            # Filter for game-like text
            if any(word in decoded.upper() for word in ['TIME', 'GATE', 'KING', 'YOU', 'THE', 'AND', 'ARE', 'NOT', 'BUT']):
                print(f"  {hex(offset)}: {decoded[:50]}")
    
    # Let's also look at what we found before - 0x34162c
    print("\n--- Examining 0x34162c ---")
    chunk = data[0x34162c:0x341700]
    print(f"Raw: {' '.join(f'{b:02X}' for b in chunk[:32])}")
    decoded = decode_text(data, 0x34162c, 100)
    print(f"Decoded: {decoded}")
    
    # Try decompressing nearby data
    print("\n--- Looking for Message Blocks ---")
    # In CT, messages are stored as LZSS compressed blocks
    # Let's find the message pointer table
    
    # Search for common message header patterns
    for offset in range(0x100000, 0x200000, 0x10):
        if data[offset] == 0x10:  # LZSS signature
            size = data[offset+1] | (data[offset+2] << 8)
            if 0x100 < size < 0x2000:
                # Try to decompress and read
                try:
                    # Simple LZSS (already tried this)
                    pass
                except:
                    pass

    # Final approach: Just look for any reasonable ASCII
    print("\n--- All ASCII-like strings in ROM ---")
    found = set()
    for offset in range(0, len(data) - 20):
        chunk = data[offset:offset+20]
        text = decode_text(data, offset, 20)
        # Filter
        if len(text) >= 8:
            # Check for game keywords
            if any(kw in text.upper() for kw in ['TIME', 'GATE', 'BATTLE', 'MAGIC', 'ITEM', 'HP', 'MP', 'LVL', 'SAVE', 'LOAD', 'KING', 'QUEEN', 'PRINCE', 'START', 'SELECT', 'POWER', 'SHIELD']):
                if offset not in found:
                    found.add(offset)
                    print(f"  {hex(offset)}: {text}")

if __name__ == "__main__":
    find_encoded_strings()
