import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QAbstractItemView

class LayerHealthCheckerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Carica il file .ui
        uic.loadUi(os.path.join(os.path.dirname(__file__), "layer_health_checker_dialog.ui"), self)

        # Imposta tabella come non editabile e selezione per riga
        self.tableResults.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableResults.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)