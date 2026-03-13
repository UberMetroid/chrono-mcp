#!/usr/bin/env python3
"""
Extract metadata from extras (OST, Artwork, Manuals)
"""

import json
from pathlib import Path
import os

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
CT_DIR = BASE_DIR / "Chrono Trigger"

print("=== Extracting Extra Metadata ===\n")

# ============ OST TRACKS ============
print("--- OST Music ---")

ost_data = {}

for i in range(1, 4):
    ost_name = f"Chrono_Trigger_OST_{i}"
    ost_path = CT_DIR / "Chrono Trigger - MUSIC" / ost_name
    
    if ost_path.exists():
        tracks = []
        for track_file in sorted(ost_path.glob("*.mp3")):
            tracks.append({
                "filename": track_file.name,
                "size_mb": round(track_file.stat().st_size / 1024 / 1024, 2)
            })
        
        ost_data[f"ost_{i}"] = {
            "name": ost_name,
            "track_count": len(tracks),
            "tracks": tracks
        }
        print(f"  OST {i}: {len(tracks)} tracks")

# Save OST data
with open(DATA_DIR / "chrono_trigger/ct_ost.json", "w") as f:
    json.dump(ost_data, f, indent=2)

# ============ ARTWORK ============
print("\n--- Artwork ---")

artwork_path = CT_DIR / "Chrono Trigger - ARTWORK"
artwork = []

if artwork_path.exists():
    for img_file in artwork_path.glob("*"):
        if img_file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
            artwork.append({
                "filename": img_file.name,
                "size_kb": round(img_file.stat().st_size / 1024, 2),
                "type": img_file.suffix[1:].upper()
            })

print(f"  Found {len(artwork)} artwork files")

with open(DATA_DIR / "chrono_trigger/ct_artwork.json", "w") as f:
    json.dump(artwork, f, indent=2)

# ============ MANUALS/GUIDES ============
print("\n--- Manuals & Guides ---")

docs = []

for pdf_file in CT_DIR.glob("*.pdf"):
    docs.append({
        "filename": pdf_file.name,
        "size_mb": round(pdf_file.stat().st_size / 1024 / 1024, 2)
    })

print(f"  Found {len(docs)} PDF documents")

with open(DATA_DIR / "chrono_trigger/ct_manuals.json", "w") as f:
    json.dump(docs, f, indent=2)

# ============ SUMMARY ============
print("\n=== Summary ===")
print(f"OSTs: {sum(o['track_count'] for o in ost_data.values())} tracks")
print(f"Artwork: {len(artwork)} images")
print(f"Documents: {len(docs)} PDFs")
