#
# Copyright 2019 Lars Pastewka
# 
# ### MIT license
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


"""
Stub implementation of mpi4py. This is necessary to run a serial version of
NuMPI and dependent projects without an MPI installation.

Disclaimer: This is at present not - and not intended to be - a full
implementation of the API provided by mpi4py. It is a minimal implementation
needed to run our codes.
"""

from enum import Enum

import numpy as np


### Data types

class Typedict(object):
    def __getitem__(self, item):
        return np.dtype(item)


_typedict = Typedict()


### Operations

class Operations(Enum):
    MIN = 1
    MAX = 2
    SUM = 3
    PROD = 4
    LAND = 5
    BAND = 6
    LOR = 7
    BOR = 8
    LXOR = 9
    BXOR = 10
    MAXLOC = 11
    MINLOC = 12


MIN = Operations.MIN
MAX = Operations.MAX
SUM = Operations.SUM
PROD = Operations.PROD
LAND = Operations.LAND
BAND = Operations.BAND
LOR = Operations.LOR
BOR = Operations.BOR
LXOR = Operations.LXOR
BXOR = Operations.BXOR
MAXLOC = Operations.MAXLOC
MINLOC = Operations.MINLOC


### Opening modes

class OpeningModes(Enum):
    MODE_RDONLY = 'r'
    MODE_WRONLY = 'a'
    MODE_RDWR = 'a'
    MODE_CREATE = 'w'
    MODE_EXCL = 'x'
    # FIXME: The following modes are not supported
    # MODE_DELETE_ON_CLOSE = 'A'
    # MODE_UNIQUE_OPEN = 'A'
    # MODE_SEQUENTIAL = 'A'
    # MODE_APPEND = 'A'


MODE_RDONLY = OpeningModes.MODE_RDONLY
MODE_WRONLY = OpeningModes.MODE_WRONLY
MODE_RDWR = OpeningModes.MODE_RDWR
MODE_CREATE = OpeningModes.MODE_CREATE
MODE_EXCL = OpeningModes.MODE_EXCL


# FIXME: The following modes are not supported
# MODE_DELETE_ON_CLOSE = OpeningModes.MODE_DELETE_ON_CLOSE
# MODE_UNIQUE_OPEN = OpeningModes.MODE_UNIQUE_OPEN
# MODE_SEQUENTIAL = OpeningModes.MODE_SEQUENTIAL
# MODE_APPEND = OpeningModes.MODE_APPEND


### Stub communicator object

class Communicator(object):
    def Barrier(self):
        pass

    def Get_rank(self):
        return 0

    def Get_size(self):
        return 1

    def Reduce(self, sendbuf, recvbuf, op=Operations.SUM, root=0):
        if root != 0:
            raise ValueError('Root must be zero for MPI stub implementation.')

        try:
            senddata, sendtype = sendbuf
        except:
            senddata = sendbuf
            sendtype = sendbuf.dtype

        try:
            recvdata, recvtype = recvbuf
        except:
            recvdata = recvbuf
            recvtype = recvbuf.dtype

        if sendtype != recvtype:
            raise TypeError('Mismatch in send and receive MPI datatypes in MPI stub implementation.')

        recvdata[...] = senddata

    Allreduce = Reduce


### Stub file I/O object

class File(object):
    def __init__(self, comm, filename, amode):
        assert isinstance(comm, Communicator)
        self.file = open(filename, amode.value + 'b')

    @classmethod
    def Open(cls, comm, filename, amode=MODE_RDONLY):  # FIXME: This method has an optional info argument
        return File(comm, filename, amode)

    def Read_all(self, buf):
        assert buf.dtype == np.int8
        data = self.file.read(len(buf))
        buf[...] = np.frombuffer(data, count=len(buf), dtype=np.int8)


COMM_WORLD = Communicator()