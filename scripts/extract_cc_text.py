#!/usr/bin/env python3
"""
Extract ALL readable text from Chrono Cross - scanning key regions
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def find_strings(data, start, size, min_len=6):
    """Extract all strings from a region"""
    chunk = data[start:start+size]
    results = []
    current = []
    
    for i, b in enumerate(chunk):
        if 32 <= b <= 126:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                results.append(''.join(current))
            current = []
    
    if len(current) >= min_len:
        results.append(''.join(current))
    
    return results

# Extract from Chrono Cross
cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
print("Loading Chrono Cross...")
cc = read_rom(cc_path)
print(f"Size: {len(cc)} bytes")

# Known text regions in Chrono Cross (PS1)
# Based on typical PS1 game layout
regions = [
    (0x250000, 0x20000, "menu_shop"),
    (0x270000, 0x20000, "battle"),
    (0x290000, 0x20000, "field"),
    (0x2B0000, 0x20000, "dialog"),
    (0x2D0000, 0x20000, "system"),
    (0x2F0000, 0x30000, "strings1"),
    (0x320000, 0x30000, "strings2"),
    (0x350000, 0x30000, "strings3"),
    (0x380000, 0x30000, "strings4"),
    (0x3B0000, 0x30000, "strings5"),
    (0x3E0000, 0x20000, "strings6"),
]

all_text = []

print("Scanning regions...")
for start, size, name in regions:
    strings = find_strings(cc, start, size, 4)
    
    for s in strings:
        # Filter: must be mostly letters, reasonable length
        if 4 < len(s) < 60:
            # Check if it's mostly alpha
            alpha = sum(1 for c in s if c.isalpha())
            if alpha > len(s) * 0.7:
                all_text.append({"region": name, "offset": hex(start), "text": s})

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
with open(DATA_DIR / "chrono_cross_text.json", 'w') as f:
    json.dump(unique, f, indent=2)

print(f"Saved to data/chrono_cross_text.json")

# Show sample
print("\nSample:")
for item in unique[:20]:
    print(f"  [{item['region']}] {item['text']}")
