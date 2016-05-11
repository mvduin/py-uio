from uio import Uio
from pathlib import Path
import ctypes
from ctypes import c_uint32 as uint
from .qep import Qep

class Regs( ctypes.Structure ):
    _fields_ = [
            ("ident",       uint),
            # 0x47400001  subarctic 2.1
            ("sysconfig",   uint),
            ("cap_clkreq",  uint,  4),
            ("qep_clkreq",  uint,  4),
            ("pwm_clkreq",  uint,  4),
            ("",            uint, 20),
            ("cap_clkack",  uint,  4),
            ("qep_clkack",  uint,  4),
            ("pwm_clkack",  uint,  4),
        ]

    # clkreq/clkack values:
    #   0 = disabled without clock stop request (rude?)
    #   1 = enabled  (default)
    #   3 = enabled, request clock stop
    #   2 = disabled
    #
    # It is not really clear to me whether the modules do anything with a clock
    # stop request other than immediately acknowledging it.  At least QEP seems
    # to remain fully operational while clock stop is requested and acked.
    #
    # The kernel code for this never bothers with clock stop request and only
    # uses clkreq values 0 and 1 (without bothering to even check clkack).
    #
    # When a submodule's clock is disabled, any attempt to access its registers
    # doesn't merely result in a bus error but also seems to result in death of
    # the whole subsystem, rendering it unusable.  (Most likely what's happening
    # is that the request is passed to the module even though it's not clocked,
    # eventually resulting in a timeout by the L4 target agent.  This means it
    # may be recoverable by clearing the error in the target agent... I'll try
    # that when I find the time.)

class Pwmss( Uio ):
    def __init__( self, path ):
        path = Path( '/dev/uio', path )
        if not path.is_dir():
            raise ValueError( "Not a directory: %s" % path )
        super().__init__( path/'module' )

        self.regs = self.map( Regs )

        # submodule devices (created lazily)
        self._qep = None
        self._cap = None
        self._pwm = None

    @property
    def qep( self ):
        if not self._qep:
            self.regs.qep_clkreq = 1
            if self.regs.qep_clkack != 1:
                raise RuntimeError( "submodule clock failure?" )
            self._qep = Qep( self.path.parent/'qep', parent=self )
        return self._qep
