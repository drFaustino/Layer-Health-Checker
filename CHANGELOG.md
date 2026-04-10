# Changelog  
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-04-10
### Added
- Initial public release of **Layer Health Checker**.
- Support for both **vector and raster** layer validation.
- Detection of invalid geometries and geometry issues.
- CRS validation and mismatch detection.
- Attribute inspection and attribute table opener.
- Raster metadata inspection (extent, resolution, nodata).
- Dual geometry repair modes:
  - *Repair Invalid Only*
  - *Repair Entire Layer*
- Zoom to invalid features.
- Export of validation results to CSV.
- Creation of a clean repaired layer.
- Logging panel and progress bar.
- Modern UI layout compatible with QGIS 4 and Qt6.
- Full translation support (`.ts` and `.qm` files).
- Toolbar icon and menu integration.

---

## [Unreleased]
### Planned
- Extended raster validation (statistics, band-level checks).
- Optional `.qrc` resource scanning.
- Batch validation via QGIS Processing.
- Automatic detection of Qt Linguist on more Linux distributions.
