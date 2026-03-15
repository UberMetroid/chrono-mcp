import json
import os
import re
import time
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from functools import lru_cache
from app.config import get_config
from app.models.database import db_service

config = get_config()
logger = logging.getLogger(__name__)

# Global cache variables (will be moved to Redis later)
_data_cache: Optional[Dict[str, Any]] = None
_load_error: Optional[str] = None
_cache_hits = 0
_cache_misses = 0

# Cache settings
MAX_RETRIES = 3
RETRY_DELAY = 1.0

@lru_cache(maxsize=100)
def sanitize_input(text: str, max_length: int = 100) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""

    # Remove dangerous characters that could be used for injection
    text = re.sub(r'[<>\"\';&|`$()\\\\]', '', text)

    # Limit length
    return text[:max_length].strip()

@lru_cache(maxsize=50)
def validate_game_name(game: str) -> Optional[str]:
    """Validate and normalize game name"""
    if not game:
        return None

    game = sanitize_input(game, max_length=50)

    # Valid game names map
    valid_games_map = {
        'chrono_trigger': 'Chrono Trigger',
        'ct': 'Chrono Trigger',
        'chrono_cross': 'Chrono Cross',
        'cc': 'Chrono Cross',
        'radical_dreamers': 'Radical Dreamers',
        'rd': 'Radical Dreamers'
    }

    game_lower = game.lower().replace(' ', '_').replace('%20', '_')

    # Direct match
    if game_lower in valid_games_map:
        return valid_games_map[game_lower]

    # Fuzzy matching
    for key, proper_name in valid_games_map.items():
        if game_lower in key or key in game_lower:
            return proper_name

    return game  # Return sanitized input if no match, let DB handle it

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    total_requests = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total_requests * 100) if total_requests > 0 else 0

    return {
        "hits": _cache_hits,
        "misses": _cache_misses,
        "hit_rate": round(hit_rate, 2),
        "total_requests": total_requests,
        "cache_size": len(_data_cache) if _data_cache else 0
    }

def clear_cache():
    """Clear the data cache"""
    global _data_cache, _load_error, _cache_hits, _cache_misses
    _data_cache = None
    _load_error = None
    _cache_hits = 0
    _cache_misses = 0

def load_data(force_reload: bool = False) -> Optional[Dict[str, Any]]:
    """Load all game data with database fallback to JSON"""
    global _data_cache, _load_error, _cache_hits, _cache_misses

    if _data_cache is not None and not force_reload:
        _cache_hits += 1
        return _data_cache

    _cache_misses += 1

    # Try database first
    try:
        if db_service.is_data_loaded():
            logger.info("Loading data from database")
            games = db_service.get_games()
            _data_cache = {"games": {}}

            for game_name in games:
                game_data = db_service.get_game_data(game_name)
                if game_data:
                    _data_cache["games"][game_name] = game_data

            _load_error = None
            logger.info(f"Loaded {len(games)} games from database")
            return _data_cache
        else:
            logger.info("Database not populated, loading from JSON and populating database")
            # Fall back to JSON and populate database
            return _load_from_json_and_populate_db(force_reload)
    except Exception as e:
        logger.warning(f"Database load failed, falling back to JSON: {e}")
        return _load_from_json_and_populate_db(force_reload)

def _load_from_json_and_populate_db(force_reload: bool = False) -> Optional[Dict[str, Any]]:
    """Load from JSON files and populate database"""
    global _data_cache, _load_error

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            data_file = config.EXTRACTED_DIR / "chrono_master_complete.json"
            with open(data_file, encoding='utf-8') as f:
                _data_cache = json.load(f)
            _load_error = None

            # Populate database in background
            try:
                if not db_service.is_data_loaded() or force_reload:
                    logger.info("Populating database from JSON data")
                    db_service.load_data_from_json(force_reload=True)
            except Exception as db_e:
                logger.warning(f"Database population failed: {db_e}")

            return _data_cache
        except json.JSONDecodeError as e:
            last_error = f"JSON parse error: {e}"
            _data_cache = {"games": {}}
        except FileNotFoundError as e:
            last_error = f"File not found: {e}"
            _data_cache = {"games": {}}
        except IOError as e:
            last_error = f"IO error: {e}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    _load_error = last_error
    return _data_cache