#include "common.h"

.struct Params
	.u32	count		// number of pulses, must be non-zero
	.u32	on_time		// on-time in 10ns units, must be > 1
	.u32	off_time	// off-time in 10ns units, must be > 2
.ends

.assign Params, r4, *, params

#define arg r14

#define OUTPUT_LINE 0

pulse_loop:
	// set output high
	set	r30,  r30, OUTPUT_LINE

	// wait (2*params.on_time - 2) cpu cycles
	sub	arg,  params.on_time, 1
	delay	arg

	// set output low
	clr	r30,  r30, OUTPUT_LINE

	// wait (2*params.off_time - 4) cpu cycles
	sub	arg,  params.off_time, 2
	delay	arg

	// check if more pulses to be sent
	sub	params.count,  params.count, 1
	bne	pulse_loop,  params.count, 0

	// send event to indicate completion
	sendevent 16

	// halt cpu
	halt
