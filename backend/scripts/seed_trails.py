import sys
import os
from datetime import datetime, timezone

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.trail import Trail, TrailPack
from app.utils.checksum import compute_trail_pack_checksum

# Create tables
Base.metadata.create_all(bind=engine)


def seed_database():
    db = SessionLocal()
    try:
        print("Seeding JEJAK database with initial trail packs...")

        # 1. Jalan Kledang Trail
        kledang_id = "trail_jalan_kledang"
        existing_kledang = db.query(Trail).filter(Trail.trail_id == kledang_id).first()

        if not existing_kledang:
            kledang = Trail(
                trail_id=kledang_id,
                name="Jalan Kledang",
                distance_m=13250.0,
                stage="Candidate",
                prediction_available=True
            )
            db.add(kledang)

            # Sample trail-pack-v1 payload
            payload_kledang = {
                "schema_version": "trail-pack-v1",
                "trail_id": kledang_id,
                "name": "Jalan Kledang",
                "pack_version": "2026-08-06T00:00:00Z",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "stage": "Candidate",
                "prediction_available": True,
                "model": {
                    "model_version": "connectivity-transfer-v0.1.0",
                    "model_family": "cross_country_transfer",
                    "validation_level": "source_country_and_external_measured",
                    "intended_use": "planning_only",
                    "training_label_sources": ["Anatel Brazil 4G", "FCC BDC US 4G LTE"],
                    "training_geographies": ["BRA", "USA"],
                    "validation_geographies": ["BRA", "USA", "GBR"],
                    "target_geography": "MYS",
                    "transfer_method": "shared_features_source_supervision",
                    "score_semantics": "cross_country_transferred_gap_score",
                    "model_stage": "Candidate",
                    "feature_schema_version": "connectivity-features-v1",
                    "malaysia_label_validation": False,
                    "malaysia_calibrated": False,
                    "field_validated": False,
                    "prediction_support": "fixed_1km_equal_area",
                    "prediction_support_m": 1000.0,
                    "prediction_support_crs": "EPSG:6933",
                    "segment_target_length_m": 250.0,
                    "approved_for_mobile_warning": True
                },
                "segments": [
                    {
                        "segment_id": f"{kledang_id}__s00000",
                        "segment_order": 0,
                        "segment_length_m": 250.0,
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[101.0621, 4.5892], [101.0631, 4.5902]]
                        },
                        "risk_score": 0.15,
                        "risk_class": "likely_covered",
                        "confidence": 0.85,
                        "model_version": "connectivity-transfer-v0.1.0",
                        "domain_similarity": 0.90,
                        "out_of_distribution": False,
                        "evidence_completeness": 0.95,
                        "warning_eligible": False,
                        "top_factors": []
                    },
                    {
                        "segment_id": f"{kledang_id}__s00001",
                        "segment_order": 1,
                        "segment_length_m": 250.0,
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[101.0631, 4.5902], [101.0641, 4.5912]]
                        },
                        "risk_score": 0.82,
                        "risk_class": "predicted_gap",
                        "confidence": 0.78,
                        "model_version": "connectivity-transfer-v0.1.0",
                        "domain_similarity": 0.76,
                        "out_of_distribution": False,
                        "evidence_completeness": 0.83,
                        "warning_eligible": True,
                        "top_factors": [
                            {
                                "feature": "terrain_obstruction",
                                "contribution": 0.31,
                                "direction": "increases_risk"
                            }
                        ]
                    }
                ]
            }

            checksum_kledang = compute_trail_pack_checksum(payload_kledang)
            payload_kledang["integrity"] = {"algorithm": "sha256", "checksum": checksum_kledang}

            pack_kledang = TrailPack(
                id=f"{kledang_id}_v1",
                trail_id=kledang_id,
                pack_version="2026-08-06T00:00:00Z",
                schema_version="trail-pack-v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
                stage="Candidate",
                json_payload=payload_kledang,
                checksum=checksum_kledang
            )
            db.add(pack_kledang)

        # 2. Bukit Larut Route Only Trail
        larut_id = "trail_jalan_bukit_larut"
        existing_larut = db.query(Trail).filter(Trail.trail_id == larut_id).first()

        if not existing_larut:
            larut = Trail(
                trail_id=larut_id,
                name="Jalan Bukit Larut",
                distance_m=11200.0,
                stage="route_only",
                prediction_available=False
            )
            db.add(larut)

            payload_larut = {
                "schema_version": "trail-pack-v1",
                "trail_id": larut_id,
                "name": "Jalan Bukit Larut",
                "pack_version": "2026-08-06T00:00:00Z",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "stage": "route_only",
                "prediction_available": False,
                "model": None,
                "segments": [
                    {
                        "segment_id": f"{larut_id}__s00000",
                        "segment_order": 0,
                        "segment_length_m": 250.0,
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[100.7931, 4.8622], [100.7941, 4.8632]]
                        },
                        "risk_score": None,
                        "risk_class": "uncertain",
                        "confidence": None,
                        "model_version": None,
                        "domain_similarity": None,
                        "out_of_distribution": None,
                        "evidence_completeness": None,
                        "warning_eligible": False,
                        "top_factors": []
                    }
                ]
            }

            checksum_larut = compute_trail_pack_checksum(payload_larut)
            payload_larut["integrity"] = {"algorithm": "sha256", "checksum": checksum_larut}

            pack_larut = TrailPack(
                id=f"{larut_id}_v1",
                trail_id=larut_id,
                pack_version="2026-08-06T00:00:00Z",
                schema_version="trail-pack-v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
                stage="route_only",
                json_payload=payload_larut,
                checksum=checksum_larut
            )
            db.add(pack_larut)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

