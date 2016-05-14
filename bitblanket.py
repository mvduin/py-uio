#!/usr/bin/python3

from uio import Uio
import ctypes

########## ADC with a bitblank implementation #####################################
#
# 
# Adapted from zmatt's l3-sn-test.py
#     The point of this class was to avoid "driver developers" from having to pass
# a c structure to the uio class. In case a different solution is found, as
# long as uio passes back a bitBlanket, which contains general functions for
# accessing registers in python, the underlying mechanics can continue to
# evolve.
#     Bit blanket works so that you can create a bitBlanket object, say ADC,
# and then read AND write BYTES (the internal cstructure uses c_ubyte) in
# the forms ADC[0:10] or ADC["SOMEREGISTERNAME"], where the string is
# mapped to an offset by a dictionary object passed when the object is
# initialized. I made a script will parse the table of contents in the
# DATASHEET and generate code for a dictionary object. This doesn't support
# bit-by-bit access, but it may in the future with a similiar dictionary
# concept. The idea was to make the interface similiar to people who
# programmed with atmel-studio (avr) or likewise, advanced Arduino.
#
#   This is both the object definition AND an example.


class bitBlanket():
    def __init__(self, uioLabel, size, bitDictionary = None):
        self.bitDictionary = bitDictionary;
        self.myUio = Uio(uioLabel)
        self.memBlanket = type("memBlanket", (ctypes.Structure,),
                          {
                              "_fields_": [("number", ctypes.c_ubyte*int(size))],
                              "__getitem__": bitBlanket.getitem,
                              "__setitem__":bitBlanket.setitem
                        }
                    )
        #we only need the class definition once, then we get the object and
        #that's our map. I don't know if the type disappears. I could probably 
        #wrap this whole thing into one line
        self.memBlanket = self.myUio.map(self.memBlanket)

# The following establish indice/assignment operators for bitBlanket and
# memBlanket (respectively)
    def __getitem__(self, i):
        returnValue = 0
        if (isinstance(i, str)):
            i = range(self.bitDictionary[i][0], self.bitDictionary[i][0] +
                      self.bitDictionary[i][1])
        elif not (isinstance(i,slice)):
            return self.memBlanket[0][i] #it's only one anyway just get it
        elif (isinstance(i, slice)):
            i = range(i.start, i.stop+1) #slices aren't iter. so range > slice
        else:
            raise TypeError('subindicies must be integers or dictionary key (strings): %r' % i)
        for i2 in i:
            returnValue = returnValue + (self.memBlanket[0][i2] << (8 *
                                         (i2-i[0])))
        return returnValue

    def __setitem__(self, i, value):
        if (isinstance(i, str)):
            i = range(self.bitDictionary[i][0], self.bitDictionary[i][0] +
                      self.bitDictionary[i][1])
        elif not (isinstance(i,slice)):
            i = range(i, i+1)
        elif (isinstance(i, slice)):
            i = range(i.start, i.stop+1) #slices aren't iter. so range > slice
        else:
            raise TypeError('subindicies must be integers or dictionary keys(strings): %r' % i)
        for i2 in i:
            tempValue = ctypes.c_ubyte(((ctypes.c_ulong(value).value>> (8 *(
                i2-i[0]))) &
                     ctypes.c_ubyte(255).value)) #if you can't tell, dynamic typing terrifies me
            self.memBlanket[0][i2] = tempValue

    def getitem(self, i):
            if not isinstance(i, int):
                raise TypeError('subindices must be integers: %r' % i)
            return getattr(self, self._fields_[i][0])
    def setitem(self, i, value):
        if not isinstance(i, int):
            raise TypeError('subindices must be integers: %r' % i)
        setattr(self, self._fields_[i][0], value)

