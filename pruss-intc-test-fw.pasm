.setcallreg r3.w2
.origin 0

#define arg r14


.struct Params
	.u32	delay
	.u8	event
.ends

.assign Params, r4, *, params


	lbco	&params, c24, 0, SIZE(params)

main_loop:
	mov	arg, params.delay
	call	delay
	add	r31, params.event, 16
	qba	main_loop


delay:
	qbeq	delay_end, arg, 0
delay_loop:
	sub	arg, arg, 1
	qbne	delay_loop, arg, 0
delay_end:
	ret
