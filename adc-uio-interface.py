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

# The following establish assignmet/indice operators for bitBlanket and
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
            tempValue = ctypes.c_ubyte(((ctypes.c_ulong(value)>> (8 * i2-i[0])) &
                     ctypes.c_ubyte(255))) #if you can't tell, dynamic typing terrifies me
            self.memBlanket[0][i2] = tempValue

    def getitem(self, i):
            if not isinstance(i, int):
                raise TypeError('subindices must be integers: %r' % i)
            return getattr(self, self._fields_[i][0])
    def setitem(self, i, value):
        if not isinstance(i, int):
            raise TypeError('subindices must be integers: %r' % i)
        setattr(self, self._fields_[i][0], value)

# Here is the example. The dictionary is ugly as hell, I'm thinking CSV or XML
adcDict = dict(REVISION=(0x0,4),SYSCONFIG=(0x10,4),IRQSTATUS_RAW=(0x24,4),IRQSTATUS=(0x28,4),IRQENABLE_SET=(0x2c,4),IRQENABLE_CLR=(0x30,4),IRQWAKEUP=(0x34,4),DMAENABLE_SET=(0x38,4),DMAENABLE_CLR=(0x3c,4),CTRL=(0x40,4),ADCSTAT=(0x44,4),ADCRANGE=(0x48,4),ADC_CLKDIV=(0x4c,4),ADC_MISC=(0x50,4),STEPENABLE=(0x54,4),IDLECONFIG=(0x58,4),TS_CHARGE_STEPCONFIG=(0x5c,4),TS_CHARGE_DELAY=(0x60,4),STEPCONFIG1=(0x64,4),STEPDELAY1=(0x68,4),STEPCONFIG2=(0x6c,4),STEPDELAY2=(0x70,4),STEPCONFIG3=(0x74,4),STEPDELAY3=(0x78,4),STEPCONFIG4=(0x7c,4),STEPDELAY4=(0x80,4),STEPCONFIG5=(0x84,4),STEPDELAY5=(0x88,4),STEPCONFIG6=(0x8c,4),STEPDELAY6=(0x90,4),STEPCONFIG7=(0x94,4),STEPDELAY7=(0x98,4),STEPCONFIG8=(0x9c,4),STEPDELAY8=(0xa0,4),STEPCONFIG9=(0xa4,4),STEPDELAY9=(0xa8,4),STEPCONFIG10=(0xac,4),STEPDELAY10=(0xb0,4),STEPCONFIG11=(0xb4,4),STEPDELAY11=(0xb8,4),STEPCONFIG12=(0xbc,4),STEPDELAY12=(0xc0,4),STEPCONFIG13=(0xc4,4),STEPDELAY13=(0xc8,4),STEPCONFIG14=(0xcc,4),STEPDELAY14=(0xd0,4),STEPCONFIG15=(0xd4,4),STEPDELAY15=(0xd8,4),STEPCONFIG16=(0xdc,4),STEPDELAY16=(0xe0,4),FIFO0COUNT=(0xe4,4),FIFO0THRESHOLD=(0xe8,4),DMA0REQ=(0xec,4),FIFO1COUNT=(0xf0,4),FIFO1THRESHOLD=(0xf4,4),DMA1REQ=(0xf8,4),FIFO0DATA=(0x100,4),FIFO1DATA=(0x200,4),)

ADC = bitBlanket("adc", 0x204, adcDict)
for x in ADC:
    print (type(x) , " : " , format(x, '0{0}b'.format(8)))
print(bin(ADC[0:3]))
print(bin(ADC["REVISION"]))
