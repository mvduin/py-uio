// vim: ft=asm

#include "common.h"

#define arg r14

	loop	loop1_end, 3
	nop
	nop
loop1_end:

	mov	r0, 3
	loop	loop2_end, r0
	nop
	nop
loop2_end:

	halt
