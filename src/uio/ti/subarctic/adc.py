from uio.utils import fix_ctypes_struct
import ctypes
from ctypes import c_uint8 as u8, c_uint16 as u16, c_uint32 as u32
from uio.ti.irqc4 import IrqCombiner

@fix_ctypes_struct
class StepBase( ctypes.Structure ):
    _fields_ = [
            ("config",  u32),
        ]

@fix_ctypes_struct
class Step( StepBase ):
    _fields_ = [
            ("open_delay",  u32, 18),  #rw  cycles
            ("",            u32,  6),
            ("sample_time", u32,  8),  #rw  cycles - 2

            # Each normal step consists of:
            #       open_delay  cycles with muxes configured (may be 0)
            #       2**averaging times:
            #           2 + sample_time  cycles of sampling
            #           13 cycles of conversion
            #
            # charge step only has open_delay, which must be non-zero.
            #
            # idle step has neither open_delay nor sample_time.
        ]

@fix_ctypes_struct
class Fifo( ctypes.Structure ):
    _fields_ = [
            ("level",       u32),  #r-  number of words (0-64) currently in fifo
            ("irq_thresh",  u32),  #rw  irq threshold (= read burst - 1)
            ("dma_thresh",  u32),  #rw  dma event threshold (= dma burst - 1)
        ]

@fix_ctypes_struct
class Adc( ctypes.Structure ):
    _fields_ = [
            ("ident",       u32),
            ("",            u32 * 3),
            ("sysconfig",   u32),
            ("",            u32 * 3),
            ("_eoi",        u32),
            ("irq",         IrqCombiner),
            ("wakeup_en",   u32),
            ("dma_enable",  u32),
            ("dma_disable", u32),
            ("ctrl",        u32),
            ("status",      u32),
            ("range_min",   u16),
            ("range_max",   u16),
            ("clkdiv",      u32),  #rw  should be 7 to get 24 MHz / (1+7) = 3 MHz adc clock
            ("misc",        u32),
            ("stepenable",  u32),
            ("idle",        StepBase),
            ("charge",      Step),
            ("step",        Step * 16),
            ("fifo",        Fifo * 2),
        ]

assert ctypes.sizeof(Adc) == 0xfc
