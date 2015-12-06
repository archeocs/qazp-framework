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

from PyQt4 import QtCore as qcore
from PyQt4 import QtGui as qgui

import c2

class EntityListModel(qcore.QAbstractTableModel):

    def __init__(self, etype, cache):
        qcore.QAbstractItemModel.__init__(self)
        self.etype = etype
        self.cache = cache
        self.attrNames = self.etype.getAttrNames()

    def _indexTuple(self, index):
        return index.row(), self.attrNames[index.column()]

    def data(self, index, role=None):
        if role != qcore.Qt.DisplayRole:
            return None
        objIndex = self._indexTuple(index)
        return self.cache.getByIndex(objIndex[0])[objIndex[1]]

    def headerData(self, column, orientation, role=None):
        if orientation == qcore.Qt.Horizontal and role == qcore.Qt.DisplayRole:
            return qcore.QString(self.attrNames[column])
        return None

    def rowCount(self, index=None, *args, **kwargs):
        size = self.cache.size()
        return size

    def columnCount(self, index=None, *args, **kwargs):
        return len(self.etype.attrs)

class EntityList(qgui.QWidget):

    def __init__(self, entityType, variant='default', queryExpr=None, parent=None):
        qgui.QWidget.__init__(self, parent)
        self.cache, self.coordinator, self.model, self.table = None, None, None, None
        self._type = entityType
        self._variant = variant
        self.queryExpr = queryExpr

    def initWidget(self, context):
        vlayout = qgui.QVBoxLayout()
        self.setLayout(vlayout)
        self.cache = c2.EntityCache(self._type)
        ds = context.prepareDataSource(self._type, variant=self._variant)
        self.coordinator = c2.CacheCoordinator(self.cache, ds)
        self.model = self._initModel()
        self.table = self._initTable(self.model)
        vlayout.addWidget(self.table)

    def initData(self, context):
        self.model.beginResetModel()
        self.coordinator.refresh(expression=self.queryExpr)
        self.model.endResetModel()

    def _initTable(self, model):
        table = qgui.QTableView(parent=self)
        table.setModel(model)
        return table

    def _initModel(self):
        return EntityListModel(self._type, self.cache)