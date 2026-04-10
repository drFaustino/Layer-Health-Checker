import os
import csv
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QAction, QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsSpatialIndex, QgsMapLayer
from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication, QTranslator, QLocale
from qgis.PyQt.QtCore import QSettings

from .layer_health_checker_dialog import LayerHealthCheckerDialog

class LayerHealthChecker:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = None
        self.invalid_feature_ids = []

        # Carica traduzioni
        locale = QSettings().value("locale/userLocale", "en")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", f"layer_health_checker_{locale}.qm"
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate("LayerHealthChecker", message)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.action = QAction(QIcon(icon_path), self.tr("Layer Health Checker"), self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr("&Layer Health Checker"), self.action)

    def unload(self):
        self.iface.removePluginMenu(self.tr("&Layer Health Checker"), self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dlg:
            self.dlg = LayerHealthCheckerDialog()

            if not self.dlg:
                self.dlg = LayerHealthCheckerDialog()

                # Inizializza combo repair mode
                self.dlg.comboRepairMode.clear()
                self.dlg.comboRepairMode.addItem(self.tr("Repair Invalid Only"), "invalid_only")
                self.dlg.comboRepairMode.addItem(self.tr("Repair Entire Layer"), "entire_layer")

            # Tabella configurazione
            self.dlg.tableResults.setColumnCount(2)  # <-- correzione: due colonne
            self.dlg.tableResults.setHorizontalHeaderLabels([self.tr("Check"), self.tr("Result")])
            self.dlg.tableResults.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.dlg.tableResults.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.dlg.tableResults.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.dlg.tableResults.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

            # Pulsanti
            self.dlg.btnRun.clicked.connect(self.check_layer)
            self.dlg.btnExport.clicked.connect(self.export_csv)
            self.dlg.btnZoomInvalid.clicked.connect(self.zoom_invalid)
            self.dlg.btnClear.clicked.connect(self.clear_all)
            self.dlg.btnCopyClean.clicked.connect(self.copy_clean_layer)
            self.dlg.btnRepair.clicked.connect(self.repair_geometries)
            self.dlg.btnOpenTable.clicked.connect(self.open_attribute_table)
            self.dlg.btnRepair.clicked.connect(self.repair_geometries)
            self.dlg.btnClose.clicked.connect(self.dlg.close)

        self.populate_layers()
        self.dlg.show()
        self.dlg.exec()

    def populate_layers(self):
        self.dlg.comboLayers.clear()
        for layer in QgsProject.instance().mapLayers().values():
            self.dlg.comboLayers.addItem(layer.name(), layer)

    def log(self, text):
        self.dlg.textLog.append(text)

    def update_progress(self, value):
        self.dlg.progressBar.setValue(value)

    def clear_all(self):
        self.dlg.tableResults.setRowCount(0)
        self.dlg.textLog.clear()
        self.dlg.progressBar.setValue(0)
        self.invalid_feature_ids = []
        self.log(self.tr("Cleared."))

    # =========================
    # CORE CHECK
    # =========================
    def check_layer(self):
        layer = self.dlg.comboLayers.currentData()
        self.clear_all()
        if not layer:
            return

        self.log(self.tr(f"Checking layer: {layer.name()}"))
        if layer.type() == QgsMapLayer.VectorLayer:
            self.check_vector(layer)
        elif layer.type() == QgsMapLayer.RasterLayer:
            self.check_raster(layer)
        else:
            self.add_result(self.tr("Layer Type"), self.tr("Unsupported layer"), False)
        self.update_progress(100)
        self.log(self.tr("Check completed."))
        self.update_progress(0)

    # =========================
    # VECTOR CHECK
    # =========================
    def check_vector(self, layer):
        features = list(layer.getFeatures())
        total = len(features)
        # CRS
        self.add_result("CRS", self.tr("Valid") if layer.crs().isValid() else self.tr("Invalid CRS"), layer.crs().isValid())
        # Geometry
        invalid_count = 0
        for i, f in enumerate(features):
            if not f.geometry().isGeosValid():
                invalid_count += 1
                self.invalid_feature_ids.append(f.id())
            if total > 0:
                self.update_progress(int((i / total) * 60))
        self.add_result(self.tr("Geometry"), self.tr("All valid") if invalid_count == 0 else self.tr(f"{invalid_count} invalid geometries"), invalid_count == 0)
        # NULL attributes
        null_count = sum(1 for f in features for val in f.attributes() if val is None)
        self.add_result(self.tr("Attributes"), self.tr("No NULL") if null_count == 0 else self.tr(f"{null_count} NULL values"), null_count == 0)
        # Duplicates
        dup_count = self.check_duplicates(layer, features)
        self.add_result(self.tr("Duplicates"), self.tr("No duplicates") if dup_count == 0 else self.tr(f"{dup_count} duplicates"), dup_count == 0)

    # =========================
    # RASTER CHECK
    # =========================
    def check_raster(self, layer):
        self.add_result(self.tr("Layer Type"), self.tr("Raster"), True)
        self.add_result(self.tr("Validity"), self.tr("Valid raster") if layer.isValid() else self.tr("Invalid raster"), layer.isValid())
        provider = layer.dataProvider()
        band_count = provider.bandCount()
        self.add_result(self.tr("Bands"), self.tr(f"{band_count} bands"), band_count > 0)
        extent = layer.extent()
        self.add_result(self.tr("Extent"), self.tr("Valid extent") if not extent.isEmpty() else self.tr("Empty extent"), not extent.isEmpty())
        nodata_issues = sum(1 for b in range(1, band_count + 1) if not provider.sourceHasNoDataValue(b))
        self.add_result(self.tr("NoData"), self.tr("All bands have NoData") if nodata_issues == 0 else self.tr(f"{nodata_issues} bands missing NoData"), nodata_issues == 0)

    # =========================
    # DUPLICATES
    # =========================
    def check_duplicates(self, layer, features):
        index = QgsSpatialIndex()
        duplicates = 0
        for f in features:
            index.insertFeature(f)
        for f in features:
            ids = index.intersects(f.geometry().boundingBox())
            for other_id in ids:
                if other_id != f.id():
                    other = layer.getFeature(other_id)
                    if f.geometry().equals(other.geometry()):
                        duplicates += 1
                        break
        return duplicates

    # =========================
    # ZOOM
    # =========================
    def zoom_invalid(self):
        layer = self.dlg.comboLayers.currentData()
        if not self.invalid_feature_ids:
            self.log(self.tr("No invalid features."))
            return
        layer.selectByIds(self.invalid_feature_ids)
        iface.mapCanvas().zoomToSelected(layer)
        self.log(self.tr("Zoomed to invalid features."))

    # =========================
    # EXPORT CSV
    # =========================
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self.dlg, self.tr("Save CSV"), "", self.tr("CSV files (*.csv)"))
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([self.tr("Check"), self.tr("Result")])
            for row in range(self.dlg.tableResults.rowCount()):
                check = self.dlg.tableResults.item(row, 0).text()
                result = self.dlg.tableResults.item(row, 1).text()
                writer.writerow([check, result])
        self.log(self.tr(f"Report saved: {path}"))

    # =========================
    # UI RESULT
    # =========================
    def add_result(self, check, message, ok):
        row = self.dlg.tableResults.rowCount()
        self.dlg.tableResults.insertRow(row)

        item_check = QTableWidgetItem(check)
        item_msg = QTableWidgetItem(message)

        # Colore ✔ / ✖
        if ok:
            item_msg.setText("✔ " + message)
            item_msg.setForeground(QColor("green"))
        else:
            item_msg.setText("✖ " + message)
            item_msg.setForeground(QColor("red"))

        # Non editabile
        item_check.setFlags(item_check.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item_msg.setFlags(item_msg.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # Scrivi nella tabella
        self.dlg.tableResults.setItem(row, 0, item_check)
        self.dlg.tableResults.setItem(row, 1, item_msg)

    # =========================
    # COPY CLEAN LAYER
    # =========================
    def copy_clean_layer(self):
        layer = self.dlg.comboLayers.currentData()
        if not layer or not self.invalid_feature_ids:
            self.log(self.tr("Nothing to copy."))
            return
        # Crea layer memory solo con geometrie valide
        crs = layer.crs()
        fields = layer.fields()
        from qgis.core import QgsVectorLayer
        clean_layer = QgsVectorLayer(f"{layer.wkbType()}?crs={crs.authid()}", layer.name() + "_clean", "memory")
        clean_layer.dataProvider().addAttributes(fields)
        clean_layer.updateFields()
        for f in layer.getFeatures():
            if f.id() not in self.invalid_feature_ids:
                clean_layer.dataProvider().addFeature(f)
        QgsProject.instance().addMapLayer(clean_layer)
        self.log(self.tr(f"Clean layer '{clean_layer.name()}' created."))
    
    # =========================
    # REPAIR GEOMETRIES
    # =========================
    def repair_geometries(self):
        layer = self.dlg.comboLayers.currentData()

        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            self.log(self.tr("No vector layer selected."))
            return

        mode = self.dlg.comboRepairMode.currentData()

        if mode == "invalid_only":
            if not self.invalid_feature_ids:
                self.log(self.tr("No invalid geometries to repair."))
                return
            self.repair_invalid_only(layer)

        elif mode == "entire_layer":
            self.repair_entire_layer(layer)

        else:
            self.log(self.tr("Unknown repair mode."))

    # =========================
    # REPAIR INVALID GEOMETRIES
    # =========================
    def repair_invalid_only(self, layer):
        import processing

        self.log(self.tr("Repairing only invalid geometries..."))

        # Estrai solo le feature invalide
        invalid_feats = [f for f in layer.getFeatures() if f.id() in self.invalid_feature_ids]

        if not invalid_feats:
            self.log(self.tr("No invalid geometries found."))
            return None

        # Crea layer temporaneo con solo le invalide
        crs = layer.crs()
        fields = layer.fields()

        temp = QgsVectorLayer(f"{layer.wkbType()}?crs={crs.authid()}", "invalid_temp", "memory")
        temp_dp = temp.dataProvider()
        temp_dp.addAttributes(fields)
        temp.updateFields()
        temp_dp.addFeatures(invalid_feats)

        # Ripara
        result = processing.run(
            "native:fixgeometries",
            {"INPUT": temp, "OUTPUT": "memory:"}
        )

        repaired = result["OUTPUT"]
        repaired.setName(layer.name() + "_invalid_repaired")

        QgsProject.instance().addMapLayer(repaired)
        self.log(self.tr(f"Repaired invalid geometries layer created: {repaired.name()}"))

        return repaired

    # =========================
    # REPAIR ENTIRE GEOMETRIES
    # =========================
    def repair_entire_layer(self, layer):
        import processing

        self.log(self.tr("Repairing entire layer..."))

        result = processing.run(
            "native:fixgeometries",
            {"INPUT": layer, "OUTPUT": "memory:"}
        )

        repaired = result["OUTPUT"]
        repaired.setName(layer.name() + "_repaired")

        QgsProject.instance().addMapLayer(repaired)
        self.log(self.tr(f"Repaired full layer created: {repaired.name()}"))

        return repaired

    # =========================
    # OPEN ATTRIBUTE TABLE
    # =========================
    def open_attribute_table(self):
        layer = self.dlg.comboLayers.currentData()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            self.log(self.tr("No vector layer selected."))
            return

        iface.showAttributeTable(layer)
        self.log(self.tr("Attribute table opened."))
