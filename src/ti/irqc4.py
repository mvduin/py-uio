# omap4 standard irq combiner

import ctypes

def define( mask_t, stride=None ):
    if stride == None:
        padding = 0
    else:
        padding = stride - ctypes.sizeof( mask_t )

    padding = ("", ctypes.c_uint8 * padding);

    class IrqCombiner( ctypes.Structure ):
        _fields_ = [
                ("_set",     mask_t), padding,
                ("_clear",   mask_t), padding,
                ("_enable",  mask_t), padding,
                ("_disable", mask_t), padding,
            ]

        @property
        def pending( self ):  return self._set

        def pending_one( self, irq ):  return bool( self._set & 1 << irq )

        @property
        def active( self ):  return self._clear  # == pending & enabled

        def active_one( self, irq ):  return bool( self._clear & 1 << irq )

        # set/clear only apply to latched inputs
        def set( self, mask ):  self._set = mask
        def clear( self, mask ):  self._clear = mask

        def set_one( self, irq ):  self._set = 1 << irq
        def clear_one( self, irq ):  self._clear = 1 << irq

        @property
        def enabled( self ):  return self._enable

        def enabled_one( self, irq ):  return bool( self._enable & 1 << irq )

        def enable( self, mask ):  self._enable = mask
        def disable( self, mask ):  self._disable = mask

        def enable_one( self, irq ):  self._enable = 1 << irq
        def disable_one( self, irq ):  self._disable = 1 << irq

        def pull( self, mask=None ):
            irqs = self._clear
            if mask != None:
                irqs &= mask
            self._clear = irqs
            return irqs

    return IrqCombiner;

# most common variant
IrqCombiner = define( ctypes.c_uint32 )
