#!/usr/bin/env python3
"""
Convert extracted PPM images to PNG format
"""

from pathlib import Path
from PIL import Image
import os

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
ART_DIR = BASE_DIR / "data" / "art"
OUTPUT_DIR = ART_DIR / "png"

OUTPUT_DIR.mkdir(exist_ok=True)

ppm_files = list(ART_DIR.glob("*.ppm"))
print(f"Found {len(ppm_files)} PPM files")

converted = 0
for ppm_path in ppm_files:
    try:
        img = Image.open(ppm_path)
        png_name = ppm_path.stem + ".png"
        png_path = OUTPUT_DIR / png_name
        img.save(png_path)
        converted += 1
        print(f"  Converted: {png_name}")
    except Exception as e:
        print(f"  Failed: {ppm_path.name} - {e}")

print(f"\nConverted {converted}/{len(ppm_files)} images to {OUTPUT_DIR}")
