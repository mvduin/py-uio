#!/usr/bin/python3

from uio.ti.icss import Icss
from ctypes import c_uint32
import struct

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

# load ELF executable
core.load( 'fw-c/test.out' )

# map shared memory
shmem = core.map( c_uint32, 0x10000 )

print( shmem.value )

core.run()

print( "waiting for core to halt" )
while not core.halted:
    pass

print( shmem.value )
