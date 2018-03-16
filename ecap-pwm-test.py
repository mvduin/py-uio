#!/usr/bin/python3

from ti.pwmss import Pwmss

cap = Pwmss( "/dev/uio/pwmss2" ).cap

FCK = 10**8  # 100 MHz


def initpwm( freq ):
    period = round( FCK / freq )
    if period < 1 or period > 0xffffffff:
        raise ValueError("invalid frequency")

    # disable module, set to pwm/timer mode
    cap.config = 1 << 25
    cap.irq.reset()

    # initialize pwm
    cap.pwm.maximum = period - 1
    cap.pwm.compare = 0

    # reset and start counter
    cap.counter = 0
    cap.config |= 1 << 20


def setpwm( duty ):
    if duty < 0 or duty > 1:
        raise ValueError("invalid duty cycle")

    period = cap.pwm.maximum + 1
    cap.pwm.ld_compare = round( duty * period )


initpwm( 2 )

setpwm( 0.75 )  # takes effect at next period

print( cap.counter, cap.counter, cap.counter )


IRQ_PERIOD  = 1 << 6
IRQ_COMPARE = 1 << 7
cap.irq.enable( IRQ_PERIOD | IRQ_COMPARE )

while True:
    events = cap.irq.recv()

    if events & (events - 1):
        print( "\revent overrun" )
    elif events & IRQ_PERIOD:
        print( "\rhigh ", end='', flush=True )
    elif events & IRQ_COMPARE:
        print( "\rlow  ", end='', flush=True )
