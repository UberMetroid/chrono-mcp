#!/usr/bin/env python3
"""
Database initialization script
Run this to set up the database and populate it with data
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.database import db_service

def main():
    """Initialize database and populate with data"""
    print("Initializing Chrono MCP Database...")

    try:
        # Initialize database schema
        print("1. Creating database schema...")
        db_service.initialize_database()

        # Load data from JSON files
        print("2. Loading data from JSON files...")
        success = db_service.load_data_from_json(force_reload=True)

        if success:
            print("✅ Database initialized and populated successfully!")

            # Print statistics
            games = db_service.get_games()
            print(f"   - Loaded {len(games)} games")
            for game in games[:5]:  # Show first 5
                print(f"     * {game}")
            if len(games) > 5:
                print(f"     ... and {len(games) - 5} more")

        else:
            print("❌ Failed to load data from JSON files")
            return 1

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())