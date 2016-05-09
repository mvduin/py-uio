#pragma once

#define LED0    21  // V15 / io 1.21
#define LED1    22  // U15 / io 1.22
#define LED2    23  // T15 / io 1.23
#define LED3    24  // V16 / io 1.24

#define AU_OSC_EN  27 // V17 / io 1.27 / audio osc enable

#define CON_CTS 90  // E18 / io 1.08 / uart 0 cts (not connected)
#define CON_RTS 91  // E17 / io 1.09 / uart 0 rts (TP9)
#define CON_RXD 92  // E15 / io 1.10 / uart 0 rxd
#define CON_TXD 93  // E16 / io 1.11 / uart 0 txd

//	P8_01       // gnd
//	P8_02       // gnd
#define P8_03    6  // R09 / io 1.06 / emmc d6
#define P8_04    7  // T09 / io 1.07 / emmc d7
#define P8_05    2  // R08 / io 1.02 / emmc d2
#define P8_06    3  // T08 / io 1.03 / emmc d3
#define P8_07   36  // R07 / io 2.02
#define P8_08   37  // T07 / io 2.03
#define P8_09   39  // T06 / io 2.05
#define P8_10   38  // U06 / io 2.04
#define P8_11   13  // R12 / io 1.13
#define P8_12   12  // T12 / io 1.12
#define P8_13    9  // T10 / io 0.23
#define P8_14   10  // T11 / io 0.26
#define P8_15   15  // U13 / io 1.15
#define P8_16   14  // V13 / io 1.14
#define P8_17   11  // U12 / io 0.27
#define P8_18   35  // V12 / io 2.01
#define P8_19    8  // U10 / io 0.22
#define P8_20   33  // V09 / io 1.31 / emmc cmd
#define P8_21   32  // U09 / io 1.30 / emmc clk
#define P8_22    5  // V08 / io 1.05 / emmc d5
#define P8_23    4  // U08 / io 1.04 / emmc d4
#define P8_24    1  // V07 / io 1.01 / emmc d1
#define P8_25    0  // U07 / io 1.00 / emmc d0
#define P8_26   31  // V06 / io 1.29
#define P8_27   56  // U05 / io 2.22 / lcd vsync
#define P8_28   58  // V05 / io 2.24 / lcd pclk
#define P8_29   57  // R05 / io 2.23 / lcd hsync
#define P8_30   59  // R06 / io 2.25 / lcd acb/oe
#define P8_31   54  // V04 / io 0.10 / lcd d14 / sysboot 14
#define P8_32   55  // T05 / io 0.11 / lcd d15 / sysboot 15
#define P8_33   53  // V03 / io 0.09 / lcd d13 / sysboot 13
#define P8_34   51  // U04 / io 2.17 / lcd d11 / sysboot 11
#define P8_35   52  // V02 / io 0.08 / lcd d12 / sysboot 12
#define P8_36   50  // U03 / io 2.16 / lcd d10 / sysboot 10
#define P8_37   48  // U01 / io 2.14 / lcd d8 / sysboot 8
#define P8_38   49  // U02 / io 2.15 / lcd d9 / sysboot 9
#define P8_39   46  // T03 / io 2.12 / lcd d6 / sysboot 6
#define P8_40   47  // T04 / io 2.13 / lcd d7 / sysboot 7
#define P8_41   44  // T01 / io 2.10 / lcd d4 / sysboot 4
#define P8_42   45  // T02 / io 2.11 / lcd d5 / sysboot 5
#define P8_43   42  // R03 / io 2.08 / lcd d2 / sysboot 2
#define P8_44   43  // R04 / io 2.09 / lcd d3 / sysboot 3
#define P8_45   40  // R01 / io 2.06 / lcd d0 / sysboot 0
#define P8_46   41  // R02 / io 2.07 / lcd d1 / sysboot 1

//	P9_01       // gnd
//	P9_02       // gnd
//	P9_03       // vdd_3v3b
//	P9_04       // vdd_3v3b
//	P9_05       // sys_5v (pmic out)
//	P9_06       // sys_5v (pmic out)
//	P9_07       // dc_5v (pmic in)
//	P9_08       // dc_5v (pmic in)
//	P9_09       // power btn (pmic)
#define P9_10  110  // A10 / reset
#define P9_11   28  // T17 / io 0.30
#define P9_12   30  // U18 / io 1.28
#define P9_13   29  // U17 / io 0.31
#define P9_14   18  // U14 / io 1.18
#define P9_15a  16  // R13 / io 1.16
#define P9_15b  34  // T13 / io 2.00
#define P9_16   19  // T14 / io 1.19
#define P9_17   87  // A16 / io 0.05 / spi 0 cs 0
#define P9_18   86  // B16 / io 0.04 / spi 0 out
#define P9_19   95  // D17 / io 0.13 / i2c 2 scl
#define P9_20   94  // D18 / io 0.12 / i2c 2 sda
#define P9_21   85  // B17 / io 0.03 / spi 0 in
#define P9_22   84  // A17 / io 0.02 / spi 0 clk
#define P9_23   17  // V14 / io 1.17
#define P9_24   97  // D15 / io 0.15
#define P9_25  107  // A14 / io 3.21 / audio osc
#define P9_26   96  // D16 / io 0.14
#define P9_27  105  // C13 / io 3.19
#define P9_28  103  // C12 / io 3.17 / hdmi audio data
#define P9_29  101  // B13 / io 3.15 / hdmi audio fs
#define P9_30  102  // D12 / io 3.16
#define P9_31  100  // A13 / io 3.14 / hdmi audio clk
#define P9_32  206  // D08 / adc vdd
#define P9_33  199  // C08 / adc ch 4
#define P9_34  207  // E08 / adc gnd
#define P9_35  197  // A08 / adc ch 6
#define P9_36  198  // B08 / adc ch 5
#define P9_37  201  // B07 / adc ch 2
#define P9_38  200  // A07 / adc ch 3
#define P9_39  203  // B06 / adc ch 0
#define P9_40  202  // C07 / adc ch 1
#define P9_41a 109  // D13 / io 0.20 / emu 3
#define P9_41b 106  // D14 / io 3.20 / clk out 1
#define P9_42a  89  // C18 / io 0.07
#define P9_42b 104  // B12 / io 3.18
//	P9_43       // gnd
//	P9_44       // gnd
//	P9_45       // gnd
//	P9_46       // gnd
