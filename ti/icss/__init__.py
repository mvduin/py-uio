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
