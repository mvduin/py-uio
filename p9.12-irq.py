#!/usr/bin/python3

from uio import Uio
from time import sleep

pin = Uio( "p9.12-irq" )
pin.irq_enable()

pin.irq_recv()
print( "Ping!" )
