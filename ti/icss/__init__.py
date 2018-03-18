########## Programmable Real-Time Unit -- ######################################
########## -- Industrial Communication Subsystem (PRU-ICSS) ####################
##
## aka PRUSS, but not to be confused with the old one of Freon/Primus.

from uio import Uio
from .cfg import Cfg
from .core import Core
from .intc import Intc
from ..ecap import ECap
from struct import unpack_from as unpack

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
        self.dram0 = self.subregion( 0x00000, 0x02000 )
        self.dram1 = self.subregion( 0x02000, 0x02000 )
        self.dram2 = self.subregion( 0x10000, 0x10000 )

        # interrupt controller
        self.intc  = self.map( Intc, 0x20000 )

        # core control/debug
        self.core0 = self.map( Core, 0x22000 )
        self.core1 = self.map( Core, 0x24000 )

        # subsystem configuration
        self.cfg   = self.map( Cfg,  0x26000 )

        # subsystem peripherals
        #self.uart = self.map( Uart, 0x28000 )
        #self.iep  = self.map( Iep,  0x2e000 )
        self.ecap  = self.map( ECap, 0x30000 )

        # instruction memories
        self.iram0 = self.subregion( 0x34000, 0x04000 )
        self.iram1 = self.subregion( 0x38000, 0x04000 )

        # make it easier to find everything related to one core
        self.core0.dram = self.dram0
        self.core0.iram = self.iram0
        self.core1.dram = self.dram1
        self.core1.iram = self.iram1
        self.core0.peer_dram = self.dram1
        self.core1.peer_dram = self.dram0

    def initialize( self ):
        # reset prcm controls to default just in case
        self.cfg.idlemode = 'auto'
        self.cfg.standbymode = 'auto'

        # enable OCP master ports
        self.cfg.standbyreq = False

        # initialize cores
        self.core0.full_reset()
        self.core1.full_reset()

        # initialize interrupt controller
        self.cfg.intc = 0
        self.intc.initialize()


    def elf_load( self, core, exe ):
        # quick and dirty ELF executable loader

        if not isinstance( exe, memoryview ):
            with memoryview( exe ) as exe:
                return self.elf_load( core, exe )

        assert core in (self.core0, self.core1)

        # parse file header
        if exe[:7] != b'\x7fELF\x01\x01\x01':
            raise RuntimeError("Invalid ELF32 header")
        if unpack( 'HH', exe, 0x10 ) != (2, 144):
            raise RuntimeError("Not a TI-PRU executable")
        (entry, phoff, phsz, nph) = unpack( 'II10xHH', exe, 0x18 )

        core.full_reset( entry >> 2 )

        for i in range(nph):
            (pt, *args) = unpack( '8I', exe, phoff )
            phoff += phsz

            if pt == 1:
                self._elf_load_segment( core, exe, *args )
            elif pt == 0x70000000:
                pass  # segment attributes
            else:
                raise RuntimeError("Unknown program header type: 0x%x" % pt)

    def _elf_load_segment( self, core, exe, offset, va, pa, fsz, msz, flags, align ):
            if flags & 1:
                ram = core.iram
            elif va < 0x2000:
                ram = core.dram
            elif va < 0x10000:
                va -= 0x2000
                ram = core.peer_dram
            else:
                va -= 0x10000
                ram = self.dram2
            ram = ram.map()
            if va + msz > len(ram) or fsz > msz or offset + fsz > len(exe):
                raise RuntimeError("Invalid segment")
            ram[ va : va + fsz ] = exe[ offset : offset + fsz ]
            ram[ va + fsz : va + msz ] = bytearray( msz - fsz )
