#!/usr/bin/python3

# This is not really an example but rather some code to test
# the behaviour of the pruss interconnect with regard to
# concurrent requests to the same local memory.

import sys
sys.path.insert( 0, '../src' )

from ti.icss import Icss
import ctypes

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()
( core0, core1 ) = pruss.cores

# setup trigger to start cores simultaneously
EVENT = 16
IRQ = 0
intc = pruss.intc
intc.ev_ch[ EVENT ] = IRQ
intc.ev_clear_one( EVENT )
intc.ev_enable_one( EVENT )
intc.out_enable_one( IRQ )

def start():
    intc.ev_set_one( EVENT )

for core in pruss.cores:
    core.load( 'fw/memspam.bin' )
    core.wake_en = 1 << ( 30 + IRQ )
del core

iterations = 1000

def prepare( core, pc, addr, length ):
    assert addr in range( 2**32 )
    assert length in range( 1, 117 )
    core.halt()
    core.r0 = length | iterations << 16
    core.r1 = addr
    core.run( pc=pc, profiling=True )

prepare( core0, 1, 0x00000, 2 * 4 )
prepare( core1, 1, 0x02000, 2 * 4 )

m = core0.dram.map( ctypes.c_uint32 )

import time

def latency():
    t0 = time.perf_counter()
    m.value
    t1 = time.perf_counter()
    return t1 - t0

t0 = latency()
t0 = latency()

start()

t1 = latency()
print( "latency while idle: %.1f us" % ( t0 * 1e6 ) )
print( "latency while ram kept busy: %.1f us" % ( t1 * 1e6 ) )
print( "latency increase: %d pru cycles" % round( ( t1 - t0 ) * 200e6 ) )

while not ( core0.halted and core1.halted ):
    pass

for core in pruss.cores:
    ( cycles, instrs ) = core.profiling_sample()
    instrs -= 3  # jmp, slp 1, loop
    cycles -= 4  # slp 1 is counted as two cycles
    if instrs <= 0:
        continue
    if instrs % iterations:
        sys.exit( "%d cycles, %d instrs, %s" % ( cycles, instrs, core.state ) )
    ii = instrs // iterations
    cc = round( cycles / iterations )
    cycles -= cc * iterations
    ss = cc - ii
    msg = "%d cycles = %d instructions + %d stalls   per iteration" % ( cc, ii, ss )
    if cycles:
        msg += "  %+d stalls" % cycles
    print( msg )
