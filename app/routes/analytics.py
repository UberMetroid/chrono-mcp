from flask import Blueprint, request, jsonify
from app.utils import sanitize_input
from datetime import datetime, date
import uuid
import json
import os
from pathlib import Path

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Simple file-based analytics
ANALYTICS_FILE = Path(__file__).parent.parent.parent / "data" / "analytics.json"

def load_analytics():
    """Load analytics data from file"""
    if not ANALYTICS_FILE.exists():
        return {
            "total_visits": 0,
            "unique_sessions": set(),
            "page_views": {},
            "daily_stats": {}
        }

    try:
        with open(ANALYTICS_FILE, 'r') as f:
            data = json.load(f)
            # Convert sessions back to set
            data["unique_sessions"] = set(data.get("unique_sessions", []))
            return data
    except Exception as e:
        print(f"Error loading analytics: {e}")
        return {
            "total_visits": 0,
            "unique_sessions": set(),
            "page_views": {},
            "daily_stats": {}
        }

def save_analytics(data):
    """Save analytics data to file"""
    try:
        # Convert set to list for JSON serialization
        data_copy = data.copy()
        data_copy["unique_sessions"] = list(data["unique_sessions"])

        ANALYTICS_FILE.parent.mkdir(exist_ok=True)
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(data_copy, f, indent=2)
    except Exception as e:
        print(f"Error saving analytics: {e}")

@analytics_bp.route('/track', methods=['POST'])
def track_visit():
    """Track a page visit using simple file storage"""
    try:
        data = request.get_json() or {}
        page = sanitize_input(data.get('page', '/'), max_length=500)
        session_id = data.get('session_id') or str(uuid.uuid4())

        # Load current analytics
        analytics = load_analytics()

        # Update stats
        analytics["total_visits"] += 1
        analytics["unique_sessions"].add(session_id)

        # Update page views
        if page not in analytics["page_views"]:
            analytics["page_views"][page] = 0
        analytics["page_views"][page] += 1

        # Update daily stats
        today = str(date.today())
        if today not in analytics["daily_stats"]:
            analytics["daily_stats"][today] = {
                "page_views": 0,
                "unique_visitors": 0,
                "api_calls": 0,
                "search_queries": 0
            }

        daily = analytics["daily_stats"][today]
        daily["page_views"] += 1

        if page.startswith('/api/'):
            daily["api_calls"] += 1
        elif 'search' in page:
            daily["search_queries"] += 1

        # Check if this is a new daily visitor
        if session_id not in daily.get("sessions", []):
            daily["unique_visitors"] += 1
            daily["sessions"] = daily.get("sessions", []) + [session_id]

        # Save analytics
        save_analytics(analytics)

        return jsonify({"status": "tracked"}), 200

    except Exception as e:
        print(f"Analytics tracking error: {e}")
        return jsonify({"error": "tracking failed"}), 500

@analytics_bp.route('/stats')
def get_stats():
    """Get analytics statistics"""
    try:
        analytics = load_analytics()
        today = str(date.today())

        # Get today's stats
        today_stats = analytics["daily_stats"].get(today, {
            "page_views": 0,
            "unique_visitors": 0,
            "api_calls": 0,
            "search_queries": 0
        })

        # Calculate total stats
        total_page_views = sum(stats["page_views"] for stats in analytics["daily_stats"].values())
        total_unique_visitors = sum(stats["unique_visitors"] for stats in analytics["daily_stats"].values())

        return jsonify({
            "today": today_stats,
            "total": {
                "page_views": total_page_views,
                "unique_visitors": total_unique_visitors
            }
        })

    except Exception as e:
        print(f"Stats retrieval error: {e}")
        return jsonify({"error": "stats unavailable"}), 500

@analytics_bp.route('/popular')
def get_popular():
    """Get popular content statistics"""
    try:
        analytics = load_analytics()

        # Get popular pages
        popular_pages = sorted(
            analytics["page_views"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Get recent activity (simplified)
        recent_activity = analytics["total_visits"]

        return jsonify({
            "popular_pages": [{"page": page, "views": views} for page, views in popular_pages],
            "recent_activity": recent_activity
        })

    except Exception as e:
        print(f"Popular stats error: {e}")
        return jsonify({"error": "stats unavailable"}), 500