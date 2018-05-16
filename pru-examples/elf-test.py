#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from ti.icss import Icss
from ctypes import c_uint32
import struct

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

# load ELF executable
core.load( 'fw-c/test.out' )

# map shared memory
shmem = core.shared_dram.map( c_uint32 )

print( shmem.value )

core.run()

print( "waiting for core to halt" )
while not core.halted:
    pass

print( shmem.value )
