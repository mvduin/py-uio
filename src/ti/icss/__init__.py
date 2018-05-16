########## Programmable Real-Time Unit -- ######################################
########## -- Industrial Communication Subsystem (PRU-ICSS) ####################
##
## aka PRUSS, but not to be confused with the old one of Freon/Primus.

from uio import Uio
from .cfg import Cfg
from .core import Core
from .intc import Intc
from ..ecap import ECap

class Icss( Uio ):
    def __init__( self, path ):
        super().__init__( path )

        try:
            self.ddr = self.region( 'ddr' )
        except KeyError:
            try:
                self.ddr = self.region( 1 )
            except KeyError:
                self.ddr = None

        # data memories
        self.dram0 = self.subregion( 0x00000, 0x02000, name='dram0' )
        self.dram1 = self.subregion( 0x02000, 0x02000, name='dram1' )
        self.dram2 = self.subregion( 0x10000, 0x10000, name='dram2' )

        # interrupt controller
        self.intc  = self.map( Intc, 0x20000 )

        # core control/debug
        self.core0 = self.map( Core, 0x22000 )
        self.core1 = self.map( Core, 0x24000 )
        self.cores = ( self.core0, self.core1 )

        # subsystem configuration
        self.cfg   = self.map( Cfg,  0x26000 )

        # subsystem peripherals
        #self.uart = self.map( Uart, 0x28000 )
        #self.iep  = self.map( Iep,  0x2e000 )
        self.ecap  = self.map( ECap, 0x30000 )

        # instruction memories
        self.iram0 = self.subregion( 0x34000, 0x04000, name='iram0' )
        self.iram1 = self.subregion( 0x38000, 0x04000, name='iram1' )

        self._link_memories()

    def _link_memories( self ):
        self.core0.iram         = self.iram0
        self.core0.dram         = self.dram0
        self.core0.peer_dram    = self.dram1
        self.core0.shared_dram  = self.dram2
        self.core1.iram         = self.iram1
        self.core1.dram         = self.dram1
        self.core1.peer_dram    = self.dram0
        self.core1.shared_dram  = self.dram2

    def _autodetect_ram( self, name ):
        ram = getattr( self, name )
        pages = ram.size // 4096
        mm = ram.map().cast( 'I', shape=(pages, 4096//4) )
        for i in reversed( range( pages ) ):
            mm[i, 0] = i
        for i in range( pages ):
            if mm[i, 0] != i:
                pages = i
                break
        offset = ram.address - self.region().address
        ram = self.subregion( offset, pages * 4096, name=name )
        setattr( self, name, ram )

    def initialize( self ):
        # reset prcm controls to default just in case
        self.cfg.idlemode = 'auto'
        self.cfg.standbymode = 'auto'

        # enable OCP master ports
        self.cfg.standbyreq = False

        # initialize cores
        self.core0.full_reset()
        self.core1.full_reset()

        # auto-detect ram sizes
        for name in 'iram0', 'iram1', 'dram0', 'dram1', 'dram2':
            self._autodetect_ram( name )
        self._link_memories()

        # initialize interrupt controller
        self.cfg.intc = 0
        self.intc.initialize()


    def elf_load( self, core, exe ):
        assert core in (self.core0, self.core1)

        core.elf_load( exe );
