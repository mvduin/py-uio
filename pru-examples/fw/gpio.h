// vim: ft=asm

// GPIO controller base addresses
#define GPIO0	0x44e07100
#define GPIO1	0x4804c100
#define GPIO2	0x481ac100
#define GPIO3	0x481ae100

// To avoid race conditions with code running on the cortex-a8, do not write
// directly to GPIO_OUT.  Use the SET/CLEAR registers instead.
#define GPIO_IN		0x38  //r-  received levels
#define GPIO_OUT	0x3c  //rw  output levels (if output enabled)
#define GPIO_CLEAR	0x90  //-s  write 1 to set output low
#define GPIO_SET	0x94  //-c  write 1 to set output high
