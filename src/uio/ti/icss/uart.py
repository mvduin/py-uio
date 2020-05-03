########## PRU-ICSS subsystem UART #############################################
##
## This is the same TL16C550-based UART used in TI C6x/Keystone DSPs.

import ctypes
from ctypes import c_uint32 as uint

RX_IRQ	= 1 << 0
TX_IRQ	= 1 << 1
ERR_IRQ = 1 << 2
MSR_IRQ = 1 << 3
RXT_IRQ = 1 << 8  # controlled by enable-bit for RX_IRQ

IIR_MAP = {
        0b0110: ERR_IRQ,
        0b0100: RX_IRQ,
        0b1100: RXT_IRQ,
        0b0010: TX_IRQ,
        0b0000: MSR_IRQ,
        0b0001: 0,
    }

class Uart( ctypes.Structure ):
    _fields_ = [
            ("_io",         uint),  #<>

            ("irq_enabled", uint),  #rw
            # bit   0       rw  receive irq(s) enabled
            # bit   1       rw  transmit irq enabled
            # bit   2       rw  error irq enabled
            # bit   3       rw  modem status irq enabled

            ("_iir_fcr",    uint),

            ("lcr",         uint),  #rw  line control
            #  bits  0- 1   rw  data bits: 0=5, 1=6, 2=7, 3=8
            #  bit   2      rw  stop bits: 0=1, 1=2, see note
            #  bit   3      rw  parity enabled (generated and checked)
            #  bits  4- 5   rw  parity bit:  0=odd, 1=even, 2=mark, 3=space
            #  bit   6      rw  transmit break
            #  bit   7      rw  (backwards compat, keep at zero)
            #
            # note: as traditional for UARTs, if 5 data bits are configured then
            # setting bit 2 results in 1.5 stop bits rather than 2 stop bits.

            ("mcr",         uint),  #rw  modem control
            #  bit   0      rw  DTR asserted (low)
            #  bit   1      rw  RTS asserted (low), see note
            #  bit   2      rw  OUT1 asserted (low)
            #  bit   3      rw  OUT2 asserted (low)
            #  bit   4      rw  local loopback enabled
            #  bit   5      rw  hw flow control enabled
            #
            # If hw flow control is enabled, transmission is halted whenever
            # CTS is deasserted, and RTS is asserted only hwne bit 1 is set and
            # the fifo receive treshold has not yet been reached (i.e. RTS is
            # deasserted when the read burst interrupt is generated).
            #
            # Local loopback connections:
            #   out:    TXD     RTS     DTR     OUT1    OUT2
            #   in:     RXD     CTS     DSR     RI      DCD

            ("lsr",         uint),  #<-  line status
            #  bit   0      r-  receive fifo non-empty
            #  bit   1      u-  overrun error
            #  bit   2      r-  next char has parity error
            #  bit   3      r-  next char has framing error
            #  bit   4      r-  next char is break
            #  bit   5      r-  transmit fifo empty
            #  bit   6      r-  transmit fifo empty and serializer idle
            #  bit   7      r-  at least one break or error in receive fifo


            ("msr",         uint),  #<-  modem status
            #  bit   0      u-  CTS change event
            #  bit   1      u-  DSR change event
            #  bit   2      u-  RI deassertion event (low -> high)
            #  bit   3      u-  DCD change event
            #
            #  bit   4      r-  CTS asserted (low)
            #  bit   5      r-  DSR asserted (low)
            #  bit   6      r-  RI asserted (low)
            #  bit   7      r-  DCD asserted (low)

            ("spare",       uint),  #rw  one byte of freely usable RAM, woohoo!

            ("div_lsb",     uint),  #rw
            ("div_msb",     uint),  #rw

            ("ident",       uint),  #r-
            #   0x11'02'0002    Keystone, OMAP-L1xx
            #   0x44'14'1102    AM572x 2.0 (icss)

            ("ident2",      uint),  #r-  (always seems to be zero)

            ("sysconfig",   uint),  #rw
            #   bit   0     rw  emu-free
            #   bit   1     r-  (always 1)
            #   bits  2-12  z-
            #   bit  13     rw  receiver enabled
            #   bit  14     rw  transmitter enabled
            #   bit  15     zz
            #
            # the receiver/transmitter is held in reset while bit 13/14 is zero

            ("mdr",         uint),  #rw
            #   bit   0     rw  oversampling: 0 = 16×, 1 = 13×
    ]

    @property
    def irq_status( self ):
        return IIR_MAP[ self._iir_fcr & 15 ];

    @property
    def fifos_enabled( self ):
        return bool( self._iir_fcr & 0x80 );