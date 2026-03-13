#!/usr/bin/env python3
"""
Chrono Trigger Text Decoder - Proper version
Based on bisqwit.iki.fi documentation
"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from lib.chrono import read_rom
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

# Load ROM
ct = read_rom('ct_snes')

# CT US text encoding table (from bisqwit.iki.fi)
# 0xA0-0xFF: Font characters
CT_FONT = {}
for i in range(26):
    CT_FONT[0xA0 + i] = chr(ord('A') + i)  # A-Z
for i in range(26):
    CT_FONT[0xBA + i] = chr(ord('a') + i)  # a-z
for i in range(10):
    CT_FONT[0xD4 + i] = chr(ord('0') + i)  # 0-9

# Add punctuation/symbols (0xDE-0xED)
symbols = "!\"#%&'()*+,-./:;<=>?@[\\]^_`{|}~"
for i, sym in enumerate("!\"#%&'()*+,-./:;<=>?@[\\]^_`{|}~"):
    CT_FONT[0xDE + i] = sym

CT_FONT[0xEF] = ' '   # Space
CT_FONT[0xF0] = '♥'  # Heart symbol
CT_FONT[0xF1] = '...' # Ellipsis
CT_FONT[0xF2] = '∞'  # Infinity
CT_FONT[0xF3] = '♪'  # Music
CT_FONT[0xFF] = ' '  # Space (8pix)

# Control codes
CT_CONTROL = {
    0x00: '\0',     # End of string
    0x03: '',       # Delay
    0x05: '\n',     # Newline
    0x0A: '\n',     # Dialog clearing + spaces
    0x0B: '\n',     # Pause + dialog clearing  
    0x0C: '\n',     # Pause + dialog clearing + spaces
    0x0D: '[NUM8]',  # 8-bit number
    0x0E: '[NUM16]', # 16-bit number
    0x0F: '[NUM32]', # 32-bit number
}

# Character names (0x13-0x1A)
CT_NAMES = {
    0x13: '[CRONO]',
    0x14: '[MARLE]',
    0x15: '[LUCCA]',
    0x16: '[ROBO]',
    0x17: '[FROG]',
    0x18: '[AYLA]',
    0x19: '[MAGUS]',
    0x1A: '[CRONO]',  # Ayla's version
    0x1B: '[PARTY1]',
    0x1C: '[PARTY2]',
}

def decode_ct_text(data):
    """Decode CT text bytes to string"""
    result = []
    i = 0
    while i < len(data):
        b = data[i]
        
        # End of string
        if b == 0x00:
            break
            
        # Control codes (0x00-0x20)
        if b in CT_CONTROL:
            result.append(CT_CONTROL[b])
            i += 1
        # Character names
        elif b in CT_NAMES:
            result.append(CT_NAMES[b])
            i += 1
        # Font characters (0xA0-0xFF)
        elif b in CT_FONT:
            result.append(CT_FONT[b])
            i += 1
        # Substring table reference (0x21-0x9F) - skip for now
        elif 0x21 <= b <= 0x9F:
            result.append(f'[{b:02X}]')  # Placeholder for substring
            i += 1
        # Regular ASCII
        elif 0x20 <= b <= 0x7F:
            result.append(chr(b))
            i += 1
        # Unknown
        else:
            result.append(f'[{b:02X}]')
            i += 1
    
    return ''.join(result)

def lzss_decompress_ct(data, offset):
    """Decompress LZSS block"""
    if offset >= len(data):
        return b'', offset
    
    header = data[offset]
    if header not in [0x10, 0x11]:
        return b'', offset
    
    offset += 1
    decomp_size = data[offset] | (data[offset+1] << 8)
    offset += 2
    
    output = bytearray()
    window_size = 4096 if header == 0x10 else 2048
    max_length = 18 if header == 0x10 else 34
    
    while len(output) < decomp_size:
        if offset >= len(data):
            break
        flags = data[offset]
        offset += 1
        
        for bit in range(8):
            if len(output) >= decomp_size:
                break
            if offset >= len(data):
                break
                
            if flags & (0x80 >> bit):
                output.append(data[offset])
                offset += 1
            else:
                if offset + 1 >= len(data):
                    break
                ref = (data[offset+1] << 8) | data[offset]
                offset += 2
                
                length = (ref >> 12) + 3
                distance = ref & 0xFFF
                
                if distance >= len(output):
                    continue
                if length > max_length:
                    length = max_length
                    
                for _ in range(length):
                    if len(output) >= decomp_size:
                        break
                    output.append(output[-(distance + 1)])
    
    return bytes(output), offset

# Find all text blocks
print("Finding text blocks...")
text_blocks = []
for i in range(len(ct) - 1):
    if ct[i] in [0x10, 0x11] and ct[i+1] == 0x00:
        if i + 4 < len(ct):
            size = ct[i+2] | (ct[i+3] << 8)
            if 500 < size < 60000:
                text_blocks.append((i, ct[i], size))

print(f"Found {len(text_blocks)} text blocks")

# Decompress and decode
decoded_dialog = []
for offset, header, size in text_blocks[:500]:
    try:
        result, _ = lzss_decompress_ct(ct, offset)
        if len(result) > 100:
            text = decode_ct_text(result)
            
            # Look for meaningful strings
            # Split by newlines and control characters
            chunks = text.split('\n')
            for chunk in chunks:
                chunk = chunk.strip()
                # Remove placeholder markers
                chunk = chunk.replace('[', '').replace(']', '')
                # Check if it has meaningful content
                if len(chunk) > 3 and len(chunk) < 60:
                    # Check if it's mostly readable (not all placeholders)
                    letters = sum(1 for c in chunk if c.isalpha())
                    if letters > 2:
                        decoded_dialog.append({
                            "offset": hex(offset),
                            "text": chunk
                        })
    except:
        pass

# Dedupe
seen = set()
unique = []
for item in decoded_dialog:
    if item["text"] not in seen:
        seen.add(item["text"])
        unique.append(item)

print(f"Decoded {len(unique)} unique dialog entries")

# Save
with open(DATA_DIR / "ct_dialog_decoded.json", 'w') as f:
    json.dump(unique[:1000], f, indent=2)

print("\n=== Sample decoded dialog ===")
for item in unique[:50]:
    print(f"  {item['text']}")
