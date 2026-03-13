#!/usr/bin/env python3
"""
Comprehensive Binary Data Extractor for Chrono Trigger
Uses known ROM offsets and data structure analysis
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()

print("=== Comprehensive CT Binary Data Extraction ===\n")

# ============ CT Character Data ============
# Known offsets from CT ROM research
# Character data starts around 0x1Dxxxx - 0x1Exxxx

# Let's search for character HP values more intelligently
# CT characters have HP in range: Crono(100-999), Marle(80-999), etc.

def find_hp_tables():
    """Find character HP tables by looking for pattern of 7 HP values"""
    hp_tables = []
    
    for offset in range(0x100000, 0x300000, 10):
        if offset + 20 > len(ct):
            break
        
        # Look for 7 consecutive 2-byte values in HP range
        values = []
        for i in range(7):
            pos = offset + (i * 2)
            if pos + 2 <= len(ct):
                val = ct[pos] | (ct[pos+1] << 8)
                if 10 <= val <= 999:
                    values.append(val)
                else:
                    break
        
        # Check if we found 7 values AND they look like character HP
        if len(values) == 7:
            # Check pattern: first 3 chars usually have higher HP
            if values[0] >= 50 and values[1] >= 50 and values[2] >= 50:
                hp_tables.append({
                    "offset": hex(offset),
                    "hp_values": values,
                    "likely_characters": ["Crono", "Marle", "Lucca", "Robo", "Frog", "Ayla", "Magus"]
                })
    
    return hp_tables

hp_tables = find_hp_tables()
print(f"Found {len(hp_tables)} potential HP tables")

# Use the first valid one
character_stats = None
if hp_tables:
    # Take the one that looks most like character data
    for table in hp_tables:
        if table["hp_values"][0] > 50:  # Crono's HP
            character_stats = table
            break
    
    if character_stats:
        print(f"\nCharacter Stats at {character_stats['offset']}:")
        for i, (name, hp) in enumerate(zip(character_stats["likely_characters"], character_stats["hp_values"])):
            print(f"  {name}: HP={hp}")

# ============ Character MP ============
# Find MP table (follows HP table usually)

def find_mp_tables():
    """Find character MP tables"""
    mp_tables = []
    
    for offset in range(0x100000, 0x300000, 10):
        if offset + 14 > len(ct):
            break
        
        values = []
        for i in range(7):
            pos = offset + (i * 2)
            if pos + 2 <= len(ct):
                val = ct[pos] | (ct[pos+1] << 8)
                if 0 <= val <= 99:
                    values.append(val)
                else:
                    break
        
        if len(values) == 7:
            mp_tables.append({
                "offset": hex(offset),
                "mp_values": values
            })
    
    return mp_tables

mp_tables = find_mp_tables()
if mp_tables:
    print(f"\nFound {len(mp_tables)} potential MP tables")
    for table in mp_tables[:1]:
        print(f"  MP at {table['offset']}: {table['mp_values']}")

# ============ Enemy Data ============
# Enemies have: name (text), HP, EXP, gold

# First find enemy names in the ROM
CT_FONT = {}
for i in range(26):
    CT_FONT[0xA0 + i] = chr(ord('A') + i)
for i in range(26):
    CT_FONT[0xBA + i] = chr(ord('a') + i)
for i in range(10):
    CT_FONT[0xD4 + i] = chr(ord('0') + i)
CT_FONT[0xEF] = ' '

def decode_ct_text_bytes(data):
    result = []
    for b in data:
        if b in CT_FONT:
            result.append(CT_FONT[b])
        elif 0x41 <= b <= 0x5A:
            result.append(chr(b))
        elif 0x61 <= b <= 0x7A:
            result.append(chr(b))
    return ''.join(result)

# Find enemies with their stats
enemies_with_stats = []
enemy_keywords = ['GUARD', 'ROBOT', 'SOLD', 'BIRD', 'BEAST', 'DRAGON', 'GHOST', 'SLIME', 'BAT', 'SPIDER', 'MAGE', 'KNIGHT', 'WARRIOR', 'TEMPLAR']

for i in range(0x100000, 0x300000):
    if ct[i] in CT_FONT:
        # Potential enemy name
        name_bytes = []
        j = i
        while j < min(i+15, len(ct)) and ct[j] in CT_FONT:
            name_bytes.append(ct[j])
            j += 1
        
        if len(name_bytes) >= 4:
            name = decode_ct_text_bytes(bytes(name_bytes)).strip()
            
            # Check if it matches enemy keywords
            if any(kw in name.upper() for kw in enemy_keywords):
                # Look for HP after name
                if j + 4 < len(ct):
                    hp = ct[j] | (ct[j+1] << 8)
                    exp = ct[j+2] | (ct[j+3] << 8)
                    
                    if 1 <= hp <= 99999 and 0 <= exp <= 99999:
                        enemies_with_stats.append({
                            "offset": hex(i),
                            "name": name,
                            "hp": hp,
                            "exp": exp
                        })

print(f"\nFound {len(enemies_with_stats)} enemies with stats")
for e in enemies_with_stats[:10]:
    print(f"  {e['name']}: HP={e['hp']} EXP={e['exp']}")

# ============ Item Data ============
# Items have: name, price, atk/def bonus

items_with_stats = []
item_keywords = ['SWORD', 'BLADE', 'GUN', 'STAFF', 'ROD', 'MITT', 'CAP', 'HELM', 'VEST', 'ROBE', 'COAT', 'BOOT', 'GLOVE', 'BELT', 'RING', 'EARRING', 'CHARM', 'SCARF', 'POTION', 'ETHER', 'TENT', 'SEED', 'HERB', 'WATER']

for i in range(0x100000, 0x300000):
    if ct[i] in CT_FONT:
        name_bytes = []
        j = i
        while j < min(i+15, len(ct)) and ct[j] in CT_FONT:
            name_bytes.append(ct[j])
            j += 1
        
        if len(name_bytes) >= 3:
            name = decode_ct_text_bytes(bytes(name_bytes)).strip()
            
            if any(kw in name.upper() for kw in item_keywords):
                # Look for price after name
                if j + 2 < len(ct):
                    price = ct[j] | (ct[j+1] << 8)
                    
                    if 1 <= price <= 99999:
                        items_with_stats.append({
                            "offset": hex(i),
                            "name": name,
                            "price": price
                        })

print(f"\nFound {len(items_with_stats)} items with prices")

# Dedupe and save
seen = set()
unique_enemies = []
for e in enemies_with_stats:
    if e["name"] not in seen and len(e["name"]) > 2:
        seen.add(e["name"])
        unique_enemies.append(e)

seen = set()
unique_items = []
for item in items_with_stats:
    if item["name"] not in seen and len(item["name"]) > 2:
        seen.add(item["name"])
        unique_items.append(item)

print(f"\nUnique enemies: {len(unique_enemies)}")
print(f"Unique items: {len(unique_items)}")

# Save
with open(DATA_DIR / "ct_enemies_binary.json", 'w') as f:
    json.dump(unique_enemies[:200], f, indent=2)

with open(DATA_DIR / "ct_items_binary.json", 'w') as f:
    json.dump(unique_items[:200], f, indent=2)

if character_stats:
    with open(DATA_DIR / "ct_character_stats_binary.json", 'w') as f:
        json.dump([character_stats], f, indent=2)

print("\n=== Binary Data Extraction Complete ===")
