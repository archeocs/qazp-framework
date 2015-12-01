# -*- coding: utf-8 -*-

# qazp_20
# (c) Milosz Piglas 2014 Wszystkie prawa zastrzezone

# Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
# 
#      * Redistributions of source code must retain the above copyright
#  notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above
#  copyright notice, this list of conditions and the following disclaimer
#  in the documentation and/or other materials provided with the
#  distribution.
#      * Neither the name of qazp_20 nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
# 
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsVectorLayer
from c2 import DataSource

def findLayerUris(layerName):
    reg = QgsMapLayerRegistry.instance()
    allLayers = reg.mapLayersByName(layerName)
    return [QgsDataSourceURI(a.dataProvider().dataSourceUri())
            for a in allLayers if isinstance(a, QgsVectorLayer)]

def getLayerByUri(layerName, uri):
    reg = QgsMapLayerRegistry.instance()
    allLayers = reg.mapLayersByName(layerName)
    for a in allLayers:
        dsUri = QgsDataSourceURI(a.dataProvider().dataSourceUri())
        if dsUri.uri() == uri:
            return a
    return None

class QgisDataSource(DataSource):

    def __init__(self, layerName):
        self.layer = layerName


    # jak obslugiwać update i delete, ktore musza tez dzialac na jakies warstwie ???

    def getAll(self, expression=None):
        uri = QgsDataSourceURI(expression)
        if uri.table() != self.layer:
            raise Exception('Invalid expression %s. Expected table %s but got %s'%(expression, self.layer, uri.table))
        qgsLayer = getLayerByUri(self.layer, uri.uri())
        if not qgsLayer:
            raise Exception('Layer with uri %s not found'%QgsDataSourceURI.removePassword(uri.uri()))
