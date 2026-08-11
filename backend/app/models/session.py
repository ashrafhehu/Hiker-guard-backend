from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from app.database import Base


class HikeSession(Base):
    __tablename__ = "hike_sessions"

    server_session_id = Column(String, primary_key=True, index=True)
    local_session_id = Column(String, unique=True, index=True, nullable=False)
    device_id = Column(String, nullable=True, index=True)
    user_id = Column(String, nullable=True)
    trail_id = Column(String, nullable=True)
    state = Column(String, default="active")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

