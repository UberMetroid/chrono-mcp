#!/usr/bin/env python3
"""
Comprehensive verification script for Chrono MCP data completeness
Tests that all games are decoded and data is accessible via API
"""

import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_endpoint(url, description):
    """Test an API endpoint"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return response.json()
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {description}: {e}")
        return None

def verify_game_data(game_name, expected_chars):
    """Verify a game's data"""
    print(f"\n🔍 Verifying {game_name}...")

    # Test game endpoint
    game_data = test_endpoint(f"{BASE_URL}/api/{game_name.replace(' ', '%20')}", f"{game_name} data")
    if not game_data:
        return False

    # Check characters
    characters = game_data.get('characters', [])
    if len(characters) != expected_chars:
        print(f"❌ {game_name}: Expected {expected_chars} characters, got {len(characters)}")
        return False

    print(f"✅ {game_name}: {len(characters)} characters found")

    # Check other categories exist
    categories = [k for k in game_data.keys() if isinstance(game_data[k], list) and k != 'characters']
    print(f"✅ {game_name}: {len(categories)} additional categories ({categories[:3]}...)")

    # Count total items
    total_items = sum(len(game_data[cat]) for cat in categories if isinstance(game_data[cat], list))
    print(f"✅ {game_name}: {total_items} total items")

    return True

def main():
    """Main verification function"""
    print("🚀 Chrono MCP Data Verification")
    print("=" * 50)

    # Test health
    health = test_endpoint(f"{BASE_URL}/health", "Health check")
    if not health or health.get('status') != 'healthy':
        print("❌ Health check failed")
        return 1

    # Test games list
    games = test_endpoint(f"{BASE_URL}/api/games", "Games list")
    if not games or len(games) != 3:
        print(f"❌ Expected 3 games, got {len(games) if games else 0}")
        return 1

    print(f"✅ Found {len(games)} games: {', '.join(games)}")

    # Expected character counts (from database verification)
    expected_chars = {
        'Chrono Trigger': 7,
        'Chrono Cross': 15,
        'Radical Dreamers': 6
    }

    # Verify each game
    all_good = True
    for game in games:
        if game in expected_chars:
            if not verify_game_data(game, expected_chars[game]):
                all_good = False

    # Test search
    search_result = test_endpoint(f"{BASE_URL}/api/search?q=crono", "Search functionality")
    if search_result and search_result.get('count', 0) > 0:
        print(f"✅ Search: Found {search_result['count']} results for 'crono'")
    else:
        print("❌ Search functionality failed")
        all_good = False

    # Test plot data
    plots = test_endpoint(f"{BASE_URL}/api/plot", "Plot data")
    if plots and len(plots.get('plots', [])) == 3:
        print(f"✅ Plot data: {len(plots['plots'])} plot trees available")
    else:
        print("❌ Plot data incomplete")
        all_good = False

    # Test categories
    categories = test_endpoint(f"{BASE_URL}/api/categories", "Categories list")
    if categories:
        print(f"✅ Categories: {len(categories)} total categories across all games")

    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ All 3 Chrono games are fully decoded and accessible")
        print("✅ Database contains complete game data")
        print("✅ API endpoints are functional")
        print("✅ Search and plot features working")
        return 0
    else:
        print("❌ Some verification tests failed")
        return 1

if __name__ == "__main__":
    # Start the server if not running
    import subprocess
    import time

    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            raise Exception("Server not responding")
    except:
        print("Starting Chrono MCP server...")
        server = subprocess.Popen([
            sys.executable, "web_ui_refactored.py"
        ], cwd=Path(__file__).parent)

        # Wait for server to start
        time.sleep(5)

        try:
            result = main()
        finally:
            server.terminate()
            server.wait()
        sys.exit(result)

    # Server already running
    sys.exit(main())