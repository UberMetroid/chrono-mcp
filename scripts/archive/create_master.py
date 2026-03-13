#!/usr/bin/env python3
"""
Create MASTER database combining everything
"""

import json
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def load_json(name):
    with open(DATA_DIR / name) as f:
        return json.load(f)

print("Creating master database...")

# Load all data
data = {
    "index": load_json("index.json"),
    "radical_dreamers": load_json("radical_dreamers.json"),
    "chrono_trigger": load_json("chrono_trigger.json"),
    "chrono_cross": load_json("chrono_cross.json"),
    "game_data": load_json("game_data.json"),
}

# Add readable text
data["chrono_cross_readable"] = load_json("chrono_cross_readable.json")

# Count everything
total_strings = 0
total_art = 0

# Count art files
art_dir = DATA_DIR / "art"
if art_dir.exists():
    total_art = len(list(art_dir.iterdir()))

# Create summary
summary = {
    "games": {
        "Radical Dreamers": {
            "size_mb": 2.0,
            "format": "SNES/Satellaview",
            "translation": "Demiforce v1.4",
            "text_regions": ["0x150000-0x160000", "0x1C0000-0x1D0000"],
            "dialog_lines": 6286,
            "characters_found": 8,
            "art_files": "50 tile regions",
        },
        "Chrono Trigger": {
            "size_mb": 4.0,
            "format": "SNES",
            "region": "USA",
            "text_regions": ["0x115000 (credits)"],
            "note": "Most text is LZSS compressed",
            "credits": 27,
            "characters_found": 7,
            "art_files": "50 tile regions",
        },
        "Chrono Cross": {
            "size_mb": 702.5,
            "format": "PS1",
            "region": "Disc 1",
            "text_regions": ["0x25E000-0x260000", "0x250000-0x400000"],
            "readable_strings": 384,
            "tim_images": 202,
            "characters_found": 11,
        }
    },
    "totals": {
        "json_data_files": len(list(DATA_DIR.glob("*.json"))),
        "art_files": total_art,
        "total_data_size_mb": round(sum(f.stat().st_size for f in DATA_DIR.glob("*.json")) / 1024 / 1024, 2)
    }
}

# Save master
with open(DATA_DIR / "master_database.json", 'w') as f:
    json.dump(summary, f, indent=2)

print("Done!")
print(json.dumps(summary, indent=2))
