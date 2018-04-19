// vim: ft=asm

#include "common.h"

#define arg r14


.struct Params
	.u32	delay
	.u8	event
.ends

.assign Params, r4, *, params


	// load parameters from local ram
	lbco	&params, c24, 0, SIZE(params)

main_loop:
	mov	arg, params.delay
	call	delay

	// send event
	add	r31, params.event, 16

	jmp	main_loop


delay:
	beq	delay_end, arg, 0
delay_loop:
	sub	arg, arg, 1
	bne	delay_loop, arg, 0
delay_end:
	ret
