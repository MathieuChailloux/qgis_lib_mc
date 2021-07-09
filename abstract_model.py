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

import os.path
import csv

from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle, QgsProject, QgsCoordinateTransform, QgsProcessingUtils, QgsProcessingFeedback

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt, QCoreApplication
from . import utils, xmlUtils, qgsUtils, qgsTreatments, feedbacks

from abc import ABC, abstractmethod
#class Abstract(ABC):
#    @abstractmethod
#    def foo(self):
#        pass

""" 
    Abstract and usual classes to implement MVC (Model-View-Controller) design pattern.
"""

# Abstract class for model items containing multiple information
# Each method must be implemented
class AbstractGroupItem:

    def __init__(self):
        pass
        
    @abstractmethod
    def getNField(self,n):
        return None
        
    @abstractmethod
    def updateNField(self,n,value):
        return None
        
    @abstractmethod
    def checkItem(self):
        return False
        
    @abstractmethod
    def equals(self,other):
        return False
        
    @abstractmethod
    def applyItem(self):
        pass
        
# Array item.
# Array elements order must be fixed.
class ArrayItem(AbstractGroupItem):
    
    def __init__(self,arr):
        self.arr = arr
        self.nb_fields = len(arr)
        
    def getNField(self,n):
        if n < self.nb_fields:
            return self.arr[n]
        else:
            utils.warn("getNField(" + str(n) + ") out of bounds : " + str(self.nb_fields))
            return None
            #assert false
            
    def updateNField(self,n,value):
        if n < self.nb_fields:
            self.arr[n] = value
        else:
            assert false
            
    def equals(self,other):
        self.arr == other.arr
                 
# Dictionary item.
# Fields not displayed must be stored at the end.
class DictItem(AbstractGroupItem):
    
    def __init__(self,dict,fields=None):
        if not fields:
            fields = list(dict.keys())
        self.field_to_idx = {f : fields.index(f) for f in fields}
        self.idx_to_fields = {fields.index(f) : f for f in fields}
        self.nb_fields = len(fields)
        self.dict = dict
        
    def __str__(self):
        return str(self.dict)
        
    def recompute(self):
        fields = list(self.dict.keys())
        self.field_to_idx = {f : fields.index(f) for f in fields}
        self.idx_to_fields = {fields.index(f) : f for f in fields}
        self.nb_fields = len(fields)
        
    def getNField(self,n):
        if n < self.nb_fields:
            return self.dict[self.idx_to_fields[n]]
        else:
            utils.debug("getNField " + str(n))
            utils.debug("item fields = " + str(self.dict.keys()))
            utils.warn("getNField(" + str(n) + ") out of bounds : " + str(self.nb_fields))
            return None
            #utils.internal_error("Accessing " + str(n) + " field >= " + str(self.nb_fields))
            
    def updateNField(self,n,value):
        if n < self.nb_fields:
            self.dict[self.idx_to_fields[n]] = value
        else:
            assert false
            
    def equals(self,other):
        return (self.dict == other.dict)
        
    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.__class__.__name__
        utils.debug("item = " + str(self))
        for k,v in self.dict.items():
            utils.debug(str(v))
            xmlStr += indent + " " + k + "=\"" + xmlUtils.xmlEscape(str(v)) + "\""
            #xmlStr += indent + " " + k + "=\"" + str(v).replace('"','&quot;') + "\""
        xmlStr += "/>"
        return xmlStr
    
# FieldsModel modelizes a unique dictionary.
# Displayed in vertical mode (1 line = 1 field, single column).
# Used for parameters for instance.
class FieldsModel(QAbstractTableModel):

    def __init__(self,parent,dict):
        QAbstractTableModel.__init__(self)
        self.dict = dict
        self.fields = dict.keys()
        
    # Number of rows = numberf of fields
    def rowCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    # Single column     
    def columnCount(self,parent=QModelIndex()):
        return 1
    
    def getNItem(self,n):
        return self.dict[self.fields[n]]
    
    # This function is called by Qt to display information at 'index' position.
    # Value at 'n' row is retrieved through getNItem.
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.getNItem(row)
        if role != Qt.DisplayRole:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(item))
        else:
            return QVariant()
            
    # Row headers = field name, column header = 'value'
    def headerData(self,col,orientation,role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("value")
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return(self.fields[col])
        return QVariant()
    
# AbstractGroupModel allows multiple group items.
# Items must implement AbstractGroupItem class.
class AbstractGroupModel(QAbstractTableModel):

    def __init__(self,parent,fields):
        QAbstractTableModel.__init__(self)
        self.fields = fields
        self.items = []
        self.orders = {}

    def __str__(self):
        res = "[[" + ",".join([str(i) for i in self.items]) + "]]"
        return res
        
    def checkNotEmpty(self):
        if len(self.items) == 0:
            utils.internal_error("Empty buffer model")
        
    def getItems(self):
        return self.items
        
    def getNbItems(self):
        return len(self.getItems())
        
    def getNItem(self,n):
        if n < self.rowCount():
            return self.items[n]
        else:
            utils.warn("[" + self.__class__.__name__ + "] Unexpected index " + str(n))
            return None
            # utils.internal_error("[" + self.__class__.__name__ + "] Unexpected index " + str(n))
            # return None
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.items)
        
    def columnCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    def headerData(self,col,orientation,role):
        if col >= len(self.fields):
            pass
            #utils.warn("Header out of bounds : " + self.__class__.__name__
            #            + " " + str(col) + " " + str(self.fields))
        elif orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.fields[col])
        return QVariant()
            
    # This function is called by Qt to display information at 'index' position.
    # Value at (row,col) position is retrieved through getNItem and getNField.
    # Items values must be strings.
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.getNItem(row)
        if not item:
            return QVariant()
        val = item.getNField(index.column())
        if role not in [Qt.DisplayRole,Qt.EditRole]:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(val))
        else:
            return QVariant()
            
    # This function is called by Qt when the view is modified at 'index' position.
    def setData(self, index, value, role):
        utils.debug("setData (" + str(index.row()) + ","
                    + str(index.column()) + ") : " + str(value))
        if role == Qt.EditRole:
            item = self.getNItem(index.row())
            item.updateNField(index.column(),value)
            self.dataChanged.emit(index, index)
            return True
        return False
            
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            
    # Add new item in model if not already existing.
    # layoutChanged signal must be emitted to update view.
    def addItem(self,item):
        utils.debug("addItem")
        for i in self.items:
            if i.equals(item):
                warn("Item " + str(item) + " already exists")
                return
        self.items.append(item)
        self.insertRow(0)
        self.layoutChanged.emit()
        
    def removeField(self,fieldname):
        self.fields.remove(fieldname)
        
    # Remove items at 'indexes' positions from model.
    # If multiple columns are selected, multiple indexes are created,
    # so only unique rows are extracted to delete items.
    # layoutChanged signal must be emitted to update view.
    def removeItems(self,indexes):
        utils.debug("[removeItems] nb of items = " + str(len(self.items)))
        rows = sorted(set([i.row() for i in indexes]))
        self.removeItemsFromRows(rows)
        
    def removeItemsFromRows(self,rows):
        n = 0
        for row in rows:
            roww = row - n
            utils.debug("[removeItems] Deleting row " + str(roww))
            del self.items[roww]
            n += 1
        self.layoutChanged.emit()
        
    # Apply items for 'indexes' (position in item list, not index from Qt selection)
    # If no 'indexes' given, apply each item
    def applyItems(self,indexes=None):
        utils.debug("[applyItems]")
        if not indexes:
            indexes = range(0,len(self.items))
        for n in indexes:
            i = self.items[n]
            i.applyItem()
            
    def getItems(self,indexes=None):
        res = []
        if not indexes:
            indexes = range(0,len(self.items))
        for n in indexes:
            i = self.items[n]
            res.append(i)
        return res
            
    # Order items based on 'idx' column/field
    # Reverse order at each call for a specific column
    # def orderItems(self,idx):
        # utils.debug("orderItems " + str(idx))
        # if idx in self.orders:
            # order_down = self.orders[idx]
        # else:
            # order_down = True
            # self.orders[idx] = order_down
        # self.items = sorted(self.items, key=lambda i: i.dict[i.idx_to_fields[idx]])
        # if not order_down:
            # self.items.reverse()
        # self.orders[idx] = not self.orders[idx]
        # self.layoutChanged.emit()
        
    def upgradeElem(self,row):
        utils.debug("upgradeElem " + str(row))
        if row > 0:
            self.swapItems(row -1, row)
        
    def downgradeElem(self,row):
        utils.debug("downgradeElem " + str(row))
        if row < len(self.items) - 1:
            self.swapItems(row, row + 1)
            
    # Switch items at position 'i1' and 'i2'
    def swapItems(self,i1,i2):
        self.items[i1], self.items[i2] = self.items[i2], self.items[i1]
        self.layoutChanged.emit()
        
# DictModel is a group model with dictionary items
class DictModel(AbstractGroupModel):

    def __init__(self,parent,fields):
        AbstractGroupModel.__init__(self,parent,fields)
        
    def sort(self,col,order):
        sorted_items = sorted(self.items, key=lambda i: i.dict[i.idx_to_fields[col]])
        if order == Qt.DescendingOrder:
            sorted_items.reverse()
        self.items = sorted_items
        self.layoutChanged.emit()
                
    def getMatchingItem(self,item):
        for i in self.items:
            if i.equals(item):
                return i
        return None
        
    def itemExists(self,item):
        matching_item = self.getMatchingItem(item)
        return (matching_item != None)
        # for i in self.items:
            # if i.equals(item):
                # return True
        # return False
        
    def addItem(self,item):
        utils.debug("DictItem.addItem " + str(item))
        if not item:
            utils.internal_error("Empty item")
        item.checkItem()
        if self.itemExists(item):
            utils.warn("Item " + str(item) + " already exists")
        else:
            utils.debug("adding item")
            self.items.append(item)
            self.insertRow(0)
            
    # Each item is updated when field is removed
    # Item recompute function must be called to keep consistency
    def removeField(self,fieldname):
        utils.debug("removeField " + fieldname)
        for i in self.items:
            utils.debug(str(i.dict.items()))
            if fieldname not in i.dict:
                utils.warn("Could not delete field '" + str(fieldname))
            else:
                del i.dict[fieldname]
            i.recompute()
        utils.debug("self = " + str(self))
        if fieldname in self.fields:
            self.fields.remove(fieldname)
        self.layoutChanged.emit()
        
    def fromXMLAttribs(self,attribs):
        pass
        
    def fromXMLRoot(self,root):
        self.fromXMLAttribs(root.attrib)
        self.items = []
        for parsed_item in root:
            dict = parsed_item.attrib
            item = self.mkItemFromDict(dict)
            self.addItem(item)
        self.layoutChanged.emit()
        
    def toXML(self,indent=" ",attribs_dict=None):
        utils.debug("toXML " + self.parser_name)
        xmlStr = indent + "<" + self.parser_name
        if attribs_dict:
            for k,v in attribs_dict.items():
                # xmlStr += " " + str(k).replace('"','&quot;')
                # xmlStr += "=\"" + str(v).replace('"','&quot;') + "\""
                xmlStr += " " + xmlUtils.xmlEscape(str(k))
                xmlStr += "=\"" + xmlUtils.xmlEscape(str(v)) + "\""
        xmlStr += ">\n"
        for i in self.items:
            xmlStr += i.toXML(indent=indent + " ") + "\n"
        xmlStr += indent + "</" + self.parser_name + ">"
        return xmlStr
        feedback.endSection()
        
    # Saves model to CSV file 'fname'
    def saveCSV(self,fname):
        with open(fname,"w", newline='') as f:
            writer = csv.DictWriter(f,fieldnames=self.fields,delimiter=';')
            writer.writeheader()
            for i in self.items:
                utils.debug("writing row " + str(i.dict))
                writer.writerow(i.dict)
        utils.info("Model saved to file '" + str(fname) + "'")
        
    def applyItemsWithContext(self,context,feedback,indexes=None):
        if not self.items:
            feedback.reportError("Empty Model")
        if not indexes:
            indexes = range(0,len(self.items))
        nb_steps = len(indexes)
        step_feedback = feedbacks.ProgressMultiStepFeedback(nb_steps,feedback)
        step_feedback.setCurrentStep(0)
        for cpt, n in enumerate(indexes,1):
            i = self.items[n]
            self.applyItemWithContext(i,context,step_feedback)
            step_feedback.setCurrentStep(cpt)
    
class NormalizingParamsModel(QAbstractTableModel):

    WORKSPACE = "workspace"
    PROJECT = "projectFile"
    EXTENT_LAYER = "extentLayer"
    RESOLUTION = "resolution"
    CRS = "crs"
    
    DEFAULT_CRS = QgsCoordinateReferenceSystem("epsg:2154")
    DEFAULT_FIELDS = [WORKSPACE,EXTENT_LAYER,
        RESOLUTION,PROJECT,CRS]
    
    def __init__(self,fields=DEFAULT_FIELDS):
        self.workspace = None
        self.extentLayer = None
        self.extentType = None
        self.resolution = 0.0
        self.projectFile = ""
        self.crs = self.DEFAULT_CRS
        self.fields = fields
        QAbstractTableModel.__init__(self)
        
    def tr(self, msg):
        return QCoreApplication.translate(self.__class__.__name__, msg)
        
    def checkWorkspaceInit(self):
        if not self.workspace:
            utils.user_error(self.tr("Workspace parameter not initialized"))
        if not os.path.isdir(self.workspace):
            utils.user_error("Workspace directory '" + self.workspace + "' does not exist")
            
    def checkExtentInit(self):
        if not self.extentLayer:
            utils.user_error(self.tr("Extent parameter not initialized"))
            
    def checkResolutionInit(self):
        if not self.resolution or self.resolution <= 0:
            utils.user_error(self.tr("Resolution parameter not initialized"))
            
    def checkCrsInit(self):
        if not self.crs:
            utils.user_error(self.tr("CRS parameter not initialized"))
        if not self.crs.isValid():
            utils.user_error(self.tr("Invalid CRS"))
            
    def checkInit(self):
        checkWorkspaceInit()
        checkExtentInit()
        checkResolutionInit()
        checkCrsInit()
        
    def setExtentLayer(self,path):
        if path:
            path = self.normalizePath(path)
        utils.info("Setting extent layer to " + str(path))
        self.extentLayer = path
        self.layoutChanged.emit()
        
    def setResolution(self,resolution):
        utils.info("Setting resolution to " + str(resolution))
        self.resolution = resolution
        self.layoutChanged.emit()
        
    def setCrs(self,crs):
        utils.info("Setting extent CRS to " + crs.description())
        self.crs = crs
        self.layoutChanged.emit()
        
    def getRasterParams(self):
        crs = self.crs
        extent = self.getExtentString()
        resolution = self.getResolution()
        return (crs, extent, resolution)
        
    def getCrsStr(self):
        return self.crs.authid().lower()

    def getTransformator(self,in_crs):
        transformator = QgsCoordinateTransform(in_crs,self.crs,QgsProject.instance())
        return transformator
    
    def getBoundingBox(self,in_extent_rect,in_crs):
        transformator = self.getTransformator(in_crs)
        out_extent_rect = transformator.transformBoundingBox(in_extent_rect)
        return out_extent_rect
        
    def setWorkspace(self,path):
        norm_path = utils.normPath(path)
        self.workspace = norm_path
        utils.info("Workspace directory set to '" + norm_path)
        if not os.path.isdir(norm_path):
            utils.user_error("Directory '" + norm_path + "' does not exist")
        return norm_path
            
    def fromXMLRoot(self,root):
        dict = root.attrib
        utils.debug("params dict = " + str(dict))
        return self.fromXMLDict(dict)
    
    def fromXMLDict(self,dict):
        if self.WORKSPACE in dict:
           if not self.workspace and os.path.isdir(dict[self.WORKSPACE]):
               self.setWorkspace(dict[self.WORKSPACE])
        if self.RESOLUTION in dict:
            try:
                self.setResolution(float(dict[self.RESOLUTION]))
            except ValueError:
                utils.user_error("Unexpected resolution : " + str(dict[self.RESOLUTION]))
        if self.EXTENT_LAYER in dict:
            self.setExtentLayer(dict[self.EXTENT_LAYER])
        elif 'extent' in dict:
            self.setExtentLayer(dict['extent'])
        if self.CRS in dict:
            crs = QgsCoordinateReferenceSystem(dict[self.CRS])
            self.setCrs(crs)
    
    def getXMLStr(self):
        xmlStr = ""
        if self.workspace:
            xmlStr += " " + self.WORKSPACE + "=\"" + str(self.workspace) + "\""
        if self.resolution:
            xmlStr += " " + self.RESOLUTION + "=\"" + str(self.resolution) + "\""
        if self.extentLayer:
            xmlStr += " " + self.EXTENT_LAYER + "=\"" + str(self.extentLayer) + "\""
        if self.crs:
            xmlStr += " " + self.CRS + "=\"" + self.getCrsStr() + "\""
        return xmlStr
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    def columnCount(self,parent=QModelIndex()):
        return 1
        
    def getNItem(self,n):
        items = [self.workspace,
                 self.extentLayer,
                 self.resolution,
                 self.projectFile,
                 self.crs.description()]
        return items[n]
            
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.getNItem(row)
        if role != Qt.DisplayRole:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(item))
        else:
            return QVariant()
            
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        
    def headerData(self,col,orientation,role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("value")
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(self.fields[col])
        return QVariant()
        
    # Checks that workspace is intialized and is an existing directory.
    def checkWorkspaceInit(self):
        if not self.workspace:
            utils.user_error("Workspace parameter not initialized")
        if not os.path.isdir(self.workspace):
            utils.user_error("Workspace directory '" + self.workspace + "' does not exist")
            
    # Returns relative path w.r.t. workspace directory.
    # File separator is set to common slash '/'.
    def normalizePath(self,path):
        self.checkWorkspaceInit()
        if not path:
            utils.user_error("Empty path")
        norm_path = utils.normPath(path)
        if os.path.isabs(norm_path):
            rel_path = os.path.relpath(norm_path,self.workspace)
        else:
            rel_path = norm_path
        final_path = utils.normPath(rel_path)
        return final_path
            
    # Returns absolute path from normalized path (cf 'normalizePath' function)
    def getOrigPath(self,path):
        self.checkWorkspaceInit()
        if path is None or path == "":
            utils.user_error("Empty path")
        elif os.path.isabs(path):
            return path
        else:
            join_path = utils.joinPath(self.workspace,path)
            norm_path = os.path.normpath(join_path)
            return norm_path
            
    # Checks that all parameters are initialized
    def checkInit(self):
        self.checkWorkspaceInit()
        if not self.extentLayer:
            utils.user_error("Extent layer parameter not initialized")
        extent_path = self.getOrigPath(self.extentLayer)
        utils.debug("extent_path = " + str(extent_path))
        utils.checkFileExists(extent_path,"Extent layer ")
        if not self.resolution:
            utils.user_error("Resolution parameter not initialized")
        if self.resolution == 0.0:
            utils.user_error("Null resolution")
        if not self.crs:
            utils.user_error("CRS parameter not initialized")
        if not self.crs.isValid():
            utils.user_error("Invalid CRS")
            
    def getResolution(self):
        return float(self.resolution)
        
    def getExtentLayer(self):
        if self.extentLayer:
            return self.getOrigPath(self.extentLayer)
        else:
            return None
        
    def getExtentLayerAndType(self):
        path = self.getExtentLayer()
        layer, type = qgsUtils.loadLayerGetType(path)
        return (path,type)
        
    def getExtentString(self):
        extent_path = self.getExtentLayer()
        if not extent_path:
            return None
        extent_layer = qgsUtils.loadLayer(extent_path)
        extent = extent_layer.extent()
        transformed_extent = self.getBoundingBox(extent,extent_layer.crs())
        res = str(transformed_extent.xMinimum())
        res += ',' + str(transformed_extent.xMaximum())
        res += ',' + str(transformed_extent.yMinimum())
        res += ',' + str(transformed_extent.yMaximum())
        res += '[' + str(self.crs.authid()) + ']'
        return res
        
    # Return bounding box coordinates of extent layer
    def getExtentCoords(self):
        extent_path = self.getExtentLayer()
        if extent_path:
            return qgsUtils.coordsOfExtentPath(extent_path)
        else:
            utils.user_error("Extent layer not initialized")
            
    # Checks that given layer matches extent layer coordinates
    def equalsParamsExtent(self,path):
        params_coords = self.getExtentCoords()
        path_coords = qgsUtils.coordsOfExtentPath(path)
        return (params_coords == path_coords)
            
    # Returns extent layer bounding box as a QgsRectangle
    def getExtentRectangle(self):
        coords = self.getExtentCoords()
        rect = QgsRectangle(float(coords[0]),float(coords[1]),
                            float(coords[2]),float(coords[3]))
        return rect 
        
    def clipByExtent(self,input,name="",out_path="",clip_raster=True,context=None,feedback=None):
        extentLayer = self.getExtentLayer()
        if not extentLayer or extentLayer == input:
            return input
        if not feedback:
            feedback = QgsProcessingFeedback()
        extent = self.getExtentRectangle()
        extent_layer_path = extentLayer
        extent_layer, extent_type = self.getExtentLayerAndType()
        feedback.pushDebugInfo("extent_type " + str(extent_type))
        feedback.pushDebugInfo("clip_raster " + str(clip_raster))
        input_layer, input_type = qgsUtils.loadLayerGetType(input)
        if not clip_raster and extent_type == 'Raster':
            return input
        if not out_path:
            bname = name + "_clipped"
            ext = ".tif" if input_type == 'Raster' else ".gpkg"
            out_path = QgsProcessingUtils.generateTempFilename(bname + ext)
        # resolution = self.getResolution()
        if input_type == 'Raster' and extent_type == 'Vector':
            self.checkResolutionInit()
            res = qgsTreatments.clipRasterFromVector(input,extent_layer_path,out_path,
                context=context,feedback=feedback)
        elif input_type == 'Raster' and extent_type == 'Raster':
            self.checkResolutionInit()
            res = qgsTreatments.applyWarpReproject(input,out_path,
                dst_crs=self.crs,extent=extent,
                context=context,feedback=feedback)
            return res
        elif input_type == 'Vector' and extent_type == 'Vector':
            res = qgsTreatments.applyVectorClip(input,extent_layer_path,out_path,
                context=context,feedback=feedback)
        elif input_type == 'Vector' and extent_type == 'Raster':
            res = qgsTreatments.clipVectorByExtent(input,extent,out_path,
                context=context,feedback=feedback)
        else:
            assert(False)
        return res
                
    # Normalize given raster layer to match global extent and resolution
    def normalizeRaster(self,path,out_path=None,resampling_mode="near",context=None,feedback=None):
        if not self.extentLayer:
            return input
        extent_layer, extent_layer_type = self.getExtentLayerAndType()
        utils.debug("extent_layer_type = " + str(extent_layer_type))
        resolution = self.getResolution()
        if extent_layer_type == 'Vector':
            extent_path = self.getExtentLayer()
            clipped_path = QgsProcessingUtils.generateTempFilename('clipped.tif')
            res = qgsTreatments.clipRasterFromVector(path,extent_path,out_path,
                resolution=resolution,context=context,feedback=feedback)
        else:
            extent = self.getExtentRectangle()
            warped_path = QgsProcessingUtils.generateTempFilename('warped.tif')
            utils.warn("Normalizing raster '" + str(path)+ "' to '" + str(warped_path) + "'")
            res = qgsTreatments.applyWarpReproject(path,out_path,resampling_mode,
                dst_crs=self.crs,resolution=resolution,extent=extent,
                context=context,feedback=feedback)
        return res
                
""" AbstractConnector connects a view and a model """
class AbstractConnector:

    def __init__(self,model,view,addButton=None,removeButton=None,
                 runButton=None,selectionCheckbox=None):
        self.model = model
        self.view = view
        self.addButton = addButton
        self.removeButton = removeButton
        self.onlySelection = False
        self.runButton = runButton
        self.selectionCheckbox = selectionCheckbox
        
    # If addButton given, it is connected to addItem function
    # If removeButton given, it is connected to removeItems function
    def connectComponents(self):
        self.view.setModel(self.model)
        if self.addButton:
            self.addButton.clicked.connect(self.addItem)
        if self.removeButton:
            self.removeButton.clicked.connect(self.removeItems)
        if self.runButton:
            self.runButton.clicked.connect(self.applyItems)
        if self.selectionCheckbox:
            self.selectionCheckbox.stateChanged.connect(self.switchOnlySelection)
        #self.view.horizontalHeader().sectionClicked.connect(self.model.orderItems)
        
    def disconnectComponents(self):
        if self.addButton:
            self.addButton.disconnect()
        if self.removeButton:
            self.removeButton.disconnect()
        if self.runButton:
            self.runButton.disconnect()
        
    def tr(self,msg):
        return self.dlg.tr(msg)
                
    def switchOnlySelection(self):
        new_val = not self.onlySelection
        utils.debug("setting onlySelection to " + str(new_val))
        self.onlySelection = new_val
        
    # This function build model item from view and is called by addItem
    @abstractmethod
    def mkItem(self):
        utils.todo_error(" [" + self.__class__.__name__ + "] mkItem not implemented")
        
    def getSelectedIndexes(self):
        if self.onlySelection:
            indexes = list(set([i.row() for i in self.view.selectedIndexes()]))
        else:
            indexes = range(0,len(self.model.items))
        return indexes
        
    def applyItems(self):
        indexes = self.getSelectedIndexes()
        utils.debug("Selected indexes = " + str(indexes))
        self.model.applyItemsWithContext(None,self.dlg.feedback,indexes)
        #self.model.applyItemsWithContext(self.dlg.context,self.dlg.feedback,indexes)
        
    def addItem(self):
        utils.debug("AbstractConnector.addItem")
        item = self.mkItem()
        self.model.addItem(item)
        self.model.layoutChanged.emit()
        
    def removeItems(self):
        indices = self.view.selectedIndexes()
        utils.debug(str(indices))
        self.model.removeItems(indices)
        
    # Upgrade selected item rank (only single selection for now)
    def upgradeItem(self):
        utils.debug("upgradeItem")
        indices = self.view.selectedIndexes()
        rows = list(set([i.row() for i in indices]))
        nb_rows = len(rows)
        if nb_rows == 0:
            utils.debug("no idx selected")
        elif nb_rows == 1:
            row = rows[0]
            if row > 0:
                self.model.swapItems(row - 1, row)
                self.view.selectRow(row - 1)
        else:
            utils.warn("Several rows selected, please select only one")
            
    # Downgrade selected item rank (only single selection for now)
    def downgradeItem(self):
        utils.debug("downgradeItem")
        indices = self.view.selectedIndexes()
        rows = list(set([i.row() for i in indices]))
        #nb_indices = len(indices)
        nb_rows = len(rows)
        if nb_rows == 0:
            utils.debug("no idx selected")
        elif nb_rows == 1:
            row = rows[0]
            if row < len(self.model.getItems()) - 1:
                self.model.swapItems(row, row + 1)
                self.view.selectRow(row + 1)
        else:
            utils.warn("Several rows selected, please select only one")

            
# Code snippet from https://stackoverflow.com/questions/17748546/pyqt-column-of-checkboxes-in-a-qtableview
class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        '''
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''

        checked = bool(index.data())
        check_box_style_option = QtWidgets.QStyleOptionButton()

        #if (index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        if (index.flags() & QtCore.Qt.ItemIsEditable):
            check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtWidgets.QStyle.State_On
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)

        # this will not run - hasFlag does not exist
        #if not index.model().hasFlag(index, QtCore.Qt.ItemIsEditable):
            #check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        check_box_style_option.state |= QtWidgets.QStyle.State_Enabled

        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        utils.debug('Check Box editor Event detected : ')
        utils.debug(str(event.type()))
        #if not (index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        if not (index.flags() & QtCore.Qt.ItemIsEditable):
            return False

        utils.debug('Check Box editor Event detected : passed first check')
        # Do not change the checkbox-state
        if event.type() == QtCore.QEvent.MouseButtonPress:
          return False
        if event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() != QtCore.Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() != QtCore.Qt.Key_Space and event.key() != QtCore.Qt.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData (self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        utils.debug('SetModelData')
        newValue = not bool(index.data())
        utils.debug('New Value : {0}'.format(newValue))
        model.setData(index, newValue, QtCore.Qt.EditRole)

    def getCheckBoxRect(self, option):
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (option.rect.x() +
                            option.rect.width() / 2 -
                            check_box_rect.width() / 2,
                            option.rect.y() +
                            option.rect.height() / 2 -
                            check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())
