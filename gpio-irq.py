#!/usr/bin/python3

from uio import Uio

pin = Uio( "gpio-irq" )
pin.irq_enable()

pin.irq_recv()
print( "Ping!" )
