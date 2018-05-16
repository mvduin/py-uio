#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from ti.icss import Icss
from ctypes import c_uint32

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

# load program
core.load( 'fw/ping.bin' )

# map and initialize ddr memory (two 32-bit ints)
shmem = pruss.ddr.map( c_uint32 * 2 )
shmem[:] = (0, 0)

# run pru program that copies from shmem[0] to shmem[1]
core.r4 = pruss.ddr.address
core.run()

for i in range( 1, 4 ):
    # write next value
    shmem[0] = i
    # wait until pru copied it
    while shmem[1] != i:
        pass
    print( "ping %d okay" % i )

core.halt()
