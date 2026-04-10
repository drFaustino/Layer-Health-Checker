# Layer Health Checker  
A comprehensive QGIS plugin to validate and repair the health of **vector and raster layers**, including geometry integrity, CRS consistency, attribute structure, and raster metadata.

Layer Health Checker provides a unified interface for diagnosing issues, repairing invalid geometries, inspecting layer properties, and exporting validation reports.  
It is fully compatible with **QGIS 4** and **Qt6**.

---

## ✨ Features

### 🔍 Vector Layer Validation
- Detect invalid geometries (self‑intersections, ring orientation, slivers, etc.)
- Highlight invalid features in the map canvas
- Zoom directly to invalid features
- Export validation results to CSV
- Copy a “clean” version of the layer

### 🛠 Geometry Repair Tools
Two repair modes are available:
- **Repair Invalid Only** — fixes only the features detected as invalid  
- **Repair Entire Layer** — runs a full geometry sanitization on the whole dataset  

Both modes use QGIS native algorithms (`native:fixgeometries`) and produce a new repaired layer.

### 📑 Attribute Tools
- Open the attribute table of the selected layer directly from the plugin
- Inspect attribute consistency and missing fields (planned)

### 🗺 Raster Layer Validation
- Check CRS definition and consistency
- Inspect raster metadata (resolution, extent, nodata values)
- Detect missing or corrupted metadata entries
- Planned: raster statistics and band‑level validation

### 🌐 CRS & Metadata Checks
- Validate CRS presence and correctness
- Detect mismatches between layer CRS and project CRS
- Inspect layer metadata for anomalies

### 🧰 User Interface
- Clean and responsive UI designed for QGIS 4
- Combo box to select repair mode
- Progress bar and logging panel
- Toolbar icon + menu entry
- Full translation support (`.ts` and `.qm` files)

---

## 📦 Installation

1. Download or clone the plugin repository:
2. Copy the plugin folder into your QGIS profile: <user profile>/python/plugins/
3. Restart QGIS.
4. Enable **Layer Health Checker** from: Plugins → Manage and Install Plugins

---

## 🚀 Usage

1. Open the plugin from the toolbar or the *Plugins* menu.
2. Select a vector or raster layer from the dropdown.
3. Click **Run Check** to analyze the layer.
4. Use the available tools:
- **Zoom Invalid**
- **Export CSV**
- **Copy Clean Layer**
- **Repair Geometries**
- **Open Attribute Table**
5. Choose the repair mode:
- *Repair Invalid Only*
- *Repair Entire Layer*

Repaired layers are added to the project automatically.

---

## 🌍 Translations

The plugin supports multilingual `.qm` files.  
Translations are stored in: i18n/

To generate translation files:

1. Extract strings using your translation builder or Qt tools.
2. Edit translations in **Qt Linguist**.
3. Compile `.qm` files using `lrelease`.
---

## 🧪 Compatibility

- **QGIS:** 4.0 – 4.99  
- **Qt:** Qt6  
- **OS:** Windows, macOS, Linux  

---

## 👤 Author

**Dr. Geol. Faustino Cetraro**  
Email: geol-faustino@libero.it  

---

## 📄 License

This project is released under the **GPL‑3 License**.

---

## 📝 Changelog

See the full changelog in `CHANGELOG.md`.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.  
Please open an issue or submit a pull request on GitHub.

---

## ⭐ Acknowledgements

This plugin uses:
- QGIS native processing algorithms  
- Qt6 translation framework  
- defusedxml for secure XML parsing  

Thanks to the QGIS community for continuous inspiration and support.
