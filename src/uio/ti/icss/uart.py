########## PRU-ICSS subsystem UART #############################################
##
## This is the same TL16C550-based UART used in TI C6x/Keystone DSPs.

import ctypes
from ctypes import c_uint32 as uint
from time import sleep
from uio.utils import cached_getter

UART_CLK = 192000000

RX_IRQ	= 1 << 0
TX_IRQ	= 1 << 1
ERR_IRQ = 1 << 2
MSR_IRQ = 1 << 3
RXT_IRQ = 1 << 8  # controlled by enable-bit for RX_IRQ

_IIR_MAP = {
        0b0110: ERR_IRQ,
        0b0100: RX_IRQ,
        0b1100: RXT_IRQ,
        0b0010: TX_IRQ,
        0b0000: MSR_IRQ,
        0b0001: 0,
    }

LSR_RX_AVAIL    = 1 << 0
LSR_RX_OVERRUN  = 1 << 1
LSR_RX_PARITY   = 1 << 2
LSR_RX_FRAMING  = 1 << 3
LSR_RX_BREAK    = 1 << 4
LSR_RX_ERR_ANY  = LSR_RX_OVERRUN | LSR_RX_PARITY | LSR_RX_FRAMING | LSR_RX_BREAK
LSR_TX_EMPTY    = 1 << 5
LSR_TX_DONE     = 1 << 6

SYSC_RX_ENABLED = 1 << 13
SYSC_TX_ENABLED = 1 << 14

class Uart( ctypes.Structure ):
    _fields_ = [
            ("",            uint),  # _read_byte and _write_byte

            ("irq_enabled", uint),  #rw
            # bit   0       rw  receive irq(s) enabled
            # bit   1       rw  transmit irq enabled
            # bit   2       rw  error irq enabled
            # bit   3       rw  modem status irq enabled

            ("",            uint),  # _read_iir and _write_fcr

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

    # XXX workaround for bad ctypes behaviour
    @cached_getter
    def _regs( self ):
        return memoryview( self ).cast('B').cast('L')

    def _read_byte( self ):
        return self._regs[0]

    def _write_byte( self, value ):
        assert value in range(256)
        self._regs[0] = value

    def _read_iir( self ):
        return self._regs[2]

    def _write_fcr( self, value ):
        assert value in range(256)
        self._regs[2] = value

    @property
    def irq_status( self ):
        return _IIR_MAP[ self._read_iir() & 15 ]

    @property
    def oversampling( self ):
        return ( 16, 13 )[ self.mdr & 1 ]

    @oversampling.setter
    def oversampling( self, value ):
        if value not in ( 16, 13 ):
            raise RuntimeError( "Invalid oversampling factor" )
        self.mdr = ( 16, 13 ).index( value )

    @property
    def divisor( self ):
        return self.div_lsb | self.div_msb << 8

    @divisor.setter
    def divisor( self, value ):
        if value not in range( 1, 0x10000 ):
            raise RuntimeError( "Invalid divisor" )
        self.div_lsb = value & 0xff
        self.div_msb = value >> 8

    @property
    def baudrate( self ):
        return UART_CLK / self.oversampling / self.divisor

    def configure_fifos( self, rx_trigger_level=1, reset_rx=False, reset_tx=False ):
        fcr = 1 << 0 | 1 << 3
        if reset_rx:
            fcr |= 1 << 1
        if reset_tx:
            fcr |= 1 << 2
        fcr |= [ 1, 4, 8, 14].index( rx_trigger_level ) << 6
        self._write_fcr( fcr );

    def initialize( self, baudrate, databits=8, parity='n', stopbits=1, rx_trigger_level=1 ):
        if baudrate > 12e6:
            raise RuntimeError( "Baudrate too high (max is 12000000)" )

        oversampling = 16
        divisor = round( 192e6 / 16 / baudrate )
        deviation = abs( 192e6 / 16 / divisor / baudrate - 1 )

        divisor13 = round( 192e6 / 13 / baudrate )
        deviation13 = abs( 192e6 / 13 / divisor13 / baudrate - 1 )

        if divisor13 <= 0xffff and deviation13 < deviation:
            oversampling = 13
            divisor = divisor13
            deviation = deviation13

        if divisor > 0xffff:
            raise RuntimeError( "Baudrate is too low" )
        if deviation > 0.02:
            raise RuntimeError( "Baudrate deviation greater than 2%" )

        if databits not in range( 5, 9 ):
            raise RuntimeError( "Invalid number of data bits" )

        if databits == 5:
            if stopbits not in ( 1, 1.5 ):
                raise RuntimeError( "Invalid number of stop bits" )
            lcr = [ 1, 1.5 ].index( stopbits ) << 2
        else:
            if stopbits not in ( 1, 2 ):
                raise RuntimeError( "Invalid number of stop bits" )
            lcr = [ 5, 6, 7, 8 ].index( databits )
            lcr |= [ 1, 2 ].index( stopbits ) << 2

        if parity != 'n':
            raise RuntimeError("TODO: parity not yet supported")

        self.irq_enabled = 0
        self.sysconfig = 0
        self._write_fcr( 0 )
        self.mcr = 0
        self.lcr = lcr
        self.msr
        while self.lsr & 1:
            self._read_byte()
        self._read_iir()
        self.oversampling = oversampling
        self.divisor = divisor
        self._write_fcr( 1 )
        self.configure_fifos( rx_trigger_level, reset_rx=True, reset_tx=True )
        self.sysconfig |= SYSC_RX_ENABLED | SYSC_TX_ENABLED


    # utility method for performing I/O via the UART.
    # obviously this should never be called while the UART is in use by PRU.
    def io( self, send_data=b'', recv_bytes=0, blocking=True ):
        send_data = bytes( send_data )
        poll_interval = 4 / self.baudrate
        recv_data = bytearray()
        send_bytes = 0

        while True:
            lsr = self.lsr

            # send up to 16 bytes whenever tx fifo is empty
            if lsr & LSR_TX_EMPTY and send_data != b'':
                for byte in send_data[ : 16 ]:
                    self._write_byte( byte )
                    send_bytes += 1
                send_data = send_data[ 16 : ]

            if lsr & LSR_RX_OVERRUN:
                # overrun happened after these 15 bytes were received
                for i in range(15):
                    recv_data.append( self._read_byte() )
                # and either before or after this byte
                self._read_byte()

            elif lsr & LSR_RX_AVAIL:
                # at least one byte available
                recv_data.append( self._read_byte() )

            else:
                # nothing available to read
                if not blocking:
                    break  # not allowed to wait
                if send_data == b'' and len( recv_data ) >= recv_bytes:
                    break  # we've sent everything and received enough

                # wait and try again later
                sleep( poll_interval )
                continue

            # bail out if an error occurred
            if lsr & LSR_RX_ERR_ANY:
                break

        return ( send_bytes, recv_data, lsr & LSR_RX_ERR_ANY )
