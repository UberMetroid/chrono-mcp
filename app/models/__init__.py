from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import get_config
import bcrypt

config = get_config()
engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Game(Base):
    """Game model"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    display_name = Column(String)
    platforms = Column(JSON)  # List of platforms
    release_year = Column(Integer, nullable=True)
    developer = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = relationship("Category", back_populates="game", cascade="all, delete-orphan")

class Category(Base):
    """Category model (characters, items, locations, etc.)"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    display_name = Column(String)
    game_id = Column(Integer, ForeignKey("games.id"), index=True)
    item_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="categories")
    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")

class Item(Base):
    """Individual item model"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    data = Column(JSON)  # Store the full item data as JSON
    searchable_text = Column(Text, nullable=True)  # For full-text search
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="items")

# User model for authentication
class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')  # user, admin, moderator
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def set_password(self, password: str):
        """Hash and set password"""
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

    def to_dict(self):
        """Convert to dict (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# Visitor tracking model
class VisitorStats(Base):
    """Visitor statistics model"""
    __tablename__ = "visitor_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String, index=True)
    user_agent = Column(Text)
    page = Column(String, default='/')
    referrer = Column(String, nullable=True)
    session_id = Column(String, index=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)

class DailyStats(Base):
    """Daily aggregated statistics"""
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    total_visitors = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    search_queries = Column(Integer, default=0)
    popular_searches = Column(JSON, default=dict)
    popular_pages = Column(JSON, default=dict)

# Create indexes for better performance
from sqlalchemy import Index
Index('idx_items_searchable_text', Item.searchable_text)
Index('idx_categories_game_name', Category.game_id, Category.name)
Index('idx_users_username', User.username)
Index('idx_users_email', User.email)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)

def reset_db():
    """Reset database (drop all tables and recreate)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)