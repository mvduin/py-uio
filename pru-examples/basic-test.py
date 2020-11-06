#!/usr/bin/python3

from uio.ti.icss import Icss

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

core.load( 'fw/test.bin' )

core.r0 = 123

core.run()

print( "waiting for core to halt" )
while not core.halted:
    pass

print( "r0 =", core.r0 )
