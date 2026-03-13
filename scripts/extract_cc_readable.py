#!/usr/bin/env python3
"""
Extract readable English text only from Chrono Cross
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def find_readable_strings(data, start, size):
    """Extract only readable English strings"""
    chunk = data[start:start+size]
    results = []
    current = []
    
    for i, b in enumerate(chunk):
        if 32 <= b <= 126:
            current.append(chr(b))
        else:
            if len(current) >= 8:
                s = ''.join(current)
                # Check if it's readable English (mostly letters/spaces)
                alpha = sum(1 for c in s if c.isalpha())
                space = sum(1 for c in s if c.isspace())
                if alpha > len(s) * 0.6 and space > 0:
                    results.append(s)
            current = []
    
    return results

# Chrono Cross
cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
print("Loading Chrono Cross...")
cc = read_rom(cc_path)

# Focus on known English text regions
regions = [
    (0x25e000, 0x2000, "shop_menu"),
    (0x260000, 0x2000, "battle_menu"),
]

all_text = []

print("Scanning...")
for start, size, name in regions:
    strings = find_readable_strings(cc, start, size)
    for s in strings:
        if len(s) > 10:
            all_text.append({"region": name, "text": s})

# Also search more broadly
print("Broader search...")
for start in range(0x250000, 0x400000, 0x10000):
    strings = find_readable_strings(cc, start, 0x10000)
    for s in strings:
        if len(s) > 15:
            # Must have significant words
            words = s.split()
            if any(len(w) > 3 for w in words):
                all_text.append({"region": hex(start), "text": s[:80]})

# Deduplicate
seen = set()
unique = []
for item in all_text:
    if item["text"] not in seen:
        seen.add(item["text"])
        unique.append(item)

print(f"Found {len(unique)} unique strings")

# Save
import json
with open(DATA_DIR / "chrono_cross_readable.json", 'w') as f:
    json.dump(unique, f, indent=2)

print("Saved to data/chrono_cross_readable.json")

# Show samples
print("\nReadable text found:")
for item in unique[:30]:
    print(f"  {item['text']}")
