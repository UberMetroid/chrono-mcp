#!/usr/bin/env python3
"""
Fix and improve Chrono Trigger data with proper text encoding
"""

import json
import struct
from pathlib import Path

BASE = Path("/home/jeryd/Code/Chrono_Series")
DATA = BASE / "data"
ROM_PATH = BASE / "Chrono Trigger" / "Chrono Trigger (MSU1) (Audio Orchestral) (USA) (1995) (Role Playing) (Super Nes)" / "Chrono_Trigger_(USA)_(MSU1).sfc"

# CT text encoding table
CT_ENCODE = {
    0xa0: 'A', 0xa1: 'B', 0xa2: 'C', 0xa3: 'D', 0xa4: 'E',
    0xa5: 'F', 0xa6: 'G', 0xa7: 'H', 0xa8: 'I', 0xa9: 'J',
    0xaa: 'K', 0xab: 'L', 0xac: 'M', 0xad: 'N', 0xae: 'O',
    0xaf: 'P', 0xb0: 'Q', 0xb1: 'R', 0xb2: 'S', 0xb3: 'T',
    0xb4: 'U', 0xb5: 'V', 0xb6: 'W', 0xb7: 'X', 0xb8: 'Y', 0xb9: 'Z',
    0xba: 'a', 0xbb: 'b', 0xbc: 'c', 0xbd: 'd', 0xbe: 'e',
    0xbf: 'f', 0xc0: 'g', 0xc1: 'h', 0xc2: 'i', 0xc3: 'j',
    0xc4: 'k', 0xc5: 'l', 0xc6: 'm', 0xc7: 'n', 0xc8: 'o',
    0xc9: 'p', 0xca: 'q', 0xcb: 'r', 0xcc: 's', 0xcd: 't',
    0xce: 'u', 0xcf: 'v', 0xd0: 'w', 0xd1: 'x', 0xd2: 'y', 0xd3: 'z',
    0xd4: '0', 0xd5: '1', 0xd6: '2', 0xd7: '3', 0xd8: '4',
    0xd9: '5', 0xda: '6', 0xdb: '7', 0xdc: '8', 0xdd: '9',
    0xde: '!', 0xdf: '?',
    0xe0: ' ', 0xe1: ',', 0xe2: '.', 0xe3: '-',
    0xe4: '\'', 0xe5: '"', 0xe6: '/',
}

def decode_ct_text(data):
    """Decode CT text encoding"""
    result = []
    for b in data:
        if b == 0:
            break
        elif b in CT_ENCODE:
            result.append(CT_ENCODE[b])
        elif 0x20 <= b <= 0x7e:
            result.append(chr(b))
        else:
            result.append('?')
    return ''.join(result).strip()

print("=== Improving CT Data ===\n")

# Load ROM
with open(ROM_PATH, 'rb') as f:
    rom = f.read()

# Fix items
print("Fixing items...")
with open(DATA / "chrono_trigger/ct_items_binary.json") as f:
    items = json.load(f)

fixed_items = []
for item in items:
    offset = int(item['offset'], 0)
    # Read name from ROM at correct offset
    name_data = rom[offset:offset+16]
    name = decode_ct_text(name_data)
    
    fixed_items.append({
        "offset": item['offset'],
        "name": name,
        "price": item.get('price', 0)
    })

with open(DATA / "chrono_trigger/ct_items_fixed.json", "w") as f:
    json.dump(fixed_items, f, indent=2)
print(f"  Fixed {len(fixed_items)} items")

# Fix enemies
print("\nFixing enemies...")
with open(DATA / "chrono_trigger/ct_enemies_binary.json") as f:
    enemies = json.load(f)

fixed_enemies = []
for enemy in enemies:
    offset = int(enemy['offset'], 0)
    name_data = rom[offset:offset+12]
    name = decode_ct_text(name_data)
    
    fixed_enemies.append({
        "offset": enemy['offset'],
        "name": name,
        "hp": enemy.get('hp', 0),
        "exp": enemy.get('exp', 0)
    })

with open(DATA / "chrono_trigger/ct_enemies_fixed.json", "w") as f:
    json.dump(fixed_enemies, f, indent=2)
print(f"  Fixed {len(fixed_enemies)} enemies")

# Fix locations
print("\nFixing locations...")
with open(DATA / "chrono_trigger/ct_locations.json") as f:
    locations = json.load(f)

fixed_locations = []
seen = set()
for loc in locations:
    offset = int(loc['offset'], 0)
    text_data = rom[offset:offset+20]
    name = decode_ct_text(text_data)
    
    if name and name not in seen and len(name) > 1:
        seen.add(name)
        fixed_locations.append({
            "offset": loc['offset'],
            "name": name
        })

with open(DATA / "chrono_trigger/ct_locations_fixed.json", "w") as f:
    json.dump(fixed_locations, f, indent=2)
print(f"  Fixed {len(fixed_locations)} locations")

# Fix shops
print("\nFixing shops...")
with open(DATA / "chrono_trigger/ct_shops.json") as f:
    shops = json.load(f)

fixed_shops = []
for shop in shops:
    fixed_shops.append({
        "name": shop.get('name', 'Unknown'),
        "offset": shop.get('offset', ''),
        "items": shop.get('items', [])
    })

with open(DATA / "chrono_trigger/ct_shops_fixed.json", "w") as f:
    json.dump(fixed_shops, f, indent=2)
print(f"  Fixed {len(fixed_shops)} shops")

print("\n=== Data Improvement Complete ===")
