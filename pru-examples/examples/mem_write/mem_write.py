#!/usr/bin/python3
""" mem_write.py - test script for writing and reading from PRU 0 mem using PyUIO library """
from pyuio.ti.icss import Icss
from pyuio.uio import Uio


IRQ = 2     # range 2 .. 9
EVENT0 = 19 # range 16 .. 31

pruss = Icss("/dev/uio/pruss/module")
irq = Uio( "/dev/uio/pruss/irq%d" % IRQ )

pruss.initialize()

pruss.intc.ev_ch[EVENT0] = IRQ
pruss.intc.ev_clear_one(EVENT0)
pruss.intc.ev_enable_one(EVENT0)

pruss.core0.load('./mem_write.bin')
data = [10,20]

pruss.core0.dram.write(data, offset = 1)

pruss.core0.run()

pruss.intc.out_enable_one(IRQ)

irq.irq_recv()
event = pruss.intc.out_event[IRQ]
pruss.intc.ev_clear_one(event)

while not pruss.core0.halted:
    pass

byte3 = pruss.core0.dram.map(length = 1, offset = 3)[0]
assert sum(data) == byte3
print("Test succesfull")
