#!/usr/bin/python3

from ti.pwmss import Pwmss

qep = Pwmss( "/dev/uio/pwmss2" ).qep

FCK = 10**8  # 100 MHz

# disable module, clear all irqs
qep.ctr_config = 0
qep.irq.reset()

# 96 steps per full revolution
qep.maximum = 96 - 1
qep.position = 0

qep.timer_maximum = FCK // 2 - 1  # 2 Hz
qep.timer_counter = 0

qep.io_config = 0
qep.ctr_config = 1 << 1 | 1 << 3 | 1 << 12 | 2 << 4
qep.irq.enable( 0xffe )

# make sure the initial position is printed
qep.irq.set( 1 << 11 )
qep.irq.clear( 1 << 11 )
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
    irq = qep.irq.recv()
    pos = qep.position

    if irq & 0x7f6 or pos != lastpos:
        s = "pos {0:02d}".format( pos )
        for bit,msg in enumerate(irq_msgs):
            if not msg: continue
            if irq & 1 << bit:
                s += ", " + msg
                if bit == 10:
                    s += " {0:02d}".format( qep.index_latch )
        print( s )
        lastpos = pos
