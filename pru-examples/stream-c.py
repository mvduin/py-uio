#!/usr/bin/python3

from uio.utils import fix_ctypes_struct
from uio.ti.icss import Icss
import ctypes
from ctypes import c_uint32 as u32, c_uint16 as u16
from time import sleep
from sys import exit

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()
ddr = pruss.ddr

core = pruss.core0
core.load( 'fw-c/stream.out' )

class Message( ctypes.Structure ):
    _fields_ = [
            ( 'id',     u32 ),
        ]

# used to communicate ddr layout to C program
class DDRLayout( ctypes.Structure ):
    _fields_ = [
            ( 'msgbuf',      u32 ),
            ( 'num_msgs',    u16 ),
            ( 'msg_size',    u16 ),
        ]

# volatile variables in pruss shared memory
class SharedVars( ctypes.Structure ):
    _fields_ = [
            ( 'abort_file', u32 ),
            ( 'abort_line', u32 ),

            ( 'ridx',       u16 ),
        ]

# if you don't want the ringbuffer at the start of the ddr region, specify offset here
MSGBUF_OFFSET = 0

# you can use a fixed ringbuffer size:
#NUM_MSGS = 1024
# or you can scale the ringbuffer to fit the size of the ddr region:
NUM_MSGS = ( ddr.size - MSGBUF_OFFSET - ctypes.sizeof( u16 ) ) // ctypes.sizeof( Message )
NUM_MSGS = min( NUM_MSGS, 65535 )  # make sure number of messages fits in u16

# map shared memory variables
ddr_layout = core.map( DDRLayout, 0x10000 )
shmem = core.map( SharedVars, 0x10100 )
msgbuf = ddr.map( Message * NUM_MSGS, MSGBUF_OFFSET )
ddr_widx = ddr.map( u16, MSGBUF_OFFSET + ctypes.sizeof( msgbuf ) )

# inform pru about layout of shared ddr memory region
ddr_layout.msgbuf       = ddr.address + MSGBUF_OFFSET
ddr_layout.num_msgs     = NUM_MSGS
ddr_layout.msg_size     = ctypes.sizeof( Message )

# local copy of read-pointer
ridx = 0

# initialize pointers in shared memory
shmem.ridx = ridx
ddr_widx.value = ridx

# ready, set, go!
core.run()

def check_core():
    if not core.halted:
        return

    if core.state.crashed:
        msg = f'core crashed at pc={core.pc}'
    elif shmem.abort_file == 0:
        msg = f'core halted at pc={core.pc}'
    else:
        # FIXME figure out better way to read C-string from PRU memory
        abort_file = core.read( ctypes.c_char * 32, shmem.abort_file ).value
        abort_file = abort_file.decode("ascii")
        msg = f'core aborted at pc={core.pc} ({abort_file}:{shmem.abort_line})'

    # dump some potentially interesting information:
    msg += f'\n   ridx       = {ridx}'
    msg += f'\n   shmem.ridx = {shmem.ridx}'
    msg += f'\n   ddr_widx   = {ddr_widx.value}'

    exit( msg )

lastid = 0

def recv_messages():
    global ridx, lastid

    while ridx != ddr_widx.value:
        # note: it may be faster to copy a batch of messages from shared memory
        # instead of directly accessing individual messages and their fields.
        msg = msgbuf[ ridx ]

        # sanity-check that message id increments monotonically
        lastid = ( lastid + 1 ) & 0xffffffff
        assert msg.id == lastid

        # consume message and update read pointer
        del msg  # direct access to message forbidden beyond this point
        ridx += 1
        if ridx == NUM_MSGS:
            ridx = 0
        shmem.ridx = ridx

    print( f'\ridx=0x{ridx:04x} id=0x{lastid:08x} ', end='', flush=True )


try:
    while True:
        recv_messages()
        check_core()

        sleep( 0.01 )

except KeyboardInterrupt:
    pass

finally:
    print( '', flush=True )
    core.halt()
