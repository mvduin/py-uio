#!/usr/bin/python3

from uio.ti.icss import Icss
from ctypes import c_uint32

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

# load ELF executable
core.load( 'fw-c/test.out' )

# map variables in pru memory
foo = core.map( c_uint32, 0x1234 )
bar = core.map( c_uint32, 0x10000 )

print( "foo = %d,  bar = %d" % ( foo.value, bar.value ) )

core.run()

print( "waiting for core to halt" )
while not core.halted:
    pass

print( "foo = %d,  bar = %d" % ( foo.value, bar.value ) )
