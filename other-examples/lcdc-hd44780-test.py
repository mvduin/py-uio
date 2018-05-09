#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from uio import Uio
from ti.subarctic.lcdc import Lcdc, lcdc_fck
from time import sleep

uio = Uio( "/dev/uio/lcdc" )
lcdc = uio.map( Lcdc )

# lcdc functional clock rate
fck = lcdc_fck()
print( "lcdc_fck = %f MHz" % (fck/1e6) )

# global config
lcdc.clock_div = 6  # FIXME pick suitable value
lcdc.pinmux = 0     # rfb

# memory clock rate
mck = fck / lcdc.clock_div
print( "lcdc_mck = %f MHz  (1 cycle = %f ns)" % (mck/1e6, 1e9/mck) )

# sanity checks
if fck > 252000000:
    raise RuntimeError('lcdc functional clock exceeds max spec')
if mck > 126000000:
    raise RuntimeError('lcdc memory clock exceeds max spec')
elif mck > 42000000 and lcdc.pinmux == 0:
    raise RuntimeError('lcdc memory clock exceeds max spec for rfb mode')

rfb = lcdc.rfb
rfb.protocol = 4    # hd44780

cs = rfb.cs0
# all timings are in mck cycles
# FIXME pick suitable values
cs.cs_delay  = 0
cs.wr_setup  = 1    # (0-31) write setup cycles
cs.wr_strobe = 1    # (1-63) write strobe cycles
cs.wr_hold   = 1    # (1-15) write hold cycles
cs.rd_setup  = 1    # (0-31) read setup cycles
cs.rd_strobe = 1    # (1-63) read strobe cycles
cs.rd_hold   = 1    # (1-15) read hold cycles

lcdc.en_rfb = True

# initialize 4-bit interface
for i in 15000, 5000, 100, 100:
    cs.cmd = 0x30
    sleep( i / 1e6 )
cs.cmd = 0x20

def cmd( value, wait=True ):
    cs.cmd = value
    cs.cmd = value << 4
    if not wait:
        return
    status = cs.status & 0xf0
    status |= cs.status >> 4
    while status & 0x80:
        status = cs.status & 0xf0
        status |= cs.status >> 4
    return status & 0x7f

cmd( 0x28 )  # 2 lines, 5x8 pixel characters

def display_onoff( display, cursor, blink ):
    return cmd( 0x08 | display << 2 | cursor << 1 | blink )

def clear_display():
    return cmd( 0x01 )

def return_home():
    return cmd( 0x02 )

# what
CURSOR  = 0
DISPLAY = 1

# direction
LEFT    = 0
RIGHT   = 1

def autoshift( what, direction ):
    return cmd( 0x04 | direction << 1 | what )

def shift( what, direction ):
    return cmd( 0x10 | what << 3 | direction << 2 )

def cgram( address ):
    assert address in range(0x40)
    return cmd( 0x40 | address )

def ddram( x, y ):
    assert x in range(0x28) and y in range(2)
    return cmd( 0x80 | y << 6 | x )

def write( *values ):
    for value in values:
        cs.data = value
        cs.data = value << 4

def read( count ):
    values = []
    for i in range(count):
        value = cs.data & 0xf0
        value |= (cs.data & 0xf0) >> 4
        values.append( value )
    return values
