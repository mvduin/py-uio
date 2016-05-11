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
            ("position",    pos_t),
            ("ld_position", pos_t),
            ("maximum",     pos_t),
            ("compare",     pos_t),   # or ld_compare depending on config
            ("index_latch", pos_t),
            ("strobe_latch", pos_t),
            ("timer_latch", pos_t),

            ("timer_counter", tim_t),
            ("timer_maximum", tim_t),

            ("wdog_counter", wdt_t),
            ("wdog_compare", wdt_t),

            ("io_config",   ushort),
            ("ctr_config",  ushort),
            ("imt_config",  ushort),
            ("cmp_config",  ushort),

            ("irq_enabled", irq_t),
            ("irq_pending", irq_t),
            ("_irq_clear",  irq_t),
            ("_irq_set",    irq_t),

            ("status",      ushort),

            ("imt_counter", imt_t),
            ("imt_capture", imt_t),
            ("imt_counter_latch", imt_t),
            ("imt_capture_latch", imt_t),

            ("", ubyte * (0x5c - 0x42)),

            ("ident",       uint),
        ]

    def irq_clear( self, bits ):
        self._irq_clear = bits

    def irq_set( self, bits ):
        self._irq_set = bits

assert ctypes.sizeof(Regs) == 0x60

class Qep( Uio ):
    def __init__( self, *args, **kwds ):
        super().__init__( *args, **kwds )

        self.regs = self.map( Regs )
