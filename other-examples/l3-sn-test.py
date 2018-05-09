#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from uio import Uio
import ctypes
from ctypes import c_uint32 as uint


########## L3 interconnect service network #####################################
#
# Welcome to the most fussy register space on the SoC!
# Only single word access allowed. Byte/halfword/multi-word access = bus error.

l3_sn = Uio( "/dev/uio/l3-sn" )

class ComponentID( ctypes.Structure ):
    _fields_ = [
            ("vendor",  uint, 16),  # 1 = Arteris
            ("type",    uint, 16),
            ("hash",    uint, 24),
            ("version", uint,  8),
        ]

class FlagOutput( ctypes.Structure ):
    src_t = uint  # one bit per input

    _fields_ = [
            ("enabled", src_t),  #rw
            ("pending", src_t),  #r-
        ]

class FaultCombiner( ctypes.Structure ):
    _anonymous_ = ["app"]
    _fields_ = [
            ("component", ComponentID), # vendor 1 type 0x37
            ("app",     FlagOutput),
            ("debug",   FlagOutput),
        ]


# L3 target agents are capable of logging faults and optionally asserting an
# irq.  Faults resulting from debug (JTAG) requests are separated from those
# resulting from non-debug (aka "application") requests.  Each target agent
# therefore has two fault irq outputs, and the faultcombiners retain this
# separation.  The device tree snippet arranges for the "app fault" output of
# the top-level faultcombiner to be deliverable as irq to userspace.
#
fc_top = l3_sn.region( "l3f" ).map( FaultCombiner, 0x1100 )
fc_l3f = l3_sn.region( "l3f" ).map( FaultCombiner, 0x1000 )
fc_l3s = l3_sn.region( "l3s" ).map( FaultCombiner,  0x600 )

for i in fc_top, fc_l3s, fc_l3f:
    assert i.component.vendor == 1
    assert i.component.type == 0x37
    i.enabled = 0xffffffff      # enable all inputs
    n = i.enabled.bit_length()  # check how many we actually got
    print( 'inputs: ' + format( i.pending, '0{0}b'.format(n) ) )
