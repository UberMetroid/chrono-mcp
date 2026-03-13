#!/usr/bin/env python3
"""
LZSS Decompression for SNES (specifically Chrono Trigger)
Based on known SNES LZSS format
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
    """
    Decompress SNES LZSS compressed data
    Returns decompressed bytes and new offset
    """
    if offset >= len(data):
        return b'', offset
    
    header = data[offset]
    
    # SNES LZSS signature
    if header not in [0x10, 0x11, 0x12]:
        return b'', offset
    
    output = bytearray()
    offset += 1
    
    # Get window size and max match length based on header
    if header == 0x10:
        window_size = 4096
        max_length = 18
    elif header == 0x11:
        window_size = 2048
        max_length = 34
    else:  # 0x12
        window_size = 8192
        max_length = 273
    
    compressed_size = 0
    
    while len(output) < compressed_size or compressed_size == 0:
        if offset >= len(data):
            break
            
        control = data[offset]
        offset += 1
        
        for bit in range(8):
            if offset >= len(data):
                break
                
            if control & (0x80 >> bit):
                # Literal byte
                output.append(data[offset])
                offset += 1
            else:
                # Back reference
                if offset + 1 >= len(data):
                    break
                    
                ref = (data[offset] << 8) | data[offset + 1]
                offset += 2
                
                # Extract length and distance
                length = (ref >> 12) + 3
                distance = (ref & 0xFFF) + 1
                
                if distance > len(output):
                    continue
                if length > max_length:
                    length = max_length
                
                # Copy from window
                for _ in range(length):
                    output.append(output[-(distance)])
    
    return bytes(output), offset

# Find all LZSS blocks in Chrono Trigger
ct_path = BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc"
print("Loading Chrono Trigger...")
ct_data = read_rom(ct_path)

print("Finding LZSS blocks...")

# Find all potential LZSS blocks
lzss_blocks = []
for i in range(0, len(ct_data) - 10):
    if ct_data[i] == 0x10:
        # Try to decompress
        try:
            result, new_offset = decompress_lzss(ct_data, i)
            if len(result) > 20:  # Reasonable decompressed size
                lzss_blocks.append({
                    "offset": i,
                    "compressed_header": hex(ct_data[i]),
                    "decompressed_size": len(result),
                    "data": result[:100]  # First 100 bytes
                })
        except:
            pass

print(f"Found {len(lzss_blocks)} LZSS blocks")

# Save some decompressed data
import json

# Show first few blocks
for i, block in enumerate(lzss_blocks[:5]):
    print(f"\nBlock {i} at {hex(block['offset'])}:")
    print(f"  Decompressed size: {block['decompressed_size']}")
    
    # Try to find text in decompressed data
    text_chars = []
    for b in block['data']:
        if 32 <= b <= 126:
            text_chars.append(chr(b))
        else:
            if len(text_chars) > 5:
                print(f"  Text: {''.join(text_chars)}")
            text_chars = []

# Save to file
with open(DATA_DIR / "lzss_blocks.json", 'w') as f:
    json.dump(lzss_blocks[:50], f, indent=2)

print(f"\nSaved to data/lzss_blocks.json")
