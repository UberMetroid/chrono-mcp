#!/usr/bin/env python3
"""
Extract Chrono Cross dialog and text
"""

import sys
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"

print("Loading Chrono Cross...")
data = open(cc_path, 'rb').read()
print(f"ROM size: {len(data)} bytes ({len(data)//1024//1024}MB)")

def find_strings(data, min_len=4):
    results = []
    current = []
    for i, byte in enumerate(data):
        if 32 <= byte <= 126:
            current.append((i, chr(byte)))
        else:
            if len(current) >= min_len:
                start = current[0][0]
                text = ''.join(c for _, c in current)
                results.append((start, text))
            current = []
    if len(current) >= min_len:
        results.append((current[0][0], ''.join(c for _, c in current)))
    return results

# Search for dialog - PS1 games often have text at certain offsets
# Let's look for the script data area
print("\nSearching for text regions...")

# Known text regions from similar games
# PS1 games often have text starting around 0x200000 or later
text_regions = []
for start in range(0x100000, min(len(data), 0x400000), 0x10000):
    chunk = data[start:start+0x10000]
    strings = find_strings(chunk, 6)
    if len(strings) > 50:
        text_regions.append((start, len(strings)))
        print(f"  0x{start:06x}: {len(strings)} strings")

# Extract from promising regions
print("\nExtracting dialog from rich regions...")

all_dialog = []
for start, count in text_regions[:5]:
    chunk = data[start:start+0x20000]
    strings = find_strings(chunk, 8)
    for offset, text in strings:
        # Filter for likely dialog (longer sentences)
        if len(text) > 15 and len(text) < 200:
            # Filter out junk
            if text.replace(' ', '').replace('.', '').replace(',', '').isalpha():
                all_dialog.append({"offset": hex(start + offset), "text": text})

# Remove duplicates
seen = set()
unique_dialog = []
for line in all_dialog:
    if line["text"] not in seen:
        seen.add(line["text"])
        unique_dialog.append(line)

print(f"Found {len(unique_dialog)} unique dialog lines")

# Save
output = BASE_DIR / "data" / "chrono_cross_dialog.json"
with open(output, 'w') as f:
    json.dump(unique_dialog[:500], f, indent=2)

print(f"Saved to {output}")

# Also extract menu text
print("\nExtracting menu text...")
menu_area = data[0x25ef00:0x25f000]
menu_strings = find_strings(menu_area, 4)
menu_text = [{"offset": hex(0x25ef00 + s[0]), "text": s[1]} for s in menu_strings if len(s[1]) > 2]

# Save menu text
with open(BASE_DIR / "data" / "chrono_cross_menu.json", 'w') as f:
    json.dump(menu_text, f, indent=2)

print(f"Found {len(menu_text)} menu strings")
