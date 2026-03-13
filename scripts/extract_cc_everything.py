#!/usr/bin/env python3
"""Extract EVERYTHING from Chrono Cross"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# Dump every 1MB of CC in relevant areas
cc_path = BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin"
print("Loading Chrono Cross...")
cc = read_rom(cc_path)
print(f"Size: {len(cc)} bytes")

# Dump all interesting regions
regions = []
for start in range(0x100000, 0x500000, 0x100000):
    name = f"cc_{start:08x}"
    chunk = cc[start:start + 0x100000]
    with open(DATA_DIR / "raw" / f"{name}.bin", 'wb') as f:
        f.write(chunk)
    print(f"Dumped {name}: {len(chunk)} bytes")
    regions.append(name)

# Extract all strings from CC
def find_all_strings(data, min_len=3):
    results = []
    current = []
    for i, b in enumerate(data):
        if 32 <= b <= 126:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                results.append((i, ''.join(current)))
            current = []
    return results

# Search EVERY text region
print("\nExtracting all strings...")
all_strings = []

# Scan entire ROM for English text
for start in range(0, min(len(cc), 0x500000), 0x50000):
    strings = find_all_strings(cc[start:start+0x50000], 4)
    for offset, text in strings:
        if len(text) > 6:
            all_strings.append({"offset": hex(start + offset), "text": text[:60]})

# Deduplicate
seen = set()
unique = []
for s in all_strings:
    if s["text"] not in seen:
        seen.add(s["text"])
        unique.append(s)

print(f"Found {len(unique)} unique strings")

# Save
import json
with open(DATA_DIR / "chrono_cross_all_strings.json", 'w') as f:
    json.dump(unique, f, indent=2)

print("Saved to data/chrono_cross_all_strings.json")

# Also scan for game-specific data
print("\nSearching for game data...")

search_terms = [
    b'SERGE', b'KID', b'HARLE', b'LYNX', b'GUARD',
    b'ATTACK', b'DEFEND', b'ITEM', b'MAGIC',
    b'FIRE', b'ICE', b'THUNDER', b'WATER',
    b'GOLD', b'GIL', b'HP', b'MP'
]

for term in search_terms:
    count = cc.count(term)
    if count > 0:
        pos = cc.find(term)
        print(f"  {term.decode()}: {count} times, first at {hex(pos)}")
