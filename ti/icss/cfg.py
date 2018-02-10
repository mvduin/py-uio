import ctypes
from ctypes import c_uint32 as uint

# icss configuration module

IDLEMODES = ['force', 'block', 'auto']

class Cfg( ctypes.Structure ):
    _fields_ = [
            ("ident",        uint),

            # sysconfig
            ("_idlemode",    uint,  2),
            ("_standbymode", uint,  2),
            ("standbyreq",   uint,  1),
            ("mwait",        uint,  1),
            ("",             uint, 26),

            ("ioconfig0",    uint),  # pru 0 io config
            ("ioconfig1",    uint),  # pru 1 io config

            ("clockgate",    uint),

            # parity error irqs
            ("irq_enabled",  uint),
            ("irq_pending",  uint),
            ("_irq_clear",   uint),
            ("_irq_set",     uint),

            ("prio",         uint),  # local interconnect config
            ("ocp",          uint),  # ocp master port config
            ("intc",         uint),  # interrupt routing config
            ("iep",          uint),  # iep clock config
            ("pad",          uint),  # scratchpad config
        ]

    @property
    def idlemode( self ):
        return IDLEMODES[ self._idlemode ]

    @idlemode.setter
    def idlemode( self, value ):
        self._idlemode = IDLEMODES.index( value )

    @property
    def standbymode( self ):
        return IDLEMODES[ self._standbymode ]

    @standbymode.setter
    def standbymode( self, value ):
        self._standbymode = IDLEMODES.index( value )
