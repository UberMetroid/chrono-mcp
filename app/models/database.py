import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models import Game, Category, Item, User, SessionLocal, init_db, reset_db
from app.config import get_config

config = get_config()
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""

    def __init__(self):
        self.db_path = Path(config.DATABASE_URL.replace('sqlite:///', ''))
        self.initialized = self.db_path.exists()

    def initialize_database(self):
        """Initialize database schema"""
        logger.info("Initializing database...")
        init_db()
        self.initialized = True
        logger.info("Database initialized successfully")

    def reset_database(self):
        """Reset database (drop all data and recreate schema)"""
        logger.warning("Resetting database...")
        reset_db()
        self.initialized = True
        logger.info("Database reset successfully")

    def load_data_from_json(self, force_reload: bool = False) -> bool:
        """Load data from JSON files into database"""
        if not self.initialized:
            self.initialize_database()

        if self.is_data_loaded() and not force_reload:
            logger.info("Data already loaded, skipping")
            return True

        logger.info("Loading data from JSON files...")

        try:
            # Load the master data file
            data_file = config.EXTRACTED_DIR / "chrono_master_complete.json"
            if not data_file.exists():
                logger.error(f"Data file not found: {data_file}")
                return False

            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._populate_database(data)
            logger.info("Data loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False

    def _populate_database(self, data: Dict[str, Any]):
        """Populate database with data"""
        db = SessionLocal()
        try:
            # Clear existing data
            db.query(Item).delete()
            db.query(Category).delete()
            db.query(Game).delete()
            db.commit()

            games_data = data.get("games", {})

            for game_name, game_data in games_data.items():
                # Create game
                game = Game(
                    name=game_name,
                    display_name=game_name.replace('_', ' ').title(),
                    platforms=game_data.get("platforms", []),
                    release_year=game_data.get("release_year"),
                    developer=game_data.get("developer"),
                    description=game_data.get("description")
                )
                db.add(game)
                db.flush()  # Get game ID

                # Create categories and items
                for category_name, items in game_data.items():
                    if not isinstance(items, list):
                        continue

                    category = Category(
                        name=category_name,
                        display_name=category_name.replace('_', ' ').title(),
                        game_id=game.id,
                        item_count=len(items)
                    )
                    db.add(category)
                    db.flush()

                    # Create items
                    for item_data in items:
                        # Create searchable text for full-text search
                        searchable_text = self._create_searchable_text(item_data)

                        item = Item(
                            category_id=category.id,
                            data=item_data,
                            searchable_text=searchable_text
                        )
                        db.add(item)

            db.commit()
            logger.info(f"Populated database with {len(games_data)} games")

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to populate database: {e}")
            raise
        finally:
            db.close()

    def _create_searchable_text(self, item_data: Any) -> Optional[str]:
        """Create searchable text from item data"""
        if isinstance(item_data, dict):
            # Concatenate all string values for search
            texts = []
            for key, value in item_data.items():
                if isinstance(value, str):
                    texts.append(f"{key}:{value}")
                elif isinstance(value, (int, float)):
                    texts.append(f"{key}:{value}")
            return ' '.join(texts).lower()
        elif isinstance(item_data, str):
            return item_data.lower()
        elif isinstance(item_data, (int, float)):
            return str(item_data).lower()
        return None

    def is_data_loaded(self) -> bool:
        """Check if data is already loaded"""
        if not self.initialized:
            return False

        db = SessionLocal()
        try:
            game_count = db.query(Game).count()
            return game_count > 0
        finally:
            db.close()

    def get_games(self) -> List[str]:
        """Get list of game names"""
        db = SessionLocal()
        try:
            games = db.query(Game.name).all()
            return [game[0] for game in games]
        finally:
            db.close()

    def get_game_data(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Get all data for a specific game"""
        db = SessionLocal()
        try:
            game = db.query(Game).filter(Game.name == game_name).first()
            if not game:
                return None

            # Build game data structure
            game_data = {
                "platforms": game.platforms or [],
                "release_year": game.release_year,
                "developer": game.developer,
                "description": game.description
            }

            # Add categories
            for category in game.categories:
                items = []
                for item in category.items:
                    items.append(item.data)
                game_data[category.name] = items

            return game_data
        finally:
            db.close()

    def get_categories(self) -> List[str]:
        """Get all unique category names across games"""
        db = SessionLocal()
        try:
            categories = db.query(Category.name).distinct().all()
            return [cat[0] for cat in categories]
        finally:
            db.close()

    def get_category_data(self, game_name: str, category_name: str,
                         page: int = 1, per_page: int = 20) -> Optional[Dict[str, Any]]:
        """Get paginated category data"""
        db = SessionLocal()
        try:
            # Find game and category
            game = db.query(Game).filter(Game.name == game_name).first()
            if not game:
                return None

            category = db.query(Category).filter(
                Category.game_id == game.id,
                Category.name == category_name
            ).first()

            if not category:
                return None

            # Get paginated items
            total_items = len(category.items)
            total_pages = (total_items + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            items = [item.data for item in category.items[start_idx:end_idx]]

            return {
                "game": game_name,
                "category": category_name,
                "items": items,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        finally:
            db.close()

    def search_items(self, query: str, game_filter: Optional[str] = None,
                    category_filter: Optional[str] = None,
                    limit: int = 500) -> List[Dict[str, Any]]:
        """Search items using full-text search"""
        db = SessionLocal()
        try:
            # Build query
            q = db.query(Item).join(Category).join(Game)

            # Apply filters
            if game_filter:
                q = q.filter(Game.name.ilike(f'%{game_filter}%'))
            if category_filter:
                q = q.filter(Category.name.ilike(f'%{category_filter}%'))

            # Search in searchable_text
            if query:
                q = q.filter(Item.searchable_text.contains(query.lower()))

            # Get results
            items = q.limit(limit).all()

            results = []
            for item in items:
                results.append({
                    "game": item.category.game.name,
                    "category": item.category.name,
                    "item": item.data
                })

            return results
        finally:
            db.close()

# Global database service instance
db_service = DatabaseService()