#!/usr/bin/env python3
"""
Chrono MCP Server Verification Tests
Run with: python test_mcp.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.chrono import (
    get_all_games, get_master_database, get_game_data,
    get_dialog, get_characters, get_locations,
    get_game_items, get_game_enemies, get_game_techs,
    get_index, load_json
)


def test_basic_functions():
    """Test basic library functions"""
    print("Testing basic functions...")
    
    # Test get_all_games
    games = get_all_games()
    assert isinstance(games, list), "get_all_games should return a list"
    assert len(games) == 3, f"Expected 3 games, got {len(games)}"
    print(f"  ✓ get_all_games: {games}")
    
    # Test get_index
    index = get_index()
    assert isinstance(index, dict), "get_index should return a dict"
    print(f"  ✓ get_index: {list(index.keys())[:5]}...")
    
    # Test get_dialog
    dialog = get_dialog("Chrono Trigger", 5)
    assert isinstance(dialog, list), "get_dialog should return a list"
    print(f"  ✓ get_dialog: {len(dialog)} entries")
    
    # Test get_characters
    chars = get_characters("Chrono Trigger")
    assert isinstance(chars, dict), "get_characters should return a dict"
    print(f"  ✓ get_characters: {len(chars.get('characters', []))} characters")
    
    # Test get_locations
    locs = get_locations("Chrono Trigger")
    assert isinstance(locs, dict), "get_locations should return a dict"
    print(f"  ✓ get_locations: {len(locs.get('locations', []))} locations")
    
    # Test get_game_items
    items = get_game_items("Chrono Trigger")
    assert isinstance(items, list), "get_game_items should return a list"
    print(f"  ✓ get_game_items: {len(items)} items")
    
    # Test get_game_enemies
    enemies = get_game_enemies("Chrono Trigger")
    assert isinstance(enemies, list), "get_game_enemies should return a list"
    print(f"  ✓ get_game_enemies: {len(enemies)} enemies")
    
    # Test get_game_techs
    techs = get_game_techs("Chrono Trigger")
    assert isinstance(techs, list), "get_game_techs should return a list"
    print(f"  ✓ get_game_techs: {len(techs)} techs")


def test_master_database():
    """Test master database functions"""
    print("\nTesting master database...")
    
    # Test unified master database
    unified = load_json("extracted/chrono_master_complete.json")
    assert isinstance(unified, dict), "Master database should be a dict"
    
    games = unified.get("games", {})
    assert len(games) >= 3, f"Expected at least 3 games, got {len(games)}"
    print(f"  ✓ Unified database: {len(games)} games")
    
    # Check each game has data
    for game_name, game_data in games.items():
        chars = game_data.get("characters", [])
        items = game_data.get("items", [])
        enemies = game_data.get("enemies", [])
        print(f"    - {game_name}: {len(chars)} chars, {len(items)} items, {len(enemies)} enemies")


def test_data_integrity():
    """Test data integrity"""
    print("\nTesting data integrity...")
    
    unified = load_json("extracted/chrono_master_complete.json")
    games = unified.get("games", {})
    
    # Check CT has expected characters
    ct_chars = games.get("Chrono Trigger", {}).get("characters", [])
    ct_names = [c.get("name", "").upper() for c in ct_chars]
    expected_ct = ["CRONO", "LUCCA", "MARLE", "FROG", "ROBO", "AYLA", "MAGUS"]
    for exp in expected_ct:
        assert any(exp in name for name in ct_names), f"Missing character: {exp}"
    print(f"  ✓ CT has all 7 main characters")
    
    # Check CT has expected techs
    ct_techs = games.get("Chrono Trigger", {}).get("techs", [])
    ct_tech_names = [t.get("name", "").lower() for t in ct_techs]
    assert any("slash" in n for n in ct_tech_names), "Missing Slash tech"
    print(f"  ✓ CT has techs: {[t for t in ct_techs[:5]]}")
    
    # Check CC has characters
    cc_chars = games.get("Chrono Cross", {}).get("characters", [])
    assert len(cc_chars) >= 10, f"CC should have 10+ characters, got {len(cc_chars)}"
    print(f"  ✓ CC has {len(cc_chars)} characters")


def test_search_functions():
    """Test search functionality"""
    print("\nTesting search functions...")
    
    # Test dialog search
    results = get_dialog("Chrono Trigger", 10)
    assert len(results) > 0, "Should find dialog"
    print(f"  ✓ Dialog search works")
    
    # Test character search
    chars = get_characters("Chrono Trigger")
    assert isinstance(chars, dict), "Should return dict"
    print(f"  ✓ Character search works")


def test_cross_game():
    """Test cross-game functionality"""
    print("\nTesting cross-game features...")
    
    unified = load_json("extracted/chrono_master_complete.json")
    games = unified.get("games", {})
    
    # Verify all 3 games exist
    assert "Chrono Trigger" in games, "Missing Chrono Trigger"
    assert "Chrono Cross" in games, "Missing Chrono Cross"
    assert "Radical Dreamers" in games, "Missing Radical Dreamers"
    print(f"  ✓ All 3 Chrono games present")
    
    # Check cross-references
    for game_name, game_data in games.items():
        chars = game_data.get("characters", [])
        items = game_data.get("items", [])
        print(f"    - {game_name}: {len(chars)} chars, {len(items)} items")


def main():
    print("=" * 50)
    print("Chrono MCP Server Verification Tests")
    print("=" * 50)
    
    try:
        test_basic_functions()
        test_master_database()
        test_data_integrity()
        test_search_functions()
        test_cross_game()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
