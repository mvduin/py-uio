// vim: ft=asm

#include "common.h"

	jmp	load_spam
	jmp	store_spam
	jmp	load_spam_nop
	jmp	store_spam_nop
	jmp	store_spam_nop4

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
