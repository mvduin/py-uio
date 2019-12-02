// vim: ft=asm

#include "common.h"

	// dispatch table
	jmp	load_spam	// 0
	jmp	store_spam	// 1
	jmp	load_spam_nop	// 2
	jmp	store_spam_nop	// 3
	jmp	store_spam_nop4	// 4
	jmp	store_toggle	// 5

load_spam:
	slp	1
	loop	load_spam_end, r0.w2
	lbbo	&r2, r1, 0, b0
load_spam_end:
	halt

store_spam:
	slp	1
	loop	store_spam_end, r0.w2
	sbbo	&r2, r1, 0, b0
store_spam_end:
	halt

load_spam_nop:
	slp	1
	loop	load_spam_nop_end, r0.w2
	lbbo	&r2, r1, 0, b0
	nop
load_spam_nop_end:
	halt

store_spam_nop:
	slp	1
	loop	store_spam_nop_end, r0.w2
	sbbo	&r2, r1, 0, b0
	nop
store_spam_nop_end:
	halt

store_spam_nop4:
	slp	1
	loop	store_spam_nop4_end, r0.w2
	sbbo	&r2, r1, 0, b0
	nop
	nop
	nop
	nop
store_spam_nop4_end:
	halt

store_toggle:
	slp	1
	loop	store_toggle_end, r0.w2
	sbbo	&r2, r1, 0, 8
	sbbo	&r4, r1, 0, 8
store_toggle_end:
	halt
