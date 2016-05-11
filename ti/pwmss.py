from uio import Uio
from pathlib import Path
import ctypes
from ctypes import c_uint32 as uint
from .qep import Qep

class Regs( ctypes.Structure ):
    _fields_ = [
            ("ident",       uint),
            ("sysconfig",   uint),
            ("cap_clkreq",  uint,  4),
            ("qep_clkreq",  uint,  4),
            ("pwm_clkreq",  uint,  4),
            ("",            uint, 20),
            ("cap_clkack",  uint,  4),
            ("qep_clkack",  uint,  4),
            ("pwm_clkack",  uint,  4),
        ]

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
