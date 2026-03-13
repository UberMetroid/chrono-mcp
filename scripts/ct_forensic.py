#!/usr/bin/env python3
"""
Chrono Trigger - Direct Analysis
Look at specific known locations from CT research
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def dump_area(data, offset, size=256, name=""):
    """Dump an area of ROM as text"""
    print(f"\n{'='*60}")
    print(f"=== {name} (offset: {hex(offset)}) ===")
    print('='*60)
    
    chunk = data[offset:offset+size]
    
    # Show hex
    print("\nHex:")
    for i in range(0, len(chunk), 32):
        hex_str = ' '.join(f'{b:02X}' for b in chunk[i:i+32])
        print(f"  {hex(offset+i)}: {hex_str}")
    
    # Show "ASCII"
    print("\nText (ASCII-ish):")
    text = ''
    for b in chunk:
        if 0x20 <= b <= 0x7E:
            text += chr(b)
        else:
            text += '.'
    print(f"  {text[:80]}")

def main():
    data = read_rom()
    
    print("CHRONO TRIGGER - FORENSIC ANALYSIS")
    print("="*60)
    
    # These are known addresses from CT research
    # Let's look at areas that should contain game data
    
    # Look at what's around the credits
    dump_area(data, 0x117000, 256, "After Credits")
    
    # Look at a known script location (based on other SNES RPGs)
    dump_area(data, 0x200000, 256, "Script Area 1")
    
    # Another common area
    dump_area(data, 0x258000, 256, "Script Area 2")
    
    # Let's also look for ANY text in the 2MB-3MB range
    print("\n" + "="*60)
    print("SEARCHING FOR ANY READABLE TEXT IN GAME AREA")
    print("="*60)
    
    # Just scan for sequences of 3+ capital letters with spaces
    found_any = []
    for offset in range(0x100000, 0x380000, 16):
        chunk = data[offset:offset+32]
        # Count words (sequences of 3+ letters)
        words = 0
        in_word = False
        for b in chunk:
            if 0x41 <= b <= 0x5A:  # A-Z
                if not in_word:
                    words += 1
                    in_word = True
            else:
                in_word = False
        
        if words >= 2:
            # Check if it looks like real words
            text = ''.join(chr(b) if 0x20 <= b <= 0x7E else ' ' for b in chunk)
            # Skip obvious garbage
            if 'THE' in text or 'AND' in text or 'YOU' in text or 'FOR' in text or 'NOT' in text:
                found_any.append((offset, text[:40]))
    
    print(f"\nFound {len(found_any)} areas with potential text:\n")
    for offset, text in found_any[:15]:
        print(f"  {hex(offset)}: {text}")

if __name__ == "__main__":
    main()
