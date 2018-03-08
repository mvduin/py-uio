from uio import Uio
import ctypes
from ctypes import c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint

pos_t = uint    # position counter
tim_t = uint    # unit timer
wdt_t = ushort  # watchdog timer
imt_t = ushort  # interval measurement timer
irq_t = ushort  # irq bits

class Regs( ctypes.Structure ):
    _fields_ = [
	    #-------- position counter --------------------------------------------
	    #
            ("position",        pos_t),     #<w
            ("ld_position",     pos_t),     #rw  loaded into counter on strobe/index if enabled
            ("maximum",         pos_t),     #rw  = period - 1
            ("compare",         pos_t),     #rw  (may be ld_compare depending on config)

            ("index_latch",     pos_t),     #r-
            ("strobe_latch",    pos_t),     #r-
            ("timer_latch",     pos_t),     #r-

	    #-------- unit timer (frequency measurement base) ---------------------
	    #
            ("timer_counter",   tim_t),     #rw
            ("timer_maximum",   tim_t),     #rw

	    #-------- watchdog timer (motor stall detection) ----------------------
	    #
	    # increments on module clock / 64.
	    # resets on every position counter change.
	    #
            ("wdog_counter",    wdt_t),     #rw
            ("wdog_compare",    wdt_t),     #rw

	    #-------- configuration -----------------------------------------------
            #
            ("io_config",       ushort),    #rw
            ("ctr_config",      ushort),    #rw
            ("imt_config",      ushort),    #rw
            ("cmp_config",      ushort),    #rw

	    #-------- status / event reporting ------------------------------------
            #
            ("irq_enabled",     irq_t),     #rw
            ("irq_pending",     irq_t),     #r-
            ("irq_clear",       irq_t),     #-c
            ("irq_set",         irq_t),     #-s

            ("status",          ushort),    #rc

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

assert ctypes.sizeof(Regs) == 0x60


class EQep( Uio ):
    def __init__( self, *args, **kwds ):
        super().__init__( *args, **kwds )

        self.regs = self.map( Regs )
