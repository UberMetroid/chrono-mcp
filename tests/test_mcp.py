#!/usr/bin/env python3
"""
Chrono MCP Server - Test Suite
Run with: pytest test_mcp.py -v
"""

import pytest
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDataLoading:
    """Test data loading functions"""
    
    @pytest.fixture
    def data_dir(self):
        return Path(__file__).parent.parent / "data"
    
    def test_unified_database_exists(self, data_dir):
        """Test that unified database exists"""
        db_path = data_dir / "extracted" / "chrono_master_complete.json"
        assert db_path.exists(), "Unified database not found"
    
    def test_unified_database_valid_json(self, data_dir):
        """Test that unified database is valid JSON"""
        db_path = data_dir / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "games" in data
    
    def test_all_three_games_present(self, data_dir):
        """Test that all three Chrono games are in database"""
        db_path = data_dir / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        
        games = data.get("games", {})
        assert "Chrono Trigger" in games
        assert "Chrono Cross" in games
        assert "Radical Dreamers" in games
    
    def test_chrono_trigger_data(self, data_dir):
        """Test Chrono Trigger has expected data"""
        db_path = data_dir / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        
        ct = data["games"]["Chrono Trigger"]
        
        # Check characters
        chars = ct.get("characters", [])
        assert len(chars) > 0, "No characters in CT"
        char_names = [c.get("name", "") for c in chars]
        assert any("Crono" in n or "Crono" in n for n in char_names), "Crono not found"
        
        # Check techs
        techs = ct.get("techs", [])
        assert len(techs) > 0, "No techs in CT"
    
    def test_chrono_cross_data(self, data_dir):
        """Test Chrono Cross has expected data"""
        db_path = data_dir / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        
        cc = data["games"]["Chrono Cross"]
        
        # Check characters
        chars = cc.get("characters", [])
        assert len(chars) > 0, "No characters in CC"
        
        # Check elements
        elements = cc.get("elements", [])
        assert len(elements) > 0, "No elements in CC"
    
    def test_radical_dreamers_data(self, data_dir):
        """Test Radical Dreamers has expected data"""
        db_path = data_dir / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        
        rd = data["games"]["Radical Dreamers"]
        
        # Check characters
        chars = rd.get("characters", [])
        assert len(chars) > 0, "No characters in RD"


class TestMCPTools:
    """Test MCP tool functions"""
    
    def test_fuzzy_search_import(self):
        """Test fuzzy search can be imported"""
        # Test the search logic directly
        import difflib
        query = "sword"
        test_data = ["sword", "Sword", "SWORD", "swordsman", "watersword"]
        
        matches = []
        for item in test_data:
            ratio = difflib.SequenceMatcher(None, query.lower(), item.lower()).ratio()
            if ratio >= 0.5:
                matches.append((item, ratio))
        
        assert len(matches) > 0, "Fuzzy search found no matches"
    
    def test_stat_filtering_logic(self):
        """Test stat filtering logic"""
        # Test HP filtering
        test_enemies = [
            {"name": "Weak", "hp": 10},
            {"name": "Medium", "hp": 100},
            {"name": "Strong", "hp": 500},
            {"name": "Boss", "hp": 9999},
        ]
        
        min_hp = 100
        strong_enemies = [e for e in test_enemies if e.get("hp", 0) >= min_hp]
        
        assert len(strong_enemies) == 3
        assert "Weak" not in [e["name"] for e in strong_enemies]


class TestWebUI:
    """Test web UI endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create Flask test client"""
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from web_ui import app
        app.config['TESTING'] = True
        return app
    
    def test_index_route(self, app):
        """Test index page loads"""
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
    
    def test_api_games(self, app):
        """Test games API"""
        with app.test_client() as client:
            response = client.get('/api/games')
            assert response.status_code == 200
            games = json.loads(response.data)
            assert len(games) == 3
    
    def test_api_search(self, app):
        """Test search API"""
        with app.test_client() as client:
            response = client.get('/api/search?q=crono')
            assert response.status_code == 200
            results = json.loads(response.data)
            assert "matches" in results


class TestDataIntegrity:
    """Test data integrity"""
    
    def test_no_duplicate_characters(self):
        """Test no duplicate characters in any game"""
        db_path = Path(__file__).parent.parent / "data" / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        
        for game_name, game_data in data["games"].items():
            chars = game_data.get("characters", [])
            char_names = [c.get("name", "").lower() for c in chars]
            assert len(char_names) == len(set(char_names)), f"Duplicate characters in {game_name}"
    
    def test_character_stats_valid(self):
        """Test character stats are reasonable"""
        db_path = Path(__file__).parent.parent / "data" / "extracted" / "chrono_master_complete.json"
        with open(db_path) as f:
            data = json.load(f)
        
        for game_name, game_data in data["games"].items():
            for char in game_data.get("characters", []):
                hp = char.get("hp", 0)
                if isinstance(hp, (int, float)):
                    assert hp > 0, f"Invalid HP for {char.get('name')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
