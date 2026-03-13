#!/usr/bin/env python3
"""Dump full ROMs"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
FULL_DIR = DATA_DIR / "full"
FULL_DIR.mkdir(exist_ok=True)

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def dump_full_rom(game_name, rom_path):
    print(f"Dumping {game_name}...")
    data = read_rom(rom_path)
    
    for i in range(0, len(data), 512*1024):
        chunk = data[i:i + 512*1024]
        with open(FULL_DIR / f"{game_name}_{i:08x}.bin", 'wb') as f:
            f.write(chunk)
        print(f"  Dumped {i:08x}")

dump_full_rom("RD", BASE_DIR / "Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc")
dump_full_rom("CT", BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc")
print("Done!")
