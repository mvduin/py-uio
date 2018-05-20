#!/usr/bin/python3

# Example for testing spi communication with a pru spi slave.
#
# This example is designed for the beagleboard-x15.  See
# dts/bbx15-spi-test.dtsi for details.  It can probably be
# adapted to the beaglebone without too much difficulty.

import sys
sys.path.insert( 0, '../src' )

from ti.icss import Icss
import random

pruss = Icss( "/dev/uio/pruss2/module" )
pruss.initialize()

core = pruss.core0
core.load( 'fw/bbx15-spi-test.bin' )
core.run()


import ctypes
from fcntl import ioctl

# linux/spi/spidev.h
class SpiTransfer( ctypes.Structure ):
    _fields_ = [
            ('tx_buf',          ctypes.c_uint64),
            ('rx_buf',          ctypes.c_uint64),
            ('len',             ctypes.c_uint32),
            ('speed_hz',        ctypes.c_uint32),
            ('delay_usecs',     ctypes.c_uint16),
            ('bits_per_word',   ctypes.c_uint8),
            ('cs_change',       ctypes.c_uint8),
            ('',                ctypes.c_uint32),
        ]
def SPI_IOC_MESSAGE( n ):
    assert n in range(0x200)
    return 0x40006b00 + 0x200000 * n

# perform transfer
num_bytes = 32
txdata = (ctypes.c_uint8 * num_bytes)()
txdata[:] = random.choices( range(256), k=num_bytes )
rxdata = (ctypes.c_uint8 * num_bytes)()
with open( "/dev/spidev3.1", "rb+", buffering=0 ) as f:
    xfer = SpiTransfer()
    xfer.tx_buf = ctypes.addressof( txdata )
    xfer.rx_buf = ctypes.addressof( rxdata )
    xfer.len    = num_bytes
    xfer.bits_per_word = 8
    ioctl( f, SPI_IOC_MESSAGE(1), xfer )

# validate received data
errdata = []
state = 0
for i in range( num_bytes ):
    state = state << 8 | txdata[ i ]
    state ^= rxdata[ i ] << 1 ^ rxdata[ i ] << 2
    errdata.append( state >> 2 )
    state &= 3

def popcount8( x ):
    assert x in range(256)
    x = ( x & 0x55 ) + ( x >> 1 & 0x55 )
    x = ( x & 0x33 ) + ( x >> 2 & 0x33 )
    x = ( x & 0x0f ) + ( x >> 4 & 0x0f )
    return x

n_errors = sum( map( popcount8, errdata ) )

if n_errors:
    msg = "%d bit errors:\n" % n_errors
    msg += "\t" + "".join( "%02x" % x for x in errdata )
    sys.exit( msg )

print( "Test passed!" )
