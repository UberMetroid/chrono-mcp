#!/usr/bin/env python3
"""
Chrono Trigger Full Text Decoder
Complete implementation with substring table support
"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from lib.chrono import read_rom
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct = read_rom('ct_snes')

# Extract substring table from 0x1EC800
SUBTABLE_OFFSET = 0x1EC800

def extract_substring_table(rom_data, offset):
    """Extract null-terminated strings from substring table"""
    strings = []
    current = []
    i = offset
    # Extract up to 128 substrings
    while len(strings) < 128 and i < len(rom_data) - 1:
        b = rom_data[i]
        if b == 0x00:
            if current:
                strings.append(bytes(current))
                current = []
        else:
            current.append(b)
        i += 1
    return strings

# Get substring table
substring_data = extract_substring_table(ct, SUBTABLE_OFFSET)
print(f"Found {len(substring_data)} substrings in table")

# Build substring table (index 0 = 0x21, etc.)
substring_table = []
for s in substring_data:
    decoded = ""
    for byte in s:
        if 0xA0 <= byte <= 0xB9:
            decoded += chr(0x41 + (byte - 0xA0))
        elif 0xBA <= byte <= 0xD3:
            decoded += chr(0x61 + (byte - 0xBA))
        elif 0xD4 <= byte <= 0xDD:
            decoded += chr(0x30 + (byte - 0xD4))
        elif byte in [0xEF, 0xFF]:
            decoded += " "
        elif 0x20 <= byte <= 0x7F:
            decoded += chr(byte)
        else:
            decoded += "?"
    substring_table.append(decoded)

print("Substring table (first 20):")
for i, s in enumerate(substring_table[:20]):
    print(f"  [{i+0x21:02X}] {s[:40]}")

# CT text decoder
CT_FONT = {}
for i in range(26):
    CT_FONT[0xA0 + i] = chr(ord('A') + i)
for i in range(26):
    CT_FONT[0xBA + i] = chr(ord('a') + i)
for i in range(10):
    CT_FONT[0xD4 + i] = chr(ord('0') + i)

symbols = "!\"#%&'()*+,-./:;<=>?@[\\]^_`{|}~"
for i, sym in enumerate("!\"#%&'()*+,-./:;<=>?@[\\]^_`{|}~"):
    CT_FONT[0xDE + i] = sym

CT_FONT[0xEF] = ' '
CT_FONT[0xF0] = '♥'
CT_FONT[0xF1] = '...'
CT_FONT[0xF3] = '♪'
CT_FONT[0xFF] = ' '

CT_CONTROL = {
    0x00: '',      # End of string
    0x03: '',      # Delay
    0x05: '\n',    # Newline
    0x0A: '\n',    # Clear dialog
    0x0B: '\n',    # Pause
    0x0C: '\n',    # Clear + pause
    0x0D: '[N8]',  # 8-bit number
    0x0E: '[N16]', # 16-bit number  
    0x0F: '[N32]', # 32-bit number
}

CT_NAMES = {
    0x13: 'CRONO', 0x14: 'MARLE', 0x15: 'LUCCA', 0x16: 'ROBO',
    0x17: 'FROG', 0x18: 'AYLA', 0x19: 'MAGUS', 0x1A: 'CRONO',
    0x1B: '[P1]', 0x1C: '[P2]', 0x1D: '[P3]', 0x1E: '[C]',
    0x1F: '[?]',
}

def decode_ct_text_full(data, substrings):
    """Decode CT text with full substring table support"""
    result = []
    i = 0
    while i < len(data):
        b = data[i]
        
        # End of string
        if b == 0x00:
            break
            
        # Control codes
        if b in CT_CONTROL:
            result.append(CT_CONTROL[b])
            i += 1
        # Character names
        elif b in CT_NAMES:
            result.append(CT_NAMES[b])
            i += 1
        # Substring table references (0x21-0x9F)
        elif 0x21 <= b <= 0x9F:
            idx = b - 0x21
            if idx < len(substrings):
                result.append(substrings[idx])
            i += 1
        # Font characters
        elif b in CT_FONT:
            result.append(CT_FONT[b])
            i += 1
        # Unknown
        else:
            result.append(f'[{b:02X}]')
            i += 1
    
    return ''.join(result)

def lzss_decompress_ct(data, offset):
    if offset >= len(data):
        return b'', offset
    header = data[offset]
    if header not in [0x10, 0x11]:
        return b'', offset
    offset += 1
    decomp_size = data[offset] | (data[offset+1] << 8)
    offset += 2
    output = bytearray()
    max_length = 18 if header == 0x10 else 34
    while len(output) < decomp_size:
        if offset >= len(data):
            break
        flags = data[offset]
        offset += 1
        for bit in range(8):
            if len(output) >= decomp_size or offset >= len(data):
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
                length = min(length, max_length)
                for _ in range(length):
                    if len(output) >= decomp_size:
                        break
                    output.append(output[-(distance + 1)])
    return bytes(output), offset

# Find all text blocks
print("\n=== Finding and decoding text blocks ===")
text_blocks = []
for i in range(len(ct) - 1):
    if ct[i] in [0x10, 0x11] and ct[i+1] == 0x00:
        if i + 4 < len(ct):
            size = ct[i+2] | (ct[i+3] << 8)
            if 500 < size < 60000:
                text_blocks.append((i, ct[i], size))

print(f"Found {len(text_blocks)} text blocks")

# Decode all blocks
decoded_dialog = []
for offset, header, size in text_blocks[:500]:
    try:
        result, _ = lzss_decompress_ct(ct, offset)
        if len(result) > 100:
            text = decode_ct_text_full(result, substring_table)
            
            # Split by newlines and filter
            chunks = text.split('\n')
            for chunk in chunks:
                chunk = chunk.strip()
                if len(chunk) > 3 and len(chunk) < 80:
                    # Count meaningful characters
                    meaningful = sum(1 for c in chunk if c.isalpha() or c in "',.-!? ")
                    if meaningful > len(chunk) * 0.4:
                        decoded_dialog.append({
                            "offset": hex(offset),
                            "text": chunk[:60]
                        })
    except Exception as e:
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
with open(DATA_DIR / "ct_dialog_full.json", 'w') as f:
    json.dump(unique[:2000], f, indent=2)

print("\n=== Sample decoded dialog ===")
for item in unique[:40]:
    print(f"  {item['text']}")
