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

from functools import partial
from contextlib import closing
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI

import connection as conapi

from actions import ListAction, miejscowosci
from constants import STANOWISKA_TYP, MIEJSCOWOSI_TYP
from c2 import DataSource, Entity

class StanowiskaDs(DataSource):

    def __init__(self, etype, qgsLayer):
        self.etype = etype
        self.layer = qgsLayer

    def getAll(self, expression=None):
        return [Entity(self.etype, id=x, obszar='00-01', nr_azp=str(x)) for x in range(0,10)]

class WykazDs(DataSource):

    def __init__(self, etype, qgsLayer, context):
        self.etype = etype
        self.layer = qgsLayer
        self.context = context

    def _connection(self):
        provider = self.layer.dataProvider()
        uri = QgsDataSourceURI(provider.dataSourceUri())
        factory = self.context.service(conapi.CONNECTION_FACTORY_CLAZZ, variant=str(provider.name()).upper())
        return factory.createConnection(uri)

    def _maxId(self, con):
        stmt = 'select coalesce(max(id) + 1, 1) from %s' % self.etype.name
        row = con.single(stmt)
        return row[0]

    def getAll(self, expression=None):
        def convert(row):
            return Entity(self.etype, id=row[0], nazwa=row[1])
        with closing(self._connection()) as con:
            return con.query(expression, [], convert)

    def create(self, entities):
        stmt = 'insert into %s(id, nazwa, start) ' \
               'values(:wid, :wnazwa, substr(:wnazwa, 1, 2))' % self.etype.name
        with closing(self._connection()) as con:
            ps = con.prepare(stmt)
            nextId = self._maxId(con)
            for e in entities:
                ps.execute(params = {
                        'wid' : nextId,
                        'wnazwa': e['nazwa']
                    }
                )
                nextId += 1
            con.commit()

def getName():
    return 'Stanowiska'

def initDataSource(etype, qgsLayer):
    return StanowiskaDs(etype, qgsLayer)

def wykazDs(etype, qgsLayer, context):
    return WykazDs(etype, qgsLayer, context)

def start(context):
    subMenu = context.menu.addMenu(getName())
    subMenu.addAction(ListAction(context))
    subMenu.addAction(miejscowosci(context))
    reg = QgsMapLayerRegistry.instance()
    allLayers = reg.mapLayersByName('stanowiska')
    for mapLayer in allLayers:
        layerId = mapLayer.id()
        context.dataSourceFactory(partial(initDataSource, qgsLayer=mapLayer), STANOWISKA_TYP, variant=layerId)
        context.dataSourceFactory(partial(wykazDs, qgsLayer=mapLayer, context=context), MIEJSCOWOSI_TYP, variant=layerId)
