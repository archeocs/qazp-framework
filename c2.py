# -*- coding: utf-8 -*-

# qazp2-genericview
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
#      * Neither the name of qazp2-genericview nor the names of its
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
from collections import OrderedDict

from copy import deepcopy

from PyQt4 import QtCore as qcore

class EntityType(object):

    def __init__(self, name, attrs=[]):
        self.name = name
        self.attrs = attrs
        self._name2Idx = dict(zip([a.name for a in attrs],
                                    range(len(attrs))))
        self.primaryKey = tuple([a.name for a in attrs if a.primaryKey])

    def clone(self):
        return EntityType(self.name, map(lambda a: a.clone(), self.attrs))

    def getAttrNames(self):
        return [a.name for a in self.attrs]

    def getAttrIndex(self, name=None, attr=None):
        if name and attr:
            raise Exception('set name or attribute')
        elif name:
            if self._name2Idx.has_key(name):
                return self._name2Idx[name]

            else:
                raise Exception('Attribute '+name+' not found')
        elif attr:
            for (ai, a) in enumerate(self.attrs):
                if a == attr:
                    return ai
            else:
                raise Exception('Attribute '+str(attr)+' not found')
        else:
            raise Exception('Set attribute or its name')

    def hasAttr(self, name):
        return self._name2Idx.has_key(name)

    def __eq__(self, other):
        if not isinstance(other, EntityType):
            return False
        elif self.name != other.name:
            return False
        elif self.attrs != other.attrs:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class EntityAttr(object):

    def __init__(self, name, primaryKey=False, inList=True):
        self.name = name
        self.primaryKey = primaryKey
        self.inList = inList

    def clone(self):
        return EntityAttr(self.name, self.primaryKey, self.inList)

    def __eq__(self, other):
        if not isinstance(other, EntityAttr):
            return False
        elif self.primaryKey != other.primaryKey:
            return False
        elif self.inList != other.inList:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class Entity(qcore.QObject):

    def __init__(self, etype, **props):
        qcore.QObject.__init__(self, None)
        self.properties = {}
        for n in etype.getAttrNames():
            self.properties[n] = props.get(n,None)
        self.etype = etype
        self._pk = None

    def __setitem__(self, key, value):
        if not self.etype.hasAttr(key):
            raise Exception('No such property '+str(key))
        old = self.properties.get(key, None)
        self.properties[key] = value
        if old != value:
            self.changed.emit(key, old, value)

    def __getitem__(self, key):
        if not self.etype.hasAttr(key):
           raise Exception('No such property '+str(key))
        return self.properties.get(key, None)

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        elif self.etype != other.etype:
            return False
        elif len(self.properties) != len(other.properties):
            return False
        elif self.properties != other.properties:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def props(self):
        return self.properties

    def clone(self):
        clonedProps = {}
        for (k, v) in self.properties.iteritems():
            clonedProps[k] = deepcopy(v)
        return Entity(self.etype.clone(), **clonedProps)

    @property
    def primaryKey(self):
        if not self._pk:
            self._pk = tuple([self[k] for k in self.etype.primaryKey])
        return self._pk

    changed = qcore.pyqtSignal(str, object, object, name='changed')

STATE_NEW = 1
STATE_COMMITED = 2
STATE_DELETED = 3
STATE_UPDATED = 4

class CacheItem(object):

    def __init__(self, entity, state=STATE_COMMITED):
        self.entity = entity.clone()
        self.original = entity.clone()
        self.entity.changed.connect(self.update)
        self.state = state

    def update(self, key, old, new):
        self.original[key] = new
        self.state = STATE_UPDATED

    @property
    def deleted(self):
        return self.state == STATE_DELETED

class EntityCache(qcore.QObject):

    def __init__(self, etype=None):
        qcore.QObject.__init__(self)
        self.items = OrderedDict()
        self.itemsIndex = []
        self.etype = etype

    def _filter(self, efilter=lambda x : not x.deleted):
        for it in self.items.itervalues():
            if efilter(it):
                yield it

    def getAll(self, efilter=lambda x : not x.deleted, fmap=lambda x : x.entity):
        for it in self._filter(efilter):
            yield fmap(it)

    def getEntity(self, *args):
        if self.items.has_key(args):
            ent = self.items.get(args)
            if not ent.deleted:
                return ent.entity #self.items.get(args).getEntity()
        return None

    def getByIndex(self, index):
        if 0 <= index < len(self.items):
            return self.items[self.itemsIndex[index]].entity
        raise Exception('Index %d out of range 0 %d' % (index, len(self.items)))

    def size(self, efilter=lambda x : not x.deleted):
        return len([e for e in self._filter(efilter)])

    changed = qcore.pyqtSignal(int, int, name='changed')

    def remove(self, *args):
        ent = self.items.get(args)
        idx = self.itemsIndex.index(args)
        if ent:
            if ent.state == STATE_DELETED:
                ent.state = STATE_DELETED
            elif ent.state == STATE_NEW:
                self.itemsIndex.remove(args)
                del self.items[args]
            self.changed.emit(idx, idx+1)

    def clear(self):
        itSize = len(self.items)
        self.items.clear()
        self.itemsIndex = []
        self.changed.emit(0, itSize)

    def setEntities(self, entities):
        start = len(self.items)
        for e in entities:
            self.items[e.primaryKey] = CacheItem(e)
            self.itemsIndex.append(e.primaryKey)
        self.changed.emit(start, len(self.items))

    def addEntities(self, entities):
        start = len(self.items)
        for e in entities:
            if self.items.has_key(e.primaryKey):
                raise Exception('Duplicated entity '+e.primaryKey)
            self.items[e.primaryKey] = CacheItem(e, state = STATE_NEW)
            self.itemsIndex.append(e.primaryKey)
        self.changed.emit(start, len(self.items))


class DataSource(object):

    def getAll(self, expression=None):
        return []

    def get(self, *primaryKey):
        return None

    def update(self, entities):
        pass

    def delete(self, entities):
        pass

    def create(self, entities):
        pass

class CacheCoordinator(object):

    def __init__(self, cache, dataSource):
        self.source = dataSource
        self.cache = cache

    def save(self):
        stateEnt = self.cache.getAll(efilter=lambda x : x.state != STATE_COMMITED,
                                     fmap=lambda it : (it.state, it.entity))
        stateGroups = self._classifyEntities(stateEnt)
        self._crudOper(stateGroups, STATE_UPDATED, self.source.update)
        self._crudOper(stateGroups, STATE_DELETED, self.source.delete)
        self._crudOper(stateGroups, STATE_NEW, self.source.create)

    def _crudOper(self, groups, stateType, opMethod):
        g = groups.get(stateType, [])
        if g:
            opMethod(g)

    def _classifyEntities(self, stateEntities):
        clsf = {}
        for se in stateEntities:
            estate = se[0]
            if estate not in clsf:
                clsf[estate] = []
            clsf[estate].append(se[1])
        return clsf

    def refresh(self, expression=None):
        allEntites = self.source.getAll(expression)
        self.cache.clear()
        self.cache.setEntities(allEntites)

