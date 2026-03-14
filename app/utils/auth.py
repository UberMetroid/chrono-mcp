import jwt
import datetime
from typing import Optional, Dict, Any
from flask import current_app
from app.models import User, SessionLocal
from app.config import get_config

config = get_config()

class AuthService:
    """Authentication service"""

    @staticmethod
    def create_token(user: User) -> str:
        """Create JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, config.SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_current_user(token: str) -> Optional[User]:
        """Get user from token"""
        payload = AuthService.verify_token(token)
        if not payload:
            return None

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == payload['user_id']).first()
            if user and user.is_active:
                # Update last login
                user.last_login = datetime.datetime.utcnow()
                db.commit()
                return user
            return None
        finally:
            db.close()

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and user.is_active and user.check_password(password):
                # Update last login
                user.last_login = datetime.datetime.utcnow()
                db.commit()
                return user
            return None
        finally:
            db.close()

    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = 'user') -> Optional[User]:
        """Create new user"""
        db = SessionLocal()
        try:
            # Check if user already exists
            existing = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing:
                return None

            user = User(username=username, email=email, role=role)
            user.set_password(password)

            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def require_role(required_role: str):
        """Decorator to require specific role"""
        def decorator(f):
            def wrapper(*args, **kwargs):
                # This will be implemented in the middleware
                return f(*args, **kwargs)
            return wrapper
        return decorator

# Initialize default admin user
def init_default_admin():
    """Create default admin user if none exists"""
    db = SessionLocal()
    try:
        admin_count = db.query(User).filter(User.role == 'admin').count()
        if admin_count == 0:
            admin = User(username='admin', email='admin@chrono.local', role='admin')
            admin.set_password('admin123')  # Change this in production!
            db.add(admin)
            db.commit()
            print("Created default admin user: admin/admin123")
    finally:
        db.close()

# Global auth service instance
auth_service = AuthService()