#!/usr/bin/python3

from ti.icss import Icss

pruss = Icss( "/dev/uio/pruss/module" )

# some sensible defaults
pruss.cfg.intc = 0
pruss.cfg.idlemode = 'auto'
pruss.cfg.standbymode = 'auto'
pruss.cfg.standbyreq = False

pruss.core0.full_reset()
pruss.core1.full_reset()


# clear iram (not really necessary)
pruss.iram0.write( bytearray(8192) )

# load program
with open('pruss-test-fw.bin', 'rb') as f:
    pruss.iram0.write( f.read() )

# alternatively you can access iram as an array of instructions:
#
#       from ctypes import c_uint32 as uint
#
#       # map iram as array of words
#       iram = pruss.iram0.map( uint * 2048 )
#
#       iram[0] = 0x0101e0e0  # add r0, r0, 1
#       iram[1] = 0x2a000000  # halt


pruss.core0.r[0] = 123

pruss.core0.run()

print( "waiting for core to halt" )
while not pruss.core0.halted:
    pass

print( "r0 =", pruss.core0.r[0] )
