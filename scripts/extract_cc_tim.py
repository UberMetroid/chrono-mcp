#!/usr/bin/env python3
"""
TIM Image Parser and Converter for PS1 (Chrono Cross)
Extracts TIM images and converts them to PNG
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
ART_DIR = DATA_DIR / "art"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def parse_tim(data, offset):
    """Parse a PS1 TIM image header"""
    if offset + 28 > len(data):
        return None
    
    tim_type = data[offset]
    if tim_type not in [0x10, 0x14, 0x18, 0x1C]:
        return None
    
    type_names = {0x10: "4-bit", 0x14: "8-bit", 0x18: "16-bit", 0x1C: "24-bit"}
    
    try:
        width = struct.unpack('<H', data[offset+8:offset+10])[0]
        height = struct.unpack('<H', data[offset+12:offset+14])[0]
        
        if width < 1 or width > 2048 or height < 1 or height > 2048:
            return None
            
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
        
        # Calculate total size including header
        total_size = 4 + 4 + 8 + pixel_size + palette_size
        
        return {
            "type": type_names.get(tim_type, "unknown"),
            "type_code": tim_type,
            "width": width,
            "height": height,
            "pixel_size": pixel_size,
            "palette_size": palette_size,
            "total_size": total_size,
            "offset": offset
        }
    except:
        return None

def tim_to_rgba(data, offset, tim_info):
    """Convert TIM image to RGBA pixel data"""
    tim_type = tim_info["type_code"]
    width = tim_info["width"]
    height = tim_info["height"]
    
    pixel_offset = offset + 20  # After header
    
    if tim_type == 0x10:  # 4-bit
        palette_offset = pixel_offset + tim_info["pixel_size"]
        palette = []
        for i in range(16):
            color = struct.unpack('<H', data[palette_offset + i*2:palette_offset + i*2 + 2])[0]
            r = (color & 0x1F) * 8
            g = ((color >> 5) & 0x1F) * 8
            b = ((color >> 10) & 0x1F) * 8
            palette.append((r, g, b))
        
        pixels = []
        for y in range(height):
            row = []
            for x in range(0, width, 2):
                byte = data[pixel_offset + y * (width // 2) + x // 2]
                hi = (byte >> 4) & 0xF
                lo = byte & 0xF
                row.append(palette[hi])
                row.append(palette[lo])
            pixels.extend(row)
            
    elif tim_type == 0x14:  # 8-bit
        palette_offset = pixel_offset + tim_info["pixel_size"]
        palette = []
        for i in range(256):
            color = struct.unpack('<H', data[palette_offset + i*2:palette_offset + i*2 + 2])[0]
            r = (color & 0x1F) * 8
            g = ((color >> 5) & 0x1F) * 8
            b = ((color >> 10) & 0x1F) * 8
            palette.append((r, g, b))
        
        pixels = []
        for y in range(height):
            for x in range(width):
                idx = data[pixel_offset + y * width + x]
                pixels.append(palette[idx])
                
    elif tim_type == 0x18:  # 16-bit
        pixels = []
        for y in range(height):
            for x in range(width):
                color = struct.unpack('<H', data[pixel_offset + (y * width + x)*2:pixel_offset + (y * width + x)*2 + 2])[0]
                r = (color & 0x1F) * 8
                g = ((color >> 5) & 0x1F) * 8
                b = ((color >> 10) & 0x1F) * 8
                pixels.append((r, g, b))
    else:
        return None
    
    return pixels

def save_ppm(pixels, width, height, path):
    """Save as PPM (simple format, easy to view)"""
    with open(path, 'wb') as f:
        f.write(f"P6\n{width} {height}\n255\n".encode())
        for r, g, b in pixels:
            f.write(bytes([r, g, b]))

# Load Chrono Cross
cc_path = BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin"
print("Loading Chrono Cross...")
cc_data = read_rom(cc_path)
print(f"ROM size: {len(cc_data) / (1024*1024):.1f} MB")

print("Finding TIM images...")
tim_images = []

# Scan for TIM signatures
for offset in range(0, min(len(cc_data), 0x500000), 4):
    result = parse_tim(cc_data, offset)
    if result:
        tim_images.append(result)

print(f"Found {len(tim_images)} TIM images")

# Group by size to find unique ones
sizes = {}
for tim in tim_images:
    key = (tim["width"], tim["height"], tim["type"])
    if key not in sizes:
        sizes[key] = []
    sizes[key].append(tim)

print(f"\nUnique sizes: {len(sizes)}")
for (w, h, t), images in list(sizes.items())[:10]:
    print(f"  {w}x{h} {t}: {len(images)} instances")

# Extract first 20 unique images
print("\nExtracting sample images...")
ART_DIR.mkdir(exist_ok=True, parents=True)

count = 0
extracted = []
seen_sizes = set()

for tim in tim_images:
    key = (tim["width"], tim["height"], tim["type"])
    if key in seen_sizes:
        continue
    seen_sizes.add(key)
    
    try:
        pixels = tim_to_rgba(cc_data, tim["offset"], tim)
        if pixels:
            ppm_path = ART_DIR / f"cc_tim_{count:04d}_{tim['width']}x{tim['height']}.ppm"
            save_ppm(pixels, tim["width"], tim["height"], ppm_path)
            extracted.append({
                "index": count,
                "offset": hex(tim["offset"]),
                "width": tim["width"],
                "height": tim["height"],
                "type": tim["type"],
                "file": ppm_path.name
            })
            count += 1
            if count >= 20:
                break
    except Exception as e:
        print(f"  Error at {hex(tim['offset'])}: {e}")

print(f"\nExtracted {len(extracted)} images")

# Save metadata
import json
with open(DATA_DIR / "cc_tim_extracted.json", 'w') as f:
    json.dump(extracted, f, indent=2)

print("Done!")
for e in extracted:
    print(f"  {e['file']}: {e['width']}x{e['height']} {e['type']}")
