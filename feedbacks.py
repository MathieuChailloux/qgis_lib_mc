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
import datetime

from qgis.core import QgsProcessingFeedback, QgsProcessingMultiStepFeedback

from . import utils
from . import qgsUtils

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QGuiApplication

progressFeedback = None

def beginSection(msg):
    if progressFeedback:
        progressFeedback.beginSection(msg)
    else:
        utils.debug("No progress feedback")
        
def endSection():
    if progressFeedback:
        progressFeedback.endSection()

class ProgressFeedback(QgsProcessingFeedback):
    
    GDAL_ERROR_PREFIX = 'ERROR '
    SET_COLOR_ERROR = 'ERROR 6: SetColorTable'
    FILE_NOT_FOUND_ERROR = 'FileNotFoundError'
    
    def __init__(self,dlg):
        self.dlg = dlg
        self.progressBar = dlg.progressBar
        self.sectionText = ""
        self.sectionHeader = "********"
        super().__init__()
        
    def pushCommandInfo(self,msg):
        utils.debug(msg)
        
    def pushConsoleInfo(self,msg):
        #if msg.startswith(self.GDAL_ERROR_PREFIX):
        if msg.startswith(self.GDAL_ERROR_PREFIX):
            self.reportError(msg)
        
    def pushDebugInfo(self,msg):
        utils.debug(msg)
        
    def pushInfo(self,msg):
        utils.info(msg)
        
    def reportError(self,error,fatalError=False):
        error_msg = str(error)
        if error_msg.startswith(self.SET_COLOR_ERROR):
            utils.warn(error_msg)
        elif fatalError:
            utils.internal_error("reportError : " + error_msg)
        elif error_msg.startswith(self.FILE_NOT_FOUND_ERROR):
            utils.user_error(error_msg)
        else:
            utils.internal_error(error_msg)
            #utils.warn(error_msg)
        
    def beginSection(self,txt):
        self.sectionText = txt
        self.dlg.lblProgress.setText(txt)
        self.setProgress(0)
        self.start_time = time.time()
        self.pushInfo(self.sectionHeader + " BEGIN : " + txt)
        
    def endSection(self):
        if self.sectionText:
            self.setSubText("DONE")
        self.end_time = time.time()
        diff_time = self.end_time - self.start_time
        self.pushInfo(self.sectionHeader + " END : " + self.sectionText + " in " + str(diff_time) + " seconds")
        self.sectionText = ""
            
    def setSubText(self,txt):
        self.setProgressText(txt)
        
    def setProgressText(self,text):
        msg = self.sectionText
        if msg:
            msg += "...  "
        msg += text
        self.dlg.lblProgress.setText(msg)
        QGuiApplication.processEvents()
        
    def setProgress(self,value):
        fv = float(value)
        # self.pushDebugInfo("fv = " + str(fv))
        if str(fv) == 'inf':
            self.pushInfo("Unexpected value in progress bar : " + str(value))
        else:
            self.progressBar.setValue(value)
        
    def setPercentage(self,percentage):
        pass
        #utils.info("setperc")
        #utils.internal_error("percentage : " + str(percentage))
        
    def focusLogTab(self):
        # self.dlg.mTabWidget.setCurrentWidget(self.dlg.logTab)
        self.dlg.txtLog.verticalScrollBar().setValue(self.dlg.txtLog.verticalScrollBar().maximum())
        
    def endJob(self):
        # self.setProgress(100)
        self.focusLogTab()
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.progressChanged.connect(self.setProgress)
        
        
class ProgressMultiStepFeedback(QgsProcessingMultiStepFeedback):
 
    def __init__(self,nb_steps,feedback):
        if nb_steps == 0:
            utils.user_error("No steps in ProgressMultiStepFeedback initialization (empty model ?)")
        self.nb_steps = nb_steps
        self.step_range = 100 / nb_steps
        self.feedback = feedback
        super().__init__(nb_steps,feedback)
        
    def reportError(self,error,fatalError=False):
        super().reportError(error,fatalError)
        

class FileFeedback(QgsProcessingFeedback):
    
    def __init__(self,fname):
        self.fname = fname
        super().__init__()
        self.sectionText = ""
        self.sectionHeader = "********"
        
    def printFunc(self,msg):
        with open(self.fname,"a") as f:
            #f.write(str(msg.encode('utf-8')) + "\n")
            f.write(str("[" + str(datetime.datetime.now()) + "] " + msg + "\n"))
        
    def pushCommandInfo(self,msg):
        self.printFunc(msg)
        
    def pushConsoleInfo(self,msg):
        #self.printFunc(msg)
        if msg.startswith(ProgressFeedback.GDAL_ERROR_PREFIX):
            self.reportError(msg)
        
    def pushDebugInfo(self,msg):
        self.printFunc(msg)
        
    def pushInfo(self,msg):
        self.printFunc(msg)
        
    def reportError(self,error,fatalError=False):
        #print("reportError : " + str(error))
        self.printFunc("reportError : " + str(error.encode('utf-8')))
        self.printFunc("reportError : " + str(error))
        
    def beginSection(self,txt):
        self.sectionText = txt
        self.start_time = time.time()
        self.pushInfo(self.sectionHeader + " BEGIN : " + txt)
        
    def endSection(self):
        self.end_time = time.time()
        diff_time = self.end_time - self.start_time
        self.pushInfo(self.sectionHeader + " END : " + self.sectionText + " in " + str(diff_time) + " seconds")
        self.sectionText = ""
        
    def setProgressText(self,text):
        pass
        
    def setProgress(self,value):
        pass

    
