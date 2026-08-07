from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.track_model import TrackModel

router = APIRouter()

@router.get("/library")
def get_library(db: Session = Depends(get_db)):
    tracks = db.query(TrackModel).order_by(TrackModel.created_at.desc()).all()
    return {
        "count": len(tracks),
        "tracks": [t.to_dict() for t in tracks]
    }

@router.get("/favorites")
def get_favorites(db: Session = Depends(get_db)):
    tracks = db.query(TrackModel).filter(TrackModel.is_favorite.is_(True)).order_by(TrackModel.created_at.desc()).all()
    return {
        "count": len(tracks),
        "tracks": [t.to_dict() for t in tracks]
    }

@router.post("/favorites/{track_id}/toggle")
def toggle_favorite(track_id: str, db: Session = Depends(get_db)):
    track = db.query(TrackModel).filter(TrackModel.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found in database")

    track.is_favorite = not track.is_favorite
    db.commit()
    db.refresh(track)

    return {
        "status": "success",
        "track_id": track.id,
        "is_favorite": track.is_favorite
    }
