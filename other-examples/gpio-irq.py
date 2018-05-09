#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from uio import Uio

pin = Uio( "/dev/uio/gpio-irq" )
pin.irq_enable()

while True:
    pin.irq_recv()
    print( "Ping!" )

    # If the irq is level-triggered instead of edge-triggered, you should
    # ensure that it is no longer asserted before reenabling it, otherwise
    # it will just immediately trigger again.
    pin.irq_enable()
