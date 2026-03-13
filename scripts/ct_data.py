#!/usr/bin/env python3
"""
Chrono Trigger - Extract Gameplay Data (Lore, Items, Enemies)
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def decode_text_simple(data, offset, max_len=50):
    """Simple text decoder"""
    result = []
    for i in range(max_len):
        b = data[offset + i]
        if b == 0 or b == 0xFF:
            break
        if 0x20 <= b <= 0x7E:
            result.append(chr(b))
        elif b >= 0x80 and b <= 0x9F:
            result.append(chr(b - 0x40))  # Unshift
        else:
            result.append('.')
    return ''.join(result)

def analyze():
    data = read_rom()
    
    print("=== CHRONO TRIGGER GAMEPLAY DATA ===\n")
    
    # Credits are at 0x115000 - let's look before/after for game data
    print("--- Credits Area (0x115000) found! ---")
    print("Now searching for game data nearby...\n")
    
    # Search in the 0x100000-0x115000 range for game content
    print("--- Looking for Location Names ---")
    # Common location names
    locations = [
        'TRESOR', 'MEDIA', 'ZEAL', 'OCEAN', 'DYING', 'NORTH', 'SOUTH', 'EAST', 'WEST',
        'MOUNTAIN', 'FOREST', 'DESERT', 'ISLAND', 'CASTLE', 'TOWER', 'CAVE', 'TEMPLE',
        'FARM', 'VILLAGE', 'TOWN', 'CITY', 'RUINS', 'TOMB', 'LAKE', 'RIVER'
    ]
    
    # Search for uncompressed text blocks
    print("\n--- Scanning for Text Blocks ---")
    
    # Text in SNES is typically stored in blocks with specific markers
    # Let's look at what comes right after the credits
    print("Area after credits (0x117000):")
    for offset in range(0x117000, 0x118000, 64):
        chunk = data[offset:offset+32]
        good = sum(1 for b in chunk if (0x20 <= b <= 0x7E))
        if good > 20:
            print(f"  {hex(offset)}: {decode_text_simple(data, offset, 32)}")
    
    # Let's find the battle data
    print("\n--- Looking for Battle Messages ---")
    # Battle messages like "Victory!", "Defeat", etc. are usually uncompressed
    
    # Search the entire ROM for battle text
    for term in [b'VICTORY', b'DEFEAT', b'RUN', b'ESCAPE', b'HP', b'MP']:
        pos = data.find(term)
        if pos != -1:
            print(f"  {term.decode()}: {hex(pos)}")
            # Try to get context
            ctx = decode_text_simple(data, pos-10, 40)
            print(f"    Context: {ctx}")
    
    # Character data
    print("\n--- Looking for Character Stats ---")
    # Character data is typically at fixed offsets
    
    # Search for "CHRONO" or character names
    for name in [b'CRONO', b'LUCCA', b'MARLE', b'FROG', b'ROBO', b'AYLA', b'MAGUS']:
        pos = data.find(name)
        if pos != -1:
            print(f"  Found {name.decode()}: {hex(pos)}")
            # Dump nearby bytes
            print(f"    Nearby: {decode_text_simple(data, pos-16, 48)}")
    
    # Item names
    print("\n--- Looking for Item Names ---")
    # Common items: Potion, Ether, Phoenix Down, etc.
    items = [b'POTION', b'ETHER', b'PHOENIX', b'ANTIDOTE', b'REVIVE', b'ELIXIR', b'MASAMUNE', b'RAINBOW', b'TEARS']
    for item in items:
        pos = data.find(item)
        if pos != -1:
            print(f"  {item.decode()}: {hex(pos)}")
    
    # Magic/Tech names  
    print("\n--- Looking for Tech/Magic Names ---")
    techs = [b'FLAME', b'FIRE', b'ICE', b'BOLT', b'AERO', b'QUAKE', b'CURE', b'HEAL', b'SLASH', b'SWIRL', b'DELTA', b'CHRONO']
    for tech in techs:
        pos = data.find(tech)
        if pos != -1:
            print(f"  {tech.decode()}: {hex(pos)}")
    
    # Enemy names
    print("\n--- Looking for Enemy Names ---")
    enemies = [b'SLIME', b'GOBLIN', b'SKELETON', b'GHOST', b'DRAGON', b'ROBOT', b'MONSTER', b'BEAST', b'DEMON', b'ANGEL']
    for enemy in enemies:
        pos = data.find(enemy)
        if pos != -1:
            print(f"  {enemy.decode()}: {hex(pos)}")
            ctx = decode_text_simple(data, pos-16, 48)
            print(f"    Context: {ctx}")
    
    # The GATE / TIME locations
    print("\n--- Looking for Location/Gate Data ---")
    for term in [b'GATE', b'TIME', b'ERA', b'PERIOD', b'EPOCH']:
        pos = data.find(term)
        if pos != -1:
            print(f"  {term.decode()}: {hex(pos)}")
    
    # Now let's try to find the actual game script
    print("\n=== GAME SCRIPT ===")
    # The script is typically in a large compressed block
    # Let's look at known message locations
    
    # Search for common dialog markers
    markers = [b'SURE', b'YES', b'NO', b'OK', b'WAIT', b'LOOK', b'TALK', b'USE', b'GET', b'FIND', b'GO', b'COME', b'SEE']
    print("\n--- Common Dialog Words ---")
    for word in markers:
        pos = data.find(word)
        if pos != -1:
            print(f"  {word.decode()}: {hex(pos)}")

if __name__ == "__main__":
    analyze()
