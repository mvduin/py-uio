#!/usr/bin/python3

from uio import Uio
import ctypes

########## bitBlanket #####################################
#
# 
# Adapted from zmatt's l3-sn-test.py
#
#   The point of this class was to avoid "driver developers" from having to pass
# a c structure to the uio class. In case a different solution is found, as
# long as uio passes back a bitBlanket, which contains general functions for
# accessing registers in python, the mechanics interacting with lib uio can continue to
# evolve without affecting libraries built on top of it.
#   Bit blanket works so that you can create a bitBlanket object, say ADC,
# and then read AND write BYTES (the internal cstructure uses c_ubyte) in
# the forms ADC[(0,4)] where it's (offset, length) and length can be ommited to
# use the default value... or use ADC[SOMEREGISTERNAME], where the string is
# mapped to an offset by a dictionary object passed when the object is
# initialized. I made a script that will parse the table of contents in the
# DATASHEET and generate code for a dictionary object. This doesn't support
# bit-by-bit access, but it may in the future with a similiar dictionary
# concept. The idea was to make the interface similiar to people who
# programmed with atmel-studio (avr) or likewise, advanced Arduino.
# 
#


class bitBlanket():
    def __init__(self, uioLabel, size, defaultWordLength = 4):
        self.defaultWordLength = defaultWordLength
        self.myUio = Uio(uioLabel)
        self.memBlanket = type("memBlanket", (ctypes.Structure,),
                          {
                              "_fields_": [("number", ctypes.c_ubyte*int(size))],
                              "__getitem__": bitBlanket.getitem,
                              "__setitem__":bitBlanket.setitem
                        }
                    )
        self.memBlanket = self.myUio.map(self.memBlanket)

    byteSize = (ctypes.c_ubyte, ctypes.c_ushort, ctypes.c_uint,
                         ctypes.c_ulong)
    def __getitem__(self, i):
        #rehandle slices
        if isinstance(i, int):
            i = (i, self.defaultWordLength)
        return self.memBlanket[i].value

    def __setitem__(self, i, value):
        #rehandle slices
        #if isinstance(i, int):
        #    i = (i, self.defaultWordLength)
        self.memBlanket[i] = value

    def getitem(self, i):
        if not isinstance(i, tuple) or (i.__len__() != 2):
            raise TypeError('subindices must be 2-element tuples: %r' % i)
        try:
            pointerType = bitBlanket.byteSize[int(i[1]/2)]
        except ValueError:
            print('second indice must be 1, 2, 4, or 8 (bytes)')
            raise
        return ctypes.cast(ctypes.byref(getattr(self, "number"), i[0]),
                           ctypes.POINTER(pointerType)).contents


    def setitem(self, i, value):
        if not isinstance(i, tuple) or (i.__len__() != 2):
            raise TypeError('subindices must be 2-element tuples: %r' % i)
        try:
            pointerType = bitBlanket.byteSize[int(i[1]/2)]
        except ValueError:
            print('second indice must be 1, 2, 4, or 8 (bytes)')
            raise
        ctypes.cast(ctypes.byref(getattr(self, "number"), i[0]),
                    ctypes.POINTER(pointerType))[0] = pointerType(value)
