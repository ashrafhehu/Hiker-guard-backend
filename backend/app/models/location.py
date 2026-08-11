from sqlalchemy import Column, String, Float, DateTime, JSON
from datetime import datetime, timezone
from app.database import Base


class LocationPoint(Base):
    __tablename__ = "location_points"

    # Client-side UUID event_id acts as primary key for idempotency
    event_id = Column(String, primary_key=True, index=True)
    local_session_id = Column(String, index=True, nullable=False)
    recorded_at = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    horizontal_accuracy_m = Column(Float, nullable=True)
    altitude_m = Column(Float, nullable=True)
    battery_level = Column(Float, nullable=True)
    segment_id = Column(String, nullable=True)
    observed_network_state = Column(String, default="unknown")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class HikeEvent(Base):
    __tablename__ = "hike_events"

    # Client-side UUID event_id acts as primary key for idempotency
    event_id = Column(String, primary_key=True, index=True)
    local_session_id = Column(String, index=True, nullable=False)
    recorded_at = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

