#!/usr/bin/env python3
"""
Pytest configuration and fixtures
"""

import pytest
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def data_dir():
    """Return data directory path"""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def master_db_path(data_dir):
    """Return path to master database"""
    return data_dir / "extracted" / "chrono_master_complete.json"


@pytest.fixture
def master_db(master_db_path):
    """Load and return master database"""
    with open(master_db_path) as f:
        return json.load(f)


@pytest.fixture
def chrono_trigger_data(master_db):
    """Return Chrono Trigger game data"""
    return master_db.get("games", {}).get("Chrono Trigger", {})


@pytest.fixture
def chrono_cross_data(master_db):
    """Return Chrono Cross game data"""
    return master_db.get("games", {}).get("Chrono Cross", {})


@pytest.fixture
def radical_dreamers_data(master_db):
    """Return Radical Dreamers game data"""
    return master_db.get("games", {}).get("Radical Dreamers", {})


@pytest.fixture
def app():
    """Create Flask test client"""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from web_ui import app
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def sample_search_query():
    """Sample search query for testing"""
    return "crono"
