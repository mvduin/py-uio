#!/usr/bin/python3

from ti.pwmss import Pwmss

qep = Pwmss( "pwmss2" ).qep
m = qep.regs

FCK = 10**8  # 100 MHz

# disable module, clear all irqs
m.ctr_config = 0
m.irq_clear( 0xfff )

# 96 steps per full revolution
m.maximum = 96 - 1
m.position = 0

m.timer_maximum = FCK // 2 - 1  # 2 Hz
m.timer_counter = 0

m.io_config = 0
m.ctr_config = 1 << 1 | 1 << 3 | 1 << 12
m.irq_enabled = 0xffe;

lastpos = -1

while True:
    pos = m.position
    irq = m.irq_pending
    m.irq_clear( irq )

    if irq & 0x7f6 or pos != lastpos:
        print( "position {0:02d}, irq {1:012b}".format( pos, irq ) )
        lastpos = pos

    qep.irq_enable()
    qep.irq_recv()
