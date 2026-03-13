#!/usr/bin/env python3
"""
Extract monster AI/scripts from Chrono Trigger
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Monster AI/Scripts ===\n")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

ct_enemies = json.load(open(DATA_DIR / "ct_enemies_binary.json"))

print(f"Loaded {len(ct_enemies)} enemies")

ai_scripts = []

ai_opcodes = set()
for i in range(0x2D0000, 0x2F0000):
    if ct_rom[i] in range(0x00, 0x20):
        ai_opcodes.add(ct_rom[i])

print(f"Found potential AI opcodes: {sorted(ai_opcodes)}")

ai_locations = []

for offset in range(0x2D0000, 0x300000, 16):
    region = ct_rom[offset:offset+32]
    
    ai_bytes = 0
    for b in region:
        if b in [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            ai_bytes += 1
    
    if ai_bytes >= 16:
        ai_locations.append({
            "offset": hex(offset),
            "data": region.hex(),
            "ai_score": ai_bytes
        })

ai_locations = sorted(ai_locations, key=lambda x: x["ai_score"], reverse=True)[:100]

print(f"\nFound {len(ai_locations)} potential AI script locations")

def decode_ai_script(data):
    ops = []
    i = 0
    while i < min(len(data), 50):
        b = data[i]
        if b == 0x00:
            ops.append("END")
            break
        elif b == 0x01:
            ops.append(f"ATTACK")
        elif b == 0x02:
            ops.append(f"COUNTER")
        elif b == 0x03:
            target = data[i+1] if i+1 < len(data) else 0
            ops.append(f"TECH {target}")
        elif b == 0x04:
            ops.append(f"RANDOM")
        elif b == 0x05:
            ops.append(f"WAIT")
        elif b == 0x06:
            ops.append(f"MAGIC")
        elif b == 0x07:
            ops.append(f"HEAL")
        elif b == 0x08:
            ops.append(f"STATUS")
        elif b == 0x09:
            ops.append(f"JUMP")
        elif b == 0x0A:
            ops.append(f"CALL")
        elif b == 0x0B:
            ops.append(f"RETURN")
        elif b == 0x0C:
            ops.append(f"SELECT")
        else:
            ops.append(f"UNK_{b:02X}")
        i += 1
    
    return " | ".join(ops[:10])

scripts_extracted = []
for loc in ai_locations[:20]:
    offset = int(loc["offset"], 0)
    script_data = bytearray()
    for i in range(offset, min(offset + 256, len(ct_rom))):
        b = ct_rom[i]
        if b == 0x00 or b == 0xFF:
            break
        script_data.append(b)
    
    scripts_extracted.append({
        "offset": loc["offset"],
        "length": len(script_data),
        "data": script_data.hex(),
        "disasm": decode_ai_script(script_data)
    })

with open(DATA_DIR / "ct_ai_scripts.json", "w") as f:
    json.dump(scripts_extracted, f, indent=2)

print(f"Saved {len(scripts_extracted)} AI scripts")

print("\n--- Finding Enemy AI Pointers ---")

enemy_ai_ptrs = []
for i in range(0x2C0000, 0x2D0000, 4):
    ptr = struct.unpack("<L", ct_rom[i:i+4])[0]
    if 0x2D0000 <= ptr < 0x300000:
        enemy_ai_ptrs.append({
            "pointer_offset": hex(i),
            "target": hex(ptr),
            "offset_value": ptr - 0x2D0000
        })

print(f"Found {len(enemy_ai_ptrs)} potential AI pointers")

with open(DATA_DIR / "ct_ai_pointers.json", "w") as f:
    json.dump(enemy_ai_ptrs[:50], f, indent=2)

print("\n=== Monster AI Extraction Complete ===")
