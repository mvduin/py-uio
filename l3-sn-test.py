#!/usr/bin/python3

from uio import Uio


########## L3 interconnect service network #####################################
#
# Welcome to the most fussy register space on the SoC!
# Only single word access allowed. Byte/halfword/multi-word access = bus error.

l3_sn = Uio( "/dev/uio/l3-sn" )

# Flag combiner structure:
#   [0] component id = 0x370001
#   [1] component hash
#   [2] flag 0, inputs enabled (read/write)
#   [3] flag 0, inputs asserted
#   [4] flag 1, inputs enabled (read/write)
#   [5] flag 1, inputs asserted
#
# On the AM335x flagcombiners are used to collect fault irqs from target agents.
# Flag 0 = non-debug fault, flag 1 = debug fault.  Generally you only care about
# the former.  Flag 0 output of the top-level combiner triggers an irq which can
# be received through the uio device.
#
# Note that some other SoCs also have flagcombiners with only one flag, in which
# case the component size is 0x10 and access beyond that gives bus error.
#
fc_top = l3_sn.map( "l3f", 0x1100, 0x18 ).cast('I')
fc_l3f = l3_sn.map( "l3f", 0x1000, 0x18 ).cast('I')
fc_l3s = l3_sn.map( "l3s",  0x600, 0x18 ).cast('I')

for i in fc_top, fc_l3s, fc_l3f:
    assert i[0] == 0x370001 # verify component type
    i[2] = 0xffffffff       # enable all inputs
    n = i[2].bit_length()   # check how many we actually got
    print( 'inputs: ' + format( i[3], '0{0}b'.format(n) ) )
