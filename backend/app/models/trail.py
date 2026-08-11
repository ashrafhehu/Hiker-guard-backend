from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Trail(Base):
    __tablename__ = "trails"

    trail_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    distance_m = Column(Float, nullable=False)
    stage = Column(String, default="route_only")  # route_only, fixture, Candidate, Champion
    prediction_available = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    packs = relationship("TrailPack", back_populates="trail", cascade="all, delete-orphan")


class TrailPack(Base):
    __tablename__ = "trail_packs"

    id = Column(String, primary_key=True, index=True)
    trail_id = Column(String, ForeignKey("trails.trail_id"), nullable=False)
    pack_version = Column(String, nullable=False)
    schema_version = Column(String, default="trail-pack-v1")
    generated_at = Column(String, nullable=False)
    stage = Column(String, default="route_only")
    json_payload = Column(JSON, nullable=False)
    checksum = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trail = relationship("Trail", back_populates="packs")

