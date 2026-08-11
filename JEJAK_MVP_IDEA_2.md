# JEJAK MVP Idea 2

> Revised 2026-08-06: the connectivity GeoAI MVP uses cross-country transfer learning without FAO,
> JENDELA, Malaysian field labels, or Malaysian probability-calibration claims.

## Phone-Only GeoAI Connectivity Intelligence for Hiking Safety

Last updated: 2026-07-28

## Vision

JEJAK is a phone-only GeoAI decision-support platform that predicts likely cellular connectivity
gaps along hiking trails before hikers enter them.

The MVP combines trail geometry, terrain, land cover, public mobile-performance observations,
and recorded cellular-infrastructure evidence. It converts these inputs into cautious planning
predictions and actionable phone warnings.

JEJAK does not claim that public datasets can confirm zero connectivity. Its purpose is to help
hikers and authorities prepare for areas where cellular service is likely to be unavailable or
uncertain.

## MVP scope

The first MVP provides:

1. Trail-level cellular connectivity-gap prediction.
2. Phone warnings before entering a predicted gap.
3. Offline GPS trajectory recording.
4. Automatic synchronisation when connectivity returns.
5. Last successfully synchronised location.
6. Connectivity planning maps for park authorities.
7. A connectivity evidence layer that can support a later Search and Rescue (SAR) model.

The MVP requires only a smartphone. Hikers do not need to carry a LoRa tracker or any additional
radio device.

## Problem statement

Mountainous terrain, ridges, valleys, and forest clutter can reduce cellular connectivity along
hiking trails. When service is lost, hikers may be unable to:

- Share their current location.
- Contact family or park authorities.
- Receive updated online information.
- Send newly recorded GPS positions to a server.

Most public coverage sources are incomplete, modelled, or biased toward populated locations.
JEJAK therefore combines several sources and represents uncertainty explicitly.

## Stakeholders

### Primary users

- Hikers using the JEJAK mobile application.
- Park and trail authorities.

### Later operational users

- Search and Rescue teams.
- Telecommunications agencies.
- Mobile network planners.

## Core value proposition

JEJAK does more than display a coverage map. It provides an explanation and a recommended action
for each trail segment.

Example:

> Predicted connectivity gap begins in approximately 600 m. Download the offline map, share your
> current position, and check your battery before continuing.

The output remains cautious:

- `likely_covered`
- `uncertain`
- `predicted_gap`

It must never be presented as confirmed zero connectivity without independent field validation.

## Data strategy

### Trail geometry

Four GPX trails provide the first inference routes:

- Gunung Tahan Summit Camp.
- Jalan Bukit Larut.
- Jalan Kledang.
- Taman Rimba Bukit Kerinchi Loop.

Each route is resampled into deterministic segments of approximately 250 m. Every segment receives
a stable `segment_id`.

### Terrain

Copernicus DEM provides:

- Elevation.
- Slope.
- Terrain ruggedness.
- Terrain obstruction indicators.

GPX elevation may support early approximate slope features, but DEM-derived terrain features are
preferred for consistent training and inference.

### Land cover

ESA WorldCover provides:

- Land-cover class.
- Forest fraction around a grid cell or trail segment.
- An environmental-clutter proxy.

WorldCover is not measured radio attenuation.

### Observed mobile performance

Ookla mobile tiles provide:

- `ookla_observed_flag`
- Average download speed.
- Average upload speed.
- Average latency.
- Test count.
- Device count.

A missing Ookla observation means `unobserved`, not no coverage. Missing performance values remain
`NaN`; they are not converted to zero.

Ookla fixed broadband data is excluded from the cellular connectivity model.

### Cellular infrastructure evidence

OpenCellID provides:

- Distance to the nearest recorded cell.
- Cell counts within defined distances.
- Operator count.
- Radio technology.

OpenCellID records are not guaranteed physical tower locations. The current local snapshot has no
usable `averageSignal` values, so that field is excluded.

### Cross-country training labels

Anatel Brazil 4G coverage is the primary source weak label and FCC BDC US 4G LTE coverage is the
secondary source weak label. Ofcom UK measured 4G data is held separately for compatible external
validation. Malaysia has no training label in the MVP.

Raw regulatory definitions are converted through a versioned 4G harmonisation contract to
`coverage_label` and `gap_label`. Labels, source IDs, country IDs, and validation outcomes are not
model predictors. Source regions are pinned before evaluation to prevent cherry-picking.

## Tabular GeoAI design

The source data is geospatial, but the ML model consumes a tabular feature table.

### Training unit

One training row represents a fixed 1 km equal-area cell in a configured Brazil or US source
region. An equivalent target-unlabelled table is generated for Malaysia using the same feature
schema.

Example schema:

```text
grid_id
country_code
region_id
row_role
spatial_group_id
elevation_mean
elevation_std
slope_mean
terrain_ruggedness
terrain_obstruction
forest_fraction_buffer
distance_to_nearest_cell_km
cell_count_5km
cell_count_10km
operator_count
ookla_observed_flag
ookla_download_kbps
ookla_upload_kbps
ookla_latency_ms
ookla_tests
ookla_devices
gap_label
```

### Trail inference unit

One inference row represents an approximately 250 m trail segment. The same feature-building
functions are reused for training grids and trail segments.

The 250 m trail output provides useful route detail by attaching each segment to its documented
1 km prediction support. It must not be described as field-validated 250 m coverage truth.

## GeoAI model

### Objective

Learn a source-domain 4G gap ranking and transfer it to compatible Malaysian feature conditions:

```text
source-domain gap score(terrain, land cover, cell and performance evidence)
```

### Baseline

Use Logistic Regression as a simple, interpretable baseline.

### Primary MVP model

Use scikit-learn `HistGradientBoostingClassifier`.

It is appropriate because:

- The feature table is tabular.
- Terrain and forest relationships can be nonlinear.
- It supports missing numerical values.
- It avoids an additional XGBoost runtime dependency.
- It is suitable for lightweight API inference.

XGBoost may be evaluated later as an experiment, but it is not required for the first MVP.

### Validation

Validation must use region-held-out spatial groups and leave-one-source-country-out stress tests
rather than a random row split. Neighbouring cells must not be divided casually between training
and validation because this can exaggerate performance.

Initial evaluation includes:

- Gap recall.
- Precision-recall AUC.
- Balanced accuracy.
- Brier score.
- Source-domain calibration quality, never described as Malaysian calibration.
- Comparison with Logistic Regression.
- Ablation with and without OpenCellID.
- Source-versus-Malaysia domain similarity or OOD diagnostics.
- Compatible external validation using the held-out Ofcom measured data.
- Malaysia Ookla positive-agreement analysis; missing Ookla is never a negative label.

These metrics measure source-label transfer performance, not Malaysian field accuracy.

## Prediction logic

The ML model produces a continuous transferred gap score.

```text
transferred_gap_score = model.predict_proba(features)[:, 1]
```

The application combines that bounded score with domain similarity and evidence availability:

```text
High score + in-domain + sufficient evidence -> predicted_gap
Low score + positive evidence                -> likely_covered
OOD, incomplete, or conflicting evidence     -> uncertain
```

`uncertain` is an abstention outcome. It is not a third training label.

For example, the absence of Ookla data may reduce confidence, but it must not independently turn a
segment into `predicted_gap`.

## Stable prediction output

Each trail prediction preserves the JEJAK backend contract:

```json
{
  "segment_id": "gunung-tahan-012",
  "risk_score": 0.82,
  "risk_class": "predicted_gap",
  "confidence": 0.71,
  "model_version": "connectivity-transfer-v0.1.0",
  "domain_similarity": 0.76,
  "out_of_distribution": false,
  "warning_eligible": false,
  "top_factors": [
    {
      "feature": "terrain_obstruction",
      "contribution": 0.31,
      "direction": "increases_risk"
    }
  ]
}
```

In the connectivity model, `risk_score` is a cross-country transferred gap score, not a
Malaysian-calibrated probability. `confidence` combines model uncertainty, source agreement,
target-domain similarity, and evidence completeness.

## Phone-only workflow

### Before the hike

The application:

- Downloads the route and connectivity predictions.
- Stores maps and warnings offline.
- Records the planned route.
- Encourages the user to share the trip plan and expected return time.

### Before entering a predicted gap

The application:

- Displays a warning.
- Attempts to synchronise the current GPS position.
- Records the timestamp, route progress, and battery level.
- Confirms whether the server acknowledged the synchronisation.
- Recommends downloading or checking the offline map.

Only a server-acknowledged position is described as the last successfully synchronised location.

### Inside the predicted gap

The phone:

- Continues recording GPS offline.
- Stores trajectory points and events locally.
- Does not assume the server can observe the hiker in real time.
- Queues synchronisation attempts.

### When connectivity returns

The phone:

- Synchronises queued locations and events.
- Records the actual connectivity-return point.
- Allows later comparison between predicted and observed connectivity behaviour.

## Connectivity timeline

The app may translate segment predictions into a route timeline:

```text
Current segment       likely_covered
Next 1.0 km           uncertain
Following 2.5 km      predicted_gap
Expected return area  likely_covered
```

Estimated duration depends on route distance and expected walking speed. It must be presented as an
estimate rather than a guaranteed time without service.

## Recommendations for hikers

For a high-confidence predicted gap, JEJAK may recommend:

- Download the offline trail map.
- Synchronise the current location.
- Notify an emergency contact.
- Check battery level.
- Enable battery-saving settings that do not disable required GPS logging.
- Avoid separating from the hiking group.
- Note the expected distance to the next likely-covered segment.

## Recommendations for authorities

For every predicted gap, the planning output may contain:

- Gap start and end segments.
- Estimated gap length.
- Prediction confidence.
- Main contributing evidence.
- Nearby junctions, shelters, and access points.
- Field-survey priority.
- Suggested warning-sign locations.
- Suggested phone check-in points before and after the gap.

Recommended actions follow an evidence hierarchy:

```text
Low confidence
-> conduct a multi-operator walk test

Predicted gap with moderate safety impact
-> warning sign + app warning + offline preparation

Field-verified high-priority gap
-> submit evidence to the relevant operator or authority
```

JEJAK does not recommend unapproved DIY cellular repeaters.

## Planning outputs

Initial outputs include:

```text
data/interim/trail_segments.parquet
data/interim/trail_segments.geojson

data/processed/connectivity_training_grid_v1.parquet
data/processed/trail_connectivity_features_v1.parquet
data/processed/trail_connectivity_predictions_v1.parquet
data/processed/trail_connectivity_predictions_v1.geojson

artifacts/<experiment-id>/connectivity_planning_map.html
```

The interactive map should display:

- Trail segments.
- `likely_covered` segments.
- `uncertain` segments.
- `predicted_gap` segments.
- Prediction confidence.
- Contributing evidence.
- Suggested warning and survey locations.

## Search and Rescue relationship

The trained SAR model is not part of the first connectivity MVP.

After the connectivity MVP is stable, a separate phone-only SAR workstream may use:

- Planned route.
- Last successfully synchronised location.
- Offline trajectory after later synchronisation.
- Expected segment travel time.
- Missing-connectivity duration.
- Checkpoint overdue status.
- Off-trail distance.
- Stationary duration.

Connectivity loss within a predicted gap may be expected. Connectivity loss outside a predicted
gap may justify additional review, but neither condition alone proves that a hiker is lost.

## Deferred features

The following are outside the first MVP:

- Trained lost-hiker or SAR risk model.
- Dynamic weather-and-terrain safety score.
- Alternative-route optimisation.
- Real-time tracking inside cellular gaps.
- LoRa trackers.
- LoRa gateways.
- Bluetooth-to-LoRa infrastructure.
- Cellular repeater deployment.

These may be reconsidered after the connectivity pipeline and phone workflow are validated.

## Implementation sequence

```text
Python 3.11 environment
-> dataset catalog alignment
-> GPX ingestion
-> deterministic 250 m segmentation
-> Ookla and OpenCellID joins
-> Malaysia and source-region DEM/WorldCover acquisition
-> Anatel/FCC labels and Ofcom validation acquisition
-> shared feature builder
-> source-labelled and Malaysia target-unlabelled 1 km tables
-> spatial/country transfer and domain-shift evaluation
-> trail inference
-> phone warning workflow
-> later SAR workstream
```

## Model-governance boundary

The first trained classifier remains an experiment or candidate proxy model. It must not be
promoted as a field-validated `Champion`.

Promotion requires:

- Independent Malaysian field measurements or an approved compatible Malaysian label source.
- Multi-operator observations.
- Spatial evaluation on locations not used for fitting.
- Probability calibration against measured outcomes.
- Documented model limitations.

## Success criteria

The connectivity MVP is successful when it can:

1. Reproducibly generate trail segments and features.
2. Train and spatially/cross-country evaluate the transfer proxy model.
3. Produce cautious connectivity predictions for all four trails.
4. Explain the major evidence behind each prediction.
5. Warn phone users before predicted connectivity gaps.
6. Continue recording locations offline.
7. Synchronise queued locations after connectivity returns.
8. Give authorities a map of areas that should be surveyed or prioritised.

The MVP demonstrates GeoAI-assisted connectivity planning. It does not claim to replace field
surveys, operator engineering data, or operational SAR procedures.
