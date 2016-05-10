#!/usr/bin/python3

import asyncio
from uio import Uio

loop = asyncio.get_event_loop()

pin = Uio( "p9.12-irq", blocking=False )

def irq_callback():
    pin.irq_recv()
    print( "Ping!" )
    loop.stop()

loop.add_reader( pin.fileno(), irq_callback )

pin.irq_enable()

loop.run_forever()
