#!/usr/bin/python3

from ti.icss import Icss
from ctypes import c_uint32 as uint

pruss = Icss( "pruss" )

# some sensible defaults
pruss.cfg.intc = 0;
pruss.cfg.idlemode = 'auto'
pruss.cfg.standbymode = 'auto'
pruss.cfg.standbyreq = False

pruss.core0.full_reset()
pruss.core1.full_reset()


# map iram as array of words
iram = pruss.iram0.map( uint * 2048 )

iram[0] = 0x0101e0e0  # add r0, r0, 1
iram[1] = 0x2a000000  # halt

pruss.core0.r[0] = 123

pruss.core0.run()

if pruss.core0.halted:
    print( "r0 =", pruss.core0.r[0] )
