from uio import fix_ctypes_struct, struct_field, cached_getter
import ctypes
from ctypes import c_uint8 as ubyte, c_uint16 as ushort, c_uint32 as uint
from ti.irqc4 import IrqCombiner

# determine lcdc functional clock
def lcdc_fck():
    try:
        with open( "/sys/kernel/debug/clk/lcd_gclk/clk_rate", 'rb' ) as f:
            return int( f.read() )
    except PermissionError:
        pass
    # fiiine, I'll do it the hard way
    from devicetree import dt
    dt_lcdc = dt('&lcdc')
    assert dt_lcdc.u32('assigned-clocks') == dt('&lcd_gclk').phandle
    lcdc_gclk_parent = dt_lcdc.u32('assigned-clock-parents')
    if lcdc_gclk_parent == dt('&dpll_core_m5_ck').phandle:
        return 250000000
    if lcdc_gclk_parent == dt('&dpll_per_m2_ck').phandle:
        return 192000000
    if lcdc_gclk_parent != dt('&dpll_disp_m2_ck').phandle:
        raise RuntimeError("unknown clock parent for lcd_gclk")
    rate = dt_lcdc.u32('assigned-clock-rates')
    if rate == 0:
        raise RuntimeError("clock rate not configured for lcd_gclk")
    return rate

#--------- Remote Framebuffer (RFB) interface ----------------------------------
#
# Pin usage for various protocols:
#
#   vsync   pclk    hsync   acb/oe  mclk        protocol
#   ------  ------  ------  ------  ------      ------------------------
#   nALE    EN      RnW     nCS0    MCLK        0: motorola 6800 (sync)
#   nALE    EN      RnW     nCS0    nCS1        1: motorola 6800 (async)
#   nALE    nRS     nWS     nCS0    MCLK        2: intel 8080 (sync)
#   nALE    nRS     nWS     nCS0    nCS1        3: intel 8080 (async)
#   RS      -       RnW     E0      E1          4: hitachi hd44780
#
# (RS in hitachi mode is equivalent to nALE in other modes.)
#
#   RnW nALE
#   0   0       write command/address
#   1   0       read status
#   0   1       write data
#   1   1       read data
#
# where:
#   nRS = ~(EN & RnW)
#   nWS = ~(EN & ~RnW)
#   E0 = EN & ~nCS0
#   E1 = EN & ~nCS1
#
# transfer cycle ( data[], nALE, RnW )
#   set nCS=0, data[], nALE, RnW
#   wait SU         (0-31 cycles)
#   set EN=1
#   wait STROBE     (1-63 cycles)
#   sample data[] if read
#   set EN=0
#   wait HOLD       (1-15 cycles)
#   set nCS=1, nALE=1, RnW=1

@fix_ctypes_struct
class RfbCs( ctypes.Structure ):
    _fields_ = [
            # timing configuration
            ('cs_delay',    uint, 2),  #rw  min idle cycles - ceil(7/clkdiv)
            ('rd_hold',     uint, 4),  #rw  read hold cycles (1-15)
            ('rd_strobe',   uint, 6),  #rw  read strobe cycles (1-63)
            ('rd_setup',    uint, 5),  #rw  read setup cycles (0-31)
            ('wr_hold',     uint, 4),  #rw  write hold cycles (1-15)
            ('wr_strobe',   uint, 6),  #rw  write strobe cycles (1-63)
            ('wr_setup',    uint, 5),  #rw  write setup cycles (0-31)

            # direct transfer (not allowed when dma is enabled)
            ('address',     uint),     #->  address transfer
            ('data',        uint),     #<>  data transfer
        ]

    # for hd44780 protocol
    cmd     = struct_field( 4, uint )  #->  cmd transfer
    status  = struct_field( 4, uint )  #<-  status transfer

assert ctypes.sizeof(RfbCs) == 12

@fix_ctypes_struct
class Rfb( ctypes.Structure ):
    _fields_ = [
            # interface configuration
            ('protocol',        uint, 3),  #rw  protocol (see above)
            ('invert_ale_rs',   uint, 1),  #rw  invert vsync pin
            ('invert_rs_en',    uint, 1),  #rw  invert pclk pin
            ('invert_ws_rw',    uint, 1),  #rw  invert hsync pin
            ('invert_cs0',      uint, 1),  #rw  invert acb/oe pin
            ('invert_cs1_mclk', uint, 1),  #rw  invert mclk pin

            # control
            ('dma_enable',      uint, 1),  #rw
            ('dma_cs',          uint, 1),  #rw

            ('cs0',             RfbCs),
            ('cs1',             RfbCs),
        ]

    @cached_getter
    def cs( self ):
        return [ self.cs0, self.cs1 ]

assert ctypes.sizeof(Rfb) == 0x28 - 0x0c


#--------- Raster controller ---------------------------------------------------

@fix_ctypes_struct
class Raster( ctypes.Structure ):
    _fields_ = [ ('', uint * 6) ]  # TODO

assert ctypes.sizeof(Raster) == 0x40 - 0x28


#--------- Dma controller ------------------------------------------------------

@fix_ctypes_struct
class Dma( ctypes.Structure ):
    _fields_ = [ ('', uint * 5) ]  # TODO

assert ctypes.sizeof(Dma) == 0x54 - 0x40


#--------- LCDC subsystem ------------------------------------------------------

@fix_ctypes_struct
class Lcdc( ctypes.Structure ):
    _fields_ = [
            #--------- global config -------------------------------------------

            ('ident',       uint),      #r-
            ('pinmux',      ubyte, 1),  #rw  0=rfb, 1=raster
            ('clock_div',   ubyte),     #rw  fck/mck divider
            ('',            uint),

            # clock_div == 0 is treated like clock_div == 1
            #
            # minimum clock_div values:
            #   1   rfb
            #   2   raster active
            #   3   raster passive color (8 pixels per 3 cycles)
            #   4   raster passive monochrome (4 pixels per cycle)
            #   8   raster passive monochrome (8 pixels per cycle)

            #--------- remote framebuffer interface ----------------------------

            ('rfb',         Rfb),

            #--------- raster controller ---------------------------------------

            ('raster',      Raster),

            #--------- dma controller ------------------------------------------

            ('dma',         Dma),

            #--------- subsystem wrapper ---------------------------------------

            # sysconfig
            ('',            uint, 2),
            ('idlemode',    uint, 2),   #rw  0=force, 1=block, 2=auto
            ('standbymode', uint, 2),   #rw  0=force, 1=block, 2=auto
            ('',            uint * 0),

            # irq combiner
            ('irq',         IrqCombiner),
            ('eoi',         uint),      #->

            # local clock control
            ('en_raster',   uint, 1),  #rw
            ('en_rfb',      uint, 1),  #rw
            ('en_dma',      uint, 1),  #rw
            ('',            uint * 0),

            # local reset control (does not affect config registers)
            ('rst_raster',  uint, 1),  #rw
            ('rst_rfb',     uint, 1),  #rw
            ('rst_dma',     uint, 1),  #rw
            ('rst_global',  uint, 1),  #rw
            ('',            uint * 0),
        ]

assert ctypes.sizeof(Lcdc) == 0x74
