from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class TrailSummaryResponse(BaseModel):
    trail_id: str
    name: str
    distance_m: float
    pack_version: str
    stage: Literal["route_only", "fixture", "Candidate", "Champion", "model_backed"]
    prediction_available: bool


class TopFactor(BaseModel):
    feature: str
    contribution: float
    direction: Literal["increases_risk", "decreases_risk"]


class GeoJSONLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: List[List[float]]  # [[lon, lat], [lon, lat]]


class SegmentPrediction(BaseModel):
    segment_id: str
    segment_order: int
    segment_length_m: float
    geometry: GeoJSONLineString
    risk_score: Optional[float] = None
    risk_class: Literal["likely_covered", "uncertain", "predicted_gap"] = "uncertain"
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    domain_similarity: Optional[float] = None
    out_of_distribution: Optional[bool] = None
    evidence_completeness: Optional[float] = None
    warning_eligible: bool = False
    top_factors: List[TopFactor] = []


class ModelMetadata(BaseModel):
    model_version: Optional[str] = None
    model_family: Optional[str] = "cross_country_transfer"
    validation_level: str = "source_country_and_external_measured"
    intended_use: str = "planning_only"
    training_label_sources: List[str] = []
    training_geographies: List[str] = []
    validation_geographies: List[str] = []
    target_geography: str = "MYS"
    transfer_method: Optional[str] = "shared_features_source_supervision"
    score_semantics: Optional[str] = "cross_country_transferred_gap_score"
    model_stage: Optional[Literal["Candidate", "Champion", "fixture"]] = "Champion"
    feature_schema_version: Optional[str] = "connectivity-features-v1"
    malaysia_label_validation: bool = False
    malaysia_calibrated: bool = False
    field_validated: bool = False
    label_source: Optional[str] = None
    label_release: Optional[str] = None
    label_resolution_m: Optional[float] = None
    prediction_support: Optional[str] = "fixed_1km_equal_area"
    prediction_support_m: float = 1000.0
    prediction_support_crs: str = "EPSG:6933"
    segment_target_length_m: float = 250.0
    approved_for_mobile_warning: bool = False


class IntegrityBlock(BaseModel):
    algorithm: Literal["sha256"] = "sha256"
    checksum: str


class TrailPackResponse(BaseModel):
    schema_version: str = "trail-pack-v1"
    trail_id: str
    name: str
    pack_version: str
    generated_at: str
    stage: Literal["route_only", "fixture", "Candidate", "Champion", "model_backed"]
    prediction_available: bool
    model: Optional[ModelMetadata] = None
    segments: List[SegmentPrediction]
    integrity: IntegrityBlock

