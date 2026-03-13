#!/usr/bin/env python3
"""
Comprehensive Game Data Extraction for Chrono Series
Extracts: items, weapons, armor, enemies, locations, techs
"""

from pathlib import Path
import json
import struct

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct_rom_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
ct = open(ct_rom_path, 'rb').read()

cc_rom_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
cc = open(cc_rom_path, 'rb').read()

rd_rom_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
rd = open(rd_rom_path, 'rb').read()

# ============ CHRONO TRIGGER DATA EXTRACTION ============

# CT custom font decoding
CT_FONT = {}
for i in range(26):
    CT_FONT[0xA0 + i] = chr(ord('A') + i)
for i in range(26):
    CT_FONT[0xBA + i] = chr(ord('a') + i)
for i in range(10):
    CT_FONT[0xD4 + i] = chr(ord('0') + i)
CT_FONT[0xEF] = ' '
CT_FONT[0xFF] = ' '

def decode_ct_text(data):
    """Decode CT custom encoding"""
    result = []
    for b in data:
        if b in CT_FONT:
            result.append(CT_FONT[b])
        elif 32 <= b <= 126:
            result.append(chr(b))
        elif b == 0x00:
            break
    return ''.join(result)

def find_ct_strings(min_len=4):
    """Find all encoded strings in CT"""
    results = []
    current = []
    start = None
    
    for i in range(len(ct)):
        b = ct[i]
        if b in CT_FONT:
            if start is None:
                start = i
            current.append(b)
        elif b == 0x00 or b > 0xE0:
            if current and start:
                text = decode_ct_text(bytes(current))
                if len(text) >= min_len:
                    results.append((start, text))
            current = []
            start = None
        else:
            if current and start:
                text = decode_ct_text(bytes(current))
                if len(text) >= min_len:
                    results.append((start, text))
            current = []
            start = None
    
    return results

# Extract CT strings
ct_strings = find_ct_strings(4)
print(f"Found {len(ct_strings)} CT encoded strings")

# Categorize CT data
ct_items = []
ct_weapons = []
ct_armor = []
ct_enemies = []
ct_locations = []
ct_techs = []
ct_other = []

# Known CT keywords for categorization
item_kw = ['POTION', 'ETHER', 'TENT', 'CLINIC', 'LAVARIDGE', 'ANTIDEPRESS', 'BARRIER', 'SHIELD', 'HELM', 'GLOVE', 'BOOT', 'BELT', 'SCARF', 'CAP', 'MASK', 'RING', 'EARRING', 'CHARM', 'SEED', 'HERB', 'WATER', 'STONE', 'FEATHER', 'WOOD', 'IRON', 'GOLD', 'SILVER', 'COPPER']
weapon_kw = ['SWORD', 'BLADE', 'DAGGER', 'KATANA', 'SCIMITAR', 'SPEAR', 'LANCE', 'AXE', 'HAMMER', 'MACE', 'FLAIL', 'CHAIN', 'BOW', 'CROSSBOW', 'GUN', 'BLASTER', 'LASER', 'STAFF', 'ROD', 'WAND', 'MITT', 'CLAW', 'FORK', 'WHIP']
armor_kw = ['ARMOR', 'VEST', 'ROBE', 'COAT', 'JACKET', 'SHIRT', 'SUIT', 'HASTE', 'BIKE', 'CAPE', 'CLOAK']
enemy_kw = ['GUARD', 'SOLDIER', 'KNIGHT', 'WARRIOR', 'MAGE', 'ROBOT', 'SLIME', 'BEAST', 'DRAGON', 'GHOST', 'SKELETON', 'ZOMBIE', 'BAT', 'SPIDER', 'SNAKE', 'SCORPION', 'BIRD', 'BUG', 'FISH', 'PLANT', 'ROCK', 'METEOR', 'BOSS', 'MEGA', 'GIGA', 'TERRA', 'TERROR', 'DEATH', 'DESTROY', 'RIPPER', 'STRIKER', 'RUNNER', 'FLYER', 'SWIMMER', 'CRAWLER']
location_kw = ['TOWN', 'CITY', 'VILLAGE', 'CASTLE', 'FOREST', 'CAVE', 'RUINS', 'TOWER', 'TEMPLE', 'SHRINE', 'PALACE', 'MANSION', 'FACTORY', 'LAB', 'BASE', 'PORT', 'HARBOR', 'BEACH', 'ISLAND', 'MOUNTAIN', 'MT', 'PEAK', 'SUMMIT', 'LAKE', 'RIVER', 'STREAM', 'FALL', 'PLAIN', 'FIELD', 'MEADOW', 'DESERT', 'JUNGLE', 'SWAMP', 'MORPH', 'DYNA', 'ZEAL', 'OCEAN', 'CONTINENT', 'ERA', 'AGE', 'PERIOD', 'MILLENNIUM', 'CENTURY', 'YEAR', 'DAY', 'TIME', 'GATE', 'ROOM', 'CHAMBER', 'HALL', 'CORRIDOR', 'FLOOR', 'WING']
tech_kw = ['SLASH', 'BOLT', 'FIRE', 'ICE', 'WATER', 'EARTH', 'WIND', 'LIGHT', 'DARK', 'MYSTIC', 'SWORD', 'SWEEP', 'KICK', 'PUNCH', 'BITE', 'CLAW', 'TORNADO', 'CYCLONE', 'BLACK HOLE', 'SPIN', 'WHIRL', 'RUSH', 'STRIKE', 'BREAK', 'BLAST', 'BURST', 'WAVE', 'SURGE', 'STORM', 'QUAKE', 'THUNDER', 'FLASH', 'BEAM', 'RAY', 'SPARK', 'FLAME', 'BURN', 'FREEZE', 'CHILL', 'SHOCK', 'VOLT', 'AURA', 'GLOW', 'SHINE', 'Dazzle']

for offset, text in ct_strings:
    t = text.upper()
    
    if any(kw in t for kw in item_kw):
        ct_items.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in weapon_kw):
        ct_weapons.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in armor_kw):
        ct_armor.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in enemy_kw):
        ct_enemies.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in location_kw):
        ct_locations.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in tech_kw):
        ct_techs.append({"offset": hex(offset), "text": text})

print(f"CT Items: {len(ct_items)}")
print(f"CT Weapons: {len(ct_weapons)}")
print(f"CT Armor: {len(ct_armor)}")
print(f"CT Enemies: {len(ct_enemies)}")
print(f"CT Locations: {len(ct_locations)}")
print(f"CT Techs: {len(ct_techs)}")

# Save CT data
with open(DATA_DIR / "ct_items.json", 'w') as f:
    json.dump(ct_items[:500], f, indent=2)

with open(DATA_DIR / "ct_weapons.json", 'w') as f:
    json.dump(ct_weapons[:500], f, indent=2)

with open(DATA_DIR / "ct_armor.json", 'w') as f:
    json.dump(ct_armor[:500], f, indent=2)

with open(DATA_DIR / "ct_enemies.json", 'w') as f:
    json.dump(ct_enemies[:500], f, indent=2)

with open(DATA_DIR / "ct_locations.json", 'w') as f:
    json.dump(ct_locations[:500], f, indent=2)

with open(DATA_DIR / "ct_techs.json", 'w') as f:
    json.dump(ct_techs[:500], f, indent=2)

# ============ CHRONO CROSS DATA EXTRACTION ============

print("\n=== Extracting Chrono Cross Data ===")

# Find all readable strings in CC
cc_strings = []
current = []
start = None

for i in range(min(len(cc), 0x2000000)):  # First 32MB
    b = cc[i]
    if 32 <= b <= 126:
        if start is None:
            start = i
        current.append(chr(b))
    else:
        if current and start and len(current) >= 4:
            cc_strings.append((start, ''.join(current)))
        current = []
        start = None

if current and start and len(current) >= 4:
    cc_strings.append((start, ''.join(current)))

print(f"Found {len(cc_strings)} CC strings")

# Categorize CC data
cc_items = []
cc_weapons = []
cc_armor = []
cc_enemies = []
cc_locations = []
cc_techs = []

# Known CC keywords
cc_item_kw = ['POTION', 'ETHER', 'HERB', 'SEED', 'STONE', 'GEM', 'FEATHER', 'TAIL', 'WING', 'CLAW', 'BONE', 'SHELL', 'SCALE', 'LEATHER', 'CLOTH', 'SILK', 'WOOL', 'COTTON', 'LINEN', 'WOOD', 'IRON', 'STEEL', 'MITHRIL', 'ORICHALCUM', 'GOLD', 'SILVER', 'COPPER', 'BRONZE', 'METAL', 'JEWEL', 'RING', 'EARRING', 'BRACELET', 'CHAIN', 'BELT', 'GLOVE', 'BOOT', 'SHOE', 'HELM', 'HAT', 'CAP', 'MASK', 'VISOR', 'CROWN', 'TIARA', 'BAND', 'SCARF', 'CLOAK', 'CAPE', 'ROBE', 'VEST', 'ARMOR', 'SHIELD', 'BUCKLER']
cc_weapon_kw = ['SWORD', 'BLADE', 'DAGGER', 'KATANA', 'WAKIZASHI', 'TANTO', 'SCIMITAR', 'SABER', 'SPEAR', 'LANCE', 'HALBERD', 'Pole', 'AXE', 'HAMMER', 'MACE', 'FLAIL', 'CHAIN', 'WHIP', 'BOW', 'CROSSBOW', 'GUN', 'PISTOL', 'RIFLE', 'BLASTER', 'LASER', 'STAFF', 'ROD', 'WAND', 'SCEPTRE', 'ORB', 'BOOK', 'TOME', 'SCROLL']
cc_armor_kw = ['ARMOR', 'VEST', 'ROBE', 'COAT', 'JACKET', 'SUIT', 'CAPE', 'CLOAK', 'MANTLE', 'TUNIC', 'HAUBERK', 'BREASTPLATE', 'PLATE', 'MAIL', 'CHAIN', 'LEATHER', 'PADDED', 'SILK', 'DRESS', 'KIMONO', 'UNIFORM']
cc_enemy_kw = ['GUARD', 'SOLDIER', 'KNIGHT', 'WARRIOR', 'MAGE', 'WIZARD', 'SORCERER', 'NECRO', 'ROBOT', 'MECH', 'ANDROID', 'CYBORG', 'SLIME', 'GEL', 'OOZE', 'BEAST', 'MONSTER', 'DRAGON', 'WYVERN', 'DRAKE', 'GHOST', 'SPECTER', 'WRAITH', 'SKELETON', 'ZOMBIE', 'LICH', 'VAMPIRE', 'WEREWOLF', 'BAT', 'VAMPIRE', 'SPIDER', 'SCORPION', 'SNAKE', 'WORM', 'CENTIPEDE', 'INSECT', 'BUG', 'FLY', 'WASP', 'BIRD', 'HARPY', 'GRIFFIN', 'HARPIE', 'BEAST', 'WOLF', 'FOX', 'TIGER', 'LION', 'BEAR', 'PANTHER', 'JAGUAR', 'EAGLE', 'HAWK', 'FALCON', 'CROW', 'RAVEN', 'PHOENIX', 'GOLEM', 'CONSTRUCT', 'STATUE', 'BOSS', 'ELDER', 'PRIME', 'ULTIMA', 'ATOMIC', 'PLANET', 'STAR', 'COMET', 'METEOR', 'VOID', 'NULL', 'ZERO', 'OMEGA', 'ALPHA', 'BETA', 'GAMMA', 'DELTA', 'SIGNAT', 'HEAD', 'CORE', 'HEART', 'EYE', 'HAND', 'CLAW', 'FANG', 'TUSK', 'HORN']
cc_location_kw = ['TOWN', 'CITY', 'VILLAGE', 'SETTLEMENT', 'CASTLE', 'FOREST', 'WOODS', 'JUNGLE', 'CAVE', 'DEN', 'LAIR', 'RUINS', 'RUIN', 'TOWER', 'TEMPLE', 'SHRINE', 'ALTAR', 'PALACE', 'MANSION', 'KEEP', 'FORT', 'FORTRESS', 'BASE', 'CAMP', 'PORT', 'HARBOR', 'DOCK', 'BEACH', 'SHORE', 'ISLAND', 'ISLE', 'ARCHIPELAGO', 'MOUNTAIN', 'MT', 'PEAK', 'SUMMIT', 'CLIFF', 'VALLEY', 'CANYON', 'GORGE', 'PASS', 'CAVERN', 'CAVE', 'GROTTO', 'TUNNEL', 'PIT', 'ABYSS', 'LAKE', 'POND', 'POOL', 'RIVER', 'STREAM', 'CREEK', 'FALL', 'WATERFALL', 'FOUNT', 'SPRING', 'OCEAN', 'SEA', 'PLAINS', 'FIELD', 'MEADOW', 'PASTURE', 'FARM', 'RANCH', 'DESERT', 'DUNE', 'OASIS', 'WASTE', 'VOID', 'SKY', 'CLOUD', 'AIR', 'WIND', 'HOME', 'HOUSE', 'HUT', 'CABIN', 'COTTAGE', 'SHOP', 'STORE', 'INN', 'HOTEL', 'TAVERN', 'BAR', 'RESTAURANT', 'TEMPLE', 'CHURCH', 'SHRINE', 'SCHOOL', 'ACADEMY', 'LAB', 'LABORATORY', 'FACTORY', 'MINE', 'QUARRY', 'FURNACE', 'SMELT', 'PORT', 'GATE', 'DOOR', 'ENTRANCE', 'EXIT', 'WAY', 'PATH', 'ROAD', 'STREET', 'LANE', 'ALLEY', 'BRIDGE', 'CROSSING']
cc_tech_kw = ['SLASH', 'CUT', 'STRIKE', 'BLOW', 'HIT', 'KICK', 'PUNCH', 'BITE', 'CLAW', 'SWIPE', 'THRUST', 'PIERCE', 'STAB', 'CLEAVE', 'CHOP', 'HACK', 'SLICE', 'DICE', 'MINCE', 'GRIND', 'CRUSH', 'BREAK', 'SHATTER', 'SMASH', 'BLAST', 'BURST', 'EXPLODE', 'DETONATE', 'FIRE', 'FLAME', 'BURN', 'SCORCH', 'CHAR', 'ICE', 'FREEZE', 'CHILL', 'FROST', 'BLIZZARD', 'COLD', 'BOLT', 'THUNDER', 'LIGHTNING', 'SHOCK', 'VOLT', 'ELECTRIC', 'WATER', 'WAVE', 'FLOOD', 'TSUNAMI', 'DROWN', 'WASH', 'EARTH', 'ROCK', 'STONE', 'QUAKE', 'TREMBLE', 'SHOCKWAVE', 'WIND', 'GALE', 'TORNADO', 'HURRICANE', 'TEMPEST', 'STORM', 'GUST', 'AIR', 'AERO', 'DARK', 'SHADOW', 'NIGHT', 'VOID', 'NULL', 'BLACK', 'CHAOS', 'EVIL', 'CURSE', 'POISON', 'TOXIC', 'VENOM', 'ACID', 'BILE', 'BLOOD', 'DRAIN', 'LEECH', 'SUCK', 'LIFE', 'DEATH', 'KILL', 'DESTROY', 'ERASE', 'WIPE', 'NULLIFY', 'CANCEL', 'DISPEL', 'CURE', 'HEAL', 'RECOVERY', 'RESTORE', 'REGEN', 'REVIVE', 'RESURRECT', 'ANIMATE', 'SUPPORT', 'BUFF', 'ENHANCE', 'BOOST', 'RAISE', 'LOWER', 'WEAKEN', 'STRENGTHEN', 'HARDEN', 'SOFTEN', 'QUICKEN', 'SLOW', 'STOP', 'FREEZE', 'PARALYZE', 'SLEEP', 'STUN', 'CONFUSE', 'CHARM', 'FEAR', 'TERROR', 'FRIGHT', 'SCARE', 'AWE', 'SILENCE', 'MUTE', 'BLIND', 'DEAFEN', 'SENSE', 'DETECT', 'LOCATE', 'SCAN', 'ANALYZE', 'READ', 'SEE', 'HEAR', 'SMELL', 'FEEL', 'TOUCH', 'TASTE']

for offset, text in cc_strings:
    t = text.upper()
    
    if any(kw in t for kw in cc_item_kw):
        cc_items.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in cc_weapon_kw):
        cc_weapons.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in cc_armor_kw):
        cc_armor.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in cc_enemy_kw):
        cc_enemies.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in cc_location_kw):
        cc_locations.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in cc_tech_kw):
        cc_techs.append({"offset": hex(offset), "text": text})

print(f"CC Items: {len(cc_items)}")
print(f"CC Weapons: {len(cc_weapons)}")
print(f"CC Armor: {len(cc_armor)}")
print(f"CC Enemies: {len(cc_enemies)}")
print(f"CC Locations: {len(cc_locations)}")
print(f"CC Techs: {len(cc_techs)}")

# Save CC data
with open(DATA_DIR / "cc_items.json", 'w') as f:
    json.dump(cc_items[:500], f, indent=2)

with open(DATA_DIR / "cc_weapons.json", 'w') as f:
    json.dump(cc_weapons[:500], f, indent=2)

with open(DATA_DIR / "cc_armor.json", 'w') as f:
    json.dump(cc_armor[:500], f, indent=2)

with open(DATA_DIR / "cc_enemies.json", 'w') as f:
    json.dump(cc_enemies[:500], f, indent=2)

with open(DATA_DIR / "cc_locations.json", 'w') as f:
    json.dump(cc_locations[:500], f, indent=2)

with open(DATA_DIR / "cc_techs.json", 'w') as f:
    json.dump(cc_techs[:500], f, indent=2)

# ============ RADICAL DREAMERS DATA EXTRACTION ============

print("\n=== Extracting Radical Dreamers Data ===")

# Find all readable strings in RD
rd_strings = []
current = []
start = None

for i in range(len(rd)):
    b = rd[i]
    if 32 <= b <= 126:
        if start is None:
            start = i
        current.append(chr(b))
    elif b == 0x81:  # RD separator
        if current and start and len(current) >= 4:
            rd_strings.append((start, ''.join(current)))
        current = []
        start = None
    else:
        if current and start and len(current) >= 4:
            rd_strings.append((start, ''.join(current)))
        current = []
        start = None

print(f"Found {len(rd_strings)} RD strings")

# Categorize RD data
rd_items = []
rd_enemies = []
rd_locations = []

rd_item_kw = ['POTION', 'ETHER', 'HERB', 'SEED', 'STONE', 'GEM', 'WEAPON', 'ARMOR', 'SHIELD', 'HELM', 'RING', 'KEY', 'MAP', 'CARD', 'COIN', 'GOLD', 'SILVER', 'BRONZE', 'IRON', 'WOOD', 'MAGIC', 'ITEM']
rd_enemy_kw = ['GUARD', 'SOLDIER', 'KNIGHT', 'ENEMY', 'BEAST', 'MONSTER', 'DRAGON', 'GHOST', 'SKELETON', 'ZOMBIE', 'BAT', 'SPIDER', 'BOSS', 'DEATH', 'KILL', 'FIGHT', 'BATTLE', 'WAR']
rd_location_kw = ['TOWN', 'CITY', 'VILLAGE', 'CASTLE', 'FOREST', 'CAVE', 'RUINS', 'TOWER', 'TEMPLE', 'HOME', 'HOUSE', 'SHOP', 'GATE', 'DOOR', 'ROOM', 'DUNGEON', 'LAIR', 'DEN', 'KEEP', 'FORT', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'SEA', 'OCEAN', 'LAKE', 'RIVER', 'MOUNTAIN', 'ISLAND']

for offset, text in rd_strings:
    t = text.upper()
    
    if any(kw in t for kw in rd_item_kw):
        rd_items.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in rd_enemy_kw):
        rd_enemies.append({"offset": hex(offset), "text": text})
    elif any(kw in t for kw in rd_location_kw):
        rd_locations.append({"offset": hex(offset), "text": text})

print(f"RD Items: {len(rd_items)}")
print(f"RD Enemies: {len(rd_enemies)}")
print(f"RD Locations: {len(rd_locations)}")

# Save RD data
with open(DATA_DIR / "rd_items.json", 'w') as f:
    json.dump(rd_items[:500], f, indent=2)

with open(DATA_DIR / "rd_enemies.json", 'w') as f:
    json.dump(rd_enemies[:500], f, indent=2)

with open(DATA_DIR / "rd_locations.json", 'w') as f:
    json.dump(rd_locations[:500], f, indent=2)

# ============ CREATE MASTER DATABASE ============

master_db = {
    "games": {
        "Chrono Trigger": {
            "items": len(ct_items),
            "weapons": len(ct_weapons),
            "armor": len(ct_armor),
            "enemies": len(ct_enemies),
            "locations": len(ct_locations),
            "techs": len(ct_techs),
            "dialog": 251,
            "credits": 8467,
        },
        "Chrono Cross": {
            "items": len(cc_items),
            "weapons": len(cc_weapons),
            "armor": len(cc_armor),
            "enemies": len(cc_enemies),
            "locations": len(cc_locations),
            "techs": len(cc_techs),
            "dialog": 384,
            "tim_images": 20,
        },
        "Radical Dreamers": {
            "items": len(rd_items),
            "enemies": len(rd_enemies),
            "locations": len(rd_locations),
            "dialog": 2523,
        },
    }
}

with open(DATA_DIR / "master_database.json", 'w') as f:
    json.dump(master_db, f, indent=2)

print("\n=== Extraction Complete ===")
print(f"Total data files created in {DATA_DIR}")
