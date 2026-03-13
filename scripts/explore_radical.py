#!/usr/bin/env python3
"""
Deep dive into Radical Dreamers text extraction
"""

import sys
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from lib.chrono import find_strings

data = open("/home/jeryd/Code/Chrono_Series/Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", 'rb').read()

print(f"ROM Size: {len(data)} bytes")
print()

# Find all meaningful strings
strings = find_strings(data, min_length=4)
print(f"Total strings: {len(strings)}")

# Extract interesting patterns
interesting = []
for offset, text in strings:
    upper = text.upper()
    
    # Character names
    if any(n in upper for n in ['KID', 'HARLE', 'NORMAN', 'NIKOLAI', 'GUARD']):
        interesting.append(('CHAR', offset, text))
    # Story/menu
    elif any(n in upper for n in ['START', 'SELECT', 'SAVE', 'LOAD', 'ITEM', 'EQUIP', 'STATUS']):
        interesting.append(('MENU', offset, text))
    # Locations
    elif any(n in upper for n in ['TOWN', 'VILLAGE', 'CASTLE', 'FOREST', 'CAVE', 'SEA', 'SHIP']):
        interesting.append(('LOC', offset, text))
    # Game text (longer strings that might be dialog)
    elif len(text) > 20 and text.replace(' ', '').isalpha():
        interesting.append(('TEXT', offset, text))

# Print by category
print("\n=== CHARACTER NAMES ===")
for cat, offset, text in sorted(interesting):
    if cat == 'CHAR':
        print(f"  {hex(offset)}: {text[:50]}")

print("\n=== MENU ITEMS ===")
for cat, offset, text in sorted(interesting):
    if cat == 'MENU':
        print(f"  {hex(offset)}: {text[:50]}")

print("\n=== LOCATIONS ===")
for cat, offset, text in sorted(interesting):
    if cat == 'LOC':
        print(f"  {hex(offset)}: {text[:50]}")

print("\n=== LONG TEXT STRINGS ===")
for cat, offset, text in sorted(interesting):
    if cat == 'TEXT':
        print(f"  {hex(offset)}: {text[:80]}")

# Look for Japanese/encoding patterns
print("\n=== LOOKING FOR ENCODING PATTERNS ===")
# Shift-JIS typical markers
for i in range(0, min(len(data), 0x100000), 0x10000):
    chunk = data[i:i+256]
    # Look for common Japanese char ranges
    kana = sum(1 for b in chunk if (0xa1 <= b <= 0xdf))
    kanji = sum(1 for b in chunk if (0x81 <= b <= 0x9f or 0xe0 <= b <= 0xfc))
    if kana + kanji > 20:
        print(f"  {hex(i)}: {kana} kana, {kanji} kanji")
