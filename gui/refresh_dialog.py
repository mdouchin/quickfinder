#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2013 Denis Rouzaud
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog
from ..core.project_finder import n_days_ago_iso_date
from ..core.my_settings import MySettings
from ..ui.ui_refresh import Ui_Refresh


class RefreshDialog(QDialog, Ui_Refresh):

    stop = False
    searchProgress = 0
    currentLayerLength = 0

    def __init__(self, project_finder, project_search_model=None, selectedRows=None):
        QDialog.__init__(self)
        self.setupUi(self)
        self.progressBar.setValue(0)

        self.settings = MySettings()
        self.project_finder = project_finder
        self.project_search_model = project_search_model
        self.selectedRows = selectedRows

        if project_search_model is None:
            self.selectionWidget.hide()
            self.unrecordedCheckBox.hide()
            self.unevaluatedCheckBox.setChecked(True)
            self.unevalutedDaysSpinBox.setValue(max(1,self.settings.value("refreshDelay")/3))

        self.progressBar.hide()
        self.cancelButton.hide()

        self.cancelButton.clicked.connect(self.cancel)
        self.refreshButton.clicked.connect(self.refresh)

        self.project_finder.recordingSearchProgress.connect(self.setProgress)

    def refresh(self):
        searches = self.project_finder.searches

        self.stop = False
        self.cancelButton.show()
        self.refreshButton.hide()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(searches)*100)  # progressBar only accepts int, so scaling
        self.progressBar.show()

        unRecorded = self.unrecordedCheckBox.isChecked()
        onlySelected = self.selectionComboBox.currentIndex() == 1
        unEvaluated = self.unevaluatedCheckBox.isChecked()
        unEvaluatedDelay = self.unevalutedDaysSpinBox.value()
        removeDeleted = self.deletedLayersCheckBox.isChecked()

        limit_date = n_days_ago_iso_date(unEvaluatedDelay)

        self.searchProgress = -1

        for search in searches.values():
            QCoreApplication.processEvents()

            self.searchProgress += 1
            self.currentLayerLength = 0
            self.setProgress()

            # user stop
            if self.stop:
                break

            # delete search if layer has been deleted
            layer = search.layer()
            if layer is None and removeDeleted:
                if self.project_search_model is not None:
                    self.project_search_model.removeSearches([search.searchId])
                else:
                    self.project_finder.deleteSearch(search.searchId)
                continue

            # if specified do not process recently evaluated search
            if unEvaluated and search.dateEvaluated >= limit_date:
                continue

            # if specified only process non evaluated searches
            if unRecorded and search.dateEvaluated is not None:
                continue

            # if specified only do selected rows
            if onlySelected and self.selectedRows is not None:
                if search.searchId not in self.selectedRows:
                    continue

            self.currentLayerLength = layer.featureCount()
            ok, message = self.project_finder.recordSearch(search, False)

        self.project_finder.optimize()

        self.progressBar.hide()
        self.cancelButton.hide()
        self.refreshButton.show()

    def closeEvent(self, e):
        self.cancel()
        e.accept()

    def cancel(self):
        self.project_finder.stop_record()
        self.stop = True

    def setProgress(self, value=0):
        p = self.searchProgress
        if self.currentLayerLength!=0:
            p += float(value) / self.currentLayerLength
        p *= 100
        self.progressBar.setValue(p)


