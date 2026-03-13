#!/usr/bin/env python3
"""
Improved Chrono Cross Dialog Extraction
Focus on proper shift-JIS / PS1 text encoding
"""

from pathlib import Path
import json
import codecs

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
cc = open(cc_path, 'rb').read()

print("=== Improved Chrono Cross Dialog Extraction ===\n")

# CC uses a variant of shift-JIS encoding
# Let's try to decode properly

def try_decode_sjis(data):
    """Try to decode as shift-JIS"""
    try:
        return data.decode('shift_jis', errors='ignore')
    except:
        return ""

def try_decode_cp932(data):
    """Try to decode as CP932 (Windows shift-JIS)"""
    try:
        return data.decode('cp932', errors='ignore')
    except:
        return ""

# CC text is typically in certain regions
# Let's search for known CC strings to find text regions

# Known CC character names to locate text
known_names = [b'SERGE', b'KID', b'GIL', b'HARLE', b'POGG', b'LETI', b'FLEU', b'VIRTU', b'NORTH', b'SOUTH', b'KARS', b'LYNX']

text_offsets = []
for name in known_names:
    pos = cc.find(name)
    if pos > 0:
        text_offsets.append(pos)
        print(f"Found {name.decode()}: {hex(pos)}")

# Text is usually in the first few MB
# Let's scan for text blocks

print("\n=== Scanning for text blocks ===")

# CC text encoding: 2-byte characters for Japanese, mixed with ASCII
# Let's find sequences of printable characters

all_dialog = []
seen = set()

# Scan in chunks
chunk_size = 100000
for chunk_start in range(0, min(len(cc), 0x10000000), chunk_size):
    chunk = cc[chunk_start:chunk_start + chunk_size]
    
    # Find sequences of printable characters
    current = []
    seq_start = 0
    
    for i in range(len(chunk)):
        b = chunk[i]
        
        # ASCII printable
        if 0x20 <= b <= 0x7E:
            if not current:
                seq_start = chunk_start + i
            current.append(b)
        # Japanese characters (0x81-0x9F, 0xE0-0xFC) 
        elif 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC:
            if not current:
                seq_start = chunk_start + i
            current.append(b)
        # Half-width katakana (0xA1-0xDF)
        elif 0xA1 <= b <= 0xDF:
            if not current:
                seq_start = chunk_start + i
            current.append(b)
        else:
            if current and len(current) >= 4:
                try:
                    text = bytes(current).decode('shift_jis', errors='ignore')
                    if len(text) >= 3:
                        # Check if it looks like dialog
                        if text not in seen:
                            seen.add(text)
                            all_dialog.append({
                                "offset": hex(seq_start),
                                "text": text[:100]
                            })
                except:
                    pass
            current = []
    
    if chunk_start % 5000000 == 0:
        print(f"  Scanned {chunk_start / 1024 / 1024:.1f} MB...")

# Also try ASCII-only extraction
print("\n=== Extracting ASCII text ===")
ascii_dialog = []

for i in range(len(cc) - 1):
    if cc[i] in [0x10, 0x11] and cc[i+1] == 0x00:
        # Could be compressed text
        pass

# Find sequences of ASCII text with spaces
current = []
start = None
for i in range(min(len(cc), 0x2000000)):
    b = cc[i]
    if 0x20 <= b <= 0x7E:
        if not start:
            start = i
        current.append(chr(b))
    else:
        if current and len(current) >= 10:
            text = ''.join(current)
            if ' ' in text:  # Multiple words
                # Filter for likely dialog
                words = text.split()
                if len(words) >= 2:
                    if text not in seen:
                        seen.add(text)
                        ascii_dialog.append({
                            "offset": hex(start),
                            "text": text[:100]
                        })
        current = []
        start = None

print(f"  Found {len(ascii_dialog)} ASCII text segments")

# Dedupe and combine
print(f"\nTotal extracted: {len(all_dialog) + len(ascii_dialog)} text segments")

# Save
combined = all_dialog + ascii_dialog
unique = []
seen = set()
for item in combined:
    if item["text"] not in seen:
        seen.add(item["text"])
        unique.append(item)

print(f"Unique: {len(unique)}")

# Filter for meaningful text
meaningful = []
common_words = {'the','a','an','is','are','was','were','to','of','and','or','but','in','on','at','for','with','i','you','he','she','it','we','they','my','your','his','her','its','our','their','this','that','what','where','when','why','how','who','can','will','would','could','should','do','does','did','have','has','had','go','come','see','know','think','say','tell','ask','get','give','make','look','want','need','feel','become','leave','put','keep','let','begin','seem','help','show','hear','play','run','move','live','believe','hold','bring','happen','write','provide','sit','stand','lose','pay','meet','include','continue','set','learn','change','lead','understand','watch','follow','stop','create','speak','read','allow','add','spend','grow','open','walk','win','offer','remember','love','consider','appear','buy','wait','serve','die','send','expect','build','stay','fall','cut','reach','kill','remain','suggest','raise','pass','sell','require','report','decide','pull','serge','kid','gil','harle','pogg','leti','fleu','virtu','north','south','east','west','kars','lynx','home','town','city','village','castle','forest','cave','tower','time','dream','radical','dreamers','chrono','cross','gate','save','load','game','start','begin','menu','select','ok','yes','no','back','return','item','magic','skill','equip','status','attack','defend','fight','battle','enemy','boss','hp','mp','level','exp','gold','gil','quest','story','world','life','death','friend','enemy','love','hate','fear','hope','wish','dream','wake','sleep','remember','forget','find','lose','kill','live','die','fight','win','lose','love','hate'}

for item in unique:
    text = item["text"]
    words = text.lower().split()
    valid = [w for w in words if w in common_words]
    if len(valid) >= 1 and len(text) > 8:
        meaningful.append(item)

print(f"Meaningful: {len(meaningful)}")

with open(DATA_DIR / "cc_dialog_complete.json", 'w') as f:
    json.dump(meaningful[:15000], f, indent=2)

print("\nSaved to cc_dialog_complete.json")
print(f"Sample:")
for item in meaningful[:10]:
    print(f"  {item['text'][:60]}")
