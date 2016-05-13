#!/usr/bin/python3

from uio import Uio
import ctypes

########## ADC with a bitblank implementation #####################################
#
# 
# Adapted from zmatt's l3-sn-test.py
#
#
#

class bitBlanket():
    def __init__(self, uioLabel, size, bitDictionary = None):
        self.myUio = Uio(uioLabel)
        self.memBlanket = type("memBlanket", (ctypes.Structure,),
                          {
                              "_fields_": [("number", ctypes.c_ubyte*int(size))],
                              "__getitem__": bitBlanket.getitem,
                              "__setitem__":bitBlanket.setitem
                        }
                    )
        #we only need the class definition once, then we get the object and
        #that's our map
        self.memBlanket = self.myUio.map(self.memBlanket)
    #indexingbitBlanket just retrieves memblanket
    def __getitem__(self, i):
        #dictionary stuff here
        return self.memBlanket[0][i]
    #this is defined here for memBlanket
    def __setitem__(self, i, value):
        #can do some sanatizing here+dictionary
        self.memBlanket[0][i] = value
    def getitem(self, i):
        #can also do dictionary stuff here
        if not isinstance(i, int):
            raise TypeError('subindices must be integers: %r' % i)
        return getattr(self, self._fields_[i][0])
    def setitem(self, i, value):
        #do i really have to access memblanket in this manner
        #remember to sanatize
        setattr(self, self._fields_[i][0], value)
ADC = bitBlanket("adc", 0x204)
for x in ADC:
    print (type(x) , " : " , format(x, '0{0}b'.format(8)))
print(bin(ADC[0]))
