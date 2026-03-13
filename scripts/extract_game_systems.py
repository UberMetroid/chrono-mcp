#!/usr/bin/env python3
"""
Extract comprehensive game systems: monster drops, elemental data, status effects
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Game Systems ===\n")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()
cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

# ============ Monster Drops ============
print("--- Monster Drops ---")

drops_ct = []

for i in range(0x240000, 0x280000, 16):
    region = ct_rom[i:i+16]
    
    # Drop data: enemy_id, common_drop, rare_drop, drop_rate
    enemy_id = struct.unpack("<H", region[0:2])[0]
    common = struct.unpack("<H", region[4:6])[0]
    rare = struct.unpack("<H", region[6:8])[0]
    
    if 1 <= enemy_id <= 100 and common < 100 and rare < 100:
        drops_ct.append({
            "offset": hex(i),
            "enemy_id": enemy_id,
            "common_drop": common,
            "rare_drop": rare
        })

print(f"Found {len(drops_ct)} potential drop entries")

with open(DATA_DIR / "ct_monster_drops.json", "w") as f:
    json.dump(drops_ct[:50], f, indent=2)

# CC Drops
drops_cc = []
for i in range(0x400000, 0x500000, 16):
    region = cc_bin[i:i+16]
    
    enemy_id = struct.unpack("<H", region[0:2])[0]
    common = struct.unpack("<H", region[4:6])[0]
    rare = struct.unpack("<H", region[6:8])[0]
    
    if 1 <= enemy_id <= 300 and common < 300 and rare < 300:
        drops_cc.append({
            "enemy_id": enemy_id,
            "common_drop": common,
            "rare_drop": rare
        })

print(f"Found {len(drops_cc)} potential CC drop entries")

with open(DATA_DIR / "cc_monster_drops.json", "w") as f:
    json.dump(drops_cc[:50], f, indent=2)

# ============ Elemental Data ============
print("\n--- Elemental Data ---")

# Elements in CT: Fire, Ice, Lightning, Water, Earth, Wind, Holy, Dark, Poison
elements_ct = []

for i in range(0x200000, 0x240000, 32):
    region = ct_rom[i:i+32]
    
    # Element data: element_id, absorb, weak, immune, null
    elem_id = region[0]
    absorb = region[4]
    weak = region[8]
    
    if 1 <= elem_id <= 10:
        elements_ct.append({
            "offset": hex(i),
            "element_id": elem_id,
            "absorb": absorb,
            "weak": weak,
            "data": region[:16].hex()
        })

print(f"Found {len(elements_ct)} potential element entries")

with open(DATA_DIR / "ct_elements.json", "w") as f:
    json.dump(elements_ct[:20], f, indent=2)

# CC Elements
elements_cc = []
for i in range(0x300000, 0x400000, 32):
    region = cc_bin[i:i+32]
    
    elem_id = region[0]
    
    if 1 <= elem_id <= 15:
        elements_cc.append({
            "element_id": elem_id,
            "data": region[:16].hex()
        })

print(f"Found {len(elements_cc)} potential CC element entries")

with open(DATA_DIR / "cc_elements.json", "w") as f:
    json.dump(elements_cc[:20], f, indent=2)

# ============ Status Effects ============
print("\n--- Status Effects ---")

# Status data: poison, blind, slow, etc.
status_ct = []

for i in range(0x200000, 0x240000, 16):
    region = ct_rom[i:i+16]
    
    status_id = region[0]
    duration = struct.unpack("<H", region[2:4])[0]
    damage = struct.unpack("<H", region[4:6])[0]
    
    if 1 <= status_id <= 15:
        status_ct.append({
            "offset": hex(i),
            "status_id": status_id,
            "duration": duration,
            "damage": damage
        })

print(f"Found {len(status_ct)} potential status entries")

with open(DATA_DIR / "ct_status_effects.json", "w") as f:
    json.dump(status_ct[:20], f, indent=2)

# ============ Character Exp/Level Data ============
print("\n--- Character Level Data ---")

level_ct = []

for i in range(0x200000, 0x240000, 16):
    region = ct_rom[i:i+16]
    
    char_id = region[0]
    level = region[2]
    exp = struct.unpack("<H", region[4:6])[0]
    
    if 1 <= char_id <= 8 and 1 <= level <= 99:
        level_ct.append({
            "char_id": char_id,
            "level": level,
            "exp_needed": exp
        })

print(f"Found {len(level_ct)} potential level entries")

with open(DATA_DIR / "ct_level_data.json", "w") as f:
    json.dump(level_ct[:50], f, indent=2)

# ============ Combo/Tech Combinations ============
print("\n--- Combo Techs ---")

combos_ct = []

for i in range(0x200000, 0x240000, 16):
    region = ct_rom[i:i+16]
    
    char1 = region[0]
    char2 = region[2]
    combo_id = region[4]
    
    if 1 <= char1 <= 8 and 1 <= char2 <= 8 and char1 != char2:
        combos_ct.append({
            "char1": char1,
            "char2": char2,
            "combo_id": combo_id,
            "tech_ids": [region[6], region[8]]
        })

print(f"Found {len(combos_ct)} potential combo entries")

with open(DATA_DIR / "ct_combos.json", "w") as f:
    json.dump(combos_ct[:30], f, indent=2)

# ============ Equipment Stats ============
print("\n--- Equipment Stats ---")

# Weapon attack power, armor defense
equip_ct = []

for i in range(0x1C0000, 0x1E0000, 16):
    region = ct_rom[i:i+16]
    
    item_id = struct.unpack("<H", region[0:2])[0]
    attack = struct.unpack("<H", region[4:6])[0]
    defense = struct.unpack("<H", region[6:8])[0]
    
    if 1 <= item_id <= 100 and (attack > 0 or defense > 0):
        equip_ct.append({
            "item_id": item_id,
            "attack": attack,
            "defense": defense,
            "sample": region[:12].hex()
        })

print(f"Found {len(equip_ct)} potential equipment entries")

with open(DATA_DIR / "ct_equipment_stats.json", "w") as f:
    json.dump(equip_ct[:50], f, indent=2)

print("\n=== Game Systems Extraction Complete ===")
