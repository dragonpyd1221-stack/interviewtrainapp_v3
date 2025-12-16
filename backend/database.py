from sqlalchemy import Column, String, Float, Text
from sqlalchemy.orm import Session
from datetime import datetime
from database_config import Base, engine, SessionLocal
from typing import List, Optional, Dict, Any

# --- SQLAlchemy Models ---

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(String, default=datetime.now().isoformat())

class Progress(Base):
    __tablename__ = "progress"

    # Composite primary key for SQLite/Postgres compatibility logic
    # But SQLAlchemy usually likes a single PK or definition in __table_args__
    # We will just define them as primary keys here.
    user_email = Column(String, primary_key=True)
    video_id = Column(String, primary_key=True) 
    timestamp = Column(Float)
    status = Column(String)
    last_watched = Column(String)

# --- Init & Helper ---

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

# --- CRUD Operations ---

def get_all_videos(category: Optional[str] = None) -> List[Dict[str, Any]]:
    db = get_db_session()
    try:
        query = db.query(Video)
        if category and category != 'all':
            query = query.filter(Video.category == category)
        videos = query.all()
        # Convert to dict
        return [
            {
                "id": v.id,
                "title": v.title,
                "description": v.description,
                "url": v.url,
                "thumbnail": v.thumbnail,
                "duration": v.duration,
                "category": v.category,
                "created_at": v.created_at
            }
            for v in videos
        ]
    finally:
        db.close()

def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    db = get_db_session()
    try:
        v = db.query(Video).filter(Video.id == video_id).first()
        if v:
            return {
                "id": v.id,
                "title": v.title,
                "description": v.description,
                "url": v.url,
                "thumbnail": v.thumbnail,
                "duration": v.duration,
                "category": v.category,
                "created_at": v.created_at
            }
        return None
    finally:
        db.close()

def create_video(video_data: Dict[str, Any]):
    db = get_db_session()
    try:
        new_video = Video(
            id=video_data['id'],
            title=video_data['title'],
            description=video_data.get('description'),
            url=video_data['url'],
            thumbnail=video_data.get('thumbnail'),
            duration=video_data.get('duration'),
            category=video_data.get('category'),
            created_at=video_data.get('created_at')
        )
        db.add(new_video)
        db.commit()
    finally:
        db.close()

def delete_video(video_id: str):
    db = get_db_session()
    try:
        db.query(Video).filter(Video.id == video_id).delete()
        db.commit()
    finally:
        db.close()

def update_progress(email: str, video_id: str, timestamp: float, status: str):
    db = get_db_session()
    try:
        # Check if exists
        progress = db.query(Progress).filter(
            Progress.user_email == email,
            Progress.video_id == video_id
        ).first()

        current_time = datetime.now().isoformat()

        if progress:
            # Update
            progress.timestamp = timestamp
            progress.status = status
            progress.last_watched = current_time
        else:
            # Insert
            new_progress = Progress(
                user_email=email,
                video_id=video_id,
                timestamp=timestamp,
                status=status,
                last_watched=current_time
            )
            db.add(new_progress)
        
        db.commit()
    finally:
        db.close()

def get_user_progress(email: str) -> Dict[str, Any]:
    db = get_db_session()
    try:
        rows = db.query(Progress).filter(Progress.user_email == email).all()
        progress_dict = {}
        for row in rows:
            progress_dict[row.video_id] = {
                "user_email": row.user_email,
                "video_id": row.video_id,
                "timestamp": row.timestamp,
                "status": row.status,
                "last_watched": row.last_watched
            }
        return progress_dict
    finally:
        db.close()
