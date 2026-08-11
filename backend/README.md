# JEJAK Application Backend (Python / FastAPI)

This is the official **Application Backend** for the **JEJAK (HikerGuard GeoAI Mobile)** hiking safety platform.

## Features
- **Trail Pack API (`GET /api/v1/trails/{trail_id}/pack`)**: Serves 250m trail segments and predicted cellular risk classes (`likely_covered`, `uncertain`, `predicted_gap`) with SHA-256 integrity checksum validation.
- **Idempotent Batch Sync API (`POST /api/v1/hikes/sync`)**: Ingests offline location points and hike events idempotently using client-generated UUID `event_id` keys.
- **FastAPI + SQLAlchemy + Pydantic v2**: High performance, typed data validation, and easy database migrations.

---

## Setup & Running Locally

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed Database
```bash
python scripts/seed_trails.py
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### 4. Run Automated Tests
```bash
pytest
```
