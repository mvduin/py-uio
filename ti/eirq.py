import ctypes
from ctypes import c_uint16 as ushort

# Irq combiner block present in ecap/eqep/epwm modules.
#
# Bit 0 represents the irq output line, which is set whenever
# (pending & enabled) != 0  and must be manually cleared.
#
# For integration with an uio_pdrv_genirq device that's hooked
# up to the output of this irq_combined, set the 'uio' attribute
# to the Uio device.

class EIrq( ctypes.Structure ):
    _fields_ = [
            ("enabled", ushort),    #rw
            ("pending", ushort),    #r-
            ("_clear",  ushort),    #-c
            ("_set",    ushort),    #-s
        ]

    def clear( self, bits, *, eoi=False ):
        if eoi:
            bits |= 1
        self._clear = bits
        if bits & 1 and hasattr( self, 'uio' ):
            self.uio.irq_enable()

    def set( self, bits ):
        self._set = bits

    def enable( self, bits ):
        self.enabled |= bits
        if hasattr( self, 'uio' ):
            self.uio.irq_enable()

    def disable( self, bits ):
        self.enabled &= ~bits

    @property
    def active( self ):
        return self.enabled & self.pending

    def recv( self ):
        if hasattr( self, 'uio' ):
            self.uio.irq_recv()
        events = self.active
        self.clear( events, eoi=True )
        return events

    def reset( self ):
        self.enabled = 0
        self.clear( 0xffff )
