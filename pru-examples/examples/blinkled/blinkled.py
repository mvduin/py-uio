#!/usr/bin/python3
""" blinkled.py - test script for the pyuio library
It blinks the user leds ten times
"""
from pyuio.ti.icss import Icss

pruss = Icss('/dev/uio/pruss/module')
pruss.initialize()

pruss.core0.load('./blinkled.bin')
pruss.core0.run()
print("Waiting for core to halt")
while not pruss.core0.halted:
    pass
print("Blinking finished")
