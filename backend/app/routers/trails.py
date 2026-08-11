from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.trail import Trail, TrailPack
from app.schemas.trail import TrailSummaryResponse, TrailPackResponse
from app.utils.checksum import compute_trail_pack_checksum

router = APIRouter(prefix="/api/v1/trails", tags=["Trails"])


@router.get("", response_model=List[TrailSummaryResponse])
def list_trails(db: Session = Depends(get_db)):
    """
    Get list of available trails.
    """
    trails = db.query(Trail).all()
    results = []
    for t in trails:
        results.append({
            "trail_id": t.trail_id,
            "name": t.name,
            "distance_m": t.distance_m,
            "pack_version": "2026-08-06T00:00:00Z",
            "stage": t.stage,
            "prediction_available": t.prediction_available
        })
    return results


@router.get("/{trail_id}/pack", response_model=TrailPackResponse)
def get_trail_pack(trail_id: str, db: Session = Depends(get_db)):
    """
    Get versioned trail pack JSON for offline map download.
    Includes SHA-256 integrity checksum calculation.
    """
    trail = db.query(Trail).filter(Trail.trail_id == trail_id).first()
    if not trail:
        raise HTTPException(status_code=404, detail=f"Trail '{trail_id}' not found")
        
    pack = db.query(TrailPack).filter(TrailPack.trail_id == trail_id).order_by(TrailPack.created_at.desc()).first()
    if not pack:
        raise HTTPException(status_code=404, detail=f"Trail pack for '{trail_id}' not found")

    payload = dict(pack.json_payload)
    
    # Recalculate checksum dynamically to ensure integrity guarantees
    computed_hash = compute_trail_pack_checksum(payload)
    payload["integrity"] = {
        "algorithm": "sha256",
        "checksum": computed_hash
    }
    
    return payload
