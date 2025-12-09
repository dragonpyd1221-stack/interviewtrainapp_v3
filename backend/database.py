import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

DB_PATH = "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Videos Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            thumbnail TEXT,
            duration TEXT,
            category TEXT,
            created_at TEXT
        )
    ''')

    # Progress Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_email TEXT,
            video_id TEXT,
            timestamp REAL,
            status TEXT,
            last_watched TEXT,
            PRIMARY KEY (user_email, video_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper functions
def get_all_videos(category: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    if category and category != 'all':
        c.execute("SELECT * FROM videos WHERE category = ?", (category,))
    else:
        c.execute("SELECT * FROM videos")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_video(video_data: Dict[str, Any]):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO videos (id, title, description, url, thumbnail, duration, category, created_at)
        VALUES (:id, :title, :description, :url, :thumbnail, :duration, :category, :created_at)
    ''', video_data)
    conn.commit()
    conn.close()

def delete_video(video_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()

def update_progress(email: str, video_id: str, timestamp: float, status: str):
    conn = get_db_connection()
    c = conn.cursor()
    last_watched = datetime.now().isoformat()
    c.execute('''
        INSERT INTO progress (user_email, video_id, timestamp, status, last_watched)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_email, video_id) DO UPDATE SET
            timestamp=excluded.timestamp,
            status=excluded.status,
            last_watched=excluded.last_watched
    ''', (email, video_id, timestamp, status, last_watched))
    conn.commit()
    conn.close()

def get_user_progress(email: str) -> Dict[str, Any]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM progress WHERE user_email = ?", (email,))
    rows = c.fetchall()
    conn.close()
    
    progress_dict = {}
    for row in rows:
        progress_dict[row['video_id']] = dict(row)
    return progress_dict
