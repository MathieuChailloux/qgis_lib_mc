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
                       QgsColorRampShader,
                       QgsColorBrewerColorRamp,
                       QgsGradientColorRamp,
                       QgsCptCityColorRamp,
                       QgsPresetSchemeColorRamp,
                       QgsRasterBandStats,
                       QgsPalettedRasterRenderer,
                       QgsSingleBandPseudoColorRenderer,
                       QgsStyle)
                       
from . import utils

redHex = '#ff0000'
yellowHex = '#ffff00'
greenHex = '#00ff00'
redCol = QColor(redHex)
yellowCol = QColor(yellowHex)
greenCol = QColor(greenHex)

singleColorRampList = [ 'Blues', 'Greens', 'Greys', 'Oranges', 'Purples', 'Reds' ]

def getDefaultStyle():
    return QgsStyle.defaultStyle()
    
def getPresetGnYlRd():
    colors = [redCol,yellowCol,greenCol]
    colorRamp = QgsPresetSchemeColorRamp(colors=colors)
    return colorRamp
    
def getColorBrewColorRampGnYlRd():
    colorRamp = QgsColorBrewerColorRamp(schemeName='RdYlGn',inverted=True)
    return colorRamp
    
def getGradientColorRampRdYlGn():
    style = getDefaultStyle()
    colorRamp = style.colorRamp('RdYlGn')
    colorRamp.invert()
    return colorRamp
    
def getRandomSingleColorRamp():
    rampName = random.choice(singleColorRampList)
    style = getDefaultStyle()
    colorRamp = style.colorRamp(rampName)
    colorRamp.invert()
    return colorRamp    
    
def getValuesFromLayer3(layer):
    pr = layer.dataProvider()
    stats = pr.bandStatistics(1,stats=QgsRasterBandStats.All)
    if (stats.minimumValue < 0):
        min = 0
    else:
        min= stats.minimumValue
    max = stats.maximumValue
    range = max - min
    half_range = range//2
    med = min + half_range
    return (min,med,max)
    
def mkRandomColorRasterShader(layer):
    min, med, max = getValuesFromLayer3(layer)
    rasterShader = QgsRasterShader(minimumValue=min,maximumValue=max)
    colorRamp = getRandomSingleColorRamp()
    if not colorRamp:
        utils.internal_error("Could not create color ramp")        
    colorRampShader = QgsColorRampShader(minimumValue=min,maximumValue=max,colorRamp=colorRamp)
    colorRampShader.classifyColorRamp(band=1,input=layer.dataProvider())
    if colorRampShader.isEmpty():
        utils.internal_error("Empty color ramp shader")
    rasterShader.setRasterShaderFunction(colorRampShader)
    return rasterShader
    
def setRandomColorRasterRenderer(layer):
    rasterShader = mkRandomColorRasterShader(layer)
    if not rasterShader:
        utils.internal_error("Could not create raster shader")
    renderer = QgsSingleBandPseudoColorRenderer(input=layer.dataProvider(),band=1,shader=rasterShader)
    if not renderer:
        utils.internal_error("Could not create renderer")
    layer.setRenderer(renderer)
    layer.triggerRepaint()
    
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
    if not renderer:
        utils.internal_error("Could not create renderer")
    layer.setRenderer(renderer)
    layer.triggerRepaint()
    
    
    
# def mkColorRampShaderPalettedGnYlRd(valueList,colorList):
    # lst =  []
    # for v, c in zip(valueList,colorList):
        # item = QgsColorRampShader.ColorRampItem(v,c)
        # lst.append(item)
    # colorRampShader = QgsColorRampShader()
    # colorRampShader.setColorRampItemList(lst)
    # return colorRampShader