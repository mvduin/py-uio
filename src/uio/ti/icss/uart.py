########## PRU-ICSS subsystem UART #############################################
##
## This is the same TL16C550-based UART used in TI C6x/Keystone DSPs.

import ctypes
import io
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
        if self.has_io:
            raise RuntimeError( "I/O object should be closed before changing baudrate" )
        self.mdr = ( 16, 13 ).index( value )

    @property
    def divisor( self ):
        return self.div_lsb | self.div_msb << 8

    @divisor.setter
    def divisor( self, value ):
        if value not in range( 1, 0x10000 ):
            raise RuntimeError( "Invalid divisor" )
        if self.has_io:
            raise RuntimeError( "I/O object should be closed before changing baudrate" )
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
            raise RuntimeError( "TODO: parity not yet supported" )

        if self.has_io:
            raise RuntimeError( "I/O object should be closed before reinitializing UART" )

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


    @cached_getter
    def io( self ):
        """Return (existing or new) object for performing I/O via the UART.

        This might for example be used to initialize an external device before
        starting the PRU core that communicates with it.  You should .close()
        the I/O object before starting the PRU core that uses the UART.
        """
        return UartIO( self )

    @property
    def has_io( self ):
        """Check if I/O object exists."""
        return 'io' in self.__dict__


class UartIO( io.BufferedIOBase ):
    def __init__( self, uart ):
        if uart.has_io:
            raise RuntimeError( "Illegal use of private constructor" )
        if uart.divisor == 0:
            raise RuntimeError( "UART has not been initialized" )

        self._uart = uart
        self._rx_buffer = bytearray()
        self._tx_fifo_space = 0
        self._tx_done = False
        self._poll_interval = ( 7 + ( uart.lcr & 3 ) ) / uart.baudrate
        self._poll()

    def readable( self ):
        return super.readable() or True

    def writable( self ):
        return super.writable() or True

    def close( self ):
        if self.closed:
            return
        super().close()
        assert self._uart.__dict__.get('io') is self
        del self._uart.__dict__['io']

    def _poll( self, until=None ):
        if self.closed:
            raise RuntimeError( "I/O object has been closed" )

        while True:
            lsr = self._uart.lsr

            if lsr & LSR_TX_EMPTY:
                self._tx_fifo_space = 16
            if lsr & LSR_TX_DONE:
                self._tx_done = True
            if not ( lsr & LSR_RX_AVAIL ):
                if until is None or until():
                    break
                sleep( self._poll_interval )
                continue

            self._rx_buffer.append( self._uart._read_byte() )

            if lsr & LSR_RX_ERR_ANY:
                if lsr & LSR_RX_OVERRUN:
                    raise RuntimeError( "Receive FIFO overrun" )
                elif lsr & LSR_RX_BREAK:
                    raise RuntimeError( "Break detected" )
                elif lsr & LSR_RX_FRAMING:
                    raise RuntimeError( "Framing error" )
                elif lsr & LSR_RX_PARITY:
                    raise RuntimeError( "Parity error" )

    def flush( self ):
        self._poll( lambda: self._tx_done )

    def _read0( self, size ):
        if size is None or size < 0 or size >= len( self._rx_buffer ):
            data = self._rx_buffer
            self._rx_buffer = bytearray()
        else:
            data = self._rx_buffer[ : size ]
            del self._rx_buffer[ : size ]
        return data

    def _read1( self, size ):
        self._poll()
        return self._read0( size )

    def _read( self, size ):
        if size is None or size < 0:
            raise ValueError( "Unbounded read not allowed" )
        self._poll( lambda: len( self._rx_buffer ) >= size )
        return self._read0( size )

    def read1( self, size=-1 ):
        return bytes( self._read1( size ) )

    def read( self, size ):
        return bytes( self._read( size ) )

    def readinto1( self, b ):
        with memoryview( b ) as m:
            with m.cast( 'B' ) as m:
                data = self._read1( len( m ) )
                m[ : len( data ) ] = data

    def readinto( self, b ):
        with memoryview( b ) as m:
            with m.cast( 'B' ) as m:
                data = self._read( len( m ) )
                m[ : len( data ) ] = data

    def write( self, b ):
        for byte in bytes( b ):
            if self._tx_fifo_space == 0:
                self._poll( lambda: self._tx_fifo_space > 0 )
            self._uart._write_byte( byte )
            self._tx_fifo_space -= 1

    def readline( self, size=-1, *, newline=b'\n' ):
        if type( newline ) is not bytes:
            raise TypeError( "'newline' argument must be a bytes object" )
        buf = self._rx_buffer
        if size is None or size < 0:
            self._poll( lambda: newline in buf )
            size = buf.index( newline ) + len( newline )
        else:
            self._poll( lambda: len( buf ) >= size or newline in buf )
            pos = buf.find( newline, 0, size )
            if pos >= 0:
                size = pos + len( newline )
                return bytes( self._read0( size ) )
        return bytes( self._read0( size ) )
