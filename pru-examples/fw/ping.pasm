// vim: ft=asm

#include "common.h"

main:
	lbbo	r0, r4, 0, 4
	sbbo	r0, r4, 4, 4
	jmp	main
