#!/usr/bin/python3

from uio import Uio
import ctypes
from ctypes import c_uint32 as uint


########## ADC  #####################################
#
# This will test the ADC Status Register
# Adapted from zmatt's l3-sn-test.py

adc = Uio( "adc" )

class Test( ctypes.Structure):
	_fields_ = [
		("status", uint, 32),
		];

testStatus  = adc.map(Test,0x44)
print( 'Status Register: ' + format( testStatus.status, '0{0}b'.format(32) ) )
