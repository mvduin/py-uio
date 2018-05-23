// vim: ft=asm

// sends a stream of fixed-size messages from pru to arm

#include "common.h"

.struct Message
	.u32	id
.ends

// constants passed by arm core
.struct BufInfo
	.u32	addr	// address of buffer
	.u32	len	// in bytes, also offset of pru->arm variables
.ends

// variables in ddr memory which are written by pru core
// located immediately after the message-buffer
.struct PruVars
	.u32	wptr	// write-pointer
.ends

// variables in pru local ram which are written by arm core
.struct ArmVars
	.u32	rptr	// read-pointer
	.u16	delay	// delay time (in cycles) between messages
.ends

// register allocation
.assign BufInfo, r4, r5,	buf
.assign PruVars, r6, r6,	pru
.assign ArmVars, r7, r8.w0,	arm
.assign Message, r9, r9,	msg


send_message:
	// generate message
	add	msg.id, msg.id, 1

	// write message to ringbuffer
	sbbo	&msg, buf.addr, pru.wptr, SIZE( msg )
	add	pru.wptr, pru.wptr, SIZE( msg )

	// wrap write-pointer around if necessary
	bne	no_wrap, pru.wptr, buf.len
	mov	pru.wptr, 0
no_wrap:

	// read arm variables
	lbco	&arm, c24, 0, SIZE( arm )

	// check for buffer overrun (write-pointer hit read-pointer)
	beq	buffer_overrun, pru.wptr, arm.rptr

	// write pru variables (update write-pointer in memory)
	sbbo	&pru, buf.addr, buf.len, SIZE( pru )
	
	// insert requested delay time
	loop	delay_end, arm.delay
	nop
delay_end:

	// next!
	jmp	send_message


buffer_overrun:
	halt
