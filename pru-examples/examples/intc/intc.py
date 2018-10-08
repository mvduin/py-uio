#!/usr/bin/python3
""" intc.py - test script for receiving interrupts from PRU 0 using PyUIO library """
from pyuio.ti.icss import Icss
from pyuio.uio import Uio


IRQ = 2           # range 2 .. 9 (IRQ = Interrupt ReQuest)
EVENTS = [19, 20]

pruss = Icss("/dev/uio/pruss/module")
irq = Uio( "/dev/uio/pruss/irq%d" % IRQ )

pruss.initialize()

for event in EVENTS:
    pruss.intc.ev_ch[event] = IRQ
    pruss.intc.ev_clear_one(event)
    pruss.intc.ev_enable_one(event)

pruss.core0.load('./intc.bin')
pruss.core0.run()

loop = 0
while loop < 2:
    pruss.intc.out_enable_one(IRQ)
    irq.irq_recv()
    event = pruss.intc.out_event[IRQ]
    print("Received event {}".format(event))
    pruss.intc.ev_clear_one(event)
    loop += 1

while not pruss.core0.halted:
    pass

