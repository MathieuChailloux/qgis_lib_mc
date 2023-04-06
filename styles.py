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
    Useful functions to perform rendering style operations.
"""

import random

from PyQt5.QtGui import QColor
from qgis.core import (QgsColorRampShader,
                       QgsRasterShader,
                       QgsColorBrewerColorRamp,
                       QgsGradientColorRamp,
                       QgsCptCityColorRamp,
                       QgsPresetSchemeColorRamp,
                       QgsRasterBandStats,
                       QgsPalettedRasterRenderer,
                       QgsSingleBandPseudoColorRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRendererRange,
                       QgsFillSymbol,
                       QgsStyle)
                       
from . import utils, qgsUtils

redHex = '#ff0000'
yellowHex = '#ffff00'
greenHex = '#00ff00'
redCol = QColor(redHex)
yellowCol = QColor(yellowHex)
greenCol = QColor(greenHex)

singleColorRampList = [ 'Blues', 'Greens', 'Oranges', 'Purples', 'Reds' ]

def getDefaultStyle():
    return QgsStyle.defaultStyle()
    
# Color utilities
    
def getPresetGnYlRd():
    colors = [redCol,yellowCol,greenCol]
    colorRamp = QgsPresetSchemeColorRamp(colors=colors)
    return colorRamp
    
def getColorBrewColorRampGnYlRd():
    colorRamp = QgsColorBrewerColorRamp(schemeName='RdYlGn',inverted=True)
    return colorRamp
    
def mkColorRamp(color,invert=False):
    style = getDefaultStyle()
    colorRamp = style.colorRamp(color)
    if invert:
        colorRamp.invert()
    return colorRamp
    
def getGradientColorRampRdYlGn():
    return mkColorRamp('RdYlGn',invert=True)
    
def getRandomSingleColorRamp():
    rampName = random.choice(singleColorRampList)
    return mkColorRamp(rampName,invert=True)  
    
def setRenderer(layer,renderer):
    if not renderer:
        utils.internal_error("Could not create renderer")
    layer.setRenderer(renderer)
    utils.info("about to repaint")
    layer.triggerRepaint()
    
# Vector utilities

def mkGraduatedRenderer(layer,fieldname,color_ramp,nb_classes=5,classif_method=QgsGraduatedSymbolRenderer.Jenks):
    # classif = QgsClassificationQuantile()
    # classes = classif.classes(layer,fieldname,nb_classes)
    renderer = QgsGraduatedSymbolRenderer(attrName=fieldname)
    renderer.setSourceColorRamp(color_ramp)
    renderer.updateClasses(layer,classif_method,nb_classes)
    # renderer.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedColor)
    # renderer.setClassificationMethod(classif)
    return renderer
    
def setGraduatedStyle(layer,fieldname,color_ramp_name,invert_ramp=False,
        classif_method=QgsGraduatedSymbolRenderer.Jenks):
    color_ramp = mkColorRamp(color_ramp_name,invert=invert_ramp)
    renderer = mkGraduatedRenderer(layer,fieldname,color_ramp,classif_method=classif_method)
    setRenderer(layer,renderer)
    
    
def setGreenGraduatedStyle(layer,fieldname):
    setGraduatedStyle(layer,fieldname,'Greens')
    # color_ramp = mkColorRamp('Greens')
    # renderer = mkGraduatedRenderer(layer,fieldname,color_ramp,classif_method=classif_method)
    # setRenderer(layer,renderer)
    
def setRdYlGnGraduatedStyle(layer,fieldname,invert_ramp=False,
        classif_method=QgsGraduatedSymbolRenderer.Jenks):
    setGraduatedStyle(layer,fieldname,'RdYlGn',invert_ramp=invert_ramp,classif_method=classif_method)
    # color_ramp = mkColorRamp('RdYlGn')
    # renderer = mkGraduatedRenderer(layer,fieldname,color_ramp,classif_method=classif_method)
    # setRenderer(layer,renderer)
    
def setCustomClasses(layer,renderer,class_bounds):
    nb_bounds = len(class_bounds)
    renderer.updateClasses(layer,nb_bounds)
    for idx, b in enumerate(class_bounds):
        if idx > 0:
            renderer.updateRangeUpperValue(idx-1,b)
        renderer.updateRangeLowerValue(idx,b)
        
def setCustomClasses2(layer,fieldname,color_ramp,class_bounds):
    nb_bounds = len(class_bounds)
    nb_classes = nb_bounds + 1
    renderer = mkGraduatedRenderer(layer,fieldname,color_ramp,nb_classes=nb_classes)
    renderer.updateClasses(layer,nb_classes)
    for idx, b in enumerate(class_bounds,1):
        renderer.updateRangeUpperValue(idx - 1,b)
        renderer.updateRangeLowerValue(idx,b)
    setRenderer(layer,renderer)
    
def setCustomClassesDSFL(layer,fieldname):
    class_bounds = [0,10,20,25,35]
    color_ramp = getGradientColorRampRdYlGn()
    renderer = mkGraduatedRenderer(layer,fieldname,color_ramp,nb_classes=5)
    setCustomClasses(layer,renderer,class_bounds)
    setRenderer(layer,renderer)
    
def setRendererUniqueValues(layer,fieldname):
    idx = layer.fields().indexOf(fieldname)
    values = list(layer.uniqueValues(idx))
    ranges = []
    for cpt, v in enumerate(values):
        lower = v - 0.5 if cpt == 0 else (v + values[cpt-1]) / 2
        upper = v + 0.5 if cpt == len(values) - 1 else (values[cpt+1] + v) / 2
        label = str(v)
        range = QgsRendererRange(lower,upper,QgsFillSymbol(),label)
        ranges.append(range)
    # print("ranges = " +str(ranges))
    renderer = QgsGraduatedSymbolRenderer (attrName=fieldname,ranges=ranges)
    color_ramp = getGradientColorRampRdYlGn()
    renderer.updateColorRamp(color_ramp)
    setRenderer(layer,renderer)
     
# Raster utilities
    
def getValuesFromLayer3(layer):
    return qgsUtils.getRasterMinMedMax(layer)
    
def mkRasterShader(layer,color_ramp,classif_mode=QgsColorRampShader.Continuous):
    min, med, max = getValuesFromLayer3(layer)
    rasterShader = QgsRasterShader(minimumValue=min,maximumValue=max)
    colorRamp = getRandomSingleColorRamp()
    if not color_ramp:
        utils.internal_error("Could not create color ramp")        
    colorRampShader = QgsColorRampShader(minimumValue=min,maximumValue=max,
        colorRamp=color_ramp,classificationMode=classif_mode)
    colorRampShader.classifyColorRamp(band=1,input=layer.dataProvider())
    if colorRampShader.isEmpty():
        utils.internal_error("Empty color ramp shader")
    rasterShader.setRasterShaderFunction(colorRampShader)
    return rasterShader
    
def mkRandomColorRasterShader(layer):
    colorRamp = getRandomSingleColorRamp()
    return mkRasterShader(layer,colorRamp)
# def mkRandomColorRasterShader(layer):
    # min, med, max = getValuesFromLayer3(layer)
    # rasterShader = QgsRasterShader(minimumValue=min,maximumValue=max)
    # colorRamp = getRandomSingleColorRamp()
    # if not colorRamp:
        # utils.internal_error("Could not create color ramp")        
    # colorRampShader = QgsColorRampShader(minimumValue=min,maximumValue=max,colorRamp=colorRamp)
    # colorRampShader.classifyColorRamp(band=1,input=layer.dataProvider())
    # if colorRampShader.isEmpty():
        # utils.internal_error("Empty color ramp shader")
    # rasterShader.setRasterShaderFunction(colorRampShader)
    # return rasterShader
    
def mkQuantileShaderFromColorRamp(layer,colorRamp):
    return mkRasterShader(layer,colorRamp,classif_mode=QgsColorRampShader.Quantile)
# def mkQuantileShaderFromColorRamp(layer,colorRamp):
    # min, med, max = getValuesFromLayer3(layer)
    # colorRampShader = QgsColorRampShader(minimumValue=min,maximumValue=max,colorRamp=colorRamp,
                                         # classificationMode=QgsColorRampShader.Quantile)
    # utils.info("about to classify")
    # colorRampShader.classifyColorRamp(classes=5,band=1,input=layer.dataProvider())
    # if colorRampShader.isEmpty():
        # utils.internal_error("Empty color ramp shader")
    # rasterShader = QgsRasterShader(minimumValue=min,maximumValue=max)
    # rasterShader.setRasterShaderFunction(colorRampShader)
    # return rasterShader
    
# SBPC = Single Band Pseudo Color
def setSBPCRasterRenderer(layer,shader):
    if not shader:
        utils.internal_error("Could not create raster shader")
    renderer = QgsSingleBandPseudoColorRenderer(input=layer.dataProvider(),band=1,shader=shader)
    setRenderer(layer,renderer)
    
def setRandomColorRasterRenderer(layer):
    rasterShader = mkRandomColorRasterShader(layer)
    setSBPCRasterRenderer(layer,rasterShader)
    # if not rasterShader:
        # utils.internal_error("Could not create raster shader")
    # renderer = QgsSingleBandPseudoColorRenderer(input=layer.dataProvider(),band=1,shader=rasterShader)
    # if not renderer:
        # utils.internal_error("Could not create renderer")
    # layer.setRenderer(renderer)
    # layer.triggerRepaint()
    
# SBPC = Single Band Pseudo Color
def setRendererSBPCGnYlRd(layer):
    colorRamp = getGradientColorRampRdYlGn()
    shader = mkQuantileShaderFromColorRamp(layer,colorRamp)
    setSBPCRasterRenderer(layer,shader)
# SBPC = Single Band Pseudo Color - continuous
def setRendererSBPCGnYlRdCont(layer):
    colorRamp = getGradientColorRampRdYlGn()
    shader = mkRasterShader(layer,colorRamp)
    setSBPCRasterRenderer(layer,shader)
    
def mkRendererPalettedGnYlRd(layer):
    pr = layer.dataProvider()
    # colorRamp = getColorBrewColorRampGnYlRd()
    # colorRamp = getPresetGnYlRd()
    # colorRamp = QgsGradientColorRamp(color1=redCol,color2=greenCol)
    # colorRamp = QgsCptCityColorRamp(schemeName='cb/div/GnYlRd_',variantName='11')
    colorRamp = getGradientColorRampRdYlGn()
    classData = QgsPalettedRasterRenderer.classDataFromRaster(pr,1,ramp=colorRamp)
    renderer = QgsPalettedRasterRenderer(pr,1,classes=classData)
    return renderer
        
def setRendererPalettedGnYlRd(layer):
    renderer = mkRendererPalettedGnYlRd(layer)
    setRenderer(layer,renderer)
    
def setLightingQuantileStyle(layer):
    utils.info("setLightingQuantileStyle")
    colorRamp = mkColorRamp('Inferno')
    if not colorRamp:
        assert(False)
    shader = mkQuantileShaderFromColorRamp(layer,colorRamp)
    if not shader:
        assert(False)
    setSBPCRasterRenderer(layer,shader)
    
# def mkColorRampShaderPalettedGnYlRd(valueList,colorList):
    # lst =  []
    # for v, c in zip(valueList,colorList):
        # item = QgsColorRampShader.ColorRampItem(v,c)
        # lst.append(item)
    # colorRampShader = QgsColorRampShader()
    # colorRampShader.setColorRampItemList(lst)
    # return colorRampShader