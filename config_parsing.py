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
    Minimal module to parse configuration from XML files.
    See plugins BioDispersal and FragScape for use cases.
"""

from . import utils

import xml.etree.ElementTree as ET

config_parsers = None

def setConfigParsers(parsers):
    global config_parsers
    config_parsers = parsers

def getParserByName(name):
    for parser in config_parsers:
        if parser.parser_name == name:
            return parser
    utils.internal_error("No parser named " + str(name))

def parseConfig(config_file,feedback=None):
    feedback.pushInfo("Parsing configuration from file '" + str(config_file) + "'")
    tree = ET.parse(config_file)
    root = tree.getroot()
    for parser in root:
        parseModel(parser,feedback=feedback)
    feedback.pushInfo("Configuration parsing successful")

# Parse model from XML root.
# Updates parsers stored in 'config_parsers'.
def parseModel(parser_root,feedback=None):
    global config_parsers, mk_item
    parser_tag = parser_root.tag
    feedback.pushDebugInfo("parse " + str(parser_tag))
    feedback.pushDebugInfo("config_parsers " + str([cf.__class__.__name__ for cf in config_parsers]))
    parser = getParserByName(parser_tag)
    parser.updateFromXML(parser_root,feedback=feedback)
        