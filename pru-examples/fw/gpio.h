// vim: ft=asm

// GPIO controller base addresses
#define GPIO0	0x44e07100
#define GPIO1	0x4804c100
#define GPIO2	0x481ac100
#define GPIO3	0x481ae100

// WARNING:  if you need PRU to change the direction of GPIOs, make absolutely
// sure to not simultaneously use linux to change the direction of other GPIOs
// belonging to the same GPIO controller, since this incurs a race condition.
//
// Similarly, to avoid race conditions with linux, avoid writing directly to
// the GPIO_OUT register, use the GPIO_SET/CLEAR registers instead.

// For each of these registers, the 32 bits of a register represent each of
// the 32 GPIOs of the GPIO controller you're accessing.
#define GPIO_DIR	0x34  //rw  direction: 0 = output, 1 = input
#define GPIO_IN		0x38  //r-  input levels
#define GPIO_OUT	0x3c  //rw  output levels (if direction is output)
#define GPIO_CLEAR	0x90  //-s  write 1 to set output low
#define GPIO_SET	0x94  //-c  write 1 to set output high
