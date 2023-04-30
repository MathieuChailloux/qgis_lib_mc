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

import sys
import os.path
import csv
import ast
import traceback
import json
import inspect
from io import StringIO

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsRectangle,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsProcessingUtils,
                       QgsProcessingFeedback)
# from qgis.gui import QgsCheckableItemModel

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel#, QgsCheckableItemModel
from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt,
                          QCoreApplication, QTranslator, QSettings,
                          qVersion, pyqtSlot)
from . import utils, xmlUtils, qgsUtils, qgsTreatments, feedbacks, config_parsing

from abc import ABC, abstractmethod
#class Abstract(ABC):
#    @abstractmethod
#    def foo(self):
#        pass

""" 
    Abstract and usual classes to implement MVC (Model-View-Controller) design pattern.
"""

# class BaseField:

    # BOOL = 0
    # INTEGER = 1
    # FLOAT = 2
    # STRING = 3
    # FILE_PATH = 4
    # LAYER_PATH = 5

    # def __init__(self,name,type,val=None):
        # self.name = name
        # self.type = type
        # self.val = val
        
    # def __str__(self):
        # return str(self.val)
        
    # def __eq__(self, other):
        # return isinstance(other, self.__class__) and self.name = other.name

    # def __ne__(self, other):
        # return not self.__eq__(other)
        
    # def updateFromStr(self,str):
        # if self.type == self.BOOL
        
# class IntField(BaseField):

    # def fromStr

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
    
    def __init__(self,arr,feedback=None):
        self.arr = arr
        self.nb_fields = len(arr)
        self.feedback = feedback
        
    def getNField(self,n):
        if n < self.nb_fields:
            return self.arr[n]
        else:
            self.feedback.pushWarning("getNField(" + str(n) + ") out of bounds : " + str(self.nb_fields))
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
    
    def __init__(self,dict,feedback=None):
        # if not fields:
            # fields = list(dict.keys())
        # self.field_to_idx = {f : fields.index(f) for f in fields}
        # if not display_fields:
            # display_fields = fields
        # self.idx_to_fields = {fields.index(f) : f for f in display_fields}
        # self.display_fields = display_fields
        # self.nb_fields = len(self.display_fields)
        self.dict = { f:dict[f] for f in dict }
        self.feedback = feedback
    
    # Initialize from values according to fields order
    @classmethod
    def fromValues(cls,valueList):
        d = dict()
        for cpt, v in enumerate(valueList):
            d[cls.FIELDS[cpt]] = v
        utils.debug(str(d))
        utils.debug(str(d.__class__.__name__))
        return cls(dict=d)
        
    def __str__(self):
        return str(self.dict)
    def __copy__(self):
        return DictItem(self.dict,feedback=self.feedback)
        
    # def toJSON(self):
        # return json.dumps(self)
    @classmethod
    def fromDict(cls,dict,feedback=None):
        feedback.pushDebugInfo("fromDict " + str(cls.__name__))
        feedback.pushDebugInfo("fromDict1 " + str(dict))
        dict = utils.castDict(dict)
        feedback.pushDebugInfo("fromDict2 " + str(dict))
        return cls(dict,feedback=feedback)
    @classmethod
    def fromStr(cls,s,feedback=None):
        d = ast.literal_eval(s)
        return cls.fromDict(dict,feedback=feedback)
    @classmethod
    def fromXML(cls,root,feedback=None):
        feedback.pushDebugInfo("fromXML " + str(cls.__name__))
        return cls.fromDict(root.attrib,feedback=feedback)
        
    # def recompute(self):
        # fields = list(self.dict.keys())
        # self.idx_to_fields = {fields.index(f) : f for f in self.display_fields}
        # self.nb_fields = len(fields)
        
    # getNField is used by data function in DictModel to display value in table
    # def getNField(self,n):
        # if n < self.nb_fields:
            # return self.dict[self.idx_to_fields[n]]
        # else:
            # self.feedback.pushDebugInfo("getNField " + str(n))
            # self.feedback.pushWarning("getNField(" + str(n) + ") out of bounds : " + str(self.nb_fields))
            # return None
            #utils.internal_error("Accessing " + str(n) + " field >= " + str(self.nb_fields))
            
    # def updateNField(self,n,value):
        # if n < self.nb_fields:
            # self.dict[self.idx_to_fields[n]] = value
        # else:
            # assert false
            
    def equals(self,other):
        return (self.dict == other.dict)
        
        
    def toXMLItems(self,indent=""):
        xmlStr = indent + "<" + self.__class__.__name__
        for k,v in self.dict.items():
            xmlStr += indent + " " + k + "=\"" + xmlUtils.xmlEscape(str(v)) + "\""
        xmlStr += ">\n"
        return xmlStr
    def toXML(self,indent=""):
        xmlStr = self.toXMLItems(indent=indent)
        # for c in self.children:
            # xmlStr += c.toXML()
        xmlStr += "</" + self.__class__.__name__ +">"
        return xmlStr
            
    def updateFromOther(self,other):
        for k in other.dict:
            self.dict[k] = other.dict[k]
    def updateFromDlgItem(self,dlgItem):
        self.updateFromOther(dlgItem)
   
class DictItemWithChild(DictItem):
    
    def __init__(self,dict=dict,feedback=None,child=None):
        super().__init__(dict=dict,feedback=feedback)
        self.setChild(child)      
        
    # def getItemClass(self,childTag):
        # return getattr(sys.modules[__name__], childTag)
        
    def toXML(self,indent=""):
        self.feedback.pushDebugInfo("childXML = " +str(self.child))
        self.feedback.pushDebugInfo("childXML = " +str(self.child.__class__.__name__))
        xmlStr = self.toXMLItems(indent=indent)
        xmlStr += self.child.toXML(indent=indent+" ")
        xmlStr += "</" + self.__class__.__name__ +">"
        return xmlStr
    def setChild(self,child):
        self.child = child
    @classmethod
    def fromChildItem(cls,dlgItem,feedback=None):
        dict = cls.childToDict(dlgItem)
        return cls(dict=dict,feedback=feedback,child=dlgItem)
    @classmethod
    def fromXML(cls,root,feedback=None):
        o = cls.fromDict(root.attrib,feedback=feedback)
        for child in root:
            childTag = child.tag
            # classObj = getattr(sys.modules[__name__], childTag)
            classObj = cls.getItemClass(childTag)
            # classObj = cls.itemClass
            childObj = classObj.fromXML(child,feedback=feedback)
            o.setChild(childObj)
        return o
    def getChild(self):
        return self.child  
            
    def updateFromOther(self,other):
        for k in other.dict:
            self.dict[k] = other.dict[k]
        self.setChild(other.child)
    def updateFromChild(self,child):
        # assert(False)
        self.dict = self.childToDict(child)
        self.setChild(child)
    def updateFromDlgItem(self,dlgItem):
        self.updateFromChild(dlgItem)
        
class DictItemWithChildren(DictItem):
    
    def __init__(self,dict=dict,feedback=None,children=[]):
        super().__init__(dict=dict,feedback=feedback)
        self.children = children
        
    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.__class__.__name__
        childrenStr = ""
        for k,v in self.dict.items():
            xmlStr += indent + " " + k + "=\"" + xmlUtils.xmlEscape(str(v)) + "\""
        xmlStr += ">\n"
        for c in self.children:
            xmlStr += c.toXML()
        xmlStr += "</" + self.__class__.__name__ +">"
        return xmlStr
    def addChild(self,childObj):
        self.children.append(childObj)
    @classmethod
    def fromDlgItem(cls,dlgItem):
        cls.toDict(dlgItem)
        cls.dlgItem = dlgItem
        return cls(dict=cls.dict,feedback=feedback,children=[dlgItem])
    @classmethod
    def fromXML(cls,root,feedback=None):
        o = cls.fromDict(root.attrib,feedback=feedback)
        for child in root:
            childTag = child.tag
            classObj = getattr(sys.modules[__name__], childTag)
            # classObj = getattr(sys.modules[cls.__name__], childTag)
            childObj = classOb.fromXML(child,feedback=feedback)
            o.addChild(childObj)
        return o
    def getDialog(self):
        if self.children:
            return self.children[0]
        else:
            self.feedback.internal_error("No children for ImportItem")    
            
    def updateFromOther(self,other):
        self.updateFromDlgItem(other)
    def updateFromDlgItem(self,dlgItem):
        self.dict = self.dlgToDict(dlgItem)
        self.children = [dlgItem]
        self.dlgItem = dlgItem
    # return getattr(sys.modules[__name__], str)
# print str_to_class("Foobar")
# print type(Foobar)
        # for child in root:
            # utils.debug("tag = " + str(child.tag))
            # model = self.getModelFromParserName(child.tag)
            # if model:
                # model.fromXMLRoot(child)
                # model.layoutChanged.emit()
    
    
# FieldsModel modelizes a unique dictionary.
# Displayed in vertical mode (1 line = 1 field, single column).
# Used for parameters for instance.
class FieldsModel(QAbstractTableModel):

    def __init__(self,parent,dict,feedback=None):
        QAbstractTableModel.__init__(self)
        self.dict = dict
        self.fields = dict.keys()
        self.feedback = feedback
        
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

    def __init__(self,itemClass=None,fields=[],feedback=None):
        QAbstractTableModel.__init__(self)
        self.feedback = feedback
        self.items = []
        self.orders = {}
        self.parser_name = self.__class__.__name__
        self.itemClass = itemClass
        # print(str(itemClassName))
        # self.itemClass = getattr(sys.modules[__name__], itemClassName)
        if fields:
            self.fields = fields
        else:
            self.feedback.pushInfo("ic " + str(self.itemClass))
            self.feedback.pushInfo("ic " + str(self.itemClass.__class__.__name__))
            self.fields = self.itemClass.FIELDS
        self.feedback.pushInfo("AGM OK")

    @staticmethod
    def getItemClass(childTag):
        return getattr(sys.modules[__name__], childTag)

    def __str__(self):
        res = "[[" + ",".join([str(i) for i in self.items]) + "]]"
        return res
    
    # @abstractmethod
    # def setItemClass(itemClass):
        # self.itemClass = itemClass
    @abstractmethod
    def mkItemFromStr(self,s):
        return self.itemClass.fromStr(s,feedback=self.feedback)
        # return DictItem.fromStr(s)
    def fromStr(self,s):
        assert(len(s)>=4)
        items_str = s[2:-2].split(",")
        for i_str in items_str:
            i = self.mkItemFromStr(i_str)
            self.addItem(i)
        self.layoutChanged.emit()
        
    def tr(self, msg):
        return QCoreApplication.translate(self.__class__.__name__, msg)
        
    def checkNotEmpty(self):
        if len(self.items) == 0:
            self.feedback.internal_error("Empty buffer model")
        
    def getItems(self):
        return self.items
        
    def getNbItems(self):
        return len(self.getItems())
        
    def getNItem(self,n):
        if n < self.rowCount():
            return self.items[n]
        else:
            self.feedback.pushWarning("[" + self.__class__.__name__
                + "] Unexpected index " + str(n))
            return None
    def getNField(self,item,n):
        return item.getNField(n)
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.items)
        
    def columnCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    def getHeaderString(self,col):
        return None
        
    def headerData(self,col,orientation,role):
        if col >= len(self.fields):
            pass
            #utils.pushWarning("Header out of bounds : " + self.__class__.__name__
            #            + " " + str(col) + " " + str(self.fields))
        elif orientation == Qt.Horizontal and role == Qt.DisplayRole:
            #return QVariant(self.fields[col])
            headerStr = self.getHeaderString(col)
            headerStr = headerStr if headerStr else self.fields[col]
            return QVariant(headerStr)
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
        val = self.getNField(item,index.column())
        if role not in [Qt.DisplayRole,Qt.EditRole]:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(val))
        else:
            return QVariant()
            
    def setDataXY(self,x,y,value):
        item = self.getNItem(x)
        item.updateNField(index.column(),value)
    
    # This function is called by Qt when the view is modified at 'index' position.
    def setData(self, index, value, role):
        self.feedback.pushDebugInfo("setData (" + str(index.row()) + ","
            + str(index.column()) + ") : " + str(value))
        if role == Qt.EditRole:
            self.setDataXY(index.row(),index.column(),value)
            self.dataChanged.emit(index, index)
            return True
        return False
            
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            
    # Add new item in model if not already existing.
    # layoutChanged signal must be emitted to update view.
    def addItem(self,item):
        # self.feedback.pushInfo("json = " + str(item.toJSON()))
        for i in self.items:
            if i.equals(item):
                self.reportError("Item " + str(item) + " already exists")
                # return
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
        self.feedback.pushDebugInfo("[removeItems] nb of items = " + str(len(self.items)))
        self.feedback.pushDebugInfo("self.clss = " + str(self.__class__.__name__))
        rows = sorted(set([i.row() for i in indexes]))
        self.removeItemsFromRows(rows)
        
    def removeItemsFromRows(self,rows):
        n = 0
        for row in rows:
            roww = row - n
            self.feedback.pushDebugInfo("[removeItems] Deleting row " + str(roww))
            del self.items[roww]
            n += 1
        self.layoutChanged.emit()
        
    # Apply items for 'indexes' (position in item list, not index from Qt selection)
    # If no 'indexes' given, apply each item
    def applyItems(self,indexes=None):
        self.feedback.pushDebugInfo("[applyItems]")
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
        self.feedback.pushDebugInfo("upgradeElem " + str(row))
        if row > 0:
            self.swapItems(row -1, row)
        
    def downgradeElem(self,row):
        self.feedback.pushDebugInfo("downgradeElem " + str(row))
        if row < len(self.items) - 1:
            self.swapItems(row, row + 1)
            
    # Switch items at position 'i1' and 'i2'
    def swapItems(self,i1,i2):
        self.items[i1], self.items[i2] = self.items[i2], self.items[i1]
        self.layoutChanged.emit()
        
# DictModel is a group model with dictionary items
class DictModel(AbstractGroupModel):

    def __init__(self,itemClass=None,fields=[],
            feedback=None,display_fields=None):
        feedback.pushInfo("iC1 " + str(itemClass.__class__.__name__))
        if not itemClass:
            # itemClass = getattr(sys.modules[__name__], DictItem.__name__)
            itemClass = getattr(sys.modules[__name__], DictItem.__name__)
            # feedback.pushInfo("iC2 " + str(itemClass.__class__.__name__))
        # feedback.pushInfo("iC3 " + str(itemClass.__class__.__name__))
        # feedback.pushInfo("DI " + str(DictItem.__class__.__name__))
        # feedback.pushInfo("fields " + str(fields))
        # feedback.pushInfo("fields class " + str(fields.__class__.__name__))
        self.all_fields = fields[:]
        if display_fields is None:
            display_fields = fields
        AbstractGroupModel.__init__(self,itemClass=itemClass,
            fields=display_fields,feedback=feedback)
        self.feedback.pushInfo("DM1 " + str(self.__class__.__name__))
        self.feedback.pushInfo("DM2 " + str(self.itemClass.__class__.__name__))
        self.feedback.pushInfo("DM OK")
        # self.idx_to_fields = {self.fields.index(f) : f for f in display_fields}
        # self.idx_to_fields = self.fields
        self.nb_fields = len(self.fields)
        # self.feedback = feedback
        
    def __copy__(self):
        return DictModel(itemClass=self.itemClass,fields=self.fields,
            feedback=self.feedback,display_fields=self.display_fields)
        
    def getNField(self,item,n):
        try:
            # return item.dict[self.display_fields.keys()[n]]
            # return item.dict[self.idx_to_fields[n]]
            return item.dict[self.fields[n]]
        except Exception as e:
            self.feedback.pushDebugInfo("fields = " + str(self.fields))
            self.feedback.pushDebugInfo("all_fields = " + str(self.all_fields))
            # self.feedback.pushDebugInfo("idx_to_fields = " + str(self.idx_to_fields))
            self.feedback.pushDebugInfo("dict = " + str(item.dict))
            self.feedback.pushDebugInfo("n = " + str(n))
            raise e
    def setDataXY(self,x,y,value):
        self.feedback.pushDebugInfo("setDataXY %s %s %s"%(x,y,value))
        self.feedback.pushDebugInfo("fields %s"%(self.fields))
        item = self.getNItem(x)
        fieldname = self.fields[y]
        item.dict[fieldname] = value
        # item.dict[self.idx_to_fields[y]] = value
        
    def sort(self,col,order):
        # sorted_items = sorted(self.items, key=lambda i: i.dict[self.idx_to_fields[col]])
        sorted_items = sorted(self.items, key=lambda i: i.dict[self.fields[col]])
        if order == Qt.DescendingOrder:
            sorted_items.reverse()
        self.items = sorted_items
        self.layoutChanged.emit()
                
    def getMatchingItem(self,item):
        for i in self.items:
            if i.equals(item):
                return i
        return None
        
    def getItemFromName(self,name):
        for i in self.items:
            if i.getName() == name:
                return i
        return None
        
    def itemExists(self,item):
        matching_item = self.getMatchingItem(item)
        return (matching_item != None)
        
    def addItem(self,item):
        self.feedback.pushDebugInfo(str(self.__class__.__name__
            + " addItem " + str(item)))
        # self.feedback.pushInfo("json = " + str(item.toJSON()))
        if not item:
            self.feedback.internal_error("Empty item")
        item.checkItem()
        if self.itemExists(item):
            self.feedback.pushWarning("Item " + str(item) + " already exists")
        else:
            self.feedback.pushDebugInfo("adding item")
            self.items.append(item)
            self.insertRow(0)
        
    def recompute(self):
        # if self.dict:
            # fields = list(self.dict.keys())
        # self.idx_to_fields = {self.fields.index(f) : f for f in self.display_fields}
        self.nb_fields = len(self.fields)
            
    def addField(self,field,defaultVal=None):
        self.feedback.pushDebugInfo("addField f1 " + str(self.fields))
        if field not in self.fields:
            self.feedback.pushDebugInfo("addField " + str(field))
            self.fields.append(field)
            self.all_fields.append(field)
            # self.idx_to_fields = {self.fields.index(f) : f for f in self.display_fields}
            self.nb_fields = len(self.fields)
            for i in self.items:
                i.dict[field] = defaultVal
            self.layoutChanged.emit()
        self.feedback.pushDebugInfo("addField f2 " + str(self.fields))
            
    def renameField(self,oldName,newName):
        if oldName not in self.fields:
            self.feedback.internal_error("Could not find field " + str(oldName))
        self.fields = [ newName if f == oldName else f for f in self.fields]
        self.all_fields = [ newName if f == oldName else f for f in self.all_fields]
            
    # Each item is updated when field is removed
    # Item recompute function must be called to keep consistency
    def removeField(self,fieldname):
        self.feedback.pushDebugInfo("removeField " + fieldname)
        for i in self.items:
            utils.debug(str(i.dict.items()))
            if fieldname not in i.dict:
                self.feedback.pushWarning("Could not delete field '" + str(fieldname))
            else:
                del i.dict[fieldname]
        self.feedback.pushDebugInfo("self = " + str(self))
        if fieldname in self.fields:
            self.fields.remove(fieldname)
        if fieldname in self.all_fields:
            self.all_fields.remove(fieldname)
            self.recompute()
        self.layoutChanged.emit()
        
    # @abstractmethod
    def mkItemFromDict(self,dict,feedback=None):
        return self.itemClass.fromDict(dict,feedback=feedback)
        # self.feedback.todo_error(" [" + self.__class__.__name__ + "] mkItemFromDict not implemented")    @abstractmethod
    def mkItemFromXML(self,root,feedback=None):
        feedback.pushDebugInfo("mkItemFromXML " + self.__class__.__name__)
        feedback.pushDebugInfo("mkItemFromXML " + self.itemClass.__name__)
        return self.itemClass.fromXML(root,feedback=feedback)
        # self.feedback.todo_error(" [" + self.__class__.__name__ + "] mkItemFromXML not implemented")
    @staticmethod
    def dictFromXMLAttribs(attribs):
        dict = utils.castDict(attribs)
    @classmethod
    def fromXML(cls,root,feedback=None):
        feedback.pushDebugInfo("fromXML " + str(cls.__class__.__name__))
        model = cls(feedback=feedback)
        model.dict = cls.dictFromXMLAttribs(root.attrib)
        for child in root:
            # childTag = child.tag
            # classObj = cls.getItemClass(childTag)
            # childObj = classObj.fromXML(child,feedback=feedback)
            item = model.mkItemFromXML(child,feedback=feedback)
            model.addItem(item)
        return model          
            
    # @abstractmethod
    def updateFromXMLAttribs(self,attribs):
        self.dict = DictModel.dictFromXMLAttribs(attribs)
        
    def updateFromXML(self,root,feedback=None):
        self.updateFromXMLAttribs(root.attrib)
        self.items = []
        if not feedback:
            feedback = self.feedback
        for parsed_item in root:
            item = self.mkItemFromXML(parsed_item,feedback=feedback)
            self.addItem(item)
        self.layoutChanged.emit()
              
        
    def toXML(self,indent=" ",attribs_dict=None):
        # self.feedback.pushDebugInfo("toXML " + self.parser_name)
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
        # self.feedback.endSection()
        
    # Saves model to CSV file 'fname'
    def saveCSV(self,fname):
        with open(fname,"w", newline='') as f:
            writer = csv.DictWriter(f,fieldnames=self.fields,delimiter=';')
            writer.writeheader()
            for i in self.items:
                self.feedback.pushDebugInfo("writing row " + str(i.dict))
                writer.writerow(i.dict)
        self.feedback.pushDebugInfo("Model saved to file '" + str(fname) + "'")
        
    def applyItemsWithContext(self,context,feedback,indexes=None):
        if not self.items:
            self.feedback.reportError("Empty Model")
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
    
    def __init__(self,fields=DEFAULT_FIELDS,feedback=None):
        self.workspace = None
        self.extentLayer = None
        self.extentType = None
        self.resolution = 0.0
        self.projectFile = ""
        self.crs = self.DEFAULT_CRS
        self.fields = fields
        self.feedback = feedback
        QAbstractTableModel.__init__(self)
        
    def tr(self, msg):
        return QCoreApplication.translate(self.__class__.__name__, msg)
        
    def checkWorkspaceInit(self):
        if not self.workspace:
            self.feedback.user_error(self.tr("Workspace parameter not initialized"))
        if not os.path.isdir(self.workspace):
            self.feedback.user_error("Workspace directory '" + self.workspace + "' does not exist")
            
    def checkExtentInit(self):
        if not self.extentLayer:
            self.feedback.user_error(self.tr("Extent parameter not initialized"))
            
    def checkResolutionInit(self):
        if not self.resolution or self.resolution <= 0:
            self.feedback.user_error(self.tr("Resolution parameter not initialized"))
            
    def checkCrsInit(self):
        if not self.crs:
            self.feedback.user_error(self.tr("CRS parameter not initialized"))
        if not self.crs.isValid():
            self.feedback.user_error(self.tr("Invalid CRS"))
            
    def checkInit(self):
        checkWorkspaceInit()
        checkExtentInit()
        checkResolutionInit()
        checkCrsInit()
        
    def setExtentLayer(self,path):
        if path:
            path = self.normalizePath(path)
        self.feedback.pushInfo("Setting extent layer to " + str(path))
        self.extentLayer = path
        self.layoutChanged.emit()
        
    def setResolution(self,resolution):
        self.feedback.pushInfo("Setting resolution to " + str(resolution))
        self.resolution = resolution
        self.layoutChanged.emit()
        
    def setCrs(self,crs):
        self.feedback.pushInfo("Setting extent CRS to " + crs.description())
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
        self.feedback.pushInfo("Workspace directory set to '" + norm_path)
        if not os.path.isdir(norm_path):
            self.feedback.user_error("Directory '" + norm_path + "' does not exist")
        return norm_path
            
    def updateFromXML(self,root,feedback=None):
        dict = root.attrib
        self.feedback.pushDebugInfo("params dict = " + str(dict))
        return self.fromXMLDict(dict)
    
    def fromXMLDict(self,dict):
        if self.WORKSPACE in dict:
            if not self.workspace and os.path.isdir(dict[self.WORKSPACE]):
                self.setWorkspace(dict[self.WORKSPACE])
            elif self.projectFile is not None:
                self.setWorkspace(os.path.dirname(self.projectFile))
        if self.RESOLUTION in dict:
            try:
                self.setResolution(float(dict[self.RESOLUTION]))
            except ValueError:
                self.feedback.user_error("Unexpected resolution : " + str(dict[self.RESOLUTION]))
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
            #return QVariant(self.fields[col])
            return QVariant(self.tr(self.fields[col]))
        return QVariant()
        
    # Checks that workspace is intialized and is an existing directory.
    def checkWorkspaceInit(self):
        if not self.workspace:
            self.feedback.user_error("Workspace parameter not initialized")
        if not os.path.isdir(self.workspace):
            self.feedback.user_error("Workspace directory '" + self.workspace + "' does not exist")
            
    # Returns relative path w.r.t. workspace directory.
    # File separator is set to common slash '/'.
    def normalizePath(self,path):
        self.checkWorkspaceInit()
        if not path:
            self.feedback.user_error("Empty path")
        norm_path = utils.normPath(path)
        if os.path.isabs(norm_path):
            try:
                rel_path = os.path.relpath(norm_path,self.workspace)
            except ValueError:
                rel_path = norm_path
        else:
            rel_path = norm_path
        final_path = utils.normPath(rel_path)
        return final_path
            
    # Returns absolute path from normalized path (cf 'normalizePath' function)
    def getOrigPath(self,path):
        self.checkWorkspaceInit()
        if path is None or path == "":
            self.feedback.user_error("Empty path")
        elif os.path.isabs(path):
            norm_path = os.path.normpath(path)
            return norm_path
        else:
            join_path = utils.joinPath(self.workspace,path)
            norm_path = os.path.normpath(join_path)
            return norm_path
            
    # Checks that all parameters are initialized
    def checkInit(self):
        self.checkWorkspaceInit()
        if not self.extentLayer:
            self.feedback.user_error("Extent layer parameter not initialized")
        extent_path = self.getOrigPath(self.extentLayer)
        self.feedback.pushDebugInfo("extent_path = " + str(extent_path))
        utils.checkFileExists(extent_path,"Extent layer ")
        if not self.resolution:
            self.feedback.user_error("Resolution parameter not initialized")
        if self.resolution == 0.0:
            self.feedback.user_error("Null resolution")
        if not self.crs:
            self.feedback.user_error("CRS parameter not initialized")
        if not self.crs.isValid():
            self.feedback.user_error("Invalid CRS")
            
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
            self.feedback.user_error("Extent layer not initialized")
            
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
        
    def clipByExtent(self,input,name="",out_path="",clip_raster=True,
            context=None,feedback=None):
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
    def normalizeRaster(self,path,out_path=None,resampling_mode="near",
            context=None,feedback=None):
        if not self.extentLayer:
            return input
        extent_layer, extent_layer_type = self.getExtentLayerAndType()
        self.feedback.pushDebugInfo("extent_layer_type = " + str(extent_layer_type))
        resolution = self.getResolution()
        if extent_layer_type == 'Vector':
            extent_path = self.getExtentLayer()
            clipped_path = QgsProcessingUtils.generateTempFilename('clipped.tif')
            res = qgsTreatments.clipRasterFromVector(path,extent_path,out_path,
                resolution=resolution,context=context,feedback=feedback)
        else:
            extent = self.getExtentRectangle()
            warped_path = QgsProcessingUtils.generateTempFilename('warped.tif')
            self.feedback.pushWarning("Normalizing raster '" + str(path)+ "' to '" + str(warped_path) + "'")
            res = qgsTreatments.applyWarpReproject(path,out_path,resampling_mode,
                dst_crs=self.crs,resolution=resolution,extent=extent,
                context=context,feedback=feedback)
        return res
                
""" AbstractConnector connects a view and a model """
class AbstractConnector:

    def __init__(self,model,view,addButton=None,removeButton=None,
                 runButton=None,selectionCheckbox=None):
        self.model = model
        self.feedback = model.feedback
        self.view = view
        self.addButton = addButton
        self.onlySelection = False
        self.removeButton = removeButton
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
        self.feedback.pushDebugInfo("setting onlySelection to " + str(new_val))
        self.onlySelection = new_val
        
    # This function build model item from view and is called by addItem
    @abstractmethod
    def mkItem(self):
        self.feedback.todo_error(" [" + self.__class__.__name__ + "] mkItem not implemented")
        
    def getSelectedIndexes(self):
        if self.onlySelection:
            indexes = list(set([i.row() for i in self.view.selectedIndexes()]))
        else:
            indexes = range(0,len(self.model.items))
        return indexes
        
    def applyItems(self):
        indexes = self.getSelectedIndexes()
        self.feedback.pushDebugInfo("Selected indexes = " + str(indexes))
        self.model.applyItemsWithContext(None,self.dlg.feedback,indexes)
        #self.model.applyItemsWithContext(self.dlg.context,self.dlg.feedback,indexes)
        
    def addItem(self):
        self.feedback.pushDebugInfo("AbstractConnector.addItem")
        item = self.mkItem()
        if item:
            self.model.addItem(item)
            self.model.layoutChanged.emit()
        
    def removeItems(self):
        if self.model.getItems():
            indices = self.view.selectedIndexes()
            self.feedback.pushDebugInfo(str([i.row() for i in indices]))
            self.model.removeItems(indices)
        else:
            self.feedback.pushWarning("Empty model, nothing to remove")
        
    # Upgrade selected item rank (only single selection for now)
    def upgradeItem(self):
        self.feedback.pushDebugInfo("upgradeItem")
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
            self.feedback.pushWarning("Several rows selected, please select only one")
            
    # Downgrade selected item rank (only single selection for now)
    def downgradeItem(self):
        self.feedback.pushDebugInfo("downgradeItem")
        indices = self.view.selectedIndexes()
        rows = list(set([i.row() for i in indices]))
        #nb_indices = len(indices)
        nb_rows = len(rows)
        if nb_rows == 0:
            self.feedback.pushDebugInfo("no idx selected")
        elif nb_rows == 1:
            row = rows[0]
            if row < len(self.model.getItems()) - 1:
                self.model.swapItems(row, row + 1)
                self.view.selectRow(row + 1)
        else:
            self.feedback.pushWarning("Several rows selected, please select only one")


# Table Model with extensive fields (possibility to add columns)
# Conceived for DictItem but might work with other items
class ExtensiveTableModel(DictModel):

    ROW_NAME = 'name'
    ROW_DESCR = 'descr'
    ROW_CODE = 'code'
    BASE_FIELDS = [ ROW_CODE, ROW_DESCR ]
    
    DEFAULT_VAL = None

    LEGACY_MATCHING = { 'class' : ROW_NAME , 'class_descr' : ROW_DESCR }

    def __init__(self,parentModel,idField=ROW_CODE,
                 rowIdField=ROW_CODE,baseFields=BASE_FIELDS):
        super().__init__(fields=list(baseFields),
            feedback=parentModel.feedback)
        self.feedback.pushInfo("EM1 " + str(self.__class__.__name__))
        self.feedback.pushInfo("EM2 " + str(self.itemClass.__class__.__name__))
        self.feedback.pushInfo("EM OK")
        self.parentModel = parentModel
        # self.feedback = parentModel.feedback
        self.defaultVal = self.DEFAULT_VAL
        self.rowNames = []
        self.baseFields = baseFields
        self.fields = list(baseFields)
        self.extFields = []
        self.idField = idField
        self.rowIdField = rowIdField
        self.valueSet = []
        
    def setValues(self,values):
        self.valueSet = values
    def getItemValue(self,item):
        return item.dict[self.idField]
    def getCodesStr(self):
        return [str(i.dict[self.idField]) for i in self.items]
                
    # True if item matching class 'rowName' exists, False otherwise.
    def rowExists(self,rowName):
        for fr in self.items:
            if fr.dict[self.idField] == rowName:
                return True
        return False
        
    # Returns item matching class 'rowName', None if there is no match.
    def getRowByName(self,rowName):
        for i in self.items:
            if str(i.dict[self.idField]) == str(rowName):
                return i
        return None
        
    # Creates RowItem from dict
    def createRowFromDict(self,d):
        return DictItem(d,feedback=self.feedback)
        # return DictItem(d,self.fields,feedback=self.feedback)
    def createRowFromBaseRow(self,baseRowItem):
        return self.createRowFromDict(baseRowItem.dict)
    # Adds new new rowItem in model.
    def addRowItem(self,rowItem):
        self.addRowFields(rowItem)
        self.addItem(rowItem)
        self.layoutChanged.emit()
    # Adds new rowItem in model from given baseRowItem.
    def addRowItemFromBase(self,baseRowItem):
        rowItem = self.createRowFromBaseRow(baseRowItem)
        self.addRowItem(rowItem)
    def addRowFromCode(self,code,descr=""):
        d = { self.ROW_CODE : code, self.ROW_DESCR : descr }
        rowItem = self.createRowFromDict(d)
        self.addRowItem(rowItem)
        
    # Removes item matching class 'name' from model.
    def removeRowFromName(self,name):
        self.feedback.pushDebugInfo("removing row " + str(name) + " from table")
        self.rowNames = [rowName for rowName in self.rowNames if rowName != name]
        for i in range(0,len(self.items)):
            if self.items[i].dict[self.idField] == name or self.items[i].dict[self.ROW_NAME]:
                del self.items[i]
                self.layoutChanged.emit()
                return
        
    # Adds subnetwork columns to given FrictionRowItem.
    # Friction values are set to defaultVal (None).
    def addRowFields(self,row):
        extFields = self.fields[len(self.baseFields):]
        self.feedback.pushDebugInfo("addRowFields " + str(extFields))
        for f in extFields:
            row.dict[f] = self.defaultVal
            
    # Adds new subnetwork entry to all items of model from given STItem.
    def addCol(self,col_name,defaultVal=DEFAULT_VAL):
        self.feedback.pushDebugInfo("addCol " + str(col_name))
        super().addField(col_name,defaultVal = self.defaultVal)
        
    # Removes subnetwork 'st_name' entry for all items of model.
    def removeColFromName(self,col_name):
        self.feedback.pushDebugInfo("removeColFromName " + str(col_name))
        self.removeField(col_name)
        self.layoutChanged.emit()
        
    # def updateFromXML(self,root,feedback=None):
        # extFields = self.fields[len(self.baseFields):]
        # for f in extFields:
            # self.removeColFromName(f)
        
    # Reload items of model to match current ClassModel.
    def reloadModel(self,baseRowItems):
        self.feedback.pushDebugInfo("reloadModel")
        currNames = [i.dict[self.idField] for i in self.items]
        rowNames = [bri.dict[self.rowIdField] for bri in baseRowItems]
        self.feedback.pushDebugInfo("currNames " + str(currNames))
        self.feedback.pushDebugInfo("rowNames " + str(rowNames))
        toDeleteNames = set(currNames) - set(rowNames)
        toAddNames = set(rowNames) - set(currNames)
        self.feedback.pushDebugInfo("Deleting row " + str(toDeleteNames))
        self.items = [i for i in self.items if i.dict[self.idField] in rowNames]
        for bri in baseRowItems:
            currItem = self.getRowByName(bri.dict[self.rowIdField])
            if currItem:
                for f in self.baseFields:
                    if f not in bri.dict:
                        if f in self.LEGACY_MATCHING:
                            bri_val = bri.dict[self.LEGACY_MATCHING[f]]
                        else:
                            utils.internal_error("Unexpected field " + str(f))
                    else:
                        bri_val = bri.dict[f]
                    if bri_val:
                        currItem.dict[f] = bri_val
            else:
                self.addRowItemFromBase(bri)
        self.layoutChanged.emit()        
                            
    # Returns reclassify matrix (list) for native:reclassifybytable call.
    def getReclassifyMatrixes(self,colNames):
        matrixes = { colName : [] for colName in colNames }
        for item in self.items:
            id = item.dict[self.idField]
            code = item.dict[self.ROW_CODE]
            for name in colNames:
                if name not in self.fields:
                    self.feedback.internal_error("Subnetwork '" + str(name)
                        + "' not found in friction model")
                new_val = item.dict[name]
                if new_val is None:
                    self.feedback.pushWarning("No friction assigned to subnetwork " + str(name)
                                     + " for class " + str(id))
                    # float(new_val) causes exception is new_val = None
                    new_val = ''
                if new_val == qgsTreatments.nodata_val:
                    self.feedback.internal_error("Reclassify to nodata "
                        + str(new_val) + "in " + str(item))
                try:
                    float(new_val)
                except ValueError:
                    self.feedback.pushWarning("Ignoring non-numeric value '" + str(new_val)
                        + "' for class ")
                    # new_val = qgsTreatments.nodata_val
                    continue
                # TODO : change self.ROW_CODE to something like self.codeField
                matrixes[name] += [ code, code, new_val ]
        return matrixes
        
    # Returns set of item' code (value in input raster)
    def getCodes(self):
        codes = set([int(item.dict[self.ROW_CODE]) for item in self.items])
        return codes
        
    # Raise an error in values of input raster do no match codes of friction items.
    def checkInVals(self,in_path):
        in_vals = qgsUtils.getRasterValsFromPath(in_path)
        codes = self.getCodes()
        diff = in_vals.difference(codes)
        if len(diff) > 0:
            self.feedback.user_error("Some values of " + str(in_path) + " are not associated to a friction value " + str(diff))
            
    # Saves friction coefficients to CSV file 'fname'
    def saveCSV(self,fname):
        with open(fname,"w", newline='') as f:
            writer = csv.DictWriter(f,fieldnames=self.fields,delimiter=';')
            writer.writeheader()
            for i in self.items:
                self.feedback.pushDebugInfo("writing row " + str(i.dict))
                writer.writerow(i.dict)
        self.feedback.pushInfo("Friction saved to file '" + str(fname) + "'")
                
    # Imports CSV row as an item
    def fromCSVRow(self,row):
        if self.idField not in row:
            self.feedback.user_error("No field '" + str(self.idField)
                + "' in row " + str(row))
        rowName = row[self.idField]
        rowItem = self.getRowByName(rowName)
        self.feedback.pushDebugInfo("rowName = " + str(rowName))
        if rowItem:
            for f in self.fields:
                if f in row:
                    rowItem.dict[f] = row[f]
                else:
                    self.feedback.pushWarning("No entry for row '" + rowName
                        + "' and col '" + str(f) + "'")
        else:
            rowItem = self.createRowFromDict(row)
            self.addItem(rowItem)
            
    # Loads CSV file 'fname' into model (insertion or update).
    def fromCSVUpdate(self,fname):
        with open(fname,"r") as f:
            reader = csv.DictReader(f,fieldnames=self.fields,delimiter=';')
            first_line = next(reader)
            for row in reader:
                self.fromCSVRow(row)
        self.layoutChanged.emit()
        
    # Loads friction coefficients from CSV file 'fname' into model.
    # Existing items are erased.
    def fromCSV(self,fname):
        self.items = []
        with open(fname,"r") as f:
            reader = csv.DictReader(f,fieldnames=self.fields,delimiter=';')
            header = reader.fieldnames
            self.fields = header
            first_line = next(reader)
            for row in reader:
                self.fromCSVRow(row)
        self.layoutChanged.emit()
        
    # Loads model from XML root (tag 'FrictionModel')    
    # def fromXML(self,root):
        # self.items = []
        # for fr in root:
                # self.fromCSVRow(fr.attrib)
        # self.layoutChanged.emit()
        
    def flags(self, index):
        if index.column() in [1,2]:
            flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return flags

# Main model for plugins that can be saved to XML file
class MainModel:

    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.parser_name + ">"
        new_indent = indent + " "
        for model in self.models:
            xmlStr += "\n" + indent + model.toXML(indent=new_indent)
        xmlStr += "\n" + indent + "</" + self.parser_name + ">"
        return xmlStr
        
    def getModelFromParserName(self,name):
        for model in self.models:
            if model.parser_name == name:
                return model
        return None
        
    def getOutLayerFromName(self,name,model):
        self.feedback.pushDebugInfo("getOutLayerFromName " + str(name))
        item = model.getItemFromName(name)
        if not item:
            self.feedback.internal_error("Item '" + str(name) + "' not found in model "
                + str(model.__class__.__name__))
        layer = model.getItemOutPath(item)
        self.feedback.pushDebugInfo("getOutLayerFromName layer " + str(layer))
        abs_layer = self.getOrigPath(layer)
        self.feedback.pushDebugInfo("getOutLayerFromName abs_layer " + str(abs_layer))
        return abs_layer
        
    # def fromXMLRoot(self,root):
        # for child in root:
            # self.feedback.pushDebugInfo("tag = " + str(child.tag))
            # childTag = child.tag
            # model = self.getModelFromParserName(child.tag)
            # if model:
                # model.fromXML(child)
                # model.layoutChanged.emit()        
    # def fromXMLRoot(self,root):
        # for child in root:
            # utils.debug("tag = " + str(child.tag))
            # model = self.getModelFromParserName(child.tag)
            # if model:
                # model.fromXML(child)
                # model.layoutChanged.emit()

# Main dialog for multi-tabs plugins            
class MainDialog(QtWidgets.QDialog):

    # Initialize Graphic elements for each tab
    def initGui(self):
        # if self.provider:
            # QgsApplication.processingRegistry().addProvider(self.provider)
        for tab in self.connectors:
            tab.initGui()
            
    def tr(self, message):
        return QCoreApplication.translate(self.pluginName, message)

    # Exception hook, i.e. function called when exception raised.
    # Displays traceback and error message in log tab.
    # Ignores CustomException : exception raised from BioDispersal and already displayed.
    def pluginExcHook(self,excType, excValue, tracebackobj):
        self.feedback.pushDebugInfo("pluginExcHook " + str(excType))
        if excType == utils.CustomException:
            msgStart = self.tr("Ignoring custom exception : ")
            self.feedback.pushDebugInfo(msgStart + str(excValue))
        else:
            tbinfofile = StringIO()
            traceback.print_tb(tracebackobj, None, tbinfofile)
            tbinfofile.seek(0)
            tbinfo = tbinfofile.read()
            errmsg = str(excType) + " : " + str(excValue)
            separator = '-' * 80
            sections = [separator, errmsg, separator]
            self.feedback.pushDebugInfo(str(sections))
            msg = '\n'.join(sections)
            self.feedback.pushDebugInfo(str(msg))
            final_msg = tbinfo + "\n" + msg
            self.feedback.pushDebugInfo("traceback : " + str(tbinfo))
            self.feedback.error_msg(errmsg,prefix="Unexpected error")
        self.mTabWidget.setCurrentWidget(self.logTab)
        self.feedback.focusLogTab()
        # self.feedback.clear()
        
    # Connects view and model components for each tab.
    # Connects global elements such as project file and language management.
    def connectComponents(self,saveAsFlag=True):
        for tab in self.connectors:
            tab.connectComponents()
        # Main tab connectors
        if saveAsFlag:
            self.saveProjectAs.clicked.connect(self.saveModelAsAction)
        self.saveProject.clicked.connect(self.saveModel)
        self.openProject.clicked.connect(self.loadModelAction)
        self.langEn.clicked.connect(self.switchLangEn)
        self.langFr.clicked.connect(self.switchLangFr)
        self.aboutButton.clicked.connect(self.openHelpDialog)
        sys.excepthook = self.pluginExcHook
                
    def initLog(self):
        utils.print_func = self.txtLog.append
        
    def switchLang(self,lang):
        utils.debug("switchLang " + str(lang))
        #loc_lang = locale.getdefaultlocale()
        #utils.info("locale = " + str(loc_lang))
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        lang_path = os.path.join(plugin_dir,'i18n',self.pluginName
            + '_' + lang + '.qm')
        if os.path.exists(lang_path):
            self.translator = QTranslator()
            self.translator.load(lang_path)
            if qVersion() > '4.3.3':
                utils.debug("Installing translator " + str(lang_path))
                QCoreApplication.installTranslator(self.translator)
            else:
                utils.internal_error("Unexpected qVersion : " + str(qVersion()))
        else:
            utils.warn("No translation file : " + str(lang_path))
        self.retranslateUi(self)
        # self.paramsConnector.refreshProjectName()
        utils.curr_language = lang
        self.tabConnector.loadHelpFile()
        
    def switchLangEn(self):
        self.switchLang("en")
        self.langEn.setChecked(True)
        self.langFr.setChecked(False)
        
    def switchLangFr(self):
        self.switchLang("fr")
        self.langEn.setChecked(False)
        self.langFr.setChecked(True)
        
    def openHelpDialog(self):
        pass
        
    # Recompute self.parsers in case they have been reloaded
    def recomputeParsers(self):
        self.parsers = [self.pluginModel]
        
    # Return XML string describing project
    def toXML(self):
        return self.pluginModel.toXML()

    # Save project to 'fname'
    def saveModelAs(self,fname):
        self.recomputeParsers()
        xmlStr = self.toXML()
        self.pluginModel.paramsModel.projectFile = fname
        self.paramsConnector.setProjectFile(fname)
        utils.writeFile(fname,xmlStr)
        self.feedback.pushInfo(self.tr("Model saved into file '") + fname + "'")
        
    def saveModelAsAction(self):
        fname = qgsUtils.saveFileDialog(parent=self,
                                        msg=self.tr("Save project as"),
                                        filter="*.xml")
        if fname:
            self.saveModelAs(fname)
        
    # Save project to projectFile if existing
    def saveModel(self):
        fname = self.pluginModel.paramsModel.projectFile
        utils.checkFileExists(fname,"Project ")
        self.saveModelAs(fname)
   
    # Load project from 'fname' if existing
    def loadModel(self,fname):
        self.feedback.pushDebugInfo("loadModel " + str(fname))
        utils.checkFileExists(fname)
        config_parsing.setConfigParsers(self.pluginModel.models)
        self.pluginModel.paramsModel.projectFile = fname
        self.paramsConnector.setProjectFile(fname)
        config_parsing.parseConfig(fname,feedback=self.feedback)
        self.feedback.pushInfo("Model loaded from file '" + fname + "'")
        
    def loadModelAction(self):
        fname = qgsUtils.openFileDialog(parent=self,
                                        msg=self.tr("Open project"),
                                        filter="*.xml")
        if fname:
            self.loadModel(fname)
        
# Table view with dialog to build items
# Butonn to create new item, double click to edit selected item
class TableToDialogConnector(AbstractConnector):

    def __init__(self,model,view,addButton=None,removeButton=None,
                 runButton=None,selectionCheckbox=None):
        super().__init__(model,view,addButton=addButton,
            removeButton=removeButton,runButton=runButton,
            selectionCheckbox=selectionCheckbox)

    def connectComponents(self):
        super().connectComponents()
        self.view.doubleClicked.connect(self.openDialogEdit)
    
    def openDialogGetResult(self,item):
        self.preDlg(item)
        item_dlg = self.openDialog(item)
        if item_dlg:
            dlg_item = item_dlg.showDialog()
            if dlg_item:
                self.postDlg(dlg_item)
            elif item:
                self.postDlg(item)
        else:
            dlg_item = None
            # self.postDlg(item.child)
        return dlg_item
    
    def openDialogEdit(self,index):
        row = index.row()
        item = self.model.getNItem(row)
        self.feedback.pushDebugInfo("openDialog item = " +str(item))
        dlg_item = self.openDialogGetResult(item)
        if dlg_item:
            self.updateFromDlgItem(item,dlg_item)
            self.model.layoutChanged.emit()
            
    def mkItem(self):
        dlg_item = self.openDialogGetResult(None)
        return dlg_item
        # if dlg_item:
            # return self.mkItemFromDlgItem(dlg_item)
        # else:
            # return None
            
    def pathFieldToRel(self,dlgItem,fieldname):
        if dlgItem and dlgItem.dict and fieldname in dlgItem.dict:
            oldVal = dlgItem.dict[fieldname]
            if oldVal:
                newVal = self.model.pluginModel.normalizePath(oldVal)
                dlgItem.dict[fieldname] = newVal
            
    def pathFieldToAbs(self,dlgItem,fieldname):
        if dlgItem and fieldname in dlgItem.dict:
            oldVal = dlgItem.dict[fieldname]
            if oldVal:
                newVal = self.model.pluginModel.getOrigPath(oldVal)
                dlgItem.dict[fieldname] = newVal
       
    @abstractmethod
    def openDialog(self,item): 
        pass
        
    def preDlg(self,dlg_item):
        pass
    def postDlg(self,dlg_item):
        pass
    
    def updateFromDlgItem(self,item,dlg_item): 
        item.updateFromDlgItem(dlg_item)
    # @abstractmethod
    # def mkItemFromDlgItem(self,dlg_item): 
        # pass
     
    
class CheckableComboDelegate(QStandardItemModel):

    def __init__(self,baseModel):
        super().__init__()
        self.baseModel = baseModel

    def rowCount(self,parent=QModelIndex()):
        return len(self.baseModel.items)
    def columnCount(self,parent=QModelIndex()):
        return 1
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.baseModel.getNItem(row)
        itemName = item.getName()
        if role != Qt.DisplayRole:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(itemName))
        else:
            return QVariant()
    def setData(self, index, value, role):
        self.feedback.pushDebugInfo("setData (" + str(index.row()) + ","
            + str(index.column()) + ") : " + str(value))
        if role == Qt.EditRole:
            # row = self.setDataXY(index.row(),index.column(),value)
            self.dataChanged.emit(index, index)
            return True
        return False
        
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
        self.feedback.pushDebugInfo('Check Box editor Event detected : ')
        self.feedback.pushDebugInfo(str(event.type()))
        #if not (index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        if not (index.flags() & QtCore.Qt.ItemIsEditable):
            return False

        self.feedback.pushDebugInfo('Check Box editor Event detected : passed first check')
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
        self.feedback.pushDebugInfo('SetModelData')
        newValue = not bool(index.data())
        self.feedback.pushDebugInfo('New Value : {0}'.format(newValue))
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

# Code snippet from https://stackoverflow.com/questions/28037126/how-to-use-qcombobox-as-delegate-with-qtableview
class ComboDelegate(QtWidgets.QItemDelegate):
    editorItems=[]
    height = 20
    width = 200
    
    def __init__(self,items):
        super().__init__()
        self.editorItems = items
        self.height = 20
        self.width = 200
    
    def createEditor(self, parent, option, index):
        editor = QtWidgets.QListWidget(parent)
        # editor.addItems(self.editorItems)
        # editor.setEditable(True)
        editor.currentItemChanged.connect(self.currentItemChanged)
        return editor

    def setEditorData(self,editor,index):
        z = 0
        for item in self.editorItems:
            ai = QtWidgets.QListWidgetItem(item)
            editor.addItem(ai)
            if item == index.data():
                editor.setCurrentItem(editor.item(z))
            z += 1
        editor.setGeometry(0,index.row()*self.height,self.width,self.height*len(self.editorItems))

    def setModelData(self, editor, model, index):
        editorIndex=editor.currentIndex()
        text=editor.currentItem().text() 
        model.setData(index, text,role=Qt.EditRole)
        # print '\t\t\t ...setModelData() 1', text

    @pyqtSlot()
    def currentItemChanged(self): 
        self.commitData.emit(self.sender())
