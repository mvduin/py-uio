#!/usr/bin/python3

import sys
sys.path.insert( 0, '../src' )

from uio import fix_ctypes_struct
from ti.icss import Icss
import ctypes
from ctypes import c_uint32 as uint, c_uint16 as ushort
from time import sleep

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()
ddr = pruss.ddr

core = pruss.core0
core.load( 'fw/stream.bin' )

class Message( ctypes.Structure ):
    _fields_ = [
            ( 'id',     uint ),
        ]
MSGLEN = ctypes.sizeof( Message )

# local copies of read/write-pointers
rptr = 0
wptr = rptr

# variables in ddr memory which are written by pru core
# located immediately after the message-buffer
class PruVars( ctypes.Structure ):
    _fields_ = [
            ( 'wptr',   uint ),
        ]

# variables in pru local ram which are written by arm core
class ArmVars( ctypes.Structure ):
    _fields_ = [
            ( 'rptr',   uint ),
            ( 'delay',  ushort ),
        ]

# leave enough space at end for pru variables
MSGCOUNT = ( ddr.size - ctypes.sizeof( PruVars ) ) // MSGLEN
BUFLEN = MSGCOUNT * MSGLEN

# map message buffer and variables
buf = ddr.map( length = BUFLEN )
pru = ddr.map( PruVars, offset = BUFLEN )
arm = core.dram.map( ArmVars )

# pass buffer info to core and initialize variables
core.r4 = pruss.ddr.address
core.r5 = BUFLEN
pru.wptr = wptr
arm.rptr = rptr
arm.delay = 4000

# to check message ids increment monotically
nextid = 1

def recv_message():
    global rptr, nextid

    # read message from memory
    msg = Message.from_buffer_copy( buf, rptr )

    # update buffer pointer
    rptr += MSGLEN
    if rptr == BUFLEN:
        rptr = 0
    arm.rptr = rptr

    # check message id sequence
    assert msg.id == nextid
    nextid = ( nextid + 1 ) & 0xffffffff

# ready, set, go!
core.run()

while not core.halted:
    wptr = pru.wptr
    while wptr != rptr:
        recv_message()
    sleep( 0.01 )

sys.exit( "buffer overflow!  id=%d" % nextid )
