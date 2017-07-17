'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from xcirculardichro.gui.choices.abstractchoices import AbstractChoices
import logging
logger = logging.getLogger(__name__)

DEFAULT_SELECTIONS = [["", "", ""],]
PLOT_CHOICES = ["Y1/Y2",]

class UndefinedChoices(AbstractChoices):
    COUNTER_OPTS = ["X", "Y1", "Y2"]
    
    def __init__(self, parent=None):
        super(UndefinedChoices, self).__init__(parent)
        layout = self.layout()        
        
        plotLayout = qtGui.QHBoxLayout()
        label = qtGui.QLabel("Plot Type: ")
        self.plotSelector = qtGui.QComboBox()
        self.plotSelector.insertItems(0, PLOT_CHOICES)
        plotLayout.addWidget(label)
        plotLayout.addWidget(self.plotSelector)
        
        layout.addLayout(plotLayout)
        self.plotSelector.currentIndexChanged[int].connect(self.plotSelectorChanged)
        self.setLayout(layout)
        self.plotSelections = DEFAULT_SELECTIONS

    def calcPlotData(self, data):
        return data
        
    def getPlotSelections(self):
        selections = self.plotSelections[0]
        logger.debug("selections %s " % selections )
        return selections
        
    @qtCore.pyqtSlot(int)
    def plotSelectorChanged(self, newType):
        self.plotTypeChanged[int].emit(newType)
        
    def setPlotSelections(self, selections):
        self.plotSelections[0] = selections
        
    def getPlotAxisLabels(self):
        return self.getPlotSelections()

    def getPlotAxisLabelsIndex(self):
        plotTypes = self.plotSelector.currentText().split("/")
        axisIndex = []
        axisIndex.append(0)    #x axis, kQTExifUserDataFlashEnergy
        for pType in plotTypes:
            axisIndex.append(1)
            
            
        return axisIndex

    def getDataLabels(self):
        plotTypes = self.plotSelector.currentText().split("/")
        labels = ['E', ]
        labels.extend(plotTypes)
        return labels