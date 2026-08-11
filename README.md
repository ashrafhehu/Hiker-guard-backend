# HikerGuard-GeoAI Application Backend (JEJAK)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Pytest](https://img.shields.io/badge/Pytest-Passed-success.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org)

Official **Application Backend** for the **JEJAK (HikerGuard GeoAI Mobile)** hiking safety decision-support system.

- **GitHub Repository:** [ashrafhehu/JEJAK-backend](https://github.com/ashrafhehu/JEJAK-backend)
- **Developer Handbook:** See [BACKEND_TEAM_HANDBOOK.md](BACKEND_TEAM_HANDBOOK.md) for complete architecture, API contracts, and database schema documentation.


---

## Architecture Overview

```text
 Mobile Application (Expo / RN)
        │ REST / HTTPS
        ▼
 Application Backend (FastAPI - THIS REPO)
        │ Internal HTTP
        ▼
 JEJAK ML Prediction API (Python GeoAI Engine)
```

---

## Key Features

1. **Trail Pack API (`GET /api/v1/trails/{trail_id}/pack`)**: Serves 250m trail segment geometry with predicted cellular coverage risk classes (`likely_covered`, `uncertain`, `predicted_gap`) and SHA-256 integrity checksums.
2. **Idempotent Batch Sync API (`POST /api/v1/hikes/sync`)**: Ingests offline location points & events safely using client-side UUID `event_id` keys to prevent duplicate records during spotty signal reconnection.
3. **Pydantic v2 & SQLAlchemy Engine**: High performance, strict data validation, and easy database migration.

---

## Quick Start

### 1. Install & Setup
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed Database
```bash
python scripts/seed_trails.py
```

### 3. Run FastAPI Dev Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Test Suite
```bash
pytest
```

---

## Documentation Links
- [BACKEND_TEAM_HANDBOOK.md](BACKEND_TEAM_HANDBOOK.md) — Comprehensive architecture, API contracts, ERD diagrams, and technical guidelines for the team.
