# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis-lib-mc
 PyQGIS utilities library to develop plugins or scripts
                             -------------------
        begin                : 2019-02-21
        author               : Mathieu Chailloux
        email                : mathieu.chailloux@irstea.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

"""
    Feedback classes to use as QgsProcessingFeedback.
"""

import time
import sys

from qgis.core import QgsProcessingFeedback, QgsProcessingMultiStepFeedback

from . import utils
from . import qgsUtils

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QGuiApplication

progressFeedback = None
tmpFeedback = None

class ProgressFeedback(QgsProcessingFeedback):
    
    def __init__(self,dlg):
        self.dlg = dlg
        self.progressBar = dlg.progressBar
        self.sectionText = ""
        self.sectionHeader = "********"
        super().__init__()
        
    def pushCommandInfo(self,msg):
        utils.info(msg)
        
    def pushConsoleInfo(self,msg):
        utils.info(msg)
        
    def pushDebugInfo(self,msg):
        utils.debug(msg)
        
    def pushInfo(self,msg):
        utils.info(msg)
        
    def reportError(self,error,fatalError=False):
        utils.internal_error("reportError : " + str(error))
        
    def beginSection(self,txt):
        self.sectionText = txt
        self.setProgressText(txt)
        self.setProgress(0)
        self.start_time = time.time()
        utils.info(self.sectionHeader + " BEGIN : " + txt)
        
    def endSection(self):
        if self.sectionText:
            self.setSubText("DONE")
        self.end_time = time.time()
        diff_time = self.end_time - self.start_time
        utils.info(self.sectionHeader + " END : " + self.sectionText + " in " + str(diff_time) + " seconds")
        self.sectionText = ""
            
    def setSubText(self,txt):
        self.setProgressText(self.sectionText,txt)
        
    def setProgressText(self,text,subText=""):
        msg = text
        if msg:
            msg += "...  "
        if subText:
            msg += subText
        self.dlg.lblProgress.setText(msg)
        QGuiApplication.processEvents()
        
    def setProgress(self,value):
        #utils.debug("setProgress " + str(value))
        self.progressBar.setValue(value)
        
    def setPercentage(self,percentage):
        utils.info("setperc")
        #utils.internal_error("percentage : " + str(percentage))
        
    def focusLogTab(self):
        self.dlg.mTabWidget.setCurrentWidget(self.dlg.logTab)
        self.dlg.txtLog.verticalScrollBar().setValue(self.dlg.txtLog.verticalScrollBar().maximum())
        
    def endJob(self):
        self.setProgress(100)
        self.focusLogTab()
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.progressChanged.connect(self.setProgress)
        
        
class ProgressMultiStepFeedback(QgsProcessingMultiStepFeedback):
 
    def __init__(self,nb_steps,feedback):
        super().__init__(nb_steps,feedback)
        
    def reportError(self,error,fatalError=False):
        super().reportError(error,fatalError)
 

class FileFeedback(QgsProcessingFeedback):
    
    def __init__(self,fname):
        self.fname = fname
        super().__init__()
        
    def printFunc(self,msg):
        with open(self.fname,"a") as f:
            f.write(str(msg.encode('utf-8')) + "\n")
    #f.write(str(msg + "\n"))
        
    def pushCommandInfo(self,msg):
        self.printFunc(msg)
        
    def pushConsoleInfo(self,msg):
        self.printFunc(msg)
        
    def pushDebugInfo(self,msg):
        self.printFunc(msg)
        
    def pushInfo(self,msg):
        self.printFunc(msg)
        
    def reportError(self,error,fatalError=False):
        #print("reportError : " + str(error))
        self.printFunc("reportError : " + str(error.encode('utf-8')))
        self.printFunc("reportError : " + str(error))
        
    def setProgressText(self,text):
        pass
        
    def setProgress(self,value):
        pass

    
