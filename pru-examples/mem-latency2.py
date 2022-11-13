#!/usr/bin/python3 -u

# This is not really an example but rather some code to do
# memory latency/throughput tests.

from uio.ti.icss import Icss
import ctypes
from time import sleep
from sys import exit

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()
core = pruss.core0

# options
action = "store"
address = pruss.ddr.address
iterations0 = 1000
iterations1 = 5000
tries = 5
cpw = False

action = "load"
address = 0x2e000
iterations0 = 0
iterations1 = 100
tries = 10

# setup trigger to start core
EVENT = 16
IRQ = 0
intc = pruss.intc
intc.ev_ch[ EVENT ] = IRQ
intc.ev_clear_one( EVENT )
intc.ev_enable_one( EVENT )
intc.out_enable_one( IRQ )

core.load( 'fw/memspam.bin' )
core.wake_en = 1 << ( 30 + IRQ )

def run_test( core, action, addr, length, iterations ):
    pc = ("load","store").index(action)
    assert addr in range( 2**32 )
    assert length in range( 1, 117 )
    assert core.halted
    core.r0 = length | iterations << 16
    core.r1 = addr
    core.run( pc=pc, profiling=True )
    intc.ev_set_one( EVENT )
    sleep( 1000 * iterations / 200e6 )
    assert core.halted
    intc.ev_clear_one( EVENT )
    return core.profiling_sample( running=False )

msg = "%s at 0x%x" % (action, address)
if iterations0:
    msg += ", skip %dx" % iterations0
msg += ", measure %dx" % iterations1
print( msg )

for nwords in range(1,29):
    msg = " %2d words: " % nwords
    for i in range( tries ):
        iterations = iterations0 + iterations1
        ( cycles, instrs ) = run_test( core, action, address, nwords * 4, iterations )
        if iterations0:
            ( cycles0, instrs0 ) = run_test( core, action, address, nwords * 4, iterations0 )
            iterations -= iterations0
            cycles -= cycles0
            instrs -= instrs0
        else:
            instrs -= 3  # jmp, slp 1, loop
            cycles -= 4  # slp 1 is counted as two cycles
        if instrs != iterations:
            exit( "%d cycles, %d instrs, %s" % ( cycles, instrs, core.state ) )
        if iterations == 1 and not cpw:
            msg += " %3d" % cycles
        elif cpw:
            msg += " %4.1f" % ( cycles / iterations / nwords )
        else:
            msg += " %6.2f" % ( cycles / iterations )
    msg += "  cycles"
    if cpw:
        msg += "/word"
    print( msg )
