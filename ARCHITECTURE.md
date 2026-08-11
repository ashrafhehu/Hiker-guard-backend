# JEJAK ML Service Architecture

JEJAK is an AI-service repository. It does not host a frontend or backend business workflows. The external backend calls stable prediction endpoints only; it never reads datasets or model artifacts directly.

```text
Backend service
    │ stable HTTP contract
    ▼
JEJAK ML API ──► Inference ──► Champion model from registry
                     ▲
Data ingestion ─► Features ─► Training ─► Evaluation ─► Registry
                     │                         │
                     └──── experiment artifacts ┘
```

## Directory responsibilities

| Location                           | Responsibility                                                                 |
| ---------------------------------- | ------------------------------------------------------------------------------ |
| `data/raw/`                        | Immutable source data; never overwritten by pipelines.                         |
| `data/interim/`, `data/processed/` | Reproducible derived datasets.                                                 |
| `configs/`                         | Dataset, feature, training, threshold, and runtime settings.                   |
| `src/jejak_ml/data/`               | Dataset catalogues, validation, and ingestion.                                 |
| `src/jejak_ml/features/`           | Versioned, shared feature definitions/builders.                                |
| `src/jejak_ml/training/`           | Experiment execution and model adapters.                                       |
| `src/jejak_ml/evaluation/`         | Spatial validation, metrics, calibration, and latency checks.                  |
| `src/jejak_ml/registry/`           | Model stages and champion promotion.                                           |
| `src/jejak_ml/inference/`          | Champion-model inference and explanations.                                     |
| `src/jejak_ml/api/`                | HTTP adapters and Pydantic contracts only.                                     |
| `artifacts/<experiment-id>/`       | Immutable per-experiment metrics, models, logs, and predictions.               |
| `models/registry/`                 | Registry metadata that identifies the current Champion.                        |
| `scripts/`                         | Operational acquisition and visualisation utilities, outside application code. |
| `tests/`                           | Unit, integration, API-contract, and feature-validation tests.                 |

## Experiment artifact contract

Each experiment must create a unique artifact directory containing, at minimum:

```text
metrics.json
feature_schema.json
model.joblib
predictions.geojson
training.log
metadata.json
model_card.md
```

Promotion to `Champion` is explicit and follows spatial evaluation; no process may automatically serve the latest experiment.
