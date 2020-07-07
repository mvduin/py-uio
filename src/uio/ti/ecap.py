from uio.utils import fix_ctypes_struct, cached_getter
import ctypes
from ctypes import c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint
from .eirq import EIrq

ctr_t = uint    # counter value

class Pwm( ctypes.Structure ):
    # pwm mode:
    #   output high while 0 <= counter < compare
    #   output low  while compare <= counter <= maximum
    # counter wraps to 0 after maximum (period = maximum + 1).
    # 100% duty cycle if compare > maximum,
    #   cannot be attained if maximum == 0xffffffff.
    # output can be inverted via config register.
    _fields_ = [
            ("maximum",     ctr_t),     #r>  write also sets ld_maximum
            ("compare",     ctr_t),     #r>  write also sets ld_compare
            ("ld_maximum",  ctr_t),     #rw  loaded into maximum on counter wrap
            ("ld_compare",  ctr_t),     #rw  loaded into compare on counter wrap
        ]

    @property
    def period( self ):
        """PWM period in clock cycles (max 2**32).

        Note: if period is set to 2**32 then 100% duty cycle is impossible.
        """
        return self.ld_maximum + 1

    @period.setter
    def period( self, value ):
        if value not in range( 1, 2**32 + 1 ):
            raise ValueError( "Invalid PWM period" )
        self.ld_maximum = value - 1

    @property
    def value( self ):
        """PWM pulse width in clock cycles."""
        return min( self.ld_compare, self.period )

    @value.setter
    def value( self, value ):
        if value not in range( self.period + 1 ):
            raise ValueError( "Invalid PWM value" )
        if value == 2**32:
            raise ValueError( "Cannot set duty cycle to 100% when period is 2**32" )
        self.ld_compare = value

    @property
    def duty_cycle( self ):
        """PWM duty cycle as float between 0.0 and 1.0 (inclusive)."""
        return self.value / self.period

    @duty_cycle.setter
    def duty_cycle( self, value ):
        self.value = round( value * self.period )

    def initialize( self, period, *, invert=False, value=None, duty_cycle=None ):
        """Initialize PWM output."""
        if value is not None and duty_cycle is not None:
            raise ValueError( "You cannot specify both 'value' and 'duty_cycle'" )
        # disable and reset counter
        self.parent.config &= 3 << 22
        self.parent.counter = 0
        # initialize pwm period and value
        self.period = period
        if duty_cycle is not None:
            self.duty_cycle = duty_cycle
        else:
            self.value = value or 0
        self.maximum = self.ld_maximum
        self.compare = self.ld_compare
        # enable pwm output
        self.parent.config |= 1 << 25 | invert << 26 | 1 << 20 | 1 << 15

@fix_ctypes_struct
class ECap( ctypes.Structure ):
    _fields_ = [
            ("counter",     ctr_t),     #rw
            ("ld_counter",  ctr_t),     #rw  loaded into counter on sync-in if enabled

            ("capture",     ctr_t * 4), #rw  captured counter values   (capture mode)

            ("", ubyte * (0x28 - 0x18) ),


            ("config",      uint),
            #
            # ## capture mode config:
            #
            # bit   0      rw  capture 0 on rising(0)/falling(1) edge
            # bit   1      rw  counter reset on capture 0
            # bit   2      rw  capture 1 on rising(0)/falling(1) edge
            # bit   3      rw  counter reset on capture 1
            # bit   4      rw  capture 2 on rising(0)/falling(1) edge
            # bit   5      rw  counter reset on capture 2
            # bit   6      rw  capture 3 on rising(0)/falling(1) edge
            # bit   7      rw  counter reset on capture 3
            #
            # bit   8      rw  enable capture to registers
            # bits  9-13   rw  capture input prescaler
            #   0 = disable
            #   n = divide by 2n (for n > 0), triggers on rising edge
            #
            # ## debug suspend:
            #
            # bit  14      rw  emu soft suspend (counter runs till 0)
            # bit  15      rw  emu-free (bit 14 ignored)
            #
            # ## capture control:
            #
            # bit  16      rw  one-shot capture mode
            # bits 17-18   rw  num captures - 1
            # bit  19      -x  rearm capture
            #
            # ## counter control:
            #
            # bit  20      rw  counter enabled
            # bit  21      rw  reload counter on sync-in
            # bit  22      rw  sync-out on:  0 sync-in  1 counter wrap (pwm mode)
            # bit  23      rw  sync-out disabled
            # bit  24      -x  trigger sync-in
            #
            # ## pwm mode config:
            #
            # bit  25      rw  module mode:  0 capture  1 pwm
            # bit  26      rw  invert output (pwm mode)


            ("irq",         EIrq),
            # bit   1      capture 0   (capture mode)
            # bit   2      capture 1   (capture mode)
            # bit   3      capture 2   (capture mode)
            # bit   4      capture 3   (capture mode)
            # bit   5      counter overflow  (capture mode)
            #
            # bit   6      maximum match   (pwm mode)
            # bit   7      compare match   (pwm mode)


            ("", u8 * (0x5c - 0x34)),

            ("ident",       u32),       #r-
            #   0x4_4d2_21_00  (v1.0.4 on subarctic 2.1)
        ]

    @cached_getter
    def pwm( self ):
        pwm = Pwm.from_buffer( self.capture )
        pwm.parent = self
        return pwm

assert ctypes.sizeof(ECap) == 0x60
