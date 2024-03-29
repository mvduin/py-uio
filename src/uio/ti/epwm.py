from uio.utils import fix_ctypes_struct, cached_getter, add_field
import ctypes
from ctypes import c_uint8 as u8, c_uint16 as u16, c_uint32 as u32
from .eirq import EIrq

ctr_t = u16  # counter value

# ePWM has a main irq and a tripzone irq. The tripzone irq uses an EIrq register
# block just like eCAP and eQEP do. The main irq's register block however is
# similar but not quite compatible.

class Irq( ctypes.Structure ):
    _fields_ = [
            ("event",       u16,  3), #rw
            #                      0 -
            #                      1 zero
            #                      2 max
            #                      3 -
            #                      4 up-a
            #                      5 down-a
            #                      6 up-b
            #                      7 down-b

            ("enabled",     u16,  1), #rw

            ("",            u16, 12),

            ("divider",     u16,  2), #rw
            ("counter",     u16,  2), #r-
            ("",            u16, 12),

            ("pending",     u16),    #r-
            ("_clear",      u16),    #-c
            ("_set",        u16),    #-s
        ]

@fix_ctypes_struct
class EPwm( ctypes.Structure ):
    _fields_ = [

            #-------- time base ------------------------------------------------

            ("config",      u16),
            # bits  0- 1   rw  counter mode:  0 up  1 down  2 updown  3 freeze
            # bit   2      rw  load counter on:  0 never  1 sync-in
            # bit   3      rw  load maximum on:  0 zero  1 write
            # bits  4- 5   rw  sync-out on:  0 sync-in  1 zero  2 cmp-b  3 none
            # bit   6      -x  trigger sync-in
            # bits  7- 9   rw  fine divider / 2 (0 = disabled, i.e. /1)
            # bits 10-12   rw  coarse divider, log2
            # bit  13      rw  updown counter direction on sync-in counter load
            # bits 14-15   rw  debug suspend:  0 hard  1 soft  2 disabled

            ("status",      u16),
            # bit   0      r-  counter direction
            # bit   1      rc  sync-in event
            # bit   2      rc  max event

            ("",            u16),       #rw
            ("ld_counter",  ctr_t),     #rw
            ("counter",     ctr_t),     #rw

            ("ld_maximum",  ctr_t),     #rw

            ("",            u16),


            #-------- comparators ----------------------------------------------
            #
            # Four events generated:
            #   up-a    if counter == cmp-a while counting up
            #   up-b    if counter == cmp-b while counting up
            #   down-a  if counter == min( cmp-a, maximum ) while counting down
            #   down-b  if counter == min( cmp-b, maximum ) while counting down
            #
            # In updown mode, at an endpoint (where the direction is reversed),
            # the new direction applies.

            ("cmp_load",    u16),
            # bits  0- 1   rw  load cmp-a ev:  0 zero  1 max  2 both  3 none
            # bits  2- 3   rw  load cmp-b ev:  0 zero  1 max  2 both  3 none
            # bit   4      rw  load cmp-a on write (bits 0-1 ignored)
            # bit   5      z-
            # bit   6      rw  load cmp-b on write (bits 2-3 ignored)
            # bit   7      z-
            # bit   8      r-  load cmp-a pending
            # bit   9      r-  load cmp-b pending

            ("",            u16),       #r>
            ("ld_compare",  ctr_t * 2), #r>


            #-------- output control -------------------------------------------

            ("pwm_config",      u16 * 2),
            # bits  0- 1   rw  action on zero
            # bits  2- 3   rw  action on max
            # bits  4- 5   rw  action on up-a
            # bits  6- 7   rw  action on down-a
            # bits  8- 9   rw  action on up-b
            # bits 10-11   rw  action on down-b
            #                      0 none  1 clear  2 set  3 toggle
            #
            # If counting up, the actions considered are:
            #      zero, up-a, up-b, max
            # If counting down, the actions considered are:
            #      max, down-a, down-b, zero
            # When an endpoint is reached in updown mode, first the actions of
            # the old direction are considered and then those of the new
            # direction.
            #
            # If multiple conditions match, the last action takes effect.
            #
            # A software triggered action (see below) always takes precedence.

            ("sw_action",   u16),
            # bits  0- 1   rw  manual pwm-a action
            # bit   2      -x  trigger manual pwm-a action
            #
            # bits  3- 4   rw  manual pwm-b action
            # bit   5      -x  trigger manual pwm-b action
            #
            # bits  6- 7   rw  load sw_force on:  0 zero  1 max  2 both  3 write

            ("sw_force",    u16),
            # bits  0- 1   rw  force pwm-a:  0 no  1 low  2 high
            # bits  2- 3   rw  force pwm-b:  0 no  1 low  2 high


            #-------- dead-band ------------------------------------------------
            #
            # Optionally replaces pwm-a by rising edge delayed (red) signal.
            # Optionally replaces pwm-b by falling edge delayed (fed) signal.
            #
            # Both edge delay units can use either pwm-a or pwm-b as input, and
            # optionally have output inverted.

            ("db_config",   u16),
            # bit   0      rw  replace pwm-b by fed output
            # bit   1      rw  replace pwm-a by red output
            # bit   2      rw  invert red output
            # bit   3      rw  invert fed output
            # bit   4      rw  red input:  0 pwm-a  1 pwm-b
            # bit   5      rw  fed input:  0 pwm-a  1 pwm-b

            ("db_rise_delay",   u16),
            ("db_fall_delay",   u16),
            # bits  0- 9   rw  rising/falling edge delay (time base clocks)


            #-------- trip-zone ------------------------------------------------

            ("tz_enabled",  u16),
            # bits  0- 7   rw  enable tripzone 0-7 inputs for auto-reset trip
            # bits  8-15   rw  enable tripzone 0-7 inputs for manual-reset trip

            ("",            u16),

            ("tz_config",   u16),
            # bits  0- 1   rw  on trip force pwm-a:  0 hZ  1 high  2 low  3 no
            # bits  2- 3   rw  on trip force pwm-b:  0 hZ  1 high  2 low  3 no

            ("tz_irq",      EIrq),
            # bit   1      auto-reset trip
            # bit   2      manual-reset trip


            #-------- irq output -----------------------------------------------

            ("irq",         Irq),


            #-------- chopper --------------------------------------------------

            ("chopper",     u16),
            # bit   0      rw  chopper enabled
            # bits  1- 4   rw  initial pulse width (cycles / 8 - 1)
            # bits  5- 7   rw  chopper period - 1
            # bits  8-10   rw  duty cycle (0..6 = 1/8..7/8)


            ("",            u8 * (0x5c - 0x3e)),


            #-------- identification -------------------------------------------
            #
            # added in Freon/Primus?

            ("ident",       u32),  #r-  4'4d1'09'03  (v1.3.1)
        ]

    @property
    def divider( self ):
        cfg = self.config
        fine = ( cfg >> 7 ) & 7
        coarse = ( cfg >> 10 ) & 7
        if fine:
            return fine << ( 1 + coarse )
        else:
            return 1 << coarse

    @divider.setter
    def divider( self, value ):
        if value not in range( 1, 1793 ):
            raise ValueError( "Invalid ePWM divider" )
        cfg = self.config & ~0x1f80
        if value != 1:
            coarse = ( value & -value ).bit_length() - 1  # count trailing zeros
            coarse = min( coarse, 8 )
            fine = value >> coarse
            if coarse == 0 or fine > 7:
                raise ValueError( "ePWM divider %d (== %d << %d) not supported" % ( value, fine, coarse ) )
            cfg |= fine << 7
            cfg |= ( coarse - 1 ) << 10
        self.config = cfg

    def stop( self ):
        self.ld_compare[:] = ( 0, 0 )

        if ( self.config & 3 ) != 3:
            while self.cmp_load >> 8:
                pass

        self.config |= 3

    def initialize( self, period, divider=1 ):
        if period not in range( 2, 65536 ):
            raise ValueError( "Invalid ePWM period" )

        self.stop()

        self.pwm_a_config = 2 << 0 | 1 << 4  # set on counter zero, clear on compare A
        self.pwm_b_config = 2 << 0 | 1 << 8  # set on counter zero, clear on compare B
        self.cmp_load = 1 << 0 | 1 << 2  # reload cmp when counter reaches max
        self.config |= 1 << 15

        self.divider = divider
        self.ld_maximum = period - 1

        # set period immediately and reset counter
        self.config |= 1 << 3
        self.counter = 0
        self.ld_maximum = period - 1
        self.config &= ~( 1 << 3 )

        self.config &= ~3  # start counter

add_field( EPwm, 'ld_compare_a', EPwm.ld_compare.offset + 0, ctr_t )
add_field( EPwm, 'ld_compare_b', EPwm.ld_compare.offset + 2, ctr_t )

add_field( EPwm, 'pwm_a_config', EPwm.pwm_config.offset + 0, u16 )
add_field( EPwm, 'pwm_b_config', EPwm.pwm_config.offset + 2, u16 )

assert ctypes.sizeof(EPwm) == 0x60
