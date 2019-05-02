
from qgis.core import (QgsColorRampShader,
                       QgsColorRampShader,
                       QgsColorBrewerColorRamp,
                       QgsRasterBandStats,
                       QgsPalettedRasterRenderer)

    
def getColorBrewColorRampGnYlRd():
    colorRamp = QgsColorBrewerColorRamp(schemeName='RdYlGn',inverted=True)
    return colorRamp
    
def getValuesFromLayer3(layer):
    pr = layer.dataProvider()
    stats = provider.bandStatistics(1,stats=QgsRasterBandStats.All)
    if (stats.minimumValue < 0):
        min = 0
    else:
        min= stats.minimumValue
    max = stats.maximumValue
    range = max - min
    half_range = range//2
    med = min + half_range
    return (min,med,max)
    
def mkRendererPalettedGnYlRd(layer):
    pr = layer.dataProvider()
    colorRamp = getColorBrewColorRampGnYlRd()
    classData = QgsPalettedRasterRenderer.classDataFromRaster(pr,1,ramp=colorRamp)
    renderer = QgsPalettedRasterRenderer(pr,1,classes=classData)
    return renderer
    
def setRendererPalettedGnYlRd(layer):
    renderer = mkRendererPalettedGnYlRd(layer)
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