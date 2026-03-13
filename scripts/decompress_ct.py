#!/usr/bin/env python3
"""
Fixed LZSS decompression - target specific CT regions
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def decompress_lzss_ct(data, offset):
    """Decompress LZSS - SNES variant used in Chrono Trigger"""
    if offset >= len(data):
        return b'', offset
    
    header = data[offset]
    
    # Check for LZSS
    if header != 0x10:
        return b'', offset
    
    output = bytearray()
    offset += 1
    
    # LZSS parameters for type 0x10
    window_size = 4096
    
    while len(output) < 65536:  # Limit output
        if offset >= len(data):
            break
            
        flags = data[offset]
        offset += 1
        
        for bit in range(8):
            if offset >= len(data):
                break
                
            if flags & (0x80 >> bit):
                # Literal - copy 1 byte
                output.append(data[offset])
                offset += 1
            else:
                # Back reference
                if offset + 1 >= len(data):
                    break
                    
                # 2-byte reference
                ref = (data[offset] << 8) | data[offset + 1]
                offset += 2
                
                # Extract length and distance
                length = (ref >> 12) + 3
                distance = (ref & 0xFFF) + 1
                
                if distance > len(output):
                    break
                if length > 18:
                    length = 18
                    
                # Copy from window
                for _ in range(length):
                    output.append(output[-distance])
    
    return bytes(output), offset

# Load Chrono Trigger
ct_path = BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc"
print("Loading Chrono Trigger...")
ct = read_rom(ct_path)

# Known compressed regions from ROM map
# Try to decompress from various locations
print("Attempting decompression...")

decompressed_data = []

# Try common dialog locations
for start in [0x100000, 0x150000, 0x1A0000, 0x200000, 0x250000, 0x300000]:
    if start < len(ct) and ct[start] == 0x10:
        try:
            result, new_offset = decompress_lzss_ct(ct, start)
            if len(result) > 100:
                # Look for text in decompressed data
                text_found = []
                current = []
                for b in result:
                    if 32 <= b <= 126:
                        current.append(chr(b))
                    else:
                        if len(current) >= 5:
                            text_found.append(''.join(current))
                        current = []
                
                if text_found:
                    decompressed_data.append({
                        "offset": hex(start),
                        "size": len(result),
                        "text_sample": text_found[:20]
                    })
                    print(f"\n{hex(start)}: {len(result)} bytes")
                    print(f"  Sample: {text_found[:5]}")
        except Exception as e:
            pass

print(f"\nFound {len(decompressed_data)} decompressed regions with text")

# Save results
import json
with open(DATA_DIR / "ct_decompressed.json", 'w') as f:
    json.dump(decompressed_data, f, indent=2)
