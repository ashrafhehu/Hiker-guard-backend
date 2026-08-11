# Connectivity MVP Implementation Tracker

Last updated: 2026-08-07

This document tracks the implementation steps, decisions, repository changes, and validation
results for the JEJAK phone-only connectivity-gap MVP.

Update this file whenever a milestone changes state, an implementation decision changes, or a
validation result changes.

## Scope and service boundary

### JEJAK repository scope

JEJAK is responsible for:

1. Ingesting and validating trail and connectivity-evidence datasets.
2. Building reusable geospatial features for training and inference.
3. Producing probabilistic cellular connectivity-gap predictions.
4. Evaluating, registering, and explaining model versions.
5. Providing versioned prediction artifacts and, after explicit promotion, a stable prediction
   API contract.
6. Producing connectivity layers that may later support Search and Rescue (SAR) analysis.

### External application responsibilities

The phone application and external backend are responsible for:

1. Warning users before they enter a predicted gap.
2. Recording GPS trajectories offline.
3. Queueing and synchronising locations and events when connectivity returns.
4. Consuming JEJAK predictions through the stable contract.

These application behaviours are integration dependencies, not implementation tasks in this
repository.

The current MVP does **not** require hikers to carry a LoRa tracker. LoRa gateways, LoRa
trackers, and Bluetooth-to-LoRa trail infrastructure are deferred and must not be treated as
requirements for the cellular connectivity model.

## Locked MVP decisions

### Prediction terminology and score semantics

Public datasets do not prove that a trail segment has zero connectivity. Outputs must use:

- `likely_covered`
- `uncertain`
- `predicted_gap`

For the cross-country transfer MVP, `risk_score` is a bounded transferred gap score:

```text
risk_score = cross-country transferred gap score in [0, 1]
```

It is not a calibrated Malaysian probability unless a future model version is explicitly
calibrated and evaluated with Malaysian labels. Every plan must expose `score_semantics` and
`malaysia_calibrated` so clients do not silently render the score as a probability.

The provisional classification thresholds are:

```text
risk_score <= 0.35 -> likely_covered, only when positive evidence is sufficient
risk_score >= 0.70 -> predicted_gap, only when evidence is sufficient
otherwise          -> uncertain
```

Incomplete, stale, or conflicting evidence can force `uncertain` regardless of the score.
Configuration must therefore use `likely_covered_max` and `predicted_gap_min`; the previous
`predicted_gap_max` and `likely_covered_min` names have the opposite meaning and must be
corrected before model inference is implemented.

`confidence` is not a duplicate of `risk_score`. It must combine model uncertainty, source-model
agreement, target-domain similarity, out-of-distribution status, and evidence completeness. Its
formula and limitations must be versioned and tested.

### Cross-country transfer-learning decision

The 2026-08-06 design decision replaces FAO/JENDELA-dependent Malaysian training with a
cross-country transfer-learning MVP. Source roles are locked as follows:

```text
Anatel Brazil 4G coverage -> primary source-country weak label
FCC BDC US 4G LTE coverage -> secondary source-country weak label
Ofcom UK 4G measurements -> source-country measured validation
Malaysia DEM + WorldCover + OpenCellID -> target-country predictors
Malaysia Ookla mobile -> target-country positive evidence only
```

The first model is 4G-only. Source labels must be harmonised by technology, coverage environment,
signal threshold, spatial support, release date, and modelled/measured semantics before rows are
combined. Source-region selection must be configured before model evaluation and must include
multiple terrain and settlement regimes rather than an entire-country download by default.

FAO 2024/2025/2026 mobile coverage is excluded from the active MVP and retained only as a
historical/reference catalog decision. JENDELA remains a possible future Malaysian validation
source only after written MCMC approval; it must not be scraped. Neither FAO nor JENDELA blocks
the cross-country baseline.

The transferred model must state:

```text
training_geographies: [BRA, USA]
validation_geographies: [BRA, USA, GBR]
target_geography: MYS
transfer_method: cross_country_supervised_transfer
malaysia_label_validation: false
malaysia_calibrated: false
field_validated: false
```

These values may change only through a new versioned dataset/model decision.

### Feature and label separation

No source-country coverage label may appear in the predictor feature vector. Use separate
contracts:

```text
ConnectivityPredictorFeatures
    Predictor columns available consistently during training and inference.

ConnectivityTrainingRow
    Predictor columns + coverage target + grid_id + country_code + region_id + spatial_group_id.

ConnectivityEvidence
    Source observations, provenance, completeness, and release-agreement indicators.
```

Anatel/FCC target fields belong only to the training row. A schema test must fail if a source
coverage field, harmonised target, pseudo-label, or another target-derived column is included in
model inputs. OpenCellID, terrain, and land-cover ablations remain mandatory. Evaluation against
source-country labels measures source-label and transfer fidelity, not Malaysian field accuracy.

### Spatial resolution

The four trails are segmented at approximately 250 m for route ordering, display, and downstream
warning integration. Training and target inference use a neutral fixed 1 km equal-area analysis
grid, provisionally EPSG:6933, rather than any provider's native label grid.

Training and inference predictors must use the same 1 km spatial support. Trail inference first
predicts the 1 km support cells intersecting a trail corridor, then attaches those predictions to
250 m trail segments. A 250 m output segment must not be described as a field-validated 250 m
coverage measurement.

Required prediction metadata:

```text
training_label_sources
training_geographies
validation_geographies
target_geography
transfer_method
score_semantics
malaysia_label_validation
malaysia_calibrated
prediction_support_m
segment_length_m
domain_similarity
out_of_distribution
warning_eligible
field_validated
```

Transferred `predicted_gap` output is experimental. It may appear in offline hackathon/model
artifacts only when the cell is in-domain and evidence gates pass. It must not trigger a mobile
warning unless `warning_eligible=true` in an explicitly approved pack. Missing Ookla or sparse
OpenCellID evidence can never create a gap label by itself.

### Model promotion

Every proxy model begins at the `Candidate` stage. Promotion to `Champion` remains explicit and
must never occur merely because an experiment is the newest.

If a proxy is promoted for an MVP planning deployment, its registry metadata and model card must
state:

```text
validation_level: proxy
intended_use: planning_only
field_validated: false
```

The production API serves only an explicitly promoted `Champion`. Candidate models may produce
offline evaluation and planning artifacts but must not be served implicitly.

## Repository audit baseline

The following facts were validated on 2026-07-28 and 2026-07-29:

- Python reports version 3.11.9.
- `pip check` reports no broken requirements.
- Unit tests pass after Milestone 2: `54 passed`.
- The four GPX files contain 4,938 points and approximately 84.708 km of trail.
- Simple per-trail `ceil(length / 250 m)` segmentation produces 341 segments.
- All current GPX elevations are stored in a non-standard local `trkpt ele="..."` attribute.
- Jalan Bukit Larut contains two duplicate consecutive points.
- The local OpenCellID snapshot contains 95,724 headerless 14-column records.
- All `averageSignal` values in the current OpenCellID snapshot are zero.
- The local Ookla mobile and fixed Parquet files are readable.
- Malaysia DEM and WorldCover predictors are now local; cross-country labels and source-region
  predictors are not yet acquired.
- `shapely`, `pyproj`, `rasterio`, and `scikit-learn` are not current project dependencies.
- The current catalog model has no repository loader, uniqueness validation, checksum metadata,
  availability state, or format-specific validation.

## Status summary

| Milestone | Status | Primary output |
| --- | --- | --- |
| 0. Python 3.11 environment | Completed | Working `.venv` and aligned project configuration |
| 1. Dataset catalog foundation | Completed | Typed loader, validation, and four registered GPX datasets |
| 2. GPX ingestion | Completed | Validated ordered trail-point records |
| 3. Deterministic trail segmentation | Completed | 250 m trail segments in Parquet and GeoJSON |
| 4. Available connectivity evidence | Completed | Normalised evidence and an early trail evidence slice |
| 5. Raster/source acquisition and provenance | In progress | Malaysia predictors local; cross-country labels/source predictors pending |
| 6. Shared predictor feature builder | Pending | Country-neutral, leakage-safe 1 km predictor features |
| 7. Multi-country transfer table | Pending | Source-labelled and Malaysia-unlabelled spatial rows |
| 8. Cross-country transfer model | Pending | Spatially evaluated, domain-aware Candidate artifact |
| 9. Trail inference and planning output | Pending | Segment predictions, planning map, and integration contract |
| 10. SAR model | Deferred | Separate later workstream |

## Milestone 0 — Python 3.11 environment

Status: **Completed**

### Changes made

- [x] Pinned project runtime to `>=3.11,<3.12` in `pyproject.toml`.
- [x] Changed Ruff target to `py311`.
- [x] Changed Black target to `py311`.
- [x] Changed the Docker base image to `python:3.11-slim`.
- [x] Changed the engineering standard in `AGENTS.md` to Python 3.11.
- [x] Updated the README setup requirement to Python 3.11.
- [x] Added `.python-version` containing `3.11`.
- [x] Installed Python 3.11.9 locally.
- [x] Rebuilt the broken `.venv`.
- [x] Installed the project and development dependencies.

### Validation

- [x] Python reports version 3.11.9.
- [x] Project metadata reports `Requires-Python: >=3.11,<3.12`.
- [x] `pip check` reports no broken requirements.
- [x] Unit tests pass: `2 passed`.
- [x] FastAPI, Pandas, PyArrow, and Pydantic import successfully.

### Existing findings not changed in this milestone

Ruff and Black checks exposed pre-existing formatting findings:

- Ten import/formatting findings across existing scripts and modules.
- Two timezone-related `date.today()` findings in Sentinel visualisation scripts.

These are not Python 3.11 compatibility failures and were left unchanged to avoid unrelated
edits during the runtime-alignment milestone.

## Milestone 1 — Dataset catalog foundation

Status: **Completed**

### Planned files

```text
configs/datasets/bundled.yaml
configs/datasets/sources.yaml
src/jejak_ml/data/catalog.py
tests/unit/test_dataset_catalog.py
docs/milestone_1.md
```

`bundled.yaml` contains files or directories that are actually available to the local pipeline.
`sources.yaml` records planned or remote source definitions without pretending that their files
exist locally.

### Catalog contract

Each entry must support the relevant subset of:

```text
id
version
path
source_url
format
license
role
usage
availability
acquired_at
sha256
crs
resolution_m
no_data
validation_profile
notes
```

`usage` must distinguish `model_input`, `weak_label`, `secondary_evidence`, `reference_only`, and
`deferred`. `availability` must distinguish `local`, `remote`, and `planned`.

### Tasks

- [x] Extend the Pydantic catalog contract and reject unknown fields with `extra="forbid"`.
- [x] Add one repository loader for catalog YAML files.
- [x] Validate that dataset IDs are unique.
- [x] Resolve local paths relative to the repository and reject unsafe path traversal.
- [x] Require local file or directory existence only when `availability: local`.
- [x] Add format- and validation-profile-specific schema checks.
- [x] Register the four GPX files with stable IDs, source notes, acquisition date, and SHA-256.
- [x] Record that current Gaia exports store elevation in `trkpt ele="..."`.
- [x] Retain Ookla fixed and LoRa entries but mark them `reference_only` or `deferred`.
- [x] Replace ambiguous versions such as `local_snapshot` with an acquisition timestamp and
      checksum-backed version.
- [x] Record exact Ookla and OpenCellID licence and attribution requirements.
- [x] Add planned source declarations for Copernicus DEM, ESA WorldCover, FAO 2024, and FAO 2026.
- [x] Add tests using small temporary fixtures so CI does not depend on ignored `data/raw/` files.

### Definition of done

The catalog loader validates both catalog files, identifies all four trails, rejects duplicate IDs
and unknown metadata, checks locally available data, and clearly separates model inputs, weak
labels, secondary evidence, reference-only data, and deferred data. Missing planned rasters do not
block completion of this milestone.

### Validation

- [x] Loaded 12 unique entries across `bundled.yaml` and `sources.yaml`.
- [x] Identified four stable GPX trail IDs.
- [x] Validated existence and basic schemas for all eight local entries.
- [x] Verified SHA-256 or `tree-sha256-v1` for all eight local entries.
- [x] Confirmed four planned sources do not require local files.
- [x] Confirmed FAO 2024 is `weak_label` at 1 km.
- [x] Confirmed FAO 2026 is `secondary_evidence` at 5 km.
- [x] Full unit-test suite passes: `17 passed`.
- [x] Targeted Ruff and Black checks pass for Milestone 1 implementation files.
- [x] Comprehensive implementation record written to `docs/milestone_1.md`.

The FAO checks above are historical validation of the catalog state on 2026-07-29. They do not
override the 2026-08-06 cross-country decision. Milestone 5 must add new planned entries for
Anatel, FCC, Ofcom, and every source-region predictor extract without deleting the historical
catalog records.

## Milestone 2 — GPX ingestion

Status: **Completed**

### Planned files

```text
src/jejak_ml/data/gpx.py
tests/unit/test_gpx.py
configs/base.yaml
docs/milestone_2.md
```

### Tasks

- [x] Parse latitude and longitude.
- [x] Parse the current local `trkpt ele="..."` elevation representation.
- [x] Also support the GPX-standard child form `<ele>...</ele>`.
- [x] Validate numeric coordinate ranges and the configured Malaysia area of interest.
- [x] Preserve trail-point and track-segment order.
- [x] Remove duplicate consecutive points and report the removal count.
- [x] Reject malformed, empty, multi-track, or unsupported files with useful errors.
- [x] Define explicit handling for multiple `trkseg` elements instead of joining them silently.
- [x] Calculate total trail length geodesically.
- [x] Generate deterministic trail IDs from catalog IDs, not display names or filenames.
- [x] Add structured ingestion logging.
- [x] Test attribute elevation, child elevation, missing elevation, malformed XML, duplicate
      points, empty tracks, and coordinate errors.

### Definition of done

All four registered GPX files produce deterministic, validated, ordered point sequences. The audit
reports input point count, removed duplicates, coordinate bounds, elevation completeness, and
total geodesic length without modifying `data/raw/`.

### Validation

- [x] All four stable trail catalog IDs resolve and pass checksum verification.
- [x] Parsed 4,938 source points and retained 4,936 ordered points.
- [x] Removed and reported two consecutive duplicates from Jalan Bukit Larut.
- [x] Confirmed all retained elevations are finite and complete.
- [x] Preserved all four source track-segment boundaries.
- [x] Calculated 84.708155 km total great-circle trail length.
- [x] Confirmed complete ingestion results are identical across repeated runs.
- [x] Milestone 2 test suite passes: `37 passed`.
- [x] Full unit-test suite passes: `54 passed`.
- [x] Targeted Ruff and Black checks pass for Milestone 1 and 2 files.
- [x] Comprehensive implementation record written to `docs/milestone_2.md`.
- [x] No source file under `data/raw/` was modified.

## Milestone 3 — Deterministic trail segmentation

Status: **Completed**

### Planned files

```text
src/jejak_ml/features/trail_segments.py
tests/unit/test_trail_segments.py
configs/base.yaml
pyproject.toml
data/README.md
docs/milestone_3.md
```

### Initial decision

Use approximately 250 m segments for route ordering and display. The earlier spherical-distance
estimate was approximately 341 segments. The implemented WGS84 ellipsoidal rule produces 340
segments across the four current trails; this measured result supersedes the estimate.

Use `pyproj` for explicit CRS and geodesic or metric operations, and `shapely` for geometry
construction. Add only the geospatial dependencies required by the implementation.

### Tasks

- [x] Resample each trail by cumulative ground distance.
- [x] Define how the final remainder shorter than 250 m is retained.
- [x] Generate stable `segment_id` values from trail ID and segment order.
- [x] Preserve trail direction and segment order.
- [x] Calculate segment length and centroid coordinates.
- [x] Retain GPX-derived elevation and slope only as source-labelled route metadata.
- [x] Name GPX fields `gpx_elevation_*` and `gpx_slope_*`.
- [x] Do not substitute GPX-derived slope for DEM-derived model features.
- [x] Write GeoParquet-compatible Parquet output to `data/interim/`.
- [x] Write GeoJSON output to `data/interim/`.
- [x] Add a documented command that builds both outputs from the catalog.
- [x] Confirm repeated runs produce identical IDs, rows, geometry, and output file hashes.

### Initial output columns

```text
trail_id
segment_id
segment_order
geometry
centroid_lat
centroid_lon
segment_length_m
gpx_elevation_mean_m
gpx_elevation_min_m
gpx_elevation_max_m
gpx_slope_mean_deg
```

### Expected outputs

```text
data/interim/trail_segments.parquet
data/interim/trail_segments.geojson
```

### Definition of done

One documented command reads the registered GPX files and writes deterministic, validated
Parquet and GeoJSON segment datasets without modifying `data/raw/`. The output reports its CRS,
segment rule, source checksum set, and measured total of 340 segments.

### Validation

- [x] Added `pyproj 3.7.2` and `shapely 2.1.2` through bounded project dependencies.
- [x] Used WGS84 ellipsoidal cumulative distance independently within every GPX `trkseg`.
- [x] Retained every positive final remainder; no source distance was discarded.
- [x] Produced 340 unique, ordered segment IDs over 84.499186 km.
- [x] Wrote 340 valid WKB `LineString` rows with GeoParquet 1.1 metadata.
- [x] Wrote the corresponding 340-feature GeoJSON dataset in CRS84 coordinate order.
- [x] Stored CRS, segmentation rule, source checksum set, and GPX metadata methods in outputs.
- [x] Repeated complete builds produced byte-identical Parquet and GeoJSON SHA-256 values.
- [x] Milestone 3 test suite passes: `22 passed`.
- [x] Full unit-test suite passes: `76 passed`.
- [x] Targeted Ruff and Black checks pass for Milestone 3 files.
- [x] Comprehensive implementation record written to `docs/milestone_3.md`.
- [x] No source file under `data/raw/` was modified.

## Milestone 4 — Available connectivity evidence

Status: **Completed**

This milestone normalises currently available evidence and implements the first reusable connectivity-evidence feature functions. Milestone 6 must extend these functions rather than create a parallel join implementation.

### Planned files

```text
src/jejak_ml/data/opencellid.py
src/jejak_ml/data/ookla.py
src/jejak_ml/features/connectivity_evidence.py
tests/unit/test_opencellid.py
tests/unit/test_ookla.py
tests/unit/test_connectivity_evidence.py
configs/base.yaml
pyproject.toml
data/README.md
README.md
scripts/visualization/visualize_ookla_osm.py
scripts/visualization/build_combined_malaysia_map.py
docs/milestone_4.md
```

### OpenCellID normalisation and features

- [x] Assign official column names when reading the headerless CSV.
- [x] Validate longitude, latitude, radio type, range, samples, and timestamps.
- [x] Preserve `changeable` as a location-quality indicator.
- [x] Treat records as computed cell records, not confirmed physical tower locations.
- [x] Do not display `range` as verified coverage radius.
- [x] Do not use `averageSignal`; all values in the current local snapshot are zero.
- [x] Calculate `distance_to_nearest_cell_km`.
- [x] Calculate `cell_count_5km`.
- [x] Calculate `cell_count_10km`.
- [x] Calculate `operator_count`.
- [x] Retain `nearest_cell_radio`.
- [x] Update or retire visualisation code that labels records as confirmed towers or displays zero
      `averageSignal` values as measured signal strength.

### Ookla mobile normalisation and features

- [x] Read only the mobile performance layer for cellular-model evidence.
- [x] Validate the expected Parquet columns and quarter.
- [x] Calculate `ookla_observed_flag`.
- [x] Retain `avg_d_kbps`, `avg_u_kbps`, `avg_lat_ms`, `tests`, and `devices`.
- [x] Keep unobserved performance metrics as `NaN`.
- [x] Never interpret a missing Ookla tile as confirmed no coverage.
- [x] Preserve source quarter and tile identifier.

### Early vertical slice

- [x] Attach current OpenCellID and Ookla evidence to the 250 m trail segments using the reusable
      feature functions.
- [x] Produce a deterministic evidence-only planning score with explicit `uncertain` handling.
- [x] Version the rules as `evidence-rules-v1`; do not register them as an ML Champion.
- [x] Produce an early planning map so data and geometry problems are visible before raster and
      model work.

### Expected outputs

```text
data/interim/opencellid_cells_v1.parquet
data/interim/ookla_mobile_tiles_2024_q4.parquet
data/processed/trail_connectivity_evidence_v1.parquet
artifacts/evidence-rules-v1/connectivity_evidence_map.html
```

### Definition of done

Every trail segment contains validated, provenance-preserving OpenCellID and Ookla mobile
evidence. Missing observations remain unknown, terminology does not imply confirmed towers or
dead zones, and an evidence-only planning map is reproducible.

### Validation

- [x] Normalized all 95,724 OpenCellID records; all source `averageSignal` values are zero.
- [x] Preserved `reported_range_m` only as a source-reported value, not a coverage feature.
- [x] Normalized 71,853 of 3,551,267 Ookla mobile tiles within the configured analysis envelope.
- [x] Attached nearest distance, 5/10 km cell counts, operator count, and nearest radio to all 340 segments.
- [x] Attached dominant intersecting Ookla mobile observations to 48 segments; missing metrics remain `NaN`.
- [x] Classified 42 segments as `likely_covered` and 298 as `uncertain`; emitted zero `predicted_gap` claims.
- [x] Produced the versioned planning-only HTML map with field-validation and missing-data disclaimers.
- [x] Corrected connectivity threshold configuration names to `likely_covered_max` and `predicted_gap_min`.
- [x] Repeated complete builds produced byte-identical hashes for all four Milestone 4 outputs.
- [x] Milestone 4 test suite passes: `48 passed`.
- [x] Full unit-test suite passes: `124 passed`.
- [x] Targeted Ruff and Black checks pass for Milestone 4 files.
- [x] Comprehensive implementation record written to `docs/milestone_4.md`.
- [x] No source file under `data/raw/` was modified.

## Milestone 5 — Predictor and source-country acquisition with provenance

Status: **Complete — all raw sources and real 1 km derived outputs validated**

The active Milestone 5 scope changed on 2026-08-06. The Malaysia DEM and WorldCover extracts remain
valid reusable predictors. The blocking work is now to acquire and pin licensed, analysis-ready
4G coverage data for configured source regions in Brazil and the United States, plus measured UK
data for external validation. FAO is no longer a dependency for Milestones 5–9.

### Active acquisition scope

- [x] Keep the immutable Malaysia Copernicus DEM and ESA WorldCover extracts and manifests.
- [x] Pin a small, pre-declared set of representative source regions before inspecting model
      results; the first experiment must not opportunistically choose easy regions.
- [x] Register versioned Anatel, FCC, and Ofcom catalog entries with explicit training/validation
      roles; keep all FAO coverage entries `reference_only`.
- [x] Implement a token-free acquisition plan and checksum-backed immutable source-manifest
      validator before any external file can be promoted to `local`.
- [x] Pin the Anatel portal dataset ID, FCC June 2025 release UUID and three provider IDs, and the
      exact Ofcom 2025 4G resource URL; record each unresolved access state explicitly.
- [x] Acquire Anatel Brazil 4G coverage polygons as the primary source-country weak
      label, with release, licence, technology, operator aggregation, and checksum metadata.
- [x] Acquire FCC Broadband Data Collection US 4G LTE mobile coverage as the secondary
      source-country weak label with equivalent provenance.
- [x] Acquire Ofcom UK measured 4G performance or coverage observations for external validation;
      do not mix this measured set into training by default.
- [x] Acquire matching Copernicus DEM and ESA WorldCover predictor extracts for every selected
      source region using the same version and native-source handling used for Malaysia.
- [x] Acquire compatible infrastructure evidence where legally available, or explicitly encode
      missing source-country evidence rather than silently substituting a different measurement.
- [x] Define the source-specific input contract for 4G technology, threshold meaning,
      operator aggregation, indoor/outdoor assumptions, spatial support, release date, and whether
      a source is modelled or measured. Final cross-source target aggregation remains Milestone 7.
- [x] Resample derived source labels and predictors to the fixed 1 km equal-area support only under
      a documented aggregation rule; immutable raw sources must retain their native geometry.
- [x] Implement and test the deterministic 1 km `EPSG:6933` coverage-geometry harmoniser and
      provenance-bearing GeoParquet writer. No real output is generated until raw sources validate.
- [x] Validate licences, checksums, CRS, no-data semantics, geometry readability, and coverage for
      every configured source region.

### Active Definition of done

Malaysia target predictors and all configured Brazil/US source-label inputs are immutable,
catalogued, checksum-backed, licensed for the intended use, and reproducibly convertible to the
fixed 1 km equal-area support. The UK measured validation data is separately identified. A reviewer
can reproduce every source-region selection and label-harmonisation decision without FAO or
JENDELA access.

Implementation checkpoint on 2026-08-07: Anatel and FCC are local, catalogued, and protected by
file-level SHA-256 manifests. Puerto Rico was replaced before modelling by North Carolina
(`state_fips=37`) because the configured FCC provider/state downloads were unavailable for Puerto
Rico. The complete Anatel national ZIP remains immutable; only 14 operator-specific 4G KML plus 3
aggregate QA KML for `MG`, `RJ`, and `SC` were losslessly extracted under `data/interim`. The actual
Anatel ZIP/KML format, KML parser, H3-versus-Raw FCC separation, and manual-portal provenance are
now explicit and tested. Ofcom is local and fully stream-validated; all eight matching DEM and
WorldCover extracts are local, and all 3,666 tiles pass checksum/native-grid/coverage validation.
Native geometry checks, Ofcom filtering, infrastructure missingness, and real harmonisation are now
complete. The `connectivity_m5_harmonised_v1` collection contains six weak-label grids, eight
predictor grids, two continuous measured-validation extracts, and 19 checksum-backed outputs under
collection SHA-256 `de8c21c0...6ac05`. See `docs/milestone_5.md`.

### Historical execution outcome — 2026-08-05 (superseded scope)

The acquisition implementation is operational and the following sources are local, immutable,
catalogued, checksum-backed, readable, native-grid aligned, and spatially validated:

- FAO GAUL 2015 Malaysia ADM0 operational mask (`ADM0_CODE=153`);
- Copernicus DEM GLO-30 `COPERNICUS/DEM/GLO30_2024_1`: 352 tiles, 2,169,690,365 bytes; and
- ESA WorldCover `ESA/WorldCover/v200`: 934 tiles, 131,974,558 bytes.

Both predictor extracts cover the complete conservative mask-plus-25 km geodesic selection and all
four canonical trails. Detailed manifests and per-tile checksums are stored in their immutable raw
directories. `docs/milestone_5.md` records the complete execution.

The milestone is not Definition-of-Done complete. The official FAO 2024 primary weak-label page
and former catalog UUID did not expose an authoritative analysis-ready numeric raster during
execution, so its native grid and values cannot be reproduced or validated. FAO 2026 is explicitly
recorded as unavailable secondary evidence because the current catalog exposes a WMTS PNG
visualization with unresolved licence and zero-versus-no-data semantics. Neither layer was
reverse-engineered from visual tiles, and FAO 2025 was not silently substituted.

### Historical FAO extraction design (superseded 2026-08-06)

The FAO-specific requirements below preserve the exact audit trail of the 2026-08-05 acquisition
attempt. They are not active completion criteria and must not be interpreted as dependencies of
the cross-country transfer MVP.

Milestone 5 must acquire analysis-ready extracts for the Malaysia training area. It must **not** acquire global DEM or WorldCover merely because a provider distributes global data, and it must not substitute the four trail corridors for national training coverage.

#### Malaysia operational training mask

Before downloading or exporting a raster, register one versioned Malaysia operational land-mask source in the dataset catalog. Its metadata must record source URL or asset ID, version, licence, acquisition date, CRS, geometry checksum, and the mask rule below.

The mask is an operational modelling boundary, not a legal or maritime boundary claim. It must:

1. Include the land area of Peninsular Malaysia, Sabah, Sarawak, Federal Territories, and islands represented by the pinned source.
2. Use EPSG:4326 source geometry unless the source requires a documented transformation.
3. Exclude marine-only cells and avoid treating the broad GPX sanity rectangle as a national boundary.
4. Include a native FAO cell in the Malaysia training set when that cell's centroid is inside the pinned mask. The source grid itself must never be shifted, snapped, or reconstructed.

The current `malaysia_sanity_bounds` configuration remains only a permissive GPX and Ookla validation envelope. It must not be used as the training mask.

#### Required raster coverage

| Dataset | Mandatory local extraction coverage | Native-grid and buffer rule | Purpose |
| --- | --- | --- | --- |
| FAO Mobile Broadband Coverage 2024, 1 km | Every native FAO cell whose centroid is inside the pinned Malaysia operational training mask | Preserve the original FAO CRS, transform, alignment, resolution, no-data value, and cell indices exactly; no buffer or resampling before label construction | Primary weak label for Malaysia 1 km training rows |
| FAO Mobile Broadband Coverage 2026, 5 km | Every native FAO 2026 cell whose centroid is inside the same pinned Malaysia mask | Preserve its separate native 5 km grid exactly; never resample it onto the 2024 label grid for training | Secondary release-agreement and uncertainty evidence |
| Copernicus DEM GLO-30 | All source pixels intersecting the pinned Malaysia mask plus a 25 km geodesic buffer around its exterior | Keep native source resolution and alignment in the immutable local export; source tiles may include unavoidable extra area | Terrain features for every Malaysia training cell and edge-safe neighbourhood calculations |
| ESA WorldCover 2021 v200 | All source pixels intersecting the same mask plus the same 25 km geodesic buffer | Keep native 10 m class values and alignment in the immutable local export; source tiles may include unavoidable extra area | Land-cover fractions for every Malaysia training cell and edge-safe neighbourhood calculations |

The 25 km buffer is measured geodesically from the pinned mask exterior, not as a fixed number of
degrees. It is an extraction buffer for raster neighbourhood operations; it does not expand the
Malaysia training labels. Training labels remain mask-centroid-selected FAO 2024 cells only.

#### Trail coverage

The four existing trails must fall inside the Malaysia mask or have their exception documented.
Milestone 9 may make additional trail-corridor extracts for faster inference, but those are
derived convenience products. They must use the same pinned source versions, source resolution,
and feature logic as the Malaysia-wide extracts; they are not a replacement for the training-area
coverage above.

#### API and download policy

An API or pinned cloud asset may be used to acquire an extract. A visual map tile, unversioned API
response, or live API call at training time is not a reproducible source. For each extraction:

1. Record the API endpoint or cloud asset ID, request parameters, source release, mask checksum,
   25 km buffer rule where applicable, export timestamp, and any tile list in an immutable
   manifest.
2. Save the resulting local source extract under `data/raw/` without modifying it afterwards.
3. Record file checksum, readable-raster metadata, native CRS, transform, dimensions, no-data
   value, spatial bounds, and coverage validation result in the catalog or extraction manifest.
4. Write mosaics, crops, reprojections, statistics, and resampled feature-support products only to
   `data/interim/` or `data/processed/`.

The expected retained local source volume is approximately 2–6 GB for Malaysia plus buffer. Plan
for at least 20 GB free working space so temporary API exports, source tiles, and derived products
can coexist safely.

### Required primary sources

- [x] Copernicus DEM GLO-30 with an exact release or asset ID.
- [x] ESA WorldCover 2021 v200.
- [ ] FAO Mobile Broadband Coverage 2024, binary 1 km release.

### Secondary source

- [x] FAO Mobile Broadband Coverage 2026, 5 km release, for release-agreement and uncertainty analysis. Its absence is explicitly recorded; the exposed WMTS PNG was not treated as an analysis raster.

### Data handling requirements

- [x] Record source URL or cloud asset ID, acquisition date, version, checksum where applicable, license, CRS, resolution, no-data value, and extraction area for every acquired local source.
- [x] Store immutable downloaded source files under `data/raw/`.
- [x] When a pinned cloud asset is used, store a reproducible extraction manifest and immutable local export rather than treating a visual map tile as source data.
- [x] Store derived and resampled outputs only under `data/interim/` or `data/processed/`.
- [x] Register and checksum a versioned Malaysia operational land mask before any extraction.
- [ ] Extract FAO 2024 for every mask-centroid-selected native cell, without shifting or resampling its source grid. Blocked on source access.
- [x] Record FAO 2026 as unavailable secondary evidence rather than extracting or reverse-engineering visual WMTS tiles.
- [x] Extract DEM and WorldCover for the entire mask plus a 25 km geodesic buffer at native source alignment.
- [x] Avoid unnecessary global downloads; tolerate unavoidable provider tile overhang around the required mask-plus-buffer area.
- [x] Treat trail-corridor extracts as optional derived inference conveniences, never as substitutes for Malaysia-wide training coverage.
- [ ] Preserve the native FAO 2024 grid definition for labels.
- [x] Note that Copernicus GLO-30 is a digital surface model, not radio ground truth.
- [x] Note that WorldCover is a land-cover classification, not measured radio attenuation.
- [x] Note that all FAO releases are modelled coverage evidence, not field validation.
- [x] Add readable-raster, CRS, resolution, no-data, checksum, and spatial-coverage validation.
- [ ] Validate that every selected FAO 2024 training cell lies inside the local label export, every selected FAO 2026 comparison cell lies inside its local export, and every four trail geometry lies inside the DEM/WorldCover extraction coverage or has a documented exception.
- [x] Validate that every four trail geometry lies inside both DEM and WorldCover extraction coverage.
- [x] Validate that DEM and WorldCover coverage includes the full 25 km mask buffer, while the future FAO training-row contract remains limited to the unbuffered mask.

### Historical Definition of done (superseded 2026-08-06)

The required primary sources are pinned, catalogued, readable, reproducibly extractable, and cover
the complete pinned Malaysia operational training mask. The FAO 2024 label grid can be reproduced
exactly, including the native cell-centroid mask-selection rule. DEM and WorldCover cover the full
mask plus a verified 25 km geodesic buffer, and all four trails are covered or explicitly
excepted. The FAO 2026 secondary layer is either available with the same mask-selection rule or
its absence is explicitly recorded.

## Milestone 6 — Shared predictor feature builder

Status: **Pending**

The same country-neutral predictor implementation and fixed 1 km equal-area support must be reused
for Brazil/US source-labelled rows, UK validation rows where compatible, Malaysia target rows, and
Malaysia trail-corridor inference rows.

### Predictor feature groups

```text
Terrain:
- dem_elevation_mean_m
- dem_elevation_std_m
- dem_slope_mean_deg
- dem_terrain_ruggedness
- dem_terrain_obstruction

Land cover:
- worldcover_tree_fraction
- worldcover_shrub_fraction
- worldcover_grass_fraction
- worldcover_built_fraction
- worldcover_class_diversity

Cellular infrastructure:
- distance_to_nearest_cell_km
- cell_count_5km
- cell_count_10km
- operator_count

Observed performance:
- ookla_observed_flag
- ookla_download_kbps
- ookla_upload_kbps
- ookla_latency_ms
- ookla_tests
- ookla_devices

Evidence quality:
- opencell_location_quality
- source_age_days
- evidence_completeness
```

The following are not predictor features:

```text
source_coverage_value
coverage_label
gap_label
label_source
label_release
```

Country identity may be retained for grouping and diagnostics, but it must not become a shortcut
predictor. Raw and harmonised coverage targets remain outside the model feature matrix.

### Tasks

- [ ] Replace or migrate the current `ConnectivityFeatureVector` to separate predictor,
      training-row, and evidence contracts.
- [ ] Version feature names, dtypes, units, null handling, CRS, and 1 km aggregation support.
- [ ] Build source-labelled predictor rows for the configured Brazil and US 1 km cells.
- [ ] Build target-unlabelled predictor rows for Malaysia and for 1 km cells intersecting buffered
      trail corridors.
- [ ] Add `country_code`, `region_id`, `row_role`, and spatial group IDs outside the predictor
      allowlist.
- [ ] Reuse Milestone 4 evidence functions rather than duplicating spatial joins.
- [ ] Add schema tests that prohibit label-derived predictors.
- [ ] Add parity tests showing that training and inference cells use identical feature logic.

### Definition of done

Predictor values use one versioned schema and identical 1 km aggregation logic across source and
target geographies. No source label, target-derived value, country shortcut, or validation outcome
can enter the model feature matrix.

## Milestone 7 — Multi-country transfer tables

Status: **Pending**

The training table contains source-labelled Brazil and US rows. Malaysia is a target-unlabelled
table used only for transfer diagnostics and inference. Ofcom UK measured data remains a separate
validation role unless a later experiment explicitly documents a compatible alternative.

### Tasks

- [ ] Load the source-region configurations and checksums pinned before model evaluation.
- [ ] Harmonise Anatel and FCC 4G coverage into a documented binary or ordinal target without
      pretending their regulatory definitions are identical.
- [ ] Generate stable `grid_id` values from country, support CRS, and 1 km grid indices.
- [ ] Extract the shared predictor set for every source-labelled and Malaysia target cell.
- [ ] Store raw source values, `coverage_label`, `gap_label`, `label_source`, and `label_release`
      outside the predictor structure.
- [ ] Set `row_role` to `source_train`, `source_validation`, `external_measured_validation`, or
      `target_unlabelled`.
- [ ] Preserve missing Ookla observations as `NaN`.
- [ ] Add region-scale spatial groups and country-level holdout identifiers.
- [ ] Record class balance, missingness, per-source feature distributions, source versions,
      checksums, CRS, harmonisation version, and feature-schema version.
- [ ] Add an explicit predictor-column allowlist.

### Expected output

```text
data/processed/connectivity_transfer_training_v1.parquet
data/processed/connectivity_target_malaysia_v1.parquet
```

### Definition of done

The outputs are reproducible source-labelled and target-unlabelled tables with identical predictor
schemas, explicit row roles, spatial/country groups, provenance, and no target leakage.

## Milestone 8 — Cross-country transfer connectivity model

Status: **Pending**

### Planned models

1. Logistic Regression as an interpretable baseline.
2. `HistGradientBoostingClassifier` as the primary nonlinear candidate.

### Tasks

- [ ] Add scikit-learn as a project dependency.
- [ ] Store model parameters, predictor allowlist, and thresholds in configuration.
- [ ] For Logistic Regression, use a pipeline that imputes missing values and adds missingness
      indicators.
- [ ] Preserve native `NaN` handling for HistGradientBoosting where appropriate.
- [ ] Use region-held-out spatial validation and leave-one-source-country-out stress tests instead
      of random row splitting.
- [ ] Assess source-domain calibration only; never describe it as Malaysian calibration.
- [ ] Measure gap recall, precision-recall AUC, balanced accuracy, Brier score, and reliability on
      compatible source-label validation partitions.
- [ ] Compare against class-prior and simple evidence baselines.
- [ ] Run source-country and feature-family ablations, including with and without OpenCellID.
- [ ] Train a source-versus-target domain classifier or equivalent distance diagnostic and attach
      `domain_similarity` and `out_of_distribution` to Malaysia predictions.
- [ ] Evaluate against the held-out Ofcom measured set only where its target definition and feature
      support are compatible; report incompatibilities rather than forcing a score.
- [ ] Use Malaysia Ookla only as positive observational evidence and agreement analysis, never as
      proof that an unobserved area is a gap.
- [ ] Verify by schema and runtime assertion that all source labels, country IDs, and `gap_label`
      are absent from predictors.
- [ ] Select and test a per-prediction explanation method capable of producing `top_factors`.
- [ ] Prefer the Logistic Regression Candidate if the nonlinear model cannot provide sufficiently
      reliable source-domain score or explanation behaviour.
- [ ] Save metrics, parameters, schema version, dataset versions, and model artifact in a unique
      experiment directory.
- [ ] Register the result as `Candidate`; do not auto-promote it.
- [ ] Label all evaluation results as source-label transfer performance, not Malaysian field
      coverage accuracy.

### Prediction conversion

The model emits a transferred gap score. It is not a calibrated Malaysian probability.
`uncertain` is an abstention outcome, not a training label.

```text
risk_score <= likely_covered_max + sufficient positive evidence -> likely_covered
risk_score >= predicted_gap_min + sufficient evidence           -> predicted_gap
middle score, incomplete evidence, source conflict, or OOD      -> uncertain
```

`predicted_gap` is experimental for Malaysia. It may be shown in offline planning or hackathon
analysis only when evidence-completeness and in-domain gates pass. Mobile warning eligibility is a
separate policy field and defaults to false.

### Definition of done

Spatial and country-held-out evaluation, source-domain calibration assessment, domain-shift
diagnostics, ablations, and explanations are reproducible. The resulting artifact is a
planning-only cross-country transfer Candidate with complete provenance and explicit statements
that Malaysian label validation, Malaysian calibration, and field validation are false.

## Milestone 9 — Trail inference and planning output

Status: **Pending**

### Tasks

- [ ] Generate 1 km support-cell predictions for each buffered trail corridor.
- [ ] Attach the intersecting 1 km predictions to ordered 250 m trail segments.
- [ ] Preserve the stable prediction contract:
      `segment_id`, `risk_score`, `risk_class`, `confidence`, `model_version`, and `top_factors`.
- [ ] Add training label sources, training/validation/target geographies, transfer method, score
      semantics, prediction support, segment length, intended use, and validation metadata.
- [ ] Attach `domain_similarity`, `out_of_distribution`, `evidence_completeness`, and
      `warning_eligible` to every segment.
- [ ] Produce a GeoJSON prediction layer.
- [ ] Produce a Parquet prediction table.
- [ ] Produce an interactive planning map.
- [ ] Clearly distinguish `predicted_gap` from a field-confirmed dead zone.
- [ ] Force `uncertain` and `warning_eligible=false` when target-domain similarity, evidence, or
      supported-feature checks fail.
- [ ] Never use absent Ookla or OpenCellID observations as evidence of a gap.
- [ ] Document the external phone/backend integration contract for entry warnings.
- [ ] Serve predictions through the production API only if the selected model is explicitly
      promoted to `Champion`.
- [ ] Permit an explicit Candidate override only for offline evaluation tooling, never as the
      production default.

### Expected outputs

```text
data/processed/trail_connectivity_predictions_v1.parquet
data/processed/trail_connectivity_predictions_v1.geojson
artifacts/<experiment-id>/connectivity_planning_map.html
artifacts/<experiment-id>/model_card.md
```

### Definition of done

Every segment receives an ordered planning prediction derived from a documented fixed 1 km
equal-area support cell. Artifacts preserve the stable contract, cross-country provenance, score
semantics, domain-shift status, proxy status, and spatial resolution. External applications may
warn only from explicitly eligible predictions and never infer Malaysian calibration from the
numeric score.

## Milestone 10 — SAR model

Status: **Deferred**

SAR work begins only after the connectivity MVP is stable.

The later phone-only SAR workstream may consume:

- Planned route.
- Last location synchronised before connectivity loss.
- Offline phone trajectory after later synchronisation.
- Expected segment travel time.
- Missing connectivity duration.
- Checkpoint overdue status.
- Off-trail distance.
- Stationary duration.

Connectivity loss alone must not be interpreted as proof that a hiker is lost.

## Change log

| Date | Area | Change | Validation |
| --- | --- | --- | --- |
| 2026-08-07 | Milestone 5 completion | Spatially filtered Ofcom to Wales/Scotland while preserving continuous top-four PCI/RSRP; validated and harmonised 4,464,977 FCC H3 plus 119,545 Anatel polygons; sampled matching DEM/WorldCover on the deterministic 1 km EPSG:6933 grid; encoded source infrastructure as null plus missing indicator; atomically promoted the 19-output collection | Collection SHA-256 `de8c21c0...6ac05`; six label/predictor grid joins match exactly; zero invalid FCC geometry; 830,076 Wales and 4,418,566 Scotland measured rows; 20 files / 171,422,659 bytes; full validation and catalog registration passed |
| 2026-08-07 | Milestone 5 Ofcom and source-region predictors | Registered and fully stream-validated the local Ofcom 2025 extracted CSV plus two methodology PDFs; pinned eight source/validation geometries; automatically acquired Copernicus DEM and ESA WorldCover across every region plus 25 km; normalized the GAUL North Carolina mixed GeometryCollection by retaining polygonal area with an explicit audit note | Ofcom 12,066,912 rows / exact 165-column schema / manifest SHA-256 `d97796bc...528b9`; 8 boundary geometries; DEM 1,051 tiles / 9,201,469,902 bytes; WorldCover 2,615 tiles / 1,412,036,958 bytes; all 3,666 raster checksums, CRS, transforms, and coverage passed; harmonisation remains pending |
| 2026-08-07 | Milestone 5 local Anatel/FCC registration and parser correction | Replaced unavailable Puerto Rico with North Carolina before modelling; organized and validated 9 FCC H3 ZIPs plus 1 Raw Coverage reference; registered 10-file FCC and 2-file Anatel SHA-256 manifests; corrected Anatel from assumed ZIP/CSV-WKT to observed ZIP/KML; implemented safe selective extraction and KML Polygon/MultiGeometry parsing; extracted only 14 operator 4G plus 3 aggregate QA KML for MG/RJ/SC | FCC tree SHA-256 `c3faa353...336ec9b6`; cleaned Anatel tree SHA-256 `da53ea96...14b3a` after removal of the misplaced Ofcom file; selective subset SHA-256 `2c239072...274c875`; 143 tests passed; catalog 17 entries/13 local with full checksum validation; Ofcom/source predictors/harmonisation remain pending |
| 2026-08-07 | Revised Milestone 5 foundation and source-access execution | Pinned eight source-region selectors, Anatel dataset ID, FCC release/provider IDs, and exact Ofcom resource; added typed access/source/semantics/support contracts, safe acquisition-plan, identity/checksum-backed immutable-manifest validation, deterministic 1 km EPSG:6933 harmonisation and GeoParquet provenance; made FAO reference-only and removed label leakage | Historical checkpoint before manual Anatel/FCC downloads; superseded by the local-registration entry above |
| 2026-08-06 | Cross-country transfer design | Replaced the active FAO/JENDELA-dependent path with Anatel Brazil and FCC US source labels, Ofcom UK external measured validation, and Malaysia target-unlabelled inference; added fixed 1 km equal-area support, domain/OOD metadata, non-calibrated score semantics, and a separate mobile warning gate | Documentation consistency audit; implementation and source acquisition remain pending |
| 2026-08-05 | Milestone 5 | Pinned FAO GAUL Malaysia mask; implemented native-grid, resumable Earth Engine acquisition and strict raster manifests; acquired Copernicus DEM and WorldCover national 25 km extracts; recorded FAO 2024 as the blocking primary source and FAO 2026 as unavailable WMTS-only secondary evidence | Mask checksum passed; DEM 352 tiles / 2,169,690,365 bytes / four trails; WorldCover 934 tiles / 131,974,558 bytes / four trails; 130 tests passed; detailed results in `docs/milestone_5.md` |
| 2026-08-05 | Milestone 5 scope | Locked extraction coverage: native-grid FAO cells across a pinned Malaysia operational mask; DEM and WorldCover across that mask plus a 25 km geodesic buffer; trail corridors are inference conveniences only | Aligned M5 acquisition requirements with M6/M7 Malaysia-wide 1 km training support and immutable API-export policy |
| 2026-08-05 | Milestone 4 | Normalized OpenCellID and Ookla mobile, added reusable proximity/density and observed-performance evidence, implemented conservative evidence-rules-v1, corrected misleading legacy visualizations, and produced a planning-only map | 95,724 cell records; 71,853 mobile tiles; 340 segments; 42 likely covered; 298 uncertain; zero predicted gaps; 48 milestone tests and 124 total tests passed |
| 2026-08-05 | Milestone 3 | Implemented configured WGS84 250 m segmentation, stable IDs, GPX route metadata, GeoParquet/GeoJSON writers, provenance metadata, and deterministic build validation | 340 segments; 84.499186 km; byte-identical repeat; 22 milestone tests and 76 total tests passed |
| 2026-08-05 | Milestone 2 | Implemented catalog-driven GPX ingestion, configured bounds, explicit track-segment handling, duplicate removal, structured logging, and JSON summaries | 4 trails; 4,938 input points; 4,936 retained; 2 duplicates removed; 84.708155 km; 54 tests passed |
| 2026-07-29 | Milestone 1 | Implemented typed catalogs, safe loading, local schema/checksum validation, four GPX registrations, and planned raster sources | 12 entries loaded; 8 local checksums verified; 17 tests passed; targeted Ruff and Black passed |
| 2026-08-05 | FAO 2026 source verification | Verified the official 16 June 2026 FAO release page and pinned the 5 km product as planned secondary release-agreement and uncertainty evidence; local acquisition remains pending Milestone 5 | FAO states that the 5 km raster is derived from the original approximately 260 m binary coverage layer, so it is not independent field ground truth |
| 2026-07-29 | FAO | Pinned FAO 2024 1 km as the primary weak label and FAO 2026 5 km as secondary uncertainty evidence | Checked against official FAO release descriptions |
| 2026-07-29 | Contracts | Separated predictors, weak labels, and evidence; corrected gap-probability threshold semantics | Compared tracker with current feature and runtime configuration |
| 2026-07-29 | Catalog | Replaced simple alignment milestone with typed loader, provenance, availability, and validation foundation | Current catalog manually loads four entries but lacks repository loader and validation |
| 2026-07-29 | Roadmap | Added early evidence vertical slice, 1 km support parity, calibration, explainability, and explicit model promotion rules | Repository and local dataset audit |
| 2026-07-29 | Scope | Moved phone warning, offline GPS, and synchronisation implementation to external application responsibilities | Aligned with JEJAK architecture boundary |
| 2026-07-28 | Runtime | Pinned repository, tooling, and Docker to Python 3.11 | Python 3.11.9, `pip check` clean, 2 tests passed |
| 2026-07-28 | Scope | Confirmed phone-only MVP; LoRa tracker/gateway work deferred | Documented in current scope |
| 2026-07-28 | Roadmap | Added connectivity MVP milestones and definitions of done | Tracker created |
