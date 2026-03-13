#!/usr/bin/env python3
"""
Extract full dialog from Radical Dreamers
"""

rd_path = "/home/jeryd/Code/Chrono_Series/Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
rd = open(rd_path, 'rb').read()

def extract_text_region(data, start, size):
    """Extract text from a region, showing ASCII"""
    chunk = data[start:start+size]
    result = []
    i = 0
    while i < len(chunk):
        b = chunk[i]
        if 32 <= b <= 126:
            # Collect consecutive printable chars
            s = chr(b)
            j = i + 1
            while j < len(chunk) and 32 <= chunk[j] <= 126:
                s += chr(chunk[j])
                j += 1
            if len(s) >= 3:
                result.append(s)
            i = j
        else:
            i += 1
    return result

# Extract from the dialog region
print("=== RADICAL DREAMERS DIALOG (0x1C0000-0x1D0000) ===\n")

texts = extract_text_region(rd, 0x1C0000, 0x10000)
for t in texts:
    if len(t) > 5:
        print(t)

# Also look at start menu / credits
print("\n=== RADICAL DREAMERS - START/SAVE REGION ===\n")
texts2 = extract_text_region(rd, 0x150000, 0x10000)
for t in texts2:
    if len(t) > 4 and any(c.isalpha() for c in t):
        print(t)
