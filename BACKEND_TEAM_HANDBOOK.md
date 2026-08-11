# JEJAK Backend Developer Handbook & System Architecture

> **Project Name:** HikerGuard-GeoAI Backend (JEJAK Application Backend)  
> **Repository:** [ashrafhehu/JEJAK-backend](https://github.com/ashrafhehu/JEJAK-backend)  
> **Tech Stack:** Python 3.10+ | FastAPI | SQLAlchemy | Pydantic v2 | SQLite / PostgreSQL | Pytest  

> **Last Updated:** August 2026

---

## 1. Executive Summary & Purpose

**JEJAK (HikerGuard)** is an offline-first hiking safety decision-support system. It predicts cellular connectivity gaps along hiking trails **before** hikers enter them.

### What Does the Application Backend Do?
The **Application Backend** acts as the central bridge between the mobile app (Expo / React Native) and the ML prediction engine. It is responsible for:
1. **Offline Trail Pack Delivery:** Serving pre-computed 250m segment trail packs with predicted cellular risk classes (`likely_covered`, `uncertain`, `predicted_gap`) and SHA-256 integrity hashes.
2. **Idempotent Batch Location Sync:** Ingesting offline GPS coordinates and events logged inside connectivity dead zones. The backend guarantees that re-sent batches from spotty connections never create duplicate records.
3. **Session & Last Synced Location Tracking:** Maintaining server-acknowledged GPS coordinates so emergency contacts or authorities know a hiker's last confirmed position.

---

## 2. 3-Tier System Architecture

```text
 ┌─────────────────────────────────────────────────────────────┐
 │                     Mobile Application                      │
 │                 (HikerGuard-GeoAI-Mobile)                   │
 │   - Expo / React Native (iOS & Android)                     │
 │   - Local SQLite database & offline queue                   │
 └──────────────────────────────┬──────────────────────────────┘
                                │ REST / JSON (HTTPS)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                     Application Backend                     │
 │                 (THIS REPOSITORY - FastAPI)                 │
 │   - Trail Pack Delivery (trail-pack-v1 + SHA-256)           │
 │   - Idempotent Batch Sync (client UUID event_ids)           │
 │   - Relational Database (SQLite / PostgreSQL)               │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Internal HTTP / REST
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                    JEJAK ML Prediction API                  │
 │                  (Separate AI Microservice)                 │
 │   - GeoAI Feature Engineering & Model Registry              │
 │   - Transfer Learning Predictions (Candidate / Champion)    │
 └─────────────────────────────────────────────────────────────┘
```

---

## 3. Quick Start Guide for Developers

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/ashrafhehu/Hiker-guard-backend.git
cd Hiker-guard-backend/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Seed Initial Database
```bash
python scripts/seed_trails.py
```
*Creates initial SQLite database (`jejak_backend.db`) and seeds sample trail packs (`trail_jalan_kledang`, `trail_jalan_bukit_larut`).*

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- **Interactive OpenAPI (Swagger) Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Automated Test Suite
```bash
pytest
```
*All tests should pass with 100% success rate (`5 passed`).*

---

## 4. API Endpoints Specification

### 1. Health Check
- **`GET /health`**
- **Response `200 OK`**:
  ```json
  {
    "status": "ok",
    "service": "JEJAK Application Backend"
  }
  ```

### 2. List Available Trails
- **`GET /api/v1/trails`**
- **Response `200 OK`**:
  ```json
  [
    {
      "trail_id": "trail_jalan_kledang",
      "name": "Jalan Kledang",
      "distance_m": 13250.0,
      "pack_version": "2026-08-06T00:00:00Z",
      "stage": "Candidate",
      "prediction_available": true
    }
  ]
  ```

### 3. Download Offline Trail Pack (`trail-pack-v1`)
- **`GET /api/v1/trails/{trail_id}/pack`**
- **Response `200 OK`**:
  ```json
  {
    "schema_version": "trail-pack-v1",
    "trail_id": "trail_jalan_kledang",
    "name": "Jalan Kledang",
    "pack_version": "2026-08-06T00:00:00Z",
    "generated_at": "2026-08-11T15:00:00Z",
    "stage": "Candidate",
    "prediction_available": true,
    "model": {
      "model_version": "connectivity-transfer-v0.1.0",
      "model_family": "cross_country_transfer",
      "validation_level": "source_country_and_external_measured",
      "intended_use": "planning_only",
      "training_label_sources": ["Anatel Brazil 4G", "FCC BDC US 4G LTE"],
      "target_geography": "MYS",
      "model_stage": "Candidate",
      "feature_schema_version": "connectivity-features-v1",
      "approved_for_mobile_warning": true
    },
    "segments": [
      {
        "segment_id": "trail_jalan_kledang__s00000",
        "segment_order": 0,
        "segment_length_m": 250.0,
        "geometry": {
          "type": "LineString",
          "coordinates": [[101.0621, 4.5892], [101.0631, 4.5902]]
        },
        "risk_score": 0.15,
        "risk_class": "likely_covered",
        "confidence": 0.85,
        "warning_eligible": false,
        "top_factors": []
      },
      {
        "segment_id": "trail_jalan_kledang__s00001",
        "segment_order": 1,
        "segment_length_m": 250.0,
        "geometry": {
          "type": "LineString",
          "coordinates": [[101.0631, 4.5902], [101.0641, 4.5912]]
        },
        "risk_score": 0.82,
        "risk_class": "predicted_gap",
        "confidence": 0.78,
        "warning_eligible": true,
        "top_factors": [
          {
            "feature": "terrain_obstruction",
            "contribution": 0.31,
            "direction": "increases_risk"
          }
        ]
      }
    ],
    "integrity": {
      "algorithm": "sha256",
      "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  }
  ```

### 4. Idempotent Batch Location Sync
- **`POST /api/v1/hikes/sync`**
- **Request Body**:
  ```json
  {
    "device_id": "phone-device-uuid-123",
    "local_session_id": "550e8400-e29b-41d4-a716-446655440000",
    "events": [
      {
        "event_id": "a1b2c3d4-0001-4000-8000-000000000001",
        "type": "location_point",
        "recorded_at": "2026-08-06T02:30:00Z",
        "payload": {
          "latitude": 4.5892,
          "longitude": 101.0621,
          "horizontal_accuracy_m": 5.2,
          "battery_level": 0.85,
          "segment_id": "trail_jalan_kledang__s00005"
        }
      }
    ]
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "server_session_id": "server-uuid-9999",
    "acknowledged_event_ids": [
      "a1b2c3d4-0001-4000-8000-000000000001"
    ],
    "rejected_events": [],
    "server_received_at": "2026-08-11T15:30:00.000000+00:00"
  }
  ```

---

## 5. Database Schema & Models

```text
  +------------------+         +------------------+
  |      trails      |         |   hike_sessions  |
  +------------------+         +------------------+
  | PK  trail_id     |<---+    | PK  server_sid   |
  |     name         |    |    | UNQ local_sid    |
  |     distance_m   |    |    |     device_id    |
  |     stage        |    |    |     state        |
  +------------------+    |    +------------------+
           | 1            |
           |              |
           | N            |
  +------------------+    |    +------------------+
  |   trail_packs    |    |    | location_points  |
  +------------------+    |    +------------------+
  | PK  id           |    |    | PK  event_id     |
  | FK  trail_id ----+----+    | IND local_sid    |
  |     pack_version |         |     latitude     |
  |     json_payload |         |     longitude    |
  |     checksum     |         |     segment_id   |
  +------------------+         +------------------+
```

1. **`trails`**: Master list of trails.
2. **`trail_packs`**: Versioned JSON trail packs stored with pre-calculated SHA-256 checksums.
3. **`hike_sessions`**: Maps client `local_session_id` to server `server_session_id`.
4. **`location_points`**: GPS trajectory points logged by phone. `event_id` is the client UUID primary key.
5. **`hike_events`**: Special events (`gap_warning_shown`, `hike_started`, `sos_requested`).

---

## 6. Strict Technical & Product Rules

1. **Idempotency Guarantee:**
   - Cellular signals on hiking trails are intermittent. Phones will attempt to send the same batch multiple times.
   - The backend uses `event_id` (client-generated UUID) as the Primary Key. Duplicate submissions will be safely acknowledged without creating duplicate DB rows.

2. **Integrity Checksums (SHA-256):**
   - The function `compute_trail_pack_checksum()` in `app/utils/checksum.py` serializes JSON keys canonically (`sort_keys=True, separators=(',', ':')`) and computes SHA-256.
   - Mobile client verifies this checksum upon download before saving to local SQLite.

3. **Mandatory Risk Class Terminology:**
   - Predictions MUST use exact risk classes: `likely_covered`, `uncertain`, `predicted_gap`.
   - **NEVER** use phrases such as "confirmed dead zone", "guaranteed coverage", or "no signal" in API responses or user-facing text.

---

## 7. Next Roadmap Items for Backend Team

- [ ] **Phase 1: User Auth (JWT):** Implement `/api/v1/auth/register` and `/api/v1/auth/login` using FastAPI OAuth2 + JWT tokens.
- [ ] **Phase 2: Emergency Contact Management:** Endpoints for saving expected return time and emergency phone numbers for a hike session.
- [ ] **Phase 3: PostGIS Spatial Queries:** Upgrade SQLite database to PostgreSQL + PostGIS for spatial intersection queries.
- [ ] **Phase 4: ML Service Integration:** Connect backend to JEJAK Python ML service to automatically pull new `Champion` trail packs when trained.
