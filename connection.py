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

from contextlib import closing

CONNECTION_FACTORY_CLAZZ = 'connection.ConnectionFactory'

class ConnectionFactory(object):

    def createConnection(self, dsUri):
        raise Exception('Not implemented')

class Statement(object):

    def __init__(self, sql, pycon):
        self.sql = sql
        self.pycon = pycon

    def query(self, params=[], convert=lambda x : x):
        result = []
        with closing(self.pycon.cursor()) as rows:
            rows.execute(self.sql, params)
            for r in rows.fetchall():
                result.append(convert(r))
        return result

    def single(self, params=[], convert=lambda x : x):
        with closing(self.pycon.cursor()) as rows:
            rows.execute(self.sql, params)
            return convert(rows.fetchone())

    def execute(self, params=[]):
        with closing(self.pycon.cursor()) as c:
            c.execute(self.sql, params)
            return c.rowcount

class Connection(object):

    def query(self, sql, params=[]):
        raise Exception('Not implemented abstract method')

    def single(self, sql, params=[]):
        raise Exception('Not implemented abstract method')

    def execute(self, stmt, params=[]):
        raise Exception('Not implemented abstract method')

    def commit(self):
        raise Exception('Not implemented abstract method')

    def prepare(self, sql):
        raise Exception('Not implemented abstract method')

    def rollback(self):
        raise Exception('Not implemented abstract method')

    def close(self):
        raise Exception('Not implemented abstract method')