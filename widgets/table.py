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
        self.cache.changeStart.connect(self._cacheChangeStart)
        self.cache.changeEnd.connect(self._cacheChangeEnd)
        self.cache.entityUpdated.connect(self._entityUpdated)

    def _indexTuple(self, index):
        return index.row(), self.attrNames[index.column()]

    def _cacheChangeStart(self, start, end, op):
        if op == 'I':
            self.beginInsertRows(qcore.QModelIndex(), start, end)
        elif op == 'R':
            self.beginRemoveRows(qcore.QModelIndex(), start, end)

    def _cacheChangeEnd(self, start, end, op):
        if op == 'I':
            self.endInsertRows()
        elif op == 'R':
            self.endRemoveRows()

    def _entityUpdated(self, index):
        cfirst = self.index(index, 0)
        clast = self.index(index, len(self.attrNames)-1)
        self.dataChanged.emit(cfirst, clast)

    def data(self, index, role=None):
        if role != qcore.Qt.DisplayRole:
            return None
        objIndex = self._indexTuple(index)
        return self.cache.getByIndex(objIndex[0])[objIndex[1]]

    def headerData(self, index, orientation, role=None):
        if role == qcore.Qt.DisplayRole:
            if orientation == qcore.Qt.Horizontal:
                return qcore.QString(self.attrNames[index])
            elif orientation == qcore.Qt.Vertical:
                state = self.cache.entityState(index)
                if state != c2.STATE_COMMITED:
                    return u'*'
                return u' '
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
        buttons = self.initActions()
        vlayout.addWidget(buttons)

    def getSelectedEntities(self):
        smodel = self.table.selectionModel()
        selection = smodel.selectedIndexes()
        return [self.cache.getByIndex(s.row()) for s in selection]

    def addAction(self):
        addDlg = EntityInputDialog(self._type)
        result = addDlg.exec_()
        if result == EntityInputDialog.Accepted:
            ent = addDlg.getEntity()
            self.cache.addEntities([ent])

    def saveAction(self):
        self.coordinator.save()
        self.initData(None)

    def deleteAction(self):
        for ent in  self.getSelectedEntities():
            self.cache.remove(ent.primaryKey)


    def editAction(self):
        selected = self.getSelectedEntities()
        if not selected:
            return
        first = selected[0]
        editDlg = EntityInputDialog(self._type, first)
        result = editDlg.exec_()
        if result == EntityInputDialog.Accepted:
            ent = editDlg.getEntity()
            self.cache.updateEntity(ent)

    def refreshAction(self):
        self.initData(None)

    def _performAction(self, btn):
        aname = str(btn.objectName())
        if hasattr(self, aname):
            getattr(self, aname)()

    def initActions(self):
        btnBar = qgui.QDialogButtonBox()
        addBtn = btnBar.addButton('Add', qgui.QDialogButtonBox.ActionRole)
        addBtn.setObjectName('addAction')
        addBtn = btnBar.addButton('Save', qgui.QDialogButtonBox.ActionRole)
        addBtn.setObjectName('saveAction')
        addBtn = btnBar.addButton('Delete', qgui.QDialogButtonBox.ActionRole)
        addBtn.setObjectName('deleteAction')
        addBtn = btnBar.addButton('Edit', qgui.QDialogButtonBox.ActionRole)
        addBtn.setObjectName('editAction')
        addBtn = btnBar.addButton('Refresh', qgui.QDialogButtonBox.ActionRole)
        addBtn.setObjectName('refreshAction')
        btnBar.clicked.connect(self._performAction)
        return btnBar

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

def lineEdit(name):
    widget = qgui.QLineEdit()
    widget.setObjectName(name)
    return widget

def spinBox(name):
    widget = qgui.QSpinBox()
    widget.setObjectName(name)
    return widget

class EntityInputDialog(qgui.QDialog):

    MODE_EDIT = 1
    MODE_ADD = 2

    def __init__(self, etype, entity=None, parent=None, flags=0):
        qgui.QDialog.__init__(self, parent)
        self.etype = etype
        self.entity = entity
        if entity:
            self.mode = self.MODE_EDIT
        else:
            self.mode = self.MODE_ADD
            self.entity = c2.Entity(self.etype)
        self.initWidget()
        self.initValues()

    def initValues(self):
        if self.mode == self.MODE_EDIT:
            for a in self.etype.attrs:
                if a.dataType == c2.STRING:
                    self.setTextValue(a.name, self.entity[a.name])
                elif a.dataType == c2.INT:
                    self.setNumValue(a.name, self.entity[a.name])


    def formWidget(self):
        widget = qgui.QWidget()
        widget.setObjectName('formWidget')
        form = qgui.QFormLayout()
        widget.setLayout(form)
        for a in self.etype.attrs:
            if a.dataType == c2.STRING:
                form.addRow(a.label, lineEdit(a.name))
            elif a.dataType == c2.INT:
                form.addRow(a.label, spinBox(a.name))
        return widget

    def initWidget(self):
        vlayout = qgui.QVBoxLayout()
        self.setLayout(vlayout)
        form = self.formWidget()
        vlayout.addWidget(form)
        btnBox = qgui.QDialogButtonBox(qgui.QDialogButtonBox.Save | qgui.QDialogButtonBox.Cancel)
        btnBox.rejected.connect(self.reject)
        btnBox.accepted.connect(self.accept)
        vlayout.addWidget(btnBox)

    def getTextValue(self, name):
        wgt = self.findChild(qgui.QLineEdit, name)
        if wgt:
            return unicode(wgt.text())
        return None

    def setTextValue(self, name, txt):
        wgt = self.findChild(qgui.QLineEdit, name)
        if wgt:
            wgt.setText(unicode(txt))

    def getNumValue(self, name):
        wgt = self.findChild(qgui.QSpinBox, name)
        if wgt:
            return wgt.value()
        return None

    def setNumValue(self, name, txt):
        wgt = self.findChild(qgui.QSpinBox, name)
        if wgt:
            wgt.setValue(txt)


    def getEntity(self):
        for a in self.etype.attrs:
            if a.dataType == c2.STRING:
                txt = self.getTextValue(a.name)
            elif a.dataType == c2.INT:
                txt = self.getNumValue(a.name)
            self.entity[a.name] = txt
        return self.entity