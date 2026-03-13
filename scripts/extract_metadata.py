#!/usr/bin/env python3
"""
Extract additional game metadata and structures
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
cc = open(BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin", 'rb').read()
rd = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", 'rb').read()

# ============ CT ANALYSIS ============

print("Analyzing Chrono Trigger...")

# Count different data types
lzss_10 = sum(1 for i in range(len(ct)-1) if ct[i] == 0x10 and ct[i+1] == 0x00)
lzss_11 = sum(1 for i in range(len(ct)-1) if ct[i] == 0x11 and ct[i+1] == 0x00)

# Find HP/MP references (for stats analysis)
hp_refs = sum(1 for i in range(len(ct)-1) if ct[i] == ord('H') and ct[i+1] == ord('P'))
mp_refs = sum(1 for i in range(len(ct)-1) if ct[i] == ord('M') and ct[i+1] == ord('P'))

ct_analysis = {
    "rom_size": len(ct),
    "rom_size_mb": round(len(ct) / 1024 / 1024, 2),
    "compression": {
        "lzss_0x10_blocks": lzss_10,
        "lzss_0x11_blocks": lzss_11,
        "total_compressed_blocks": lzss_10 + lzss_11,
    },
    "string_references": {
        "hp": hp_refs,
        "mp": mp_refs,
    },
    "known_offsets": {
        "credits": "0x250000-0x320000",
        "substring_table": "0x1EC800",
        "dialog_region": "0x100000-0x250000",
    }
}

# ============ CC ANALYSIS ============

print("Analyzing Chrono Cross...")

# Count data types
tim_count = cc.count(b'\x10\x00\x00\x00')
lzss_count = sum(1 for i in range(len(cc)-1) if cc[i] in [0x10, 0x11, 0x12] and cc[i+1] == 0x00)

# Find ISO9660 partition
iso_offset = cc.find(b'CD001')

cc_analysis = {
    "rom_size": len(cc),
    "rom_size_mb": round(len(cc) / 1024 / 1024, 2),
    "format": "PS1 CD-ROM (ISO9660)",
    "iso_partition_offset": iso_offset,
    "compression": {
        "potential_lzss_blocks": lzss_count,
    },
    "images": {
        "tim_signatures": tim_count,
    },
    "system": {
        "config_offset": 0xcaf5,
    }
}

# ============ RD ANALYSIS ============

print("Analyzing Radical Dreamers...")

# RD uses 0x81 as word separator
rd_separators = rd.count(0x81)

# Check save area
rd_save_area = rd[0x1E0000:0x1F0000]

rd_analysis = {
    "rom_size": len(rd),
    "rom_size_mb": round(len(rd) / 1024 / 1024, 2),
    "encoding": {
        "word_separator": "0x81 (@)",
    },
    "save_area": {
        "offset": "0x1E0000-0x1F0000",
        "size": "64KB",
    },
    "text_regions": {
        "primary": "0x100000-0x200000",
    }
}

# ============ SAVE ALL ============

with open(DATA_DIR / "ct_analysis.json", 'w') as f:
    json.dump(ct_analysis, f, indent=2)

with open(DATA_DIR / "cc_analysis.json", 'w') as f:
    json.dump(cc_analysis, f, indent=2)

with open(DATA_DIR / "rd_analysis.json", 'w') as f:
    json.dump(rd_analysis, f, indent=2)

print("\\nDone!")
print(f"CT: {lzss_10 + lzss_11} compressed blocks")
print(f"CC: {tim_count} TIM signatures, {lzss_count} LZSS blocks")
print(f"RD: {rd_separators} word separators")
