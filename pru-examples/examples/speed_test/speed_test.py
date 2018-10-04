from __future__ import print_function

import pypruss
import os

print("This example toggles pin P8.12 as fast as it can, 5ns pr cycle.")
print("It muxes the pin to mode 6 and does not stop, so use Ctrl-c to end the script.")

os.system("echo 6 > /sys/kernel/debug/omap_mux/gpmc_ad12")

pypruss.modprobe()
pypruss.init()                                      # Init the PRU
pypruss.open(0)                                     # Open PRU event 0 which is PRU0_ARM_INTERRUPT
pypruss.pruintc_init()                              # Init the interrupt controller
pypruss.exec_program(0, "./speed_test.bin")         # Load firmware "blinkled.bin" on PRU 0
pypruss.wait_for_event(0)                           # Wait for event 0 which is connected to PRU0_ARM_INTERRUPT
