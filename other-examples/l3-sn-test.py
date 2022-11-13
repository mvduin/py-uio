#!/usr/bin/python3

from uio.device import Uio
from uio.utils import fix_ctypes_struct
import ctypes
from ctypes import c_uint32 as uint


########## L3 interconnect service network #####################################
#
# Welcome to the most fussy register space on the SoC!
# Only single word access allowed. Byte/halfword/multi-word access = bus error.

@fix_ctypes_struct
class ComponentID( ctypes.Structure ):
    _fields_ = [
            ("vendor",  uint, 16),  # 1 = Arteris
            ("type",    uint, 16),
            ("hash",    uint, 24),
            ("version", uint,  8),
        ]

@fix_ctypes_struct
class FlagCombiner( ctypes.Structure ):
    src_t = uint  # one bit per input

    _fields_ = [
            ("component",   ComponentID), # vendor 1 type 0x37
            ("enabled",     src_t),  #rw
            ("pending",     src_t),  #r-
            # these may be a second enabled/pending pair used for debug (jtag) access
        ]

@fix_ctypes_struct
class ErrorLog( ctypes.Structure ):
    err_policy_t = uint  # 0 = ignore, 1 = log, 2 = log+irq

    _fields_ = [
            ("req_policy",  err_policy_t),
            ("resp_policy", err_policy_t),
            ("status",      uint),
            ("raw",         uint * 13),
        ]

@fix_ctypes_struct
class TargetAgent( ctypes.Structure ):
    _fields_ = [
            ("component",   ComponentID), # vendor 1 type 0x13
            ("ctrlstat",    uint),
            #                   bit   0     rw  access enabled
            #                   bit   1     --
            #                   bit   2     r-  fault output asserted
            #                   bit   3     rw  "cm" internal testing, must be zero
            ("",            uint),
            ("_id",         uint),  #r-
            ("",            uint*11),
            ("err",         ErrorLog),
            ("_size",       uint),  #rw  size of address space / 4KB, log2
        ]

    @property
    def enabled( self ):
        return bool( self.ctrlstat & 1 )

    @enabled.setter
    def enabled( self, value ):
        if value:
            self.ctrlstat |= 1
        else:
            self.ctrlstat &= ~1

    @property
    def fault_asserted( self ):
        return bool( self.ctrlstat & 4 )

# L3 SN HostAgent is too similar to TargetAgent to bother with a separate struct
HostAgent = TargetAgent


########## AM335x ("Subarctic") L3 interconnect service network ################

l3_sn = Uio( "/dev/uio/l3-sn" )
l3f_sn = l3_sn.region( "l3f" )
l3s_sn = l3_sn.region( "l3s" )

host_l3f  = l3f_sn.map( HostAgent,     0x000 )  # id 0x00, no irq
ta_hash   = l3f_sn.map( TargetAgent,   0x200 )  # id 0x02, fc_l3f  9
ta_aes1   = l3f_sn.map( TargetAgent,   0x300 )  # id 0x03, fc_l3f 10 -- UNUSED
ta_ocmc   = l3f_sn.map( TargetAgent,   0x400 )  # id 0x10, fc_l3f  2
ta_aes0   = l3f_sn.map( TargetAgent,   0x500 )  # id 0x04, fc_l3f 11
ta_exp    = l3f_sn.map( TargetAgent,   0x600 )  # id 0x06, fc_l3f  8 -- UNUSED
ta_tptc0  = l3f_sn.map( TargetAgent,   0x700 )  # id 0x07, fc_l3f  3
ta_tptc1  = l3f_sn.map( TargetAgent,   0x800 )  # id 0x08, fc_l3f  4
ta_tptc2  = l3f_sn.map( TargetAgent,   0x900 )  # id 0x09, fc_l3f  5
ta_l4hs   = l3f_sn.map( TargetAgent,   0xa00 )  # id 0x05, fc_l3f 12
ta_tpcc   = l3f_sn.map( TargetAgent,   0xb00 )  # id 0x0b, fc_l3f  6
ta_sgx    = l3f_sn.map( TargetAgent,   0xc00 )  # id 0x0e, fc_l3f 13
ta_dbgss  = l3f_sn.map( TargetAgent,   0xd00 )  # id 0x1f, fc_l3f  7
ta_pcie   = l3f_sn.map( TargetAgent,   0xe00 )  # id 0x0f, fc_l3f  1 -- UNUSED
ta_emif   = l3f_sn.map( TargetAgent,   0xf00 )  # id 0x01, fc_l3f  0
fc_l3f    = l3f_sn.map( FlagCombiner, 0x1000 )  # 14 × { app, dbg }, fc_top 0
fc_top    = l3f_sn.map( FlagCombiner, 0x1100 )  #  2 × { app, dbg }

host_l3s  = l3s_sn.map( HostAgent,     0x000 )  # id 0x0c, no irq
ta_l4ls_0 = l3s_sn.map( TargetAgent,   0x100 )  # id 0x11, fc_l3s  0
ta_l4ls_1 = l3s_sn.map( TargetAgent,   0x200 )  # id 0x12, fc_l3s  1 ?
ta_l4ls_2 = l3s_sn.map( TargetAgent,   0x300 )  # id 0x13, fc_l3s  2 ?
ta_l4ls_3 = l3s_sn.map( TargetAgent,   0x400 )  # id 0x14, fc_l3s  3 ?
ta_adc    = l3s_sn.map( TargetAgent,   0x500 )  # id 0x0a, fc_l3s 10
fc_l3s    = l3s_sn.map( FlagCombiner,  0x600 )  # 13 × { app, dbg }, fc_top 1
ta_gpmc   = l3s_sn.map( TargetAgent,   0x700 )  # id 0x1e, fc_l3s  7
ta_mcasp0 = l3s_sn.map( TargetAgent,   0x800 )  # id 0x20, fc_l3s  4
ta_mcasp1 = l3s_sn.map( TargetAgent,   0x900 )  # id 0x21, fc_l3s  5
ta_mcasp2 = l3s_sn.map( TargetAgent,   0xa00 )  # id 0x22, fc_l3s  6 -- UNUSED
ta_usb    = l3s_sn.map( TargetAgent,   0xb00 )  # id 0x27, fc_l3s  9
ta_mmc2   = l3s_sn.map( TargetAgent,   0xc00 )  # id 0x26, fc_l3s 12
ta_l4fw   = l3s_sn.map( TargetAgent,   0xd00 )  # id 0x1b, fc_l3s  8
ta_l4wk_0 = l3s_sn.map( TargetAgent,   0xe00 )  # id 0x0d, fc_l3s 11

fc_top.src = [ fc_l3f, fc_l3s ]
fc_l3f.src = [ ta_emif, ta_pcie, ta_ocmc, ta_tptc0, ta_tptc1, ta_tptc2, ta_tpcc, ta_dbgss,
        ta_exp, ta_hash, ta_aes1, ta_aes0, ta_l4hs, ta_sgx ]
fc_l3s.src = [ ta_l4ls_0, ta_l4ls_1, ta_l4ls_2, ta_l4ls_3, ta_mcasp0, ta_mcasp1, ta_mcasp2,
        ta_gpmc, ta_l4fw, ta_usb, ta_adc, ta_l4wk_0, ta_mmc2 ]


for i in fc_top, fc_l3s, fc_l3f:
    assert i.component.vendor == 1
    assert i.component.type == 0x37
    i.enabled = 0xffffffff      # enable all inputs
    n = i.enabled.bit_length()  # check how many we actually got
    print( 'inputs: ' + format( i.pending, '0{0}b'.format(n) ) )
