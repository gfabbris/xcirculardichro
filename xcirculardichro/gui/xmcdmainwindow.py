'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging

import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore

from spec2nexus.spec import SpecDataFile
from xcirculardichro.config.loggingConfig import METHOD_ENTER_STR,\
    METHOD_EXIT_STR
from xcirculardichro.gui.xmcddatanavigator import XMCDDataNavigator
from xcirculardichro.gui.plotwidget import PlotWidget
from xcirculardichro.gui.dataselection.selectionholder import SelectionHolder
from xcirculardichro.data.intermediatedatanode import SELECTED_NODES

logger = logging.getLogger(__name__)

APP_NAME = 'XMCD'

class XMCDMainWindow(qtWidgets.QMainWindow):
    '''
    Main Window for X-Ray Magnetic Circular Dichroism Application
    '''
    
    def __init__(self, parent=None):
        super(XMCDMainWindow, self).__init__(parent)
        logger.debug(METHOD_ENTER_STR)
        self.setAttribute(qtCore.Qt.WA_DeleteOnClose)
        self._createMenuBar()
        splitter = qtWidgets.QSplitter()
        
        self._dataNavigator = XMCDDataNavigator()
        self._dataSelections = SelectionHolder()
        self._plotWidget = PlotWidget()
        
        splitter.addWidget(self._dataNavigator)
        splitter.addWidget(self._dataSelections)
        splitter.addWidget(self._plotWidget)
        
        self.setCentralWidget(splitter)
        self.setWindowTitle(APP_NAME)
        self.show()
        
        self._dataNavigator.model().dataChanged.connect(self.handleNavigatorDataChanged)
        self._dataSelections.dataSelectionsChanged.connect(self.handleDataSelectionsChanged)
        self._dataSelections.plotOptionChanged.connect(self.updatePlotData)
        self._plotWidget.leftSelectionChanged[str].connect(self.handleLeftDataSelectionChanged)
        self._plotWidget.rightSelectionChanged[str].connect(self.handleRightDataSelectionChanged)
        self._dataSelections.pointSelectionAxisChanged[int].connect(self._plotWidget.setPointSelectionAxis)
        self._dataSelections.pointSelectionTypeChanged[int].connect(self._plotWidget.setPointSelectionType)
        self._dataSelections.pointSelectionReloadPicks.connect(self.handlePointSelectionReloadPicks)
        logger.debug(METHOD_EXIT_STR)
        
    def _createMenuBar(self):
        '''
        internal method to setup the menu bar for this application
        '''
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        fileMenu = menuBar.addMenu('File')
        dataMenu = menuBar.addMenu('Data')
        
        openAction = qtWidgets.QAction("Open", self)
        openAction.triggered.connect(self.openFile)
        
        saveAction = qtWidgets.QAction("Save", self)
        saveAction.triggered.connect(self.saveFile)

        saveAsAction = qtWidgets.QAction("Save As", self)
        saveAsAction.triggered.connect(self.saveAsFile)
        
        exportAction = qtWidgets.QAction("Export", self)
        exportAction.triggered.connect(self.export)
        
        closeAction = qtWidgets.QAction("Close", self)
        closeAction.triggered.connect(self.closeFile)

        captureCurrentAction = qtWidgets.QAction("Capture Current", self)
        captureCurrentAction.triggered.connect(self.captureCurrent)
        
        captureCurrentAverageAction = qtWidgets.QAction("Capture Current Average", self)
        captureCurrentAverageAction.triggered.connect(self.captureCurrentAverage)
        
        exitAction = qtWidgets.QAction("Exit", self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(closeAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exportAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        dataMenu.addAction(captureCurrentAction)
        
    @qtCore.pyqtSlot() 
    def captureCurrent(self):
        logger.debug(METHOD_ENTER_STR)
        dataSelection = self._dataSelections._selectionWidget
        self._dataNavigator.addIntermediateDataNode(dataSelection)
        
    @qtCore.pyqtSlot() 
    def captureCurrentAverage(self):
        logger.debug(METHOD_ENTER_STR)
        dataSelection = self._dataSelections._selectionWidget
        self._dataNavigator.addIntermediateDataNode(dataSelection)
        
    @qtCore.pyqtSlot()
    def closeFile(self):
        logger.debug(METHOD_ENTER_STR)
        
    @qtCore.pyqtSlot()
    def export(self):
        logger.debug(METHOD_ENTER_STR)

    @qtCore.pyqtSlot()
    def handleDataSelectionsChanged(self):
        logger.debug(METHOD_ENTER_STR)
        self.updatePlotData()
        
    @qtCore.pyqtSlot(str)
    def handleLeftDataSelectionChanged(self, label):
        '''
        Handle selection on left side of the plot.  Feed selection information 
        to the choice widget and then handle any necessary plot changes
        '''
        logger.debug(METHOD_ENTER_STR % label)
        selection = self._plotWidget.getLeftSelectionIndexes(label)
        average = self._plotWidget.getLeftSelectionAverage(label)
        self._dataSelections.setLeftDataSelection(label, selection, average)
        #self.updatePlotData()
        
    @qtCore.pyqtSlot(str)
    def handleRightDataSelectionChanged(self, label):
        '''
        Handle selection on right side of the plot.  Feed selection information 
        to the choice widget and then handle any necessary plot changes
        '''
        logger.debug(METHOD_ENTER_STR % label)
        selection = self._plotWidget.getRightSelectionIndexes(label)
        average = self._plotWidget.getRightSelectionAverage(label)
        self._dataSelections.setRightDataSelection(label, selection, average)
        #self.updatePlotData()
        
    @qtCore.pyqtSlot(qtCore.QModelIndex, qtCore.QModelIndex)
    def handleNavigatorDataChanged(self, beginIndex, endIndex):
        logger.debug("begin Index %s, endIndex %s" % (beginIndex, endIndex))
        checkedNodes = self._dataNavigator.model().getTopDataSelectedNodes()
        self._dataSelections.setSelectedNodes(checkedNodes)
                
    def handlePointSelectionReloadPicks(self, preEdgePoints, postEdgePoints):
        logger.debug(METHOD_ENTER_STR % ((preEdgePoints, postEdgePoints, "a"),))
        self._plotWidget.applyPickPoints(preEdgePoints, postEdgePoints)     
        logger.debug(METHOD_EXIT_STR)
        
    @qtCore.pyqtSlot()
    def openFile(self):
        '''
        Open a file, populate the navigator window as appropriate
        '''
        logger.debug(METHOD_ENTER_STR)
        fileName = qtWidgets.QFileDialog.getOpenFileName(None, "Open Spec File")[0]
        specFile = None
        if fileName != "":
            try:
                specFile = SpecDataFile(fileName)
            except NotASpecDataFile as ex:
                qtWidgets.QMessageBox.warning(self, "Not a Spec File", 
                              "The file %s does not seem to be a spec file" %
                              fileName)
                return
        else:
            return
        self._dataNavigator.addSpecDataFileNode(specFile)
        
        
    @qtCore.pyqtSlot()
    def saveFile(self):
        logger.debug(METHOD_ENTER_STR)
        
    @qtCore.pyqtSlot()
    def saveAsFile(self):
        logger.debug(METHOD_ENTER_STR)
        
    '''
    Performs all updates to the plots given real data.
    '''
    def updatePlotData(self):
        counters, counterNames = self._dataSelections.getSelectedCounterInfo()
        logger.debug("Data selected for this plot %s" % counters)
        if not self._dataSelections.isMultipleScansSelected():
            if (len(counters) == 0) and (len(counterNames)==0):
                self._plotWidget.clear()
                return
            self.updatePlotDataSingle(counters, counterNames)
        else:
            self.updatePlotDataMultiple(counters, counterNames)
            
    '''
    Handle updating the plot window when multiple scans are selected
    '''
    def updatePlotDataMultiple(self, counters, counterNames, 
                               displayAverage=True, displayEach=True):
        logger.debug(METHOD_ENTER_STR % ((counters, counterNames),))
        data = {}
        dataOut = {}
        self._plotWidget.clear()
        
        dataSum = []
        dataAverage = []
        selectedScans = self._dataSelections.getSelectedScans()
        logger.debug("SelectedScans %s" % selectedScans)
        
        for scan in selectedScans:
            data[scan] = []
            dataOut[scan] = []
#             thisScan = self._dataNavigator.model().getTopDataSelectedNodes()[0]._specDataFile.scans[scan]
            node = self._dataSelections.getNodeContainingScan(scan)
            logger.debug("Scans in node %s: %s" % (node, node.scans))
            thisScan = node.scans[scan]
            for counter in counterNames:
                try:
                    logger.debug("Type of data %s" % type(thisScan.data[counter][:]))
                    data[scan].append(thisScan.data[counter][:])
                except KeyError as ie:
                    logger.exception("Tried to load data which does" +
                                     " not have counters selected."  +
                                     "Multiple scans are selected and some" +
                                     "may not have the selected counters " +
                                     "Scan %s \n %s" % (str(scan), str(ie)))
            try:
                dataOut[scan] = self._dataSelections.calcPlotData(data[scan])
                logger.debug("Type for data out %s" % type(dataOut[scan]))
            except IndexError:
                qtWidgets.QMessageBox.warning(self, "No Data Warning", 
                                          "No Data Was Selected")
            countIndex = range(1, len(dataOut[scan]))   #start at 1 since 0 is x axis
            plotAxisLabels = self._dataSelections.getPlotAxisLabels()
            axisLabelIndex = self._dataSelections.getPlotAxisLabelsIndex()
            if self._dataSelections.plotIndividualData():
                for index in countIndex:
                    dataLabel = "%s - Scan %s" % (plotAxisLabels[index], scan) 
                    if axisLabelIndex[index] == 1:
                        self._plotWidget.plotAx1(dataOut[scan][0], 
                                                dataOut[scan][index], 
                                                dataLabel)
                        self._plotWidget.setXLabel(plotAxisLabels[0])
                        self._plotWidget.setYLabel(plotAxisLabels[index])
                    elif axisLabelIndex[index] == 2:
                        self._plotWidget.plotAx2(dataOut[scan][0], 
                                                dataOut[scan][index], 
                                                dataLabel)
                        self._plotWidget.setXLabel(plotAxisLabels[0])
                        self._plotWidget.setY2Label(plotAxisLabels[index])
                        
            if scan == selectedScans[0]:
                dataSum = dataOut[scan][:] 
            else:
                for index in countIndex:
                    logger.debug("dataSum[%d] %s" % (index,dataSum[index]))
#                     logger.debug("dataSum[index].shape %s" % 
#                                  dataSum[index].shape)
#                     logger.debug("dataOut[scan][index].shape %s" % 
#                                  dataOut[scan][index].shape)
                    try:
                        dataSum[index] += dataOut[scan][index][:]
                    except ValueError as ve:
                        qtWidgets.QMessageBox.warning(self, "Data Error", 
                                                   "Trouble mixing" +
                                                   "data from different scans." +
                                                   "Common cause is scans " +
                                                   "have different number of " +
                                                   "data points\n %s" %
                                                   str(ve))
                       
        if self._dataSelections.plotAverageData():
            for index in countIndex:
                dataAverage = dataSum[index][:]/len(selectedScans)
                plotDataLabel = self._dataSelections.getPlotAxisLabels()
                dataLabel = "%s - Avg" % plotDataLabel[index] 
                if axisLabelIndex[index] == 1:
                    self._plotWidget.plotAx1Average(dataOut[scan][0], dataAverage, dataLabel)
                if axisLabelIndex[index] == 2:
                    self._plotWidget.plotAx2Average(dataOut[scan][0], dataAverage, dataLabel)
        self._plotWidget.plotDraw()                            
    '''
    Handle updating the plot window when only one scan is selected
    '''        
    def updatePlotDataSingle(self, counters, counterNames):
        logger.debug(METHOD_ENTER_STR % ((counters, counterNames), ))
        data = []
        dataOut = []
        logger.debug("SelectedScans %s" % self._dataSelections.getSelectedScans())
        node = self._dataSelections.getNodeContainingScan(self._dataSelections.getSelectedScans()[0])
        logger.debug("Scans in node %s: %s" % (node, node.scans))
        scans = node.scans[self._dataSelections.getSelectedScans()[0]]
#         scans = self._dataNavigator.model().getTopDataSelectedNodes()[0]._specDataFile.scans[self._dataSelections.getSelectedScans()[0]]
        logger.debug("counters %s", counters)
        logger.debug("counterNames %s", counterNames)
        
        for counter in counterNames:
            try:
                data.append(scans.data[counter])
            except KeyError as ie:
                logger.exception("Tried to load data which does not have " +
                                 "counters selected. Please make a selection " +
                                 "for this type of data: \nScan --%s--\nScans.data.keys -- %s\n%s" % 
                                 (str(scans), str(list(scans.data.keys())), str(ie)))
        try:
            dataOut = self._dataSelections.calcPlotData(data)
        except IndexError:
            qtWidgets.QMessageBox.warning(self, "No Data Warning", "NoData was selected")
        countIndex = range(1, len(dataOut))
        self._plotWidget.clear()
        plotAxisLabels = self._dataSelections.getPlotAxisLabels()
#         plotDataLabel = self._dataSelections.getPlotAxisLabels()
        axisLabelIndex = self._dataSelections.getPlotAxisLabelsIndex()
        logger.debug("plotAxesLabels %s", plotAxisLabels)
        for index in countIndex:
            logger.debug("index, counters %s %s" % (index, counters))
            #logger.debug("index, len(counters)-1 %s, %s" % (index, len(counters)-1 ))
            if axisLabelIndex[index] == 1:
                logger.debug("dataOut %s" %dataOut)
                self._plotWidget.plotAx1(dataOut[0], dataOut[index], plotAxisLabels[index])
                logger.debug("plotAxisLabels: %s" % plotAxisLabels)
                self._plotWidget.setXLabel(plotAxisLabels[0])
                self._plotWidget.setYLabel(plotAxisLabels[index])
            if axisLabelIndex[index] == 2:
                self._plotWidget.plotAx2(dataOut[0], dataOut[index], plotAxisLabels[index])
                logger.debug("plotAxisLabels: %s" % plotAxisLabels)
                self._plotWidget.setXLabel(plotAxisLabels[0])
                self._plotWidget.setY2Label(plotAxisLabels[index])
        
        self._plotWidget.plotDraw()
                   
        