########## Programmable Real-Time Unit (PRU) core ##############################
##
## ICSS has two PRU v3 cores equipped with several XFR components:
##       0  multiplier/MAC  (32 × 32 -> 64-bit, single cycle)
##       1  CRC module  (added in ICSS v1)
##      10  scratch pad 0  (30 words)
##      11  scratch pad 1  (30 words)
##      12  scratch pad 2  (30 words)
##      14  direct core-to-core transfer
##      20  mii-rt L2 ringbuffer (bank 0)
##      21  mii-rt L2 ringbuffer (bank 1)
##
## The scratch pads are shared between the cores, allowing fast data exchange.
## In rare instances they may be omitted.  The MAC, CRC, and mii-rt buffers are
## private for each core.
##
## When mii-rt is present but not used or its L2 ringbuffer is not enabled, XFR
## 20 and 21 can be used as extra scratchpads (12 words each) for R2-R13.
##
##
## R30 and R31 support I/O functionality similar to original PRUSS but with
## more and more features added in subsequent revisions.
##
##
## The memory map for a core is:
##      000'00'000 - 000'3f'fff   local PRU subsystem
##      000'40'000 - 000'7f'fff   linked PRU subsystem (if any)
##      000'80'000 - fff'ff'fff   32-bit master port to L3 (one per core)
##
## Note however that dram0 and dram1 are swapped for core 1, allowing each core
## to access its own data ram at address 0x0.
##
## The cores do not have direct access to debug registers or instruction RAM.
##
## Requests to the master ports can optionally subtract 0x80'000 from addresses
## to allow accessing address range 000'00'000 - fff'7f'fff of the L3.  This
## can be configured per core in the subsystem control module (see icss/cfg.py).
##
## Beware that the master ports are disabled by default and need to be enabled
## via the subsystem control module to avoid lockup.
##
##
## The PRU core has a 32-bit VBUSP slave port with three address spaces:
##      core control registers
##      debug registers
##      instruction ram (iram)
##
## The debug and iram spaces are only accessible when the core is halted.
##
## In PRU-ICSS, the core control and debug register spaces are adjacent, hence
## they are viewed as one structure here.

from uio import cached_getter
import ctypes
from ctypes import ( c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint )

nRESET  = 1 <<  0
RUN     = 1 <<  1
SLEEP   = 1 <<  2
PROFILE = 1 <<  3
SINGLE  = 1 <<  8
EXC     = 1 << 13
BIG_END = 1 << 14
BUSY    = 1 << 15

CONTROL_MASK = nRESET | RUN | SLEEP | PROFILE | SINGLE

class State( int ):
    @property
    def running( self ):
        return bool( self & RUN )

    @property
    def sleeping( self ):
        return bool( self & SLEEP )

    @property
    def profiling( self ):
        return bool( self & PROFILE )

    @property
    def crashed( self ):
        return bool( self & EXC )

    @property
    def halted( self ):
        return not ( self & BUSY )

    def __new__( self, control ):
        if control & RUN:
            control |= BUSY  # probably redundant, but just to be sure
        if control & SINGLE:
            control &= ~RUN
        return int.__new__( self, control )

    def __str__( self ):
        if self.halted:
            s = 'halted'
            if self.crashed:
                s += ', crashed'
        elif self.running:
            s = 'running'
        else:
            s = 'halting'
        if self.sleeping:
            s += ', sleeping'
        if self.profiling:
            s += ', profiling'
        return s


class Core( ctypes.Structure ):
    _fields_ = [
            ("control",     ushort),  #rw
            # bit   0     ru  core initialized; clear to reset core
            # bit   1     rw  core enabled
            # bit   2     ru  core sleeping; clear to force wakeup
            # bit   3     rw  cycle and stall counters enabled
            # bits  4- 7  z-
            # bit   8     rw  single-step mode
            # bit   9-12  z-
            # bit  13     r-  exception occurred
            # bit  14     r-  big endian
            # bit  15     r-  core busy (not halted)
            #
            # After clearing "core enabled" the core halts at the next
            # instruction boundary.  If the core is sleeping, it is necessary
            # to force wakeup to let the sleep instruction complete.  Check the
            # "core busy" flag has cleared to confirm the core has halted.
            #
            # Single-step mode causes the "core enabled" bit to clear and the
            # core to halt after executing one instruction.
            #
            # The halt instruction causes the core to halt on (rather than
            # after) that instruction: neither the program counter nor the
            # cycle counter is advanced.  An invalid instruction behaves
            # similarly but also sets the exception flag.  The exception flag
            # is cleared when the core is reenabled (not when it is reset!).
            #
            # Resetting the core:
            #   - loads reset_pc into cur_pc
            #   - resets the stall and cycle counters
            #   - clears the carry-flag
            #   - resets the hardware loop state
            # It does not seem to affect any other visible state.  In
            # particular, the control register is unaffected, hence writing 2
            # to control will start the core at reset_pc.

            ("reset_pc",    ushort),  #rw  loaded into pc when core is reset
            ("pc",          ushort),  #r-  current program counter
            ("",            ushort),
            ("wake_en",     uint),  #rw  mask of r31 bits that wake up the core


            ("cycles",      uint),  #r>
            ("stalls",      uint),  #r-
            # Cycle counters are automatically disabled after 0xffffffff cycles
            # to prevent overflow.  When either core or counters are disabled,
            # writing any value to the cycle counter clears both counters.
            #
            # While sleeping the counters freeze, presumably due to internal
            # clock gating, and only a single stall cycle is recorded.
            # However, access to registers briefly ungates the core clock and
            # causes additional stall cycles to be recorded.

            ("",            ubyte * (0x20 - 0x14)),


            ("blk",         ushort * 4),  #rw
            ("ptr",         ushort * 4),  #rw
            # blk[i] programs bits 8-11 of register c[24+i]
            # ptr[i] programs bits 8-23 of register c[28+i]

            ("",            ubyte * (0x400 - 0x30)),


            ("r",           uint * 32),  #rw
            ("c",           uint * 32),  #r-
            # Debug access to core registers (only allowed when core is halted)
        ]

    def full_reset( self, pc=0 ):
        self.halt()
        self.reset_pc = pc
        self.control = 0
        assert( ( self.control & ( CONTROL_MASK | BUSY ) ) == nRESET )
        self.wake_en = 0
        self.blk[:] = (0,) * 4
        self.ptr[:] = (0,) * 4
        self.r[:] = (0,) * 32

    def halt( self, *, wakeup=True, check=None ):
        control = self.control
        if not ( control & ( RUN | BUSY ) ):
            return True
        if wakeup:
            control &= ~SLEEP
        else:
            control |= SLEEP
        self.control = control & ~RUN

        for i in range(10):
            if self.halted:
                return True
        if check == None:
            check = wakeup
        if check:
            raise RuntimeError("PRU core failed to halt")
        return False

    def reset( self, *, pc=None ):
        if self.control & ( RUN | BUSY ):
            raise RuntimeError("PRU core is not halted")
        if pc != None:
            self.reset_pc = pc
        self.control = 0

    def run( self, *, pc=None, reset=None, single=False, profile=None ):
        control = self.control
        if control & ( RUN | BUSY ):
            raise RuntimeError("PRU core is not halted")
        if profile == None:
            profile = bool( control & PROFILE )
        if reset == None:
            reset = pc != None
        if pc != None and pc != self.pc and not reset:
            raise RuntimeError("Cannot change pc without resetting core")

        if pc != None:
            self.reset_pc = pc

        if reset:
            self.control = 0

        control = nRESET | RUN
        if single:
            control |= SINGLE
        if profile:
            control |= PROFILE
        self.control = control

    def step( self, **kwargs ):
        self.run( single=True, **kwargs )

    @property
    def halted( self ):
        return not ( self.control & ( RUN | BUSY ) )

    @property
    def state( self ):
        return State( self.control )

    @property
    def profiling( self ):
        return bool( self.control & PROFILE )

    @profiling.setter
    def profiling( self, value ):
        control = self.control | SLEEP
        if control & SINGLE:
            control &= ~RUN
        if value:
            control |= PROFILE
        else:
            control &= ~PROFILE
        self.control = control

    @cached_getter
    def _profiling( self ):
        return ctypes.c_uint64.from_buffer( self, 0x0c )

    def profiling_sample( self ):
        # Sample cycles and stalls near-simultaneously (single 64-bit read).
        # It takes 3 pru cycles to sample each field, therefore you should add
        # 3 to cycles if you call this method while the counters are running to
        # compensate for the time passed before stalls was sampled.  Also keep
        # in mind that the counters are not accurately maintained when sleeping.
        x = self._profiling.value
        cycles = x & 0xffffffff
        stalls = x >> 32
        return (cycles, stalls)
