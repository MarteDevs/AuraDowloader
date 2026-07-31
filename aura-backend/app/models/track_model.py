from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from app.core.db import Base

class TrackModel(Base):
    __tablename__ = "aura_tracks"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    artist = Column(String(255), nullable=False, index=True)
    album = Column(String(255), nullable=True)
    thumbnail = Column(String(500), nullable=True)
    duration = Column(String(30), nullable=True)
    duration_sec = Column(Integer, default=0)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    quality = Column(String(30), default="320k")
    engine = Column(String(30), default="youtube")
    is_favorite = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
            "duration_sec": self.duration_sec,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "quality": self.quality,
            "engine": self.engine,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
