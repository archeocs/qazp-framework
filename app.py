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

import importlib
from PyQt4 import QtCore as qcore
from PyQt4 import QtGui as qgui


class AppModule(object):

    def initModule(self, application):
        pass

class NullException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)

class BundleContext(object):

    def __init__(self):
        self.menu = None
        self.parent = None
        self.dataSources = {}

    def showWidget(self, widget):
        window = self.parent.addSubWindow(widget)
        window.setAttribute(qcore.Qt.WA_DeleteOnClose)
        widget.show()
        return window

    def dataSourceFactory(self, dataSourceFactory, etype, variant='default'):
        self.dataSources[(etype.name,variant)] = dataSourceFactory

    def prepareDataSource(self, etype, variant='default'):
        return self.dataSources[(etype.name, variant) ](etype)

class Application(qgui.QMainWindow):

    def __init__(self, parent=None, iface=None):
        qgui.QMainWindow.__init__(self, parent)
        self._appArea = qgui.QMdiArea(self)
        self.setCentralWidget(self._appArea)
        self._initModules()

    def _initModules(self):
        with open('modules.txt', 'r') as modList:
            for name in modList.readlines():
                bundle = importlib.import_module(name.rstrip('\n'))
                context = BundleContext()
                context.menu = self.menuBar().addMenu(bundle.getName())
                context.parent = self._appArea
                context.main = self
                bundle.start(context)

def start(qgis=None, qgsIface=None, guiApp=None):
    app = Application(qgis, qgsIface)
    app.show()
    if guiApp:
        guiApp.exec_()

def main():
    from sys import argv
    import qgsctx
    qgsctx.initProviders('/usr/lib/qgis/plugins/')
    suri = qgsctx.liteUri('/home/user/nowa_test.db', 'stanowiska', 'wspolrzedne')
    qgsctx.addVectorLayer(suri, 'spatialite')
    turi = qgsctx.liteUri('/home/user/nowa_test.db', 'trasy', 'wspolrzedne')
    qgsctx.addVectorLayer(turi, 'spatialite')
    muri = qgsctx.liteUri('/home/user/nowa_test.db', 'miejsca', 'wspolrzedne')
    qgsctx.addVectorLayer(muri, 'spatialite')
    zuri = qgsctx.liteUri('/home/user/nowa_test.db', 'zdjecia_lotnicze', 'wspolrzedne')
    qgsctx.addVectorLayer(zuri, 'spatialite')
    qif = qgsctx.Iface()
    app = qgui.QApplication(argv)
    start(qgsIface=qif, guiApp=app)

if __name__ == '__main__':
    main()
