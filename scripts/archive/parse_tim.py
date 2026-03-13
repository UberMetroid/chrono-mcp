#!/usr/bin/env python3
"""
TIM Image Parser for PS1 (Chrono Cross)
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def parse_tim(data, offset):
    """
    Parse a PS1 TIM image
    Returns image info or None
    """
    if offset + 28 > len(data):
        return None
    
    # Check TIM magic (could be at different offsets due to alignment)
    # TIM format: starts with header, then either 0x10, 0x14, 0x18, 0x1C
    
    tim_type = data[offset]
    
    if tim_type not in [0x10, 0x14, 0x18, 0x1C]:
        return None
    
    # Get image parameters
    type_names = {0x10: "4-bit", 0x14: "8-bit", 0x18: "16-bit", 0x1C: "24-bit"}
    
    try:
        # Skip 4 bytes, read dimensions
        width = struct.unpack('<H', data[offset+8:offset+10])[0]
        height = struct.unpack('<H', data[offset+12:offset+14])[0]
        
        if width < 1 or width > 2048 or height < 1 or height > 2048:
            return None
            
        # Calculate sizes
        if tim_type == 0x10:  # 4-bit
            pixel_size = width * height // 2
            palette_size = 32
        elif tim_type == 0x14:  # 8-bit
            pixel_size = width * height
            palette_size = 256 * 2
        elif tim_type == 0x18:  # 16-bit
            pixel_size = width * height * 2
            palette_size = 0
        else:  # 24-bit
            pixel_size = width * height * 3
            palette_size = 0
        
        return {
            "type": type_names.get(tim_type, "unknown"),
            "width": width,
            "height": height,
            "pixel_size": pixel_size,
            "palette_size": palette_size,
            "offset": offset
        }
    except:
        return None

# Load Chrono Cross and find TIMs
cc_path = BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin"
print("Loading Chrono Cross...")
cc_data = read_rom(cc_path)

print("Finding TIM images...")

tim_images = []

# Scan for TIM signatures - they're usually aligned
# Try multiple offsets in each 16-byte boundary
for offset in range(0, min(len(cc_data), 0x500000), 4):
    result = parse_tim(cc_data, offset)
    if result:
        tim_images.append(result)

print(f"Found {len(tim_images)} TIM images")

# Show some examples
print("\nExamples:")
for tim in tim_images[:10]:
    print(f"  {hex(tim['offset'])}: {tim['width']}x{tim['height']} {tim['type']}")

# Save
import json
with open(DATA_DIR / "tim_images_parsed.json", 'w') as f:
    json.dump(tim_images[:100], f, indent=2)

print(f"\nSaved {len(tim_images[:100])} to data/tim_images_parsed.json")
