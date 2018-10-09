#!/usr/bin/python3

from pyuio.ti.icss import Icss
from pyuio.uio import Uio
import ctypes

EVENT0 = 16 # range 16..31
EVENT1 = 17 # range 16..31
IRQ = 2     # range 2..9

pruss = Icss( "/dev/uio/pruss/module" )
irq = Uio( "/dev/uio/pruss/irq%d" % IRQ )
intc = pruss.intc
(core0, core1) = pruss.cores

pruss.initialize()

# clear and enable events and route them to our irq
for event in EVENT0, EVENT1:
    intc.ev_ch[ event ] = IRQ
    intc.ev_clear_one( event )
    intc.ev_enable_one( event )

# load program onto both cores
core0.load( 'fw/intc-test.bin' )
core1.load( 'fw/intc-test.bin' )

# map and set parameters
class Params( ctypes.Structure ):
    _fields_ = [
            ("interval", ctypes.c_uint32),  # in 10ns units
            ("event",    ctypes.c_uint8),
        ]

params0 = core0.dram.map( Params )
params0.interval = round( 1.0 * 1e8 )
params0.event = EVENT0

params1 = core1.dram.map( Params )
params1.interval = round( 0.5 * 1e8 )
params1.event = EVENT1

# start cores
core0.run()
core1.run()

def handle_events():
    while True:
        event = intc.out_event[ IRQ ]
        if event < 0:
            break
        intc.ev_clear_one( event )
        print( "event", event )

def main_loop():
    while True:
        # wait until any enabled event is pending
        intc.out_enable_one( IRQ )
        irq.irq_recv()

        # process events
        handle_events()

try:
    main_loop()
except KeyboardInterrupt:
    pass
