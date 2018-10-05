#!/usr/bin/python3
""" mem_write.py - test script for writing to PRU 0 mem using PyUIO library """
from pyuio.ti.icss import Icss
from pyuio.uio import Uio
from ctypes import c_uint32


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

pru0mem = pruss.core0.dram.map(length = len(data), offset = 1)
for idx in range(0,len(data)):
    pru0mem[idx] = data[idx]

pruss.core0.run()

pruss.intc.out_enable_one(IRQ)

irq.irq_recv()
event = pruss.intc.out_event[IRQ]
pruss.intc.ev_clear_one(event)


while not pruss.core0.halted:
    pass

pru0mem = pruss.core0.dram.map(length = 1, offset = 3)
assert sum(data) == pru0mem[0]
print("Test succesfull")
