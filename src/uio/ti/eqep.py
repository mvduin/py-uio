from uio.utils import fix_ctypes_struct
import ctypes
from ctypes import c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint
from .eirq import EIrq

pos_t = uint    # position counter
tim_t = uint    # unit timer
wdt_t = ushort  # watchdog timer
imt_t = ushort  # interval measurement timer

@fix_ctypes_struct
class EQep( ctypes.Structure ):
    _fields_ = [
            #-------- position counter --------------------------------------------
            #
            ("position",        pos_t),     #<w
            ("ld_position",     pos_t),     #rw  loaded into position on strobe/index if enabled
            ("maximum",         pos_t),     #rw  = period - 1
            ("compare",         pos_t),     #rw  (may be ld_compare depending on config)

            ("index_latch",     pos_t),     #r-
            ("strobe_latch",    pos_t),     #r-
            ("timer_latch",     pos_t),     #r-

            #-------- unit timer (frequency measurement base) ---------------------
            #
            ("timer_counter",   tim_t),     #rw
            ("timer_maximum",   tim_t),     #rw  = period - 1

            #-------- watchdog timer (motor stall detection) ----------------------
            #
            # increments on module clock / 64.
            # resets on every position counter change.
            #
            ("wdog_counter",    wdt_t),     #rw
            ("wdog_compare",    wdt_t),     #rw

            #-------- configuration -----------------------------------------------
            #
            ("io_config",       ushort),
            # bits  0- 4  z-
            # bit   5     rw  invert strobe input
            # bit   6     rw  invert index input
            #
            # bit   7     rw  invert input B
            # bit   8     rw  invert input A
            #
            # bit   9     rw  gate index using strobe
            #
            # bit  10     rw  (qd) swap A/B inputs (invert direction)
            # bit  11     rw  (non-qd) count on:  0 both edges  1 rising edge
            #
            # bit  12     rw  compare-output to:  0 index pin  1 strobe pin
            # bit  13     rw  compare-output enabled
            #
            # bits 14-15  rw  counter mode:
            #                   0  quadrature decoding of A/B
            #                   1  up(B=1)/down(B=0) counting on A
            #                   2  up counting on A
            #                   3  down counting on A
            #
            # In quadrature mode, the decoder issues up/down events based on
            # transitions of inputs A/B.  Bit 11 has no effect in this mode.
            # Bits 7, 8, and 10 all have equivalent function of inverting dir.
            #
            # The non-quadrature modes combine an event source:
            #       0 << 11             any edge of input A
            #       1 << 11 | 0 << 8    rising edge of input A
            #       1 << 11 | 1 << 8    falling edge of input A
            # with a direction:
            #       1 << 14 | 0 << 7    down if B=0,  up   if B=1
            #       1 << 14 | 1 << 7    up   if B=0,  down if B=1
            #       2 << 14             up   regardless of B
            #       3 << 14             down regardless of B
            #
            # Bit 10 has no effect in non-quadrature modes.

            ("ctr_config",      ushort),
            # bit   0     rw  watchdog timer enabled
            # bit   1     rw  unit timer enabled
            # bit   2     rw  latch imt on:  0 position read  1 unit period
            # bit   3     rw  position counter enabled
            # bits  4- 5  rw  latch position on index mode
            #                   1 latch position on rising edge of index
            #                   2 latch position on falling edge of index
            #                   3 latch position on index marker
            # bit   6     rw  latch position on strobe edge
            #                   0 rising edge
            #                   1 direction-dependent
            # bit   7     rw  load position now (XXX does it auto-clear?)
            # bit   8     rw  load position on index edge:  0 rising  1 falling
            # bit   9     rw  load position on index enabled
            # bit  10     rw  load position on strobe edge:  (see latch on strobe)
            # bit  11     rw  load position on strobe enabled
            # bits 12-13  rw  reset position on
            #                   0 index event
            #                   1 (disabled)
            #                   2 first index event
            #                   3 unit timer event
            # bit  14     rw  emu soft suspend (counters run till zero)
            # bit  15     rw  emu-free (bit 14 ignored)

            ("imt_config",      ushort),
            # bits  0- 3  rw  imt position event prescaler, log2 (0..11)
            # bits  4- 6  rw  imt counter prescaler, log2
            # bit  15     rw  imt enabled

            ("cmp_config",      ushort),
            # bits  0-11  rw  output pulse width (cycles / 4 - 1)
            # bit  12     rw  position-compare enabled
            # bit  13     rw  invert output
            # bit  14     rw  load compare on  0 position zero  1 compare register
            # bit  15     rw  load compare enabled

            #-------- status / event reporting ------------------------------------
            #
            ("irq",             EIrq),
            # bit   0     (pending) irq active / (clear) eoi
            #
            # bit   1     position counter error
            # bit   2     quadrature decoder error (A and B toggled at same time)
            # bit   3     direction change event
            # bit   4     watchdog timeout
            # bit   5     position counter underflow
            # bit   6     position counter overflow
            # bit   7     compare load event
            # bit   8     compare event
            # bit   9     strobe latch event
            # bit  10     index latch event
            # bit  11     timer event

            ("status",          ushort),
            # bit   0     r-  position counter error (updated on index)
            # bit   1     rc  first index event
            # bit   2     rc  direction change event
            # bit   3     rc  imt overflow event
            # bit   4     r-  direction of last index
            # bit   5     r-  direction of last position change
            # bit   6     r-  direction of first index
            # bit   7     rc  imt capture event

            #-------- interval measurement timer (aka "capture timer") ------------
            #
            # increments on prescaled module clock.
            # counter is captured and reset on prescaled position event.
            # counter and capture are latched on position read or unit timer event.
            #
            ("imt_counter",     imt_t),     #rw
            ("imt_capture",     imt_t),     #r-
            ("imt_counter_latch", imt_t),   #r-
            ("imt_capture_latch", imt_t),   #r-

            ("", ubyte * (0x5c - 0x42)),

            #-------- identification ----------------------------------------------
            #
            ("ident",           uint),      #r-
            #
            #   0x4_4d3_11_03  (v1.3.2 on subarctic 2.1)
        ]

    def reset( self ):
        self.irq.enabled = 0
        self.imt_config = 0
        self.ctr_config = 0
        self.io_config = 0
        self.cmp_config = 0
        self.status = 0xffff
        self.irq.clear( 0xffff )
        self.position = 0
        self.ld_position = 0
        self.maximum = 0xffffffff
        self.compare = 0
        self.timer_counter = 0
        self.timer_maximum = 0xffffffff
        self.wdog_counter = 0
        self.wdog_compare = 0
        self.imt_counter = 0

EQep.ld_compare = EQep.compare

assert ctypes.sizeof(EQep) == 0x60
