# Satellite Image-Based Deforestation Detection

Transfer-learning land-cover classification and NDVI change analysis for detecting
deforestation from multi-temporal Sentinel-2 imagery, validated against Global Forest Watch.

*D A S K R Manognya and Divisht Dahiya — Dept. of Computer Science and Engineering, IIT Gandhinagar*

## Overview

A natural way to detect deforestation is to train a land-cover classifier and run it on
imagery of the same region in two years, flagging tiles that change from forest to a
non-forest class. This project tests that idea, shows it fails, and demonstrates a working
alternative based on NDVI differencing.

Research question: Can a transfer-learning land-cover classifier detect deforestation by
comparing satellite images from different years, and how well do detections agree with
official environmental reports? Short answer: not through class transitions
(F1 <= 0.25 across three regions), but yes through NDVI differencing, reaching F1 = 0.73
against Global Forest Watch.

## Key results

- EuroSAT ResNet-50 classifier: 98.61% test accuracy (Forest F1 = 0.997)
- Class-transition change detection: F1 = 0.011 to 0.251 across three regions (fails)
- NDVI differencing: precision 0.811, recall 0.666, F1 0.731, IoU 0.576

Why class transitions fail: of the 1,356 tiles Hansen recorded as lost in the Washington
study area, the classifier labelled only 16% as Forest in the first year, so a
forest-to-non-forest transition was impossible to detect on 84% of true loss. Causes:
domain shift (EuroSAT is European), error multiplication across two noisy classifications,
and no cleared-land class in the EuroSAT label set. NDVI sidesteps all three.

## Method

1. Fine-tune ResNet-50 (ImageNet-pretrained) on EuroSAT RGB (two-stage transfer learning).
2. Acquire Sentinel-2 summer composites for 2018 and 2024 via Google Earth Engine.
3. Baseline: classify each 640 m tile in both years, flag Forest to non-forest.
4. Proposed: NDVI differencing, flag tiles where vegetated pixels (NDVI >= 0.60) lose at
   least DROP greenness over at least FRAC of the tile.
5. Validate against the Hansen Global Forest Change lossyear layer.

Study area: Washington Cascades, USA, bbox [-123.4, 46.8, -122.9, 47.2]. Comparison
regions: Brazilian Amazon (Rondonia) and Romanian Carpathians.

## Repository structure

- notebooks/deforestation_detection.ipynb : full pipeline (640 m, F1 0.731)
- notebooks/experiments/deforestation_detection_30m.ipynb : 30 m tile experiment (F1 0.648)
- assets/ : figures, metrics, confusion matrix
- Deforestation_Detection_NDVI_GFW.pdf : compiled IEEE paper

## Reproduce

Run notebooks/deforestation_detection.ipynb top to bottom: train and evaluate the
classifier, acquire imagery (needs a free Earth Engine account and earthengine authenticate),
run NDVI differencing (DROP = 0.18, FRAC = 0.05), and validate against Global Forest Watch.
Figures are written to assets/. 
Download EuroSAT RGB from the Kaggle dataset (https://www.kaggle.com/datasets/apollo2506/eurosat-dataset), which bundles the RGB and multispectral versions; the original dataset is from Helber et al. (https://zenodo.org/records/7711810). Unzip so the class folders sit at data/EuroSAT/.

## Limitations

640 m tiles are coarse versus the 30 m Hansen product; a 30 m experiment (F1 0.648) showed
finer granularity does not improve agreement, due to co-registration and edge effects.
Two-date differencing misses within-window loss that regrows, the main source of false
negatives in fast-cycle Pacific-Northwest forestry.

## Data acquisition (Google Earth Engine)

The Sentinel-2 imagery and the Hansen forest-loss layer are pulled through Google Earth Engine (free for research use). One-time setup:

- Create a free account at https://earthengine.google.com, register a Google Cloud project, and enable the Earth Engine API for it.
- Install the client: `pip install earthengine-api geemap`
- Authenticate once: `earthengine authenticate`

Then edit `scripts/earth_engine_export.py`, set `PROJECT` to your Cloud project ID (and `BBOX` / years if changing the region), and run:

    python scripts/earth_engine_export.py

This exports five GeoTIFFs to a "deforestation" folder in Google Drive: `s2_rgb_2018.tif`, `s2_rgb_2024.tif`, `ndvi_2018.tif`, `ndvi_2024.tif`, and `hansen_lossyear.tif`. Track progress at https://code.earthengine.google.com/tasks, then download them into `data/study_region/`. Imagery uses a season-matched summer composite (1 June to 15 September), under 20% cloud, at 10 m resolution.
