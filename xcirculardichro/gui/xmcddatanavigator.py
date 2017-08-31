'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
from xcirculardichro.config.loggingConfig import METHOD_ENTER_STR,\
    METHOD_EXIT_STR
from xcirculardichro.gui.model.xmcddatanavigatormodel import XMCDDataNavigatorModel
from xcirculardichro.gui.datanavigator import DataNavigator
from xcirculardichro.data.datanode import DataNode
from xcirculardichro.data.specdatafilenode import SpecFileDataNode

logger = logging.getLogger(__name__)

class XMCDDataNavigator(qtWidgets.QDialog):
    
    dataSelectionChanged = qtCore.pyqtSignal(list, name="dataSelectionChanged")

    def __init__(self, parent=None):
        super(XMCDDataNavigator, self).__init__(parent=parent)
        logging.debug(METHOD_ENTER_STR)
        layout = qtWidgets.QHBoxLayout()

        self._rootNode = DataNode("/")
        self._model = XMCDDataNavigatorModel(self._rootNode)
        self._view = qtWidgets.QTreeView()
        self._view.setModel(self._model)
        self._view.setSelectionMode(qtWidgets.QAbstractItemView.SingleSelection)
        self._view.setMinimumWidth(200)
        layout.addWidget(self._view)
        self.setLayout(layout)

        # connect up signals
        #self._view.selectionModel().selectionChanged.connect(self.selectionChanged)
            
    def addDataNode(self, nodeName):
        logger.debug(METHOD_ENTER_STR % nodeName)
        self._rootNode.addChild(DataNode(nodeName))
        numCurrentNodes = self._rootNode.childCount()
        logger.debug("starting to insertRows")
        self._model.insertRows(numCurrentNodes, 1)
        logger.debug(METHOD_EXIT_STR)

    def addSpecDataFileNode(self, specDataFile):
        logger.debug(METHOD_ENTER_STR % specDataFile)
        specNode = SpecFileDataNode(specDataFile, parent=self._rootNode)
        specNode.setChecked(True)
        numCurrentNodes = self._rootNode.childCount()
        self._model.insertRows(numCurrentNodes, 1)
        
        logger.debug
        
    def model(self):
        '''
        return the data model for the view
        '''
        return self._model
    
    def rootNode(self):
        '''
        return the root node of the navigator.  This is essentially just a dummy 
        place holder node.  It will serve as parent for all other nodes.
        '''
        return self._rootNode
    
    def selectionChanged(self, selected, deselected):
        logger.debug(METHOD_ENTER_STR % ((selected.indexes(),deselected.indexes()),))
        logger.debug("Selected start")
        for index in selected.indexes():
            logger.debug("Selected Item: %s" % self._model.getNode(index))
        logger.debug("Selected end")
        logger.debug("Deselected start")
        for index in deselected.indexes():
            logger.debug("DeSeleced item: %s" %self._model.getNode(index))
        logger.debug("Deselected End")

    def view(self):
        '''
        return the model's view
        '''
        return self._view
    
    