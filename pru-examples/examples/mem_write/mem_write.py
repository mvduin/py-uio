""" mem_write.py - test script for writing to PRU 0 mem using PyPRUSS library """

import pypruss                              # The Programmable Realtime Unit Library
import numpy as np                          # Needed for braiding the pins with the delays

steps = [(7 << 22), 0] * 10                 # 10 blinks, this control the GPIO1 pins
delays = [0xFFFFFF] * 20                    # number of delays. Each delay adds 2 instructions, so ~10ns

data = np.array([steps, delays])            # Make a 2D matrix combining the ticks and delays
data = data.transpose().flatten()           # Braid the data so every other item is a
data = [20] + list(data)                    # Make the data into a list and add the number of ticks total

pypruss.modprobe()                          # This only has to be called once pr boot
pypruss.init()                              # Init the PRU
pypruss.open(0)                             # Open PRU event 0 which is PRU0_ARM_INTERRUPT
pypruss.pruintc_init()                      # Init the interrupt controller
pypruss.pru_write_memory(0, 0, data)        # Load the data in the PRU ram
pypruss.exec_program(0, "./mem_write.bin")  # Load firmware "mem_write.bin" on PRU 0
pypruss.wait_for_event(0)                   # Wait for event 0 which is connected to PRU0_ARM_INTERRUPT
pypruss.clear_event(0, pypruss.PRU0_ARM_INTERRUPT)  # Clear the event
pypruss.exit()                              # Exit
