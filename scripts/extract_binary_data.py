#!/usr/bin/env python3
"""
Fast Dialog Extraction - focuses on key text regions
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

# Load existing dialog
with open(DATA_DIR / "cc_dialog_complete.json") as f:
    cc_existing = json.load(f)

with open(DATA_DIR / "rd_dialog_complete.json") as f:
    rd_existing = json.load(f)

with open(DATA_DIR / "ct_dialog_complete.json") as f:
    ct_existing = json.load(f)

print("=== Current Dialog Status ===")
print(f"CT: {len(ct_existing)} entries")
print(f"CC: {len(cc_existing)} entries")
print(f"RD: {len(rd_existing)} entries")

# Let's focus on extracting binary data structures
# CT character stats are at known offsets

print("\n=== Extracting CT Character Stats (Fixed Offsets) ===")

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()

# CT character data - known offsets from ROM hacking documentation
# Character base stats at around 0x1EF000 (varies by version)
# Format: 7 characters x (HP, MP, Attack, Defense, Speed, Magic) = 42 bytes

CHAR_STATS_OFFSET = 0x1EF000  # Approximate

# Extract character data
characters = []
for char_idx in range(7):
    offset = CHAR_STATS_OFFSET + (char_idx * 12)
    if offset + 12 < len(ct):
        hp = ct[offset] | (ct[offset+1] << 8)
        mp = ct[offset+2] | (ct[offset+3] << 8)
        attack = ct[offset+4] | (ct[offset+5] << 8)
        defense = ct[offset+6] | (ct[offset+7] << 8)
        speed = ct[offset+8] | (ct[offset+9] << 8)
        magic = ct[offset+10] | (ct[offset+11] << 8)
        
        characters.append({
            "index": char_idx,
            "offset": hex(offset),
            "hp": hp,
            "mp": mp,
            "attack": attack,
            "defense": defense,
            "speed": speed,
            "magic": magic
        })

print("Character stats:")
for c in characters:
    print(f"  Char {c['index']}: HP={c['hp']} MP={c['mp']} ATK={c['attack']} DEF={c['defense']} SPD={c['speed']} MAG={c['magic']}")

with open(DATA_DIR / "ct_character_stats_fixed.json", 'w') as f:
    json.dump(characters, f, indent=2)

# Extract weapon data
print("\n=== Extracting CT Weapon Data ===")
weapons = []

# Search for weapon names + stats
# Format: name (encoded), then stats

CT_FONT = {}
for i in range(26):
    CT_FONT[0xA0 + i] = chr(ord('A') + i)
for i in range(26):
    CT_FONT[0xBA + i] = chr(ord('a') + i)
for i in range(10):
    CT_FONT[0xD4 + i] = chr(ord('0') + i)

# Find weapon data around known item tables
weapon_offsets = []
for i in range(0x100000, 0x200000):
    if ct[i:i+4] == b'SWORD':
        weapon_offsets.append(i)

print(f"Found {len(weapon_offsets)} SWORD markers")

# Extract enemy data around monster locations
print("\n=== Extracting CT Enemy Stats ===")
enemies = []

# Look for boss patterns
boss_names = [b'GANON', b'GRIFF', b'LYNAS', b'NIZBEL', b'ATROPOS', b'LAVOS', b'ZEAL', b'MAGUS']

boss_locations = []
for name in boss_names:
    pos = ct.find(name)
    if pos > 0:
        boss_locations.append((pos, name.decode()))

print(f"Found {len(boss_locations)} boss locations:")
for pos, name in boss_locations:
    print(f"  {name}: {hex(pos)}")

# Save enemy locations
enemy_data = []
for pos, name in boss_locations:
    enemy_data.append({
        "name": name,
        "offset": hex(pos)
    })

with open(DATA_DIR / "ct_boss_locations.json", 'w') as f:
    json.dump(enemy_data, f, indent=2)

# Extract CC character data
print("\n=== Extracting CC Character Stats ===")
cc = open(BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin", 'rb').read()

# CC has 9 playable characters
# Stats: HP, MP, Strength, Defense, Magic, Speed, etc.

# Find character data near known offsets
cc_char_offsets = []
for name in [b'SERGE', b'KID', b'GIL', b'HARLE']:
    pos = cc.find(name)
    if pos > 0:
        cc_char_offsets.append((pos, name.decode()))

print(f"Found {len(cc_char_offsets)} CC character locations")

# Extract save data structure
print("\n=== Analyzing Save Data Structures ===")

# CT save data
ct_save = ct[0xE00000:0xE10000] if len(ct) > 0xE00000 else b''
print(f"CT save area: {len(ct_save)} bytes")

# CC save data (in SRAM)
cc_save = cc[0x1F000000:0x1F010000] if len(cc) > 0x1F000000 else b''
print(f"CC save area: {len(cc_save)} bytes")

# RD save data (BS-X cart)
rd = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", 'rb').read()
rd_save = rd[0x1E0000:0x1F0000]
print(f"RD save area: {len(rd_save)} bytes")

# Extract save data info
save_info = {
    "ct": {
        "offset": "0xE00000",
        "size": len(ct_save),
        "format": "SRAM"
    },
    "cc": {
        "offset": "0x1F000000 (estimated)",
        "size": len(cc_save),
        "format": "PS1 Memory Card"
    },
    "rd": {
        "offset": "0x1E0000",
        "size": len(rd_save),
        "format": "BS-X Flash Cart"
    }
}

with open(DATA_DIR / "save_data_info.json", 'w') as f:
    json.dump(save_info, f, indent=2)

print("\n=== Extraction Complete ===")
