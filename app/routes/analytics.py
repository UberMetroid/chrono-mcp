from flask import Blueprint, request, jsonify
from app.models import VisitorStats, DailyStats, SessionLocal
from app.utils import sanitize_input
from datetime import datetime, date
import uuid

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/track', methods=['POST'])
def track_visit():
    """Track a page visit"""
    try:
        data = request.get_json() or {}
        ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')
        user_agent = request.headers.get('User-Agent', '')
        page = sanitize_input(data.get('page', '/'), max_length=500)
        referrer = sanitize_input(data.get('referrer', ''), max_length=500) or None
        session_id = data.get('session_id') or str(uuid.uuid4())

        # Create visitor record
        visitor = VisitorStats(
            ip_address=ip,
            user_agent=user_agent,
            page=page,
            referrer=referrer,
            session_id=session_id
        )

        # Update daily stats
        today = date.today()
        db = SessionLocal()
        try:
            # Check if daily stats exist
            daily_stat = db.query(DailyStats).filter(DailyStats.date == today).first()
            if not daily_stat:
                daily_stat = DailyStats(date=today)
                db.add(daily_stat)

            # Increment counters based on page type
            daily_stat.page_views += 1

            if page.startswith('/api/'):
                daily_stat.api_calls += 1
            elif 'search' in page:
                daily_stat.search_queries += 1

            # Track unique visitors (simple approximation)
            recent_visitors = db.query(VisitorStats).filter(
                VisitorStats.session_id == session_id,
                VisitorStats.date >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()

            if recent_visitors == 0:
                daily_stat.unique_visitors += 1

            db.add(visitor)
            db.commit()

            return jsonify({"status": "tracked"}), 200

        finally:
            db.close()

    except Exception as e:
        print(f"Analytics tracking error: {e}")
        return jsonify({"error": "tracking failed"}), 500

@analytics_bp.route('/stats')
def get_stats():
    """Get analytics statistics"""
    try:
        db = SessionLocal()
        try:
            today = date.today()

            # Get today's stats
            daily_stat = db.query(DailyStats).filter(DailyStats.date == today).first()
            if not daily_stat:
                return jsonify({
                    "today": {"page_views": 0, "unique_visitors": 0, "api_calls": 0, "search_queries": 0},
                    "total": {"page_views": 0, "unique_visitors": 0}
                })

            # Get total stats
            total_stats = db.query(
                db.func.sum(DailyStats.page_views).label('total_views'),
                db.func.sum(DailyStats.unique_visitors).label('total_visitors')
            ).first()

            return jsonify({
                "today": {
                    "page_views": daily_stat.page_views,
                    "unique_visitors": daily_stat.unique_visitors,
                    "api_calls": daily_stat.api_calls,
                    "search_queries": daily_stat.search_queries
                },
                "total": {
                    "page_views": total_stats.total_views or 0,
                    "unique_visitors": total_stats.total_visitors or 0
                }
            })

        finally:
            db.close()

    except Exception as e:
        print(f"Stats retrieval error: {e}")
        return jsonify({"error": "stats unavailable"}), 500

@analytics_bp.route('/popular')
def get_popular():
    """Get popular content statistics"""
    try:
        db = SessionLocal()
        try:
            # Get popular pages
            popular_pages = db.query(
                VisitorStats.page,
                db.func.count(VisitorStats.id).label('count')
            ).group_by(VisitorStats.page).order_by(db.desc('count')).limit(10).all()

            # Get recent searches (from search API calls)
            recent_searches = db.query(VisitorStats).filter(
                VisitorStats.page.like('%/api/search%')
            ).order_by(db.desc(VisitorStats.date)).limit(20).all()

            return jsonify({
                "popular_pages": [{"page": p.page, "views": p.count} for p in popular_pages],
                "recent_activity": len(recent_searches)
            })

        finally:
            db.close()

    except Exception as e:
        print(f"Popular stats error: {e}")
        return jsonify({"error": "stats unavailable"}), 500