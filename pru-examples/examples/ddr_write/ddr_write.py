""" ddr_write.py - Finds the DDR address and size, passes that info to the PRU0
data memory, executes a program and reads back data from the first and last banks
"""

from __future__ import print_function

import pypruss
import mmap
import struct

pypruss.modprobe()
ddr_addr = pypruss.ddr_addr()
ddr_size = pypruss.ddr_size()

print("DDR memory address is 0x%x and the size is 0x%x" % (ddr_addr, ddr_size))

ddr_offset = ddr_addr - 0x10000000
ddr_filelen = ddr_size + 0x10000000
ddr_start = 0x10000000
ddr_end = 0x10000000 + ddr_size

pypruss.init()                                                      # Init the PRU
pypruss.open(0)                                                     # Open PRU event 0 which is PRU0_ARM_INTERRUPT
pypruss.pruintc_init()                                              # Init the interrupt controller
pypruss.pru_write_memory(0, 0, [ddr_addr, ddr_addr + ddr_size - 4]) # Put the ddr address in the first region
pypruss.exec_program(0, "./ddr_write.bin")                          # Load firmware "ddr_write.bin" on PRU 0
pypruss.wait_for_event(0)                                           # Wait for event 0 which is connected to PRU0_ARM_INTERRUPT
pypruss.clear_event(0, pypruss.PRU0_ARM_INTERRUPT))                 # Clear the event
pypruss.exit()                                                      # Exit PRU

with open("/dev/mem", "r+b") as f:                                  # Open the physical memory device
    ddr_mem = mmap.mmap(f.fileno(), ddr_filelen, offset=ddr_offset)  # mmap the right area

read_back = struct.unpack("L", ddr_mem[ddr_start:ddr_start + 4])[0]  # Parse the data
read_back2 = struct.unpack("L", ddr_mem[ddr_end - 4:ddr_end])[0]        # Parse the data

print("The first 4 bytes of DDR memory reads " + hex(read_back))
print("The last 4 bytes of DDR memory reads " + hex(read_back2))

ddr_mem.close()                                                     # Close the memory
f.close()                                                           # Close the file
