########## PRU-ICSS subsystem config module ####################################
##
## Note that sigma-delta and EnDAT were not yet present in ICSS v0, which is
## present in subarctic (am335x) and silicon versions 1.x of vayu (am572x).

import ctypes
from ctypes import c_uint32 as uint
from ti.irqc4 import IrqCombiner


IDLEMODES = ['force', 'block', 'auto']

class Cfg( ctypes.Structure ):
    _fields_ = [
            ("ident",        uint),  # r-
            # 4'700'00'00   subarctic 2.1
            # 4'700'02'00   aegis pruss1 (according to TRM)
            # 4'701'01'00   aegis pruss0 (according to TRM)
            # 4'700'02'01   am572x 2.0 (both instances)


            # sysconfig
            ("_idlemode",    uint,  2),  #rw  idlemode (no wakeup supported)
            ("_standbymode", uint,  2),  #rw  standbymode (no wakeup supported)
            ("standbyreq",   uint,  1),  #rw  request master port standby
            ("mwait",        uint,  1),  #rw  master port not ready
            ("",             uint, 26),


            ("ioconfig0",    uint),  # pru 0 io config
            ("ioconfig1",    uint),  # pru 1 io config
            # bits  0- 1  rw  gpi mode:
            #                   0 = direct
            #                   1 = 16-bit parallel capture
            #                   2 = 28-bit serial capture
            #                   3 = mii-rt
            # bit   2     rw  parallel capture edge:  0=rising,  1=falling
            # bits  3- 7  rw  gpi serial clock divider 0
            # bits  8-12  rw  gpi serial clock divider 1
            # bit  13     rc  gpi serial capture start event
            #                   write 1 to clear event and shift register
            #
            # bit  14     rw  gpo mode:
            #                   0 = direct
            #                   1 = serial
            # bits 15-19  rw  gpo serial clock divider 0
            # bits 20-24  rw  gpo serial clock divider 1
            # bit  25     r-  gpo current shift register
            #
            # bits 26-29  rw  extended io mode:
            #                   0 = normal (see above)
            #                   1 = EnDAT / BISS peripheral interface
            #                   2 = <reserved>
            #                   3 = sigma-delta
            #                   4 = mii-rt alternative mux
            #
            # All dividers: 0=/1, 1=/1.5, 2=/2, 3=/2.5, ..., 30=/16
            # The two dividers for each direction are cascaded.
            # Non-integer divider results in asymmetric clock waveform.
            #
            #   9/2         4 high 5 low
            #   3/2, 3      5 high 4 low
            #   3, 3/2      6 high 3 low
            #
            #   15/2        7 high 8 low
            #    5/2, 3     7 high 8 low
            #    3/2, 5     8 high 7 low
            #    3, 5/2     6 high 9 low
            #    5, 3/2     10 high 5 low
            #
            #   27/2        13 high 14 low
            #    9/2, 3     13 high 14 low
            #    3/2, 9     14 high 13 low
            #    3, 9/2     12 high 15 low
            #    9, 3/2     18 high 9 low
            #
            #    5/2, 3/2   5 high 3 low 5 high 2 low
            #    3/2, 5/2   3 high 4 low 3 high 5 low


            ("clockgate",    uint),
            # three bits per submodule:
            # bit   0     rw  idle request
            # bit   1     r-  idle ack
            # bit   2     rw  module clock enabled
            #
            # submodules:
            # bits  0- 2  pru core 0
            # bits  3- 5  pru core 1
            # bits  6- 8  interrupt controller
            # bits  9-11  uart
            # bits 12-14  cap
            # bits 15-17  iep


            # parity error irqs
            ("parity_irq", IrqCombiner),
            # bits  0- 3  rc  core 0 iram bytes 0-3
            # bits  4- 7  rc  data ram 0 bytes 0-3
            # bits  8-11  rc  core 1 iram bytes 0-3
            # bits 12-15  rc  data ram 1 bytes 0-3
            # bits 16-19  rc  data ram 2 bytes 0-3


            ("prio",         uint),  # local interconnect (VBUSP switch) config
            # bits  0- 1  rw  priority of element 1  (default 3)
            # bits  2- 3  rw  priority of element 2  (default 2)
            # bits  4- 5  rw  priority of element 3  (default 0)
            # bits  6- 7  rw  priority of element 4  (default 1)
            # bits  8-21  rw  priorities of elements 5-18
            #                   (defaults: 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1)
            #
            # It is not documented what exactly is controlled by these, other
            # than that lower values mean higher priority, and the first four
            # elements have 4 priority levels while the remaining ones have
            # only two.
            #
            # There are 4 master ports, so presumably the first four entries
            # are related to those?


            ("ocp",          uint),  # ocp master port config
            # bit   0     rw  pru 0 ocp master port address offset enable
            # bit   1     rw  pru 1 ocp master port address offset enable
            #
            # When enabled, 0x80'000 is subtracted.


            ("intc",         uint),  # interrupt routing
            # bit   0     rw  use mii-rt events (default 1)


            ("iep",          uint),
            # bit   0     rw  iep clock mode
            #                   0 = asynchronous (dedicated functional clock)
            #                   1 = synchronous
            #
            # By default IEP is in asynchronous mode.  Switching to synchronous
            # mode results in deterministic access timing.  Switching back to
            # asynchronous mode is not permitted other than by subsystem reset.


            ("pad",          uint),  # scratchpad config
            # bit   0     rw  on access contention give priority to
            #                   0 = core 0,  1 = core 1
            # bit   1     rw  enable pad shift functionality


            ("",             uint * 2),

            ("pinmux",       uint),
            # bit   0     rw  use pru 1 gpi 8-11 pins for pru mii 0 rxd 0-3
            # bit   1     rw  use pru 0 gpio 8-13 pins for pru 1 gpio 0-5
            # other device-specific bits may be defined
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
