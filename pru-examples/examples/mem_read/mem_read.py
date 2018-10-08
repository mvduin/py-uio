#!/usr/bin/python3
""" mem_read.py - test script for reading from PRU 0 mem using pyuio library """
from pyuio.ti.icss import Icss
from ctypes import c_uint32

pruss = Icss("/dev/uio/pruss/module")
pruss.initialize()

pruss.core0.load('./mem_read.bin')

pruss.core0.run()

while not pruss.core0.halted:
    pass

pru0mem = pruss.core0.dram.map(c_uint32)
print(hex(pru0mem.value))
pru1mem = pruss.core1.dram.map(c_uint32)
print(hex(pru1mem.value))
sharedmem = pruss.core0.shared_dram.map(c_uint32)
print(hex(sharedmem.value))
shmem = pruss.ddr.map(c_uint32)
print(hex(shmem.value))

