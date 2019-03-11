// vim: ft=asm

#include "common.h"

main:
	// toggle pru outputs 0-3
	xor	r30, r30, 0xF

	// wait half a second
	mov	r14, 500 * DELAY_MS
	delay	r14

	// repeat in infinite loop
	jmp	main
