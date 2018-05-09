#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

import asyncio
from uio import Uio

loop = asyncio.get_event_loop()

pin = Uio( "/dev/uio/gpio-irq", blocking=False )
pin.irq_enable()

def irq_callback():
    pin.irq_recv()
    print( "Ping!" )

    # If the irq is level-triggered instead of edge-triggered, you should
    # ensure that it is no longer asserted before reenabling it, otherwise
    # it will just immediately trigger again.
    pin.irq_enable()

loop.add_reader( pin.fileno(), irq_callback )

loop.run_forever()
