from uio import Uio
from pathlib import Path
from ctypes import ( c_uint32 as uint )
from .cfg import Cfg
from .core import Core

IRam = uint * ( 0x04000 >> 2 )

class Icss( Uio ):
    def __init__( self, path ):
        super().__init__( Path( path, 'module' ) )

        try:
            self.ddr = self.region( 'ddr' );
        except KeyError:
            self.ddr = None;

        self.dram0 = self.subregion( 0x00000, 0x02000 );
        self.dram1 = self.subregion( 0x02000, 0x02000 );
        self.dram2 = self.subregion( 0x10000, 0x10000 );
        #self.intc = self.map( Intc, 0x20000 )
        self.core0 = self.map( Core, 0x22000 )
        self.core1 = self.map( Core, 0x24000 )
        self.cfg = self.map( Cfg, 0x26000 )
        #self.uart = self.map( Uart, 0x28000 )
        #self.iep = self.map( Iep, 0x2e000 )
        #self.ecap = self.map( ECap, 0x30000 )
        self.iram0 = self.map( IRam, 0x34000 )
        self.iram1 = self.map( IRam, 0x38000 )
