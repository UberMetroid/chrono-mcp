#!/usr/bin/env python3
"""
Chrono Series Web UI - Refactored
Simple browser for Chrono game data
Run: python web_ui.py
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    config = app.config
    app.run(
        host=config['HOST'],
        port=config['PORT'],
        debug=config['DEBUG']
    )