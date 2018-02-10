import ctypes
from ctypes import ( c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint )

# icss pru core

class Core( ctypes.Structure ):
    _fields_ = [
            ("control",     ushort),  #rw
            ("reset_pc",    ushort),  #rw  loaded into pc when core is reset
            ("pc",          ushort),  #r-  current program counter
            ("",            ushort),

            ("wake_en",     uint),  #rw  mask of r31 bits that may wake up the core

            ("cycles",      uint),  #r>
            ("stalls",      uint),  #r-

            ("",            ubyte * (0x20 - 0x14)),

            ("blk",         ushort * 4),  #rw  blk[i] programs bits 8-11 of register c[24+i]
            ("ptr",         ushort * 4),  #rw  ptr[i] programs bits 8-23 of register c[28+i]

            ("",            ubyte * (0x400 - 0x30)),

            # debug access to registers (only when core is halted)
            ("r",           uint * 32),  #rw
            ("c",           uint * 32),  #r-
        ]

    def full_reset( self, pc=0 ):
        self.reset_pc = pc
        self.control = 0
        assert( self.control == 1 )
        self.wake_en = 0
        self.cycles = 0
        self.blk[:] = (0,) * 4
        self.ptr[:] = (0,) * 4
        self.r[:] = (0,) * 32

    def run( self ):
        self.control |= 1 << 1

    @property
    def halted( self ):
        return not ( self.control & (1 << 15) )
