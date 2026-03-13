#!/usr/bin/env python3
"""
Proper SNES LZSS - Chrono Trigger specific
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def decompress_lzss(data, offset):
    """LZSS decompression - returns (decompressed_data, new_offset)"""
    
    if offset >= len(data):
        return b'', offset
    
    header = data[offset]
    
    if header not in [0x10, 0x11]:
        return b'', offset
    
    output = bytearray()
    offset += 1
    
    # Window config
    if header == 0x10:
        window = 4096
    else:
        window = 2048
    
    while len(output) < 65536:
        if offset >= len(data):
            break
            
        control = data[offset]
        offset += 1
        
        for i in range(8):
            if offset >= len(data):
                break
                
            if control & (0x80 >> i):
                # Literal
                output.append(data[offset])
                offset += 1
            else:
                # Match
                if offset + 1 >= len(data):
                    break
                    
                match = (data[offset] << 8) | data[offset + 1]
                offset += 2
                
                length = ((match >> 12) & 0xF) + 3
                distance = (match & 0xFFF) + 1
                
                if distance > len(output):
                    break
                    
                for _ in range(length):
                    output.append(output[-distance])
    
    return bytes(output), offset

# Find ALL LZSS blocks in CT
ct = read_rom(BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc")
print("Scanning for LZSS blocks...")

# Known locations with text
text_offsets = []

for i in range(0x100000, 0x380000, 16):
    if i < len(ct) - 1:
        if ct[i] == 0x10 and ct[i+1] == 0x00:
            # Try decompressing
            try:
                result, next_off = decompress_lzss(ct, i)
                if len(result) > 50:
                    # Check for readable text
                    readable = sum(1 for b in result if 32 <= b <= 126)
                    if readable > len(result) * 0.3:
                        text_offsets.append({
                            "offset": hex(i),
                            "size": len(result),
                            "readable_pct": round(readable / len(result) * 100, 1)
                        })
            except:
                pass

print(f"Found {len(text_offsets)} text blocks")

# Show first few
for t in text_offsets[:10]:
    print(f"  {t}")

# Save
import json
with open(DATA_DIR / "ct_text_blocks.json", 'w') as f:
    json.dump(text_offsets, f, indent=2)
