#!/usr/bin/python3

from ti.pwmss import Pwmss

cap = Pwmss( "/dev/uio/pwmss2" ).cap
m = cap.regs

FCK = 10**8  # 100 MHz


# disable module, set to capture mode, clear all irqs
m.config = 0
m.irq_clear = 0xfff

# reset and start counter
m.counter = 0
m.config |= 1 << 20
