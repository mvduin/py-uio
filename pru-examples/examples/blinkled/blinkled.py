""" blinkled.py - test script for the PyPRUSS library
It blinks the user leds ten times
"""
#!/usr/bin/python3

from pyuio.ti.icss import Icss

pruss = Icss('/dev/uio/pruss/module')
pruss.initialize()

core = pruss.core0
# load program
core.load('./blinkled.bin')
core.run()
print("Waiting for core to halt")
while not core.halted:
    pass
print("Blinking finished")
