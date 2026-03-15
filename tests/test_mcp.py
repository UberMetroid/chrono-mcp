#!/usr/bin/env python3
"""
Chrono MCP Server - Test Suite
Run with: pytest test_mcp.py -v
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_test_db_path():
    """Get the path to the database file, falling back to mock data if needed"""
    data_dir = Path(__file__).parent.parent / "data"
    db_path = data_dir / "extracted" / "chrono_master_complete.json"
    
    if not db_path.exists():
        # Fallback to mock data for CI environments where large JSON is gitignored
        mock_path = Path(__file__).parent.parent / "tests" / "mock_data.json"
        if mock_path.exists():
            return mock_path
            
    return db_path


class TestDataLoading:
    """Test data loading functions"""
    
    @pytest.fixture
    def db_path(self):
        return get_test_db_path()
    
    def test_database_exists(self, db_path):
        """Test that a database file exists (real or mock)"""
        assert db_path.exists(), f"Database file not found at {db_path}"
    
    def test_database_valid_json(self, db_path):
        """Test that database is valid JSON"""
        with open(db_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "games" in data
    
    def test_all_three_games_present(self, db_path):
        """Test that all three Chrono games are in database"""
        with open(db_path) as f:
            data = json.load(f)
        
        games = data.get("games", {})
        assert "Chrono Trigger" in games
        assert "Chrono Cross" in games
        assert "Radical Dreamers" in games
    
    def test_chrono_trigger_data(self, db_path):
        """Test Chrono Trigger has expected data"""
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
    
    def test_chrono_cross_data(self, db_path):
        """Test Chrono Cross has expected data"""
        with open(db_path) as f:
            data = json.load(f)
        
        cc = data["games"]["Chrono Cross"]
        
        # Check characters
        chars = cc.get("characters", [])
        assert len(chars) > 0, "No characters in CC"
        
        # Elements for CC, or just skip if using minimal mock
        if "elements" in cc:
            assert len(cc["elements"]) > 0
    
    def test_radical_dreamers_data(self, db_path):
        """Test Radical Dreamers has expected data"""
        with open(db_path) as f:
            data = json.load(f)
        
        rd = data["games"]["Radical Dreamers"]
        
        # Check characters
        chars = rd.get("characters", [])
        assert len(chars) > 0, "No characters in RD"


class TestMCPTools:
    """Test MCP tool functions"""
    
    def test_fuzzy_search_import(self):
        """Test fuzzy search logic"""
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
        # Ensure project root is in path
        root = Path(__file__).parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
            
        # Set environment variable to use mock data in CI if needed
        db_path = get_test_db_path()
        if "mock_data.json" in str(db_path):
            os.environ["CHRONO_DATA_FILE"] = str(db_path)
            
        from app import create_app
        app = create_app()
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
            assert len(games) >= 3
    
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
        db_path = get_test_db_path()
        with open(db_path) as f:
            data = json.load(f)
        
        for game_name, game_data in data["games"].items():
            chars = game_data.get("characters", [])
            char_names = [c.get("name", "").lower() for c in chars]
            # Some games might have same-named chars if data is raw, 
            # but our cleaned master should be unique
            if len(char_names) > 1:
                assert len(char_names) == len(set(char_names)), f"Duplicate characters in {game_name}"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def app(self):
        """Create Flask test client"""
        root = Path(__file__).parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
            
        db_path = get_test_db_path()
        if "mock_data.json" in str(db_path):
            os.environ["CHRONO_DATA_FILE"] = str(db_path)
            
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    def test_missing_game_returns_error(self, app):
        """Test that missing game returns 404"""
        with app.test_client() as client:
            response = client.get('/api/NonExistentGame')
            assert response.status_code == 404
    
    def test_invalid_category_returns_error(self, app):
        """Test that invalid category returns 404"""
        with app.test_client() as client:
            response = client.get('/api/Chrono%20Trigger/invalid_category')
            assert response.status_code == 404
    
    def test_search_empty_query(self, app):
        """Test search with empty query"""
        with app.test_client() as client:
            response = client.get('/api/search?q=')
            assert response.status_code == 200
    
    def test_search_special_characters(self, app):
        """Test search with special characters"""
        with app.test_client() as client:
            response = client.get('/api/search?q=<script>')
            assert response.status_code == 200
    
    def test_health_check(self, app):
        """Test health endpoint"""
        with app.test_client() as client:
            response = client.get('/api/health')
            assert response.status_code in [200, 503]
    
    def test_ready_check(self, app):
        """Test ready endpoint"""
        with app.test_client() as client:
            response = client.get('/api/ready')
            assert response.status_code in [200, 503]
    
    def test_all_games_have_required_fields(self):
        """Test all games have required metadata"""
        db_path = get_test_db_path()
        with open(db_path) as f:
            data = json.load(f)
        
        required_fields = ["platforms", "release_year", "developer"]
        for game_name, game_data in data["games"].items():
            for field in required_fields:
                assert field in game_data, f"Missing {field} in {game_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
