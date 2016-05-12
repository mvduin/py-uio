#!/usr/bin/python3

from uio import Uio
import ctypes
from ctypes import c_uint32 as uint
from ctypes import c_char as byte

########## ADC  #####################################
#
# This will test the ADC Status Register
# Adapted from zmatt's l3-sn-test.py

adc = Uio( "adc" )
class Step( ctypes.Structure ):
    _fields_ = [
        ("stepconfig", uint, 32),
        ("stepdelay", uint, 32),
    ];
class ADC( ctypes.Structure ):
    _fields_ = [
        ("revision", uint, 32),
        ("spacer01", byte*(0x10-4)),
        ("sysconfig", uint, 32),
        ("spacer02", byte*16),
        ("irqstatus_raw", uint, 32),
        ("irqstatus", uint, 32),
        ("irqenable_set", uint, 32),
        ("irqenable_clr", uint, 32),
        ("irqwakeup", uint, 32),
        ("dmaenable_set", uint, 32),
        ("dmaenable_clr", uint, 32),
        ("ctrl", uint, 32),
        ("adcstat", uint, 32),
        ("adcrange", uint, 32),
        ("adc_clkdiv", uint, 32),
        ("adc_misc", uint, 32),
        ("stepenable", uint,  32),
        ("idleconfig", uint, 32),
        ("ts_charge_stepconfig", uint, 32),
        ("ts_charge_delay", uint, 32),
        ("steps", Step*16),
        ("fifo0count", uint, 32),
        ("fifo0threshold", uint, 32),
        ("dma0req", uint, 32),
        ("fifo1count", uint, 32),
        ("fifo1threshold", uint, 32),
        ("dma1req", uint, 32),
        ("spacer03", byte*4),
        ("fifo0data", uint, 32),
        ("spacer04", byte*0x1FC),
        ("fifo1data", uint, 32)
    ];
testStatus  = adc.map(ADC)
print( 'Status Register: ' + format( testStatus.dmaenable_set, '0{0}b'.format(32) ) )
