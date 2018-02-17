#!/usr/bin/python3

from ti.pwmss import Pwmss

qep = Pwmss( "/dev/uio/pwmss2" ).qep
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
m.ctr_config = 1 << 1 | 1 << 3 | 1 << 12 | 2 << 4
m.irq_enabled = 0xffe

lastpos = -1

irq_msgs = (
        None,
        "position counter error",
        "quadrature decoder error",
        "dir change",
        "watchdog",
        "underflow",
        "overflow",
        "compare load",
        "compare match",
        "strobe latch",
        "index latch",
        "timer",
        )

while True:
    pos = m.position
    irq = m.irq_pending
    m.irq_clear( irq )

    if irq & 0x7f6 or pos != lastpos:
        s = "pos {0:02d}".format( pos )
        for bit,msg in enumerate(irq_msgs):
            if not msg: continue
            if irq & 1 << bit:
                s += ", " + msg
                if bit == 10:
                    s += " {0:02d}".format( m.index_latch )
        print( s )
        lastpos = pos

    qep.irq_enable()
    qep.irq_recv()
