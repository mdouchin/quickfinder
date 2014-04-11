#-----------------------------------------------------------
#
# Item Browser is a QGIS plugin which allows you to browse a multiple selection.
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QDialog

from qgis.gui import QgsGenericProjectionSelector

from quickfinder.qgissettingmanager import SettingDialog
from quickfinder.core.mysettings import MySettings
from quickfinder.ui.ui_settings import Ui_Settings
from quickfinder.qgiscombomanager import VectorLayerCombo, ExpressionFieldCombo

class ConfigurationDialog(QDialog, Ui_Settings, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()

        SettingDialog.__init__(self, self.settings)

        self.layerComboManager = VectorLayerCombo(self.layerId,
                                                  lambda: self.settings.value("layerId"))
        self.fieldComboManager = ExpressionFieldCombo(self.fieldName,
                                                      self.expressionButton,
                                                      self.layerComboManager,
                                                      lambda: self.settings.value("fieldName"))

        self.layerComboManager.layerChanged.connect(self.layerChanged)
        self.fieldName.activated.connect(self.fieldChanged)

        self.layer = None
        self.fieldName.setEnabled(False)
        self.expressionButton.setEnabled(False)

        self.layerChanged()

        self.geomapfish_crsButton.clicked.connect(self.geomapfish_crsButtonClicked)

    def layerChanged(self):
        print "layerChanged"
        self.fieldName.setEnabled(False)
        self.expressionButton.setEnabled(False)
        self.layer = self.layerComboManager.getLayer()
        if self.layer is None:
            return
        self.fieldName.setEnabled(True)
        self.expressionButton.setEnabled(True)

    def fieldChanged(self):
        print "fieldchanged"
        # self.searchWidget.setEnabled(False)
        if self.layer is None:
            return
        field, isExpression = self.fieldComboManager.getExpression()
        print field
        if field is None:
            print "ret"
            return
        # self.searchWidget.setEnabled(True)
        if not isExpression:
            fieldType = self.layer.pendingFields().field(field).type()
            # if field is a string set operator to "LIKE"
            if fieldType == QVariant.String:
                self.operatorBox.setCurrentIndex(6)
            # if field is not string, do not use "LIKE"
            if (fieldType != QVariant.String
                and self.operatorBox.currentIndex() == 6):
                self.operatorBox.setCurrentIndex(0)
            return
        # is expression, use string by default
        self.operatorBox.setCurrentIndex(6)

    def geomapfish_crsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish serveur CRS')
        dlg.setSelectedAuthId(self.geomapfish_crs.text())
        dlg.exec_()
        self.geomapfish_crs.setText(dlg.selectedAuthId())
        del dlg

