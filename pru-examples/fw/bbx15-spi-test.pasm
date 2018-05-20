// vim: ft=asm

#include "common.h"

// Simple spi peripheral (mode 3) for testing purposes

// r31:
//	bit  1 = sclk
//	bit  2 = cs
//	bit 11 = mosi
// r30:
//	bit  8 = miso

main:
	weq	r31.b0, 0		// wait until chip select and clock are low
	xor	r30.b1, r30.b1, r0	// toggle miso if previous mosi was high
	wbs	r31.t1			// wait until clock high
	lsr	r0, r31, 11		// sample mosi
	jmp	main
