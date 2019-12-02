#!/usr/bin/python3

# This is not really an example but rather some code to test
# the behaviour of the pruss interconnect with regard to
# concurrent requests to the same local memory.

from uio.ti.icss import Icss
import ctypes
from math import floor
from time import sleep
import sys

# this is not great, but neither is the built-in round()
def round( number ):
    return floor( number + 1/2 )

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

def prepare( core, pc, addr, length, iterations ):
    assert addr in range( 2**32 )
    assert length in range( 1, 117 )
    core.halt()
    core.r0 = length | iterations << 16
    core.r1 = addr
    core.run( pc=pc, profiling=True )

action = "store"
iterations0 = 0
iterations1 = 1000
address = 0x4a310000
tries = 5
cpw = False

msg = f"{action} at 0x{address:x}"
if iterations0:
    msg += f", skip {iterations0}x"
msg += f", measure {iterations1}x"
print( msg )
for nwords in range(1,25):
    msg = f"{nwords:3d} words: "
    for i in range( tries ):
        iterations = iterations0 + iterations1
        prepare( core0, ("load","store").index(action), address, nwords * 4, iterations )
        start()
        sleep(0.01)
        assert core0.halted
        ( cycles, instrs ) = core0.profiling_sample( running=False )
        if iterations0:
            iterations = iterations0
            prepare( core0, ("load","store").index(action), address, nwords * 4, iterations )
            start()
            sleep(0.01)
            assert core0.halted
            ( cycles0, instrs0 ) = core0.profiling_sample( running=False )
            iterations = iterations1
            cycles -= cycles0
            instrs -= instrs0
        else:
            instrs -= 3  # jmp, slp 1, loop
            cycles -= 4  # slp 1 is counted as two cycles
        if instrs != iterations:
            sys.exit( "%d cycles, %d instrs, %s" % ( cycles, instrs, core.state ) )
        if iterations == 1 and not cpw:
            msg += f" {cycles:3d}"
        else:
            cc = cycles / iterations
            if cpw:
                cc /= nwords
                msg += f" {cc:4.1f}"
            else:
                msg += f" {cc:5.1f}"
    msg += "  cycles"
    if cpw:
        msg += "/word"
    print( msg )

sys.exit()


if True:
    prepare( core0, 1, 0x4a310000, nwords * 4 )
    #prepare( core1, 0, 0x10000, 1 * 4 )
    start()
else:
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
