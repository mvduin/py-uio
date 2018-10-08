#!/usr/bin/python3
""" intc.py - test script for receiving interrupts from PRU 0 using PyUIO library """
from pyuio.ti.icss import Icss
from pyuio.uio import Uio


IRQ = 2           # range 2 .. 9 (IRQ = Interrupt ReQuest)
EVENT = 19  

pruss = Icss("/dev/uio/pruss/module")
irq = Uio( "/dev/uio/pruss/irq%d" % IRQ )

pruss.initialize()

pruss.intc.ev_ch[EVENT] = IRQ
pruss.intc.ev_clear_one(EVENT)
pruss.intc.ev_enable_one(EVENT)

pruss.core0.load('./intc.bin')
pruss.core0.run()

pruss.intc.out_enable_one(IRQ)

irq.irq_recv()
event = pruss.intc.out_event[IRQ]
print("Received event {}".format(event))
pruss.intc.ev_clear_one(event)

while not pruss.core0.halted:
    pass

