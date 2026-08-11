from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class LocationPayload(BaseModel):
    latitude: float
    longitude: float
    horizontal_accuracy_m: Optional[float] = None
    altitude_m: Optional[float] = None
    battery_level: Optional[float] = None
    segment_id: Optional[str] = None
    observed_network_state: Optional[str] = "unknown"


class BatchEventItem(BaseModel):
    event_id: str  # Client-side UUID
    type: str     # "location_point", "hike_started", "gap_warning_shown", etc.
    recorded_at: str
    payload: Dict[str, Any]


class SyncRequest(BaseModel):
    device_id: Optional[str] = None
    local_session_id: str
    events: List[BatchEventItem]


class RejectedEventItem(BaseModel):
    event_id: str
    reason: str


class SyncResponse(BaseModel):
    server_session_id: str
    acknowledged_event_ids: List[str]
    rejected_events: List[RejectedEventItem] = []
    server_received_at: str
