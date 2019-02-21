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
    Proxy functions to call usual processing algorithms.
"""

from qgis.core import (QgsProcessingFeedback,
                       QgsProject,
                       QgsProperty,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsField,
                       QgsProcessingContext,
                       QgsExpression)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QGuiApplication
import gdal

import os.path
import sys
import subprocess
import time

import processing

from . import utils, qgsUtils, feedbacks

nodata_val = '-9999'

gdal_calc_cmd = None
gdal_merge_cmd = None
gdal_rasterize_cmd = None
gdal_warp_cmd = None

def initGdalCommands():
    global gdal_calc_cmd, gdal_merge_cmd, gdal_rasterize_cmd, gdal_warp_cmd
    if utils.platform_sys == 'Windows':
        gdal_calc_cmd = 'gdal_calc.bat'
        gdal_merge_cmd = 'gdal_merge.bat'
        gdal_rasterize_cmd = 'gdal_rasterize'
        gdal_warp_cmd = 'gdalwarp'
    elif utils.platform_sys == 'Linux':
        gdal_calc_cmd = 'gdal_calc.py'
        gdal_merge_cmd = 'gdal_merge.py'
        gdal_rasterize_cmd = 'gdal_rasterize'
        gdal_warp_cmd = 'gdalwarp'
    elif utils.platform_sys == 'Darwin':
        gdal_path = '/Library/Frameworks/GDAL.framework'
        gdal_calc_cmd = 'gdal_calc.py'
        gdal_rasterize_cmd = 'gdal_rasterize'
        gdal_warp_cmd = 'gdalwarp'
        gdal_merge_cmd = 'gdal_merge.py'
        if not os.path.isfile(gdal_calc_cmd):
            gdal_calc_cmd = utils.findFileFromDir(gdal_path,'gdal_calc.py')
        if not os.path.isfile(gdal_merge_cmd):
            gdal_merge_cmd = utils.findFileFromDir(gdal_path,'gdal_merge.py')
        if not os.path.isfile(gdal_rasterize_cmd):
            gdal_rasterize_cmd = utils.findFileFromDir(gdal_path,'gdal_rasterize')
        if not os.path.isfile(gdal_warp_cmd):
            gdal_warp_cmd = utils.findFileFromDir(gdal_path,'gdalwarp')
    else:
        utils.internal_error("Unexpected system : " + str(utils.platform_sys))
    if utils.platform_sys in ['Linux','Darwin']:
        if os.path.isfile(gdal_calc_cmd):
            utils.debug("gdal_calc command set to " + str(gdal_calc_cmd))
        else:
            utils.user_error("Could not find gdal_calc command")
        if os.path.isfile(gdal_merge_cmd):
            utils.debug("gdal_merge command set to " + str(gdal_merge_cmd))
        else:
            utils.user_error("Could not find gdal_merge command")
        if os.path.isfile(gdal_rasterize_cmd):
            utils.debug("gdal_rasterize command set to " + str(gdal_rasterize_cmd))
        else:
            utils.user_error("Could not find gdal_rasterize command")
        if os.path.isfile(gdal_warp_cmd):
            utils.debug("gdalwarp command set to " + str(gdal_warp_cmd))
        else:
            utils.user_error("Could not find gdalwarp command")
        
def applyProcessingAlg(provider,alg_name,parameters,context=None,feedback=None,onlyOutput=True):
    # Dummy function to enable running an alg inside an alg
    def no_post_process(alg, context, feedback):
        pass
    if feedback is None:
        feedback = feedbacks.progressFeedback
    utils.debug("parameters : " + str(parameters))
    feedback.pushDebugInfo("parameters : " + str(parameters))
    QGuiApplication.processEvents()
    try:
        complete_name = provider + ":" + alg_name
        feedback.pushInfo("Calling processing algorithm '" + complete_name + "'")
        start_time = time.time()
        utils.debug("context = " + str(context))
        if context is None:
            context = QgsProcessingContext()
            context.setFeedback(feedback)
        res = processing.run(complete_name,parameters,context=context,feedback=feedback,onFinish=no_post_process)
        feedback.pushDebugInfo("res1 = " + str(res))
        end_time = time.time()
        diff_time = end_time - start_time
        feedback.pushInfo("Call to " + alg_name + " successful"
                    + ", performed in " + str(diff_time) + " seconds")
        feedbacks.progressFeedback.endJob()
        feedback.pushDebugInfo("res = " + str(res))
        if onlyOutput:
            if "OUTPUT" in res:
                feedback.pushDebugInfo("output = " + str(res["OUTPUT"]))
                feedback.pushDebugInfo("output type = " + str(type(res["OUTPUT"])))
                return res["OUTPUT"]
            else:
                return None
        else:
            return res
    except Exception as e:
        utils.warn ("Failed to call " + alg_name + " : " + str(e))
        raise e
    finally:  
        feedback.pushDebugInfo("End run " + alg_name)

def applyGrassAlg(parameters,alg_name):
    applyProcessingAlg("grass7",alg_name,parameters)

def selectGeomByExpression(in_layer,expr,out_path,out_name):
    #utils.info("Calling 'selectGeomByExpression' algorithm")
    start_time = time.time()
    qgsUtils.removeVectorLayer(out_path)
    out_layer = qgsUtils.createLayerFromExisting(in_layer,out_name)
    orig_field = QgsField("Origin", QVariant.String)
    out_layer.dataProvider().addAttributes([orig_field])
    out_layer.updateFields()
    fields = out_layer.fields()
    out_provider = out_layer.dataProvider()
    in_name = in_layer.name()
    if expr:
        feats = in_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr))
    else:
        feats = in_layer.getFeatures(QgsFeatureRequest())
    for f in feats:
        geom = f.geometry()
        new_f = QgsFeature(fields)
        new_f.setGeometry(geom)
        new_f["Origin"] = in_layer.name()
        res = out_provider.addFeature(new_f)
        if not res:
            internal_error("addFeature failed")
    out_layer.updateExtents()
    qgsUtils.writeVectorLayer(out_layer,out_path)
    end_time = time.time()
    diff_time = end_time - start_time
    #utils.info("Call to 'selectGeomByExpression' successful"
    #           + ", performed in " + str(diff_time) + " seconds")
    
def joinToReportingLayer(init_layer,reporting_layer_path,out_name):
    init_pr = init_layer.dataProvider()
    out_layer = qgsUtils.createLayerFromExisting(in_layer,out_name)
    
        
def extractByExpression(in_layer,expr,out_layer,context=None,feedback=None):
    #utils.checkFileExists(in_layer)
    #if out_layer:
    #    qgsUtils.removeVectorLayer(out_layer)
    parameters = { 'EXPRESSION' : expr,
                   'INPUT' : in_layer,
                   'OUTPUT' : out_layer }
    res = applyProcessingAlg("native","extractbyexpression",parameters,context=context,feedback=feedback)
    return res
    
def selectByExpression(in_layer,expr,context=None,feedback=None):
    parameters = { 'EXPRESSION' : expr,
                   'INPUT' : in_layer,
                   'METHOD' : 0 }
    res = applyProcessingAlg("qgis","selectbyexpression",parameters,context=context,feedback=feedback)
    return res
    
def saveSelectedAttributes(in_layer,out_layer,context=None,feedback=None):
    parameters = { 'INPUT' : in_layer,
                   'OUTPUT' : out_layer }
    res = applyProcessingAlg("native","saveselectedfeatures",parameters,context=context,feedback=feedback)
    return res
    
def cloneLayer(layer):
    layer.selectAll()
    clone_layer = saveSelectedAttributes(layer,'memory:')
    return clone_layer
                   
def multiToSingleGeom(in_layer,out_layer,context=None,feedback=None):
    feedbacks.progressFeedback.setSubText("Multi to single geometry")
    parameters = { 'INPUT' : in_layer,
                   'OUTPUT' : out_layer }
    res = applyProcessingAlg("native","multiparttosingleparts",parameters,context=context,feedback=feedback)
    return res
    
def dissolveLayer(in_layer,out_layer,context=None,feedback=None):
    #utils.checkFileExists(in_layer)
    feedbacks.progressFeedback.setSubText("Dissolve " + str(in_layer))
    #if out_layer:
    #    qgsUtils.removeVectorLayer(out_layer)
    parameters = { 'FIELD' : [],
                   'INPUT' : in_layer,
                   'OUTPUT' : out_layer }
    if feedback:
        feedback.pushInfo("parameters = " + str(parameters))
    res = applyProcessingAlg("native","dissolve",parameters,context,feedback)
    return res
    
def applyBufferFromExpr(in_layer,expr,out_layer,context=None,feedback=None):
    #utils.checkFileExists(in_layer)
    feedbacks.progressFeedback.setSubText("Buffer (" + str(expr) + ") on " + str(out_layer))
    #if out_layer:
    #    qgsUtils.removeVectorLayer(out_layer)
    parameters = { 'DISSOLVE' : False,
                   #'DISTANCE' : QgsProperty.fromExpression(expr),
                   'DISTANCE' : expr,
                   'INPUT' : in_layer,
                   'OUTPUT' : out_layer,
                   'END_CAP_STYLE' : 0,
                   'JOIN_STYLE' : 0,
                   'MITER_LIMIT' : 2,
                   'SEGMENTS' : 5 }
    res = applyProcessingAlg("native","buffer",parameters,context,feedback)
    return res
    
def mergeVectorLayers(in_layers,crs,out_layer,context=None,feedback=None):
    feedbacks.progressFeedback.setSubText("Merge vector layers")
    parameters = { 'CRS' : crs,
                   'LAYERS' : in_layers,
                   'OUTPUT' : out_layer }
    res = applyProcessingAlg("native","mergevectorlayers",parameters,context,feedback)
    return res
                   
    
def applyDifference(in_layer,diff_layer,out_layer,context=None,feedback=None):
    feedbacks.progressFeedback.setSubText("Difference")
    parameters = { 'INPUT' : in_layer,
                   'OUTPUT' : out_layer,
                   'OVERLAY' : diff_layer }
    res = applyProcessingAlg("native","difference",parameters,context=context,feedback=feedback)
    return res  
    
def applyVectorClip(in_layer,clip_layer,out_layer,context=None,feedback=None):
    feedbacks.progressFeedback.setSubText("Clip")
    parameters = { 'INPUT' : in_layer,
                   'OUTPUT' : out_layer,
                   'OVERLAY' : clip_layer }
    res = applyProcessingAlg("qgis","clip",parameters,context,feedback)
    return res
    
def applyReprojectLayer(in_layer,target_crs,out_layer,context=None,feedback=None):
    feedbacks.progressFeedback.setSubText("Reproject")
    parameters = { 'INPUT' : in_layer,
                   'OUTPUT' : out_layer,
                   'TARGET_CRS' : target_crs }
    res = applyProcessingAlg("native","reprojectlayer",parameters,context,feedback)
    return res
    
    
# Apply rasterization on field 'field' of vector layer 'in_path'.
# Output raster layer in 'out_path'.
# Resolution set to 25 if not given.
# Extent can be given through 'extent_path'. If not, it is extracted from input layer.
# Output raster layer is loaded in QGIS if 'load_flag' is True.
def applyRasterization(in_path,field,out_path,resolution=None,
                       extent_path=None,load_flag=False,to_byte=False,
                       more_args=[]):
    utils.debug("applyRasterization")
    in_layer = qgsUtils.loadVectorLayer(in_path)
    if extent_path:
        extent_layer = qgsUtils.loadLayer(extent_path)
    else:
        extent_layer = qgsUtils.loadVectorLayer(in_path)
    extent = extent_layer.extent()
    #extent_crs = qgsUtils.getLayerCrsStr(extent_layer)
    extent_crs = extent_layer.crs()
    utils.internal_error("TODO : params refactoring needed")
    #transformed_extent = params.params.getBoundingBox(extent,extent_crs)
    x_min = transformed_extent.xMinimum()
    x_max = transformed_extent.xMaximum()
    y_min = transformed_extent.yMinimum()
    y_max = transformed_extent.yMaximum()
    utils.debug("resolution  = " + str(resolution))
    if resolution == 0.0:
        utils.user_error("Empty resolution")
    parameters = [gdal_rasterize_cmd,
                  '-at',
                  '-te',str(x_min),str(y_min),str(x_max),str(y_max),
                  #'-ts', str(width), str(height),
                  '-tr', str(resolution), str(resolution),
                  #'-ot','Int32',
                  #'-a_srs','epsg:2154',
                  '-of','GTiff']
                  #'-a_nodata',nodata_val]
    if to_byte:
        parameters += ['-ot', 'Int16','-a_nodata',nodata_val]
    if field == "geom":
        parameters += ['-burn', '1']
    else:
        parameters += ['-a',field]
    parameters += more_args
    parameters += [in_path,out_path]
    utils.debug("rasteization cmd = " + str(parameters))
    p = subprocess.Popen(parameters,stderr=subprocess.PIPE)
    out,err = p.communicate()
    utils.debug(str(p.args))
    if out:
        utils.info(str(out))
    if err:
        utils.user_error(str(err))
    elif load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
        

# Apply raster calculator from expression 'expr'.
# Calculation is made on a single file and a signled band renamed 'A'.
# Output format is Integer32.
def applyResampleProcessing(in_path,out_path):
    utils.debug("qgsTreatments.applyResampleProcessing")
    parameters = {'input' : in_path,
                   'output' : out_path,
                   '--overwrite' : True,
                   'GRASS_REGION_CELLSIZE_PARAMETER' : 50,
                   'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                   'GRASS_MIN_AREA_PARAMETER' : 0}
    feedback = QgsProcessingFeedback()
    try:
        processing.run("grass7:r.resample",parameters,feedback=feedback)
        utils.debug ("call to r.cost successful")
    except Exception as e:
        utils.warn ("Failed to call r.reclass : " + str(e))
        raise e
    finally:
        utils.debug("End resample")
        
# TODO
def applyWarpGdal(in_path,out_path,resampling_mode,
                  crs=None,resolution=None,extent_path=None,
                  load_flag=False,to_byte=False):
    utils.debug("qgsTreatments.applyWarpGdal")
    in_layer = qgsUtils.loadRasterLayer(in_path)
    if extent_path:
        utils.debug("extent_path = " + str(extent_path))
        extent_layer = qgsUtils.loadLayer(extent_path)
    else:
        extent_layer = in_layer
    extent = extent_layer.extent()
    extent_crs = extent_layer.crs()
    utils.internal_error("TODO : params refactoring")
    transformed_extent = params.params.getBoundingBox(extent,extent_crs)
    x_min = transformed_extent.xMinimum()
    x_max = transformed_extent.xMaximum()
    y_min = transformed_extent.yMinimum()
    y_max = transformed_extent.yMaximum()
    #x_min = extent.xMinimum()
    #x_max = extent.xMaximum()
    #y_min = extent.yMinimum()
    #y_max = extent.yMaximum()
    if not resolution:
        resolution = in_layer.rasterUnitsPerPixelX()
        utils.warn("Setting rasterization resolution to " + str(resolution))
    #width = int((x_max - x_min) / float(resolution))
    #height = int((y_max - y_min) / float(resolution))
    in_crs = qgsUtils.getLayerCrsStr(in_layer)
    extent_crs = qgsUtils.getLayerCrsStr(extent_layer)
    cmd_args = [gdal_warp_cmd,
                '-s_srs',in_crs,
                '-t_srs',crs.authid(),
                '-te',str(x_min),str(y_min),str(x_max),str(y_max),
                #'-te_srs',extent_crs,
                #'-ts', str(width), str(height),
                '-tr', str(resolution), str(resolution),
                #'-dstnodata',nodata_val,
                #'-ot','Int16',
                '-overwrite']
    if resampling_mode:
        cmd_args += ['-r',resampling_mode]
    if to_byte:
        cmd_args += ['-dstnodata',nodata_val]
        cmd_args += ['-ot','Int16']
    #cmd_args += more_args
    cmd_args += [in_path, out_path]
    utils.executeCmd(cmd_args)
    if load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
        
# TO TEST
def applyReclassProcessing(in_path,out_path,rules_file,title):
    parameters = {'input' : in_path,
                  'output' : out_path,
                  'rules' : rules_file,
                  'title' : title,
                   'GRASS_REGION_CELLSIZE_PARAMETER' : 50,
                   'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                   'GRASS_MIN_AREA_PARAMETER' : 0}
    feedback = QgsProcessingFeedback()
    try:
        processing.run("grass7:r.reclass",parameters,feedback=feedback)
        utils.debug ("call to r.cost successful")
    except Exception as e:
        utils.warn ("Failed to call r.reclass : " + str(e))
        raise e
    finally:
        utils.debug("End reclass")
        
# Apply raster calculator from expression 'expr'.
# Calculation is made on a single file and a signled band renamed 'A'.
# Output format is Integer32.
def applyGdalCalc(in_path,out_path,expr,load_flag=False,more_args=[]):
    global gdal_calc_cmd
    utils.debug("qgsTreatments.applyGdalCalc(" + str(expr) + ")")
    if os.path.isfile(out_path):
        qgsUtils.removeRaster(out_path)
    #cmd_args = ['gdal_calc.bat',
    utils.debug("gdal_calc commnad = " + str(gdal_calc_cmd))
    cmd_args = [gdal_calc_cmd,
                '-A', in_path,
                '--type=Int32',
                '--outfile='+out_path,
                '--NoDataValue='+nodata_val,
                '--overwrite']
    cmd_args += more_args
    expr_opt = '--calc=' + expr
    cmd_args.append(expr_opt)
    utils.executeCmd(cmd_args)
    if load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
        
# Filters input raster 'in_path' to keep values inferior to 'max_val' 
# in output raster 'out_path'.
def applyFilterGdalFromMaxVal(in_path,out_path,max_val,load_flag=False):
    utils.debug("qgsTreatments.applyReclassGdalFromMaxVal(" + str(max_val) + ")")
    expr = ('(A*less_equal(A,' + str(max_val) + ')*less_equal(0,A))'
        + '+(' + str(nodata_val) + '*less(' + str(max_val) + ',A))'
        + '+(' + str(nodata_val) + '*less(A,0))')
    applyGdalCalc(in_path,out_path,expr,load_flag,more_args=['--type=Float32'])
    # utils.executeCmdAsScript(cmd_args)
    # res_layer = qgsUtils.loadRasterLayer(out_path)
    # QgsProject.instance().addMapLayer(res_layer)
    
# Applies reclassification from 'in_path' to 'out_path' according to 'reclass_dict'.
# Dictionary contains associations of type {old_val -> new_val}.
# Pixels of value 'old_val' are set to 'new_val' value.
def applyReclassGdalFromDict(in_path,out_path,reclass_dict,load_flag=False):
    utils.debug("qgsTreatments.applyReclassGdalFromDict(" + str(reclass_dict) + ")")
    expr = ''
    for old_cls,new_cls in reclass_dict.items():
        if expr != '':
            expr += '+'
        expr += str(new_cls) + '*(A==' + str(old_cls)+ ')'
    applyGdalCalc(in_path,out_path,expr,load_flag)
    # cmd_args.append(expr)
    # utils.executeCmd(cmd_args)
    # res_layer = qgsUtils.loadRasterLayer(out_path)
    # QgsProject.instance().addMapLayer(res_layer)
    
def applyGdalCalcAB_ANull(in_path1,in_path2,out_path,expr,load_flag=False):
    utils.debug("qgsTreatments.applyGdalCalcAB")
    if os.path.isfile(out_path):
        qgsUtils.removeRaster(out_path)
    cmd_args = [gdal_calc_cmd,
                '-A', in_path1,
                '-B', in_path2,
                #'--type=Int32',
                '--NoDataValue='+nodata_val,
                '--overwrite',
                '--outfile='+out_path]
    expr_opt = '--calc=' + str(expr)
    cmd_args.append(expr_opt)
    utils.executeCmd(cmd_args)
    if load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
    
# Creates raster 'out_path' from 'in_path1', 'in_path2' and 'expr'.
def applyGdalCalcAB(in_path1,in_path2,out_path,expr,load_flag=False):
    utils.debug("qgsTreatments.applyGdalCalcAB")
    if os.path.isfile(out_path):
        qgsUtils.removeRaster(out_path)
    tmp_no_data_val = -1
    nonull_p1 = utils.mkTmpPath(in_path1,suffix="_nonull")
    nonull_p2 = utils.mkTmpPath(in_path2,suffix="_nonull")
    nonull_out = utils.mkTmpPath(out_path,suffix="_nonull")
    nonull_out_tmp = utils.mkTmpPath(nonull_out,suffix="_tmp")
    applyRNull(in_path1,tmp_no_data_val,nonull_p1)
    applyRNull(in_path2,tmp_no_data_val,nonull_p2)
    cmd_args = [gdal_calc_cmd,
                '-A', nonull_p1,
                '-B', nonull_p2,
                #'--type=Int32',
                '--NoDataValue='+nodata_val,
                '--overwrite',
                '--outfile='+nonull_out]
    expr_opt = '--calc=' + str(expr)
    cmd_args.append(expr_opt)
    utils.executeCmd(cmd_args)
    reset_nodata_expr = '(A==' + str(tmp_no_data_val) + ')*' + str(nodata_val)
    reset_nodata_expr += '+(A!=' + str(tmp_no_data_val) + ')*A'
    applyGdalCalc(nonull_out,nonull_out_tmp,reset_nodata_expr)
    applyRSetNull(nonull_out_tmp,nodata_val,out_path)
    remove_tmp_flag = not utils.debug_flag
    if remove_tmp_flag:
        qgsUtils.removeRaster(nonull_p1)
        qgsUtils.removeRaster(nonull_p2)
        qgsUtils.removeRaster(nonull_out)
        qgsUtils.removeRaster(nonull_out_tmp)
    if load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
    
# Applies ponderation on 'in_path1' according to 'in_path2' values.
# Result stored in 'out_path'.
def applyPonderationGdal(a_path,b_path,out_path,pos_values=False):
    utils.debug("qgsTreatments.applyPonderationGdal")
    if os.path.isfile(out_path):
        qgsUtils.removeRaster(out_path)
    cmd_args = [gdal_calc_cmd,
                '-A', a_path,
                '-B', b_path,
                #'--type=Int32',
                '--NoDataValue='+nodata_val,
                '--overwrite',
                '--outfile='+out_path]
    if pos_values:
        expr_opt = '--calc=A*B*less_equal(0,A)*less_equal(0,B)'
    else:
        expr_opt = '--calc=A*B'
    cmd_args.append(expr_opt)
    utils.executeCmd(cmd_args)
    res_layer = qgsUtils.loadRasterLayer(out_path)
    QgsProject.instance().addMapLayer(res_layer)
    
# Creates raster 'out_path' keeping maximum value from 'in_path1' and 'in_path2'.
def applyMaxGdal(in_path1,in_path2,out_path,load_flag=False):
    utils.debug("qgsTreatments.applyMaxGdal")
    expr = 'B*less_equal(A,B) + A*less(B,A)'
    applyGdalCalcAB(in_path1,in_path2,out_path,expr,load_flag)
    
# Creates raster 'out_path' keeping maximum value from 'in_path1' and 'in_path2'.
def applyMinGdal(in_path1,in_path2,out_path,load_flag=False):
    utils.debug("qgsTreatments.applyMinGdal")
    expr = 'A*less_equal(A,B) + B*less(B,A)'
    applyGdalCalcAB(in_path1,in_path2,out_path,expr,load_flag)
    
def applyRNull(in_path,new_val,out_path):
    utils.debug("applyRNull")
    parameters = { 'map' : in_path,
                   'null' : str(new_val),
                   'output' : out_path }
    applyGrassAlg(parameters,"r.null")
    
def applyRSetNull(in_path,new_val,out_path):
    utils.debug("applyRNull")
    parameters = { 'map' : in_path,
                   'setnull' : str(new_val),
                   'output' : out_path }
    applyGrassAlg(parameters,"r.null")
        
def applyRBuffer(in_path,buffer_vals,out_path):
    utils.debug ("applyRBuffer")
    utils.checkFileExists(in_path,"Buffer input layer ")
    distances_str = ""
    for v in buffer_vals:
        if distances_str != "":
            distances_str += ","
        distances_str += str(v)
    parameters = { 'input' : in_path,
                    'output' : out_path,
                    'distances' : distances_str, #"0,100,200",
                    'units' : 0, # 0 = meters ?
                    #'memory' : 5000,
                    'GRASS_RASTER_FORMAT_META' : '',
                    'GRASS_RASTER_FORMAT_OPT' : '',
                    'GRASS_REGION_CELLSIZE_PARAMETER' : 25,
                    'GRASS_REGION_PARAMETER' : None,
                    '-z' : False,
                    '--type' : 'Int32',
                    '--overwrite' : False}
    applyGrassAlg(parameters,"r.buffer.lowmem")
    # feedback = QgsProcessingFeedback()
    # utils.debug("parameters : " + str(parameters))
    # try:
        # res = processing.run("grass7:r.buffer.lowmem",parameters,feedback=feedback)
        # print(str(feedback))
        # print(str(res["output"]))
        # print ("call to r.buffer successful")
    # except Exception as e:
        # print ("Failed to call r.buffer : " + str(e))
        # raise e
    # finally:  
        # utils.debug("End runBuffer")
        
def applyRCost(start_path,cost_path,cost,out_path):
    utils.debug ("applyRCost")
    utils.checkFileExists(start_path,"Dispersion Start Layer ")
    utils.checkFileExists(cost_path,"Dispersion Permeability Raster ")
    parameters = { 'input' : cost_path,
                    'start_raster' : start_path,
                    'maxcost' : int(cost),
                    'null_cost' : None,
                    'output' : out_path,
                    'start_points' : None,
                    'stop_points' : None,
                    'start_coordinates' : None,
                    'stop_coordinates' : None,
                    'outir' : None,
                    'memory' : 5000,
                    'GRASS_MIN_AREA_PARAMETER' : 0.0001, 
                    'GRASS_RASTER_FORMAT_META' : '',
                    'GRASS_RASTER_FORMAT_OPT' : '',
                    'GRASS_REGION_CELLSIZE_PARAMETER' : 0,
                    'GRASS_REGION_PARAMETER' : None,
                    'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                    '-k' : False,
                    '-n' : True,
                    '-r' : True,
                    '-i' : False,
                    '-b' : False,
                    '--overwrite' : True}
    applyGrassAlg(parameters,"r.cost")
    #feedback = QgsProcessingFeedback()
    #utils.debug("parameters : " + str(parameters))
    #try:
    #    processing.run("grass7:r.cost",parameters,feedback=feedback)
    #    utils.info ("call to r.cost successful")
        #res_layer = qgsUtils.loadRasterLayer(out_path)
        #QgsProject.instance().addMapLayer(res_layer)
    #except Exception as e:
    #    utils.info ("Failed to call r.cost : " + str(e))
    #    raise e
    #finally:  
    #    utils.debug("End runCost")
        
        
def applyGdalMerge(files,out_path,load_flag=False):
    cmd_args = [gdal_merge_cmd,
                '-o', out_path,
                '-of', 'GTiff',
                '-ot','Int32',
                '-n', nodata_val,
                '-a_nodata', nodata_val]
    cmd_args += files
    utils.executeCmd(cmd_args)
    if load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
        
