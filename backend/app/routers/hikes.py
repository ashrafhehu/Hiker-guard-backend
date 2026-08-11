from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.database import get_db
from app.models.session import HikeSession
from app.models.location import LocationPoint, HikeEvent
from app.schemas.sync import SyncRequest, SyncResponse

router = APIRouter(prefix="/api/v1/hikes", tags=["Hikes & Sync"])



@router.post("/sync", response_model=SyncResponse)
def sync_hike_batch(request: SyncRequest, db: Session = Depends(get_db)):
    """
    Idempotent batch upload of GPS locations and hike events.
    Uses client-generated event_id as Primary Key. Duplicate event_ids are safely ignored.
    """
    # 1. Get or create server hike session
    session = db.query(HikeSession).filter(
        HikeSession.local_session_id == request.local_session_id
    ).first()

    if not session:
        server_session_id = str(uuid.uuid4())
        session = HikeSession(
            server_session_id=server_session_id,
            local_session_id=request.local_session_id,
            device_id=request.device_id,
            state="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        server_session_id = session.server_session_id

    acknowledged_ids = []
    rejected_events = []

    # 2. Process event batch idempotently
    for item in request.events:
        try:
            if item.type == "location_point":
                # Check if already exists (idempotency check)
                existing_point = db.query(LocationPoint).filter(
                    LocationPoint.event_id == item.event_id
                ).first()

                if not existing_point:
                    payload = item.payload
                    point = LocationPoint(
                        event_id=item.event_id,
                        local_session_id=request.local_session_id,
                        recorded_at=item.recorded_at,
                        latitude=payload.get("latitude", 0.0),
                        longitude=payload.get("longitude", 0.0),
                        horizontal_accuracy_m=payload.get("horizontal_accuracy_m"),
                        altitude_m=payload.get("altitude_m"),
                        battery_level=payload.get("battery_level"),
                        segment_id=payload.get("segment_id"),
                        observed_network_state=payload.get("observed_network_state", "unknown")
                    )
                    db.add(point)
                    db.commit()
                acknowledged_ids.append(item.event_id)
            else:
                # Handle generic hike event (gap_warning_shown, hike_started, etc.)
                existing_event = db.query(HikeEvent).filter(
                    HikeEvent.event_id == item.event_id
                ).first()

                if not existing_event:
                    evt = HikeEvent(
                        event_id=item.event_id,
                        local_session_id=request.local_session_id,
                        recorded_at=item.recorded_at,
                        event_type=item.type,
                        payload=item.payload
                    )
                    db.add(evt)
                    db.commit()
                acknowledged_ids.append(item.event_id)

        except Exception as e:
            db.rollback()
            # If primary key conflict or unexpected DB error, check if record exists
            existing_loc = db.query(LocationPoint).filter(LocationPoint.event_id == item.event_id).first()
            existing_evt = db.query(HikeEvent).filter(HikeEvent.event_id == item.event_id).first()
            
            if existing_loc or existing_evt:
                acknowledged_ids.append(item.event_id)
            else:
                rejected_events.append({
                    "event_id": item.event_id,
                    "reason": f"Failed to ingest: {str(e)}"
                })

    return {
        "server_session_id": server_session_id,
        "acknowledged_event_ids": acknowledged_ids,
        "rejected_events": rejected_events,
        "server_received_at": datetime.now(timezone.utc).isoformat()
    }

