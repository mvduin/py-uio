from uio.device import Uio
from uio.utils import fix_ctypes_struct
from pathlib import Path
import ctypes
from ctypes import c_uint32 as u32
from .ecap import ECap
from .eqep import EQep
from .epwm import EPwm

@fix_ctypes_struct
class Cfg( ctypes.Structure ):
    _fields_ = [
            ("ident",       u32),
            # 0x4_740_00_01  subarctic 2.1

            ("sysconfig",   u32),
            # bit   0     rx  reset
            # bit   1     rw  emu-free
            # bits  2- 3  rw  idlemode  (no wakeup support, default is auto)

            ("_clkreq",     u32),  # rw
            ("_clkack",     u32),  # r-
            # bit   0     cap: clock enable (set by default)
            # bit   1     cap: clock stop
            # bits  2- 3  -
            # bit   4     qep: clock enable (set by default)
            # bit   5     qep: clock stop
            # bits  6- 7  -
            # bit   8     pwm: clock enable (set by default)
            # bit   9     pwm: clock stop
            #
            # Disabling submodule clocks is deprecated, just leave this alone.
        ]

class Pwmss( Uio ):
    def __init__( self, path ):
        path = Path( '/dev/uio', path )
        if not path.is_dir():
            raise ValueError( "Not a directory: %s" % path )

        super().__init__( path )

        self.cfg = self.map( Cfg )
        assert self.cfg._clkreq == 0x111
        assert self.cfg._clkack == 0x111

        self._add_submodule( 'cap', ECap, 0x100 )
        self._add_submodule( 'qep', EQep, 0x180 )
        self._add_submodule( 'pwm', EPwm, 0x200 )

    def _add_submodule( self, name, Module, offset ):
        module = None

        path = self.path / name
        if path.exists():
            uio = Uio( path, parent=self )
            assert uio.region().address == self.region().address + offset

            module = uio.map( Module )
            module._uio = uio

            module.irq.uio = uio

        setattr( self, name, module )

        if module is None:
            # fallback, mainly for debugging:
            module = self.map( Module, offset )

        setattr( self, '_' + name, module )
