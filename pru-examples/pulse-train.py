#!/usr/bin/python3

from uio.ti.icss import Icss
from uio.device import Uio
import ctypes

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0
core.load( 'fw/pulse-train.bin' )

# completion event and irq
EVENT = 16
IRQ = 2
irq = Uio( "/dev/uio/pruss/irq%d" % IRQ )

# set up completion event
intc = pruss.intc
intc.ev_ch[ EVENT ] = IRQ
intc.ev_clear_one( EVENT )
intc.ev_enable_one( EVENT )

def send_pulses( count, frequency, duty_cycle=0.5 ):
    # convert frequency and duty-cycle to on/off time in 10ns units
    period = round( 100e6 / frequency )
    on_time = round( duty_cycle * period )
    off_time = period - on_time

    # validate parameters are in range
    assert count in range( 1, 2**32 )
    assert on_time in range( 2, 2**32 )
    assert off_time in range( 3, 2**32 )

    # make sure PRU core isn't already running
    assert core.halted

    # clear completion event
    intc.ev_clear_one( EVENT )

    # start PRU core
    core.r4 = count
    core.r5 = on_time
    core.r6 = off_time
    core.run()

def wait_irq():
    intc.out_enable_one( IRQ )
    irq.irq_recv()
    return intc.out_event[ IRQ ]

def wait_completion():
    if core.halted or wait_irq() == EVENT:
        return
    # tolerate one spurious irq, try again
    if core.halted or wait_irq() == EVENT:
        return
    raise RuntimeError("Bogus IRQ")

# send pulses and wait until done
def send_pulses_sync( count, frequency, duty_cycle=0.5 ):
    send_pulses( count, frequency, duty_cycle )
    wait_completion()

send_pulses_sync( 100, 10e3 )  # send 100 pulses at 10 kHz
