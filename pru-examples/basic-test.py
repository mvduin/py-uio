#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from ti.icss import Icss

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

# load program
core.load( 'fw/test.bin' )

# alternatively you can access iram as an array of instructions:
#
#       from ctypes import c_uint32 as uint
#
#       # map iram as array of words
#       iram = core.iram.map( uint * 2048 )   # option one
#       iram = core.iram.map().cast( 'I' )    # option two
#
#       iram[0] = 0x0101e0e0  # add r0, r0, 1
#       iram[1] = 0x2a000000  # halt


core.r0 = 123

core.run()

print( "waiting for core to halt" )
while not core.halted:
    pass

print( "r0 =", core.r0 )
