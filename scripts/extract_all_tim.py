#!/usr/bin/env python3
"""
Extract all TIM images from Chrono Cross ROM
"""

import struct
import json
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
ART_DIR = DATA_DIR / "art"
CC_DIR = BASE_DIR / "Chrono Cross"

ART_DIR.mkdir(exist_ok=True)

print("=== Extracting All TIM Images from Chrono Cross ===\n")

# Load TIM metadata
with open(DATA_DIR / "cc_tim_all.json", "r") as f:
    tim_data = json.load(f)

# Load ROM
rom_path = "/home/jeryd/Code/Chrono_Series/Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin"
print(f"Loading ROM: {rom_path}")
with open(rom_path, "rb") as f:
    rom = f.read()

print(f"ROM size: {len(rom):,} bytes")
print(f"Total TIM images to extract: {len(tim_data)}\n")

# TIM format decoder
def decode_tim(rom_data, offset, width, height):
    """Decode TIM image data to PPM"""
    try:
        offset = int(offset, 0) if isinstance(offset, str) else offset
        
        # TIM header: 0x10 = 16-bit color, 0x08 = 8-bit color, 0x00 = 4-bit color
        tim_type = rom_data[offset]
        
        if tim_type != 0x10:
            return None  # Only handle 24-bit TIM for now
        
        # Skip 8-byte TIM header
        data_offset = offset + 8
        
        # Calculate expected size
        pixels = width * height
        pixel_data = rom_data[data_offset:data_offset + pixels * 3]
        
        if len(pixel_data) < pixels * 3:
            return None
        
        # Convert BGR to RGB
        ppm = f"P6\n{width} {height}\n255\n"
        rgb_data = bytearray()
        for i in range(pixels):
            b = pixel_data[i * 3]
            g = pixel_data[i * 3 + 1]
            r = pixel_data[i * 3 + 2]
            rgb_data.extend([r, g, b])
        
        return ppm.encode() + bytes(rgb_data)
    except Exception as e:
        return None

# Extract images
extracted = 0
failed = 0

for idx, tim in enumerate(tim_data):
    offset = tim["offset"]
    width = tim["width"]
    height = tim["height"]
    
    # Skip very large images
    if width > 1024 or height > 1024:
        continue
    
    img_data = decode_tim(rom, offset, width, height)
    
    if img_data:
        output_path = ART_DIR / f"cc_tim_{idx:04d}_{width}x{height}.ppm"
        with open(output_path, "wb") as f:
            f.write(img_data)
        extracted += 1
    else:
        failed += 1
    
    if (idx + 1) % 500 == 0:
        print(f"  Processed {idx + 1}/{len(tim_data)} images...")

print(f"\nExtracted: {extracted} images")
print(f"Failed: {failed} images")

# List output
ppm_files = list(ART_DIR.glob("*.ppm"))
print(f"\nTotal PPM files in {ART_DIR}: {len(ppm_files)}")
