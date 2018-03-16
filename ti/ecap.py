from uio import Uio, fix_ctypes_struct, cached_getter
import ctypes
from ctypes import c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint
from .eirq import EIrq

ctr_t = uint    # counter value
irq_t = ushort

class Pwm( ctypes.Structure ):
    # pwm mode:
    #	output high while 0 <= counter < compare
    #	output low  while compare <= counter <= maximum
    # counter wraps to 0 after maximum (period = maximum + 1).
    # 100% duty cycle if compare > maximum,
    # 	cannot be attained if maximum == 0xffffffff.
    # output can be inverted via config register.
    _fields_ = [
            ("maximum",     ctr_t),     #r>  write also sets ld_maximum
            ("compare",     ctr_t),     #r>  write also sets ld_compare
            ("ld_maximum",  ctr_t),     #rw  loaded into maximum on counter wrap
            ("ld_compare",  ctr_t),     #rw  loaded into compare on counter wrap
        ]

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
	    #	0 = disable
	    #	n = divide by 2n (for n > 0), triggers on rising edge
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


            ("", ubyte * (0x5c - 0x34)),

            ("ident",       uint),      #r-
            #   0x4_4d2_21_00  (v1.0.4 on subarctic 2.1)
        ]

    @cached_getter
    def pwm( self ):
        return Pwm.from_buffer( self.capture )

assert ctypes.sizeof(ECap) == 0x60
