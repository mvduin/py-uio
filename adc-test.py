#!/usr/bin/python3

from uio import Uio
import ctypes
from ctypes import c_uint32 as uint
from ctypes import c_byte as byte

########## ADC  #####################################
#
# This will test the ADC Status Register
# Adapted from zmatt's l3-sn-test.py
from ctypes import Structure

class IterableStructure(Structure):
    def __getitem__(self, i):
      if not isinstance(i, int):
        raise TypeError('subindices must be integers: %r' % i)
      return getattr(self, self._fields_[i][0])

adc = Uio( "adc" )
class Step( IterableStructure ):
    _fields_ = [
        ("stepconfig", uint, 32),
        ("stepdelay", uint, 32),
    ];
class ADC( IterableStructure ):
    _fields_ = [
        ("revision", uint, 32),
        ("spacer01", byte*(0x10-4)),
        ("sysconfig", uint, 32),
        ("spacer02", byte*16),
        ("irqstatus_raw", uint, 32),
        ("irqstatus", uint, 32),
        ("irqenable_set", uint, 32),
        ("irqenable_clr", uint, 32),
        ("irqwakeup", uint, 32),
        ("dmaenable_set", uint, 32),
        ("dmaenable_clr", uint, 32),
        ("ctrl", uint, 32),
        ("adcstat", uint, 32),
        ("adcrange", uint, 32),
        ("adc_clkdiv", uint, 32),
        ("adc_misc", uint, 32),
        ("stepenable", uint,  32),
        ("idleconfig", uint, 32),
        ("ts_charge_stepconfig", uint, 32),
        ("ts_charge_delay", uint, 32),
        ("steps", Step*16),
        ("fifo0count", uint, 32),
        ("fifo0threshold", uint, 32),
        ("dma0req", uint, 32),
        ("fifo1count", uint, 32),
        ("fifo1threshold", uint, 32),
        ("dma1req", uint, 32),
        ("spacer03", byte*4),
        ("fifo0data", uint, 32),
        ("spacer04", byte*0xFC),
        ("fifo1data", uint, 32)
    ];
testStatus  = adc.map(ADC)
i = 0
for x in testStatus:
#    if ( i % 5 == 0):
#        input("Press Enter to Continue:")
    if isinstance(x, int):
        print(hex(i), ": ", format(x, '0{0}b'.format(32)), end="")
        i = i + 4
    if hasattr(x, "__len__"):
        for x2 in x:
            if isinstance(x2, Step):
                for x3 in x2:
                    if isinstance(x3, int):
                        print(hex(i), ": ", format(x3, '0{0}b'.format(32)))
                        i = i + 4
            else:
                print(hex(i), ": " , "BUFFER: ", x2.__sizeof__())
                i = i + 1
#                if (i % 5 == 0):
#                    input("Press Enter to Continue:")
    else:
        print("<")
