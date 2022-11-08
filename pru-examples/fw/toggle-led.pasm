// vim: ft=asm

#include "common.h"
#include "gpio.h"

// give names to the registers we use
#define gpio1	r10
#define tmp	r14

// leds are gpios 21-24 on gpio1
#define USR0	21
#define USR1	22
#define USR2	23
#define USR3	24

// select which one we use
#define LED	USR3


start:
	mov	gpio1, GPIO1

	// check if led is currently on or off
	lbbo	tmp, gpio1, GPIO_OUT, 4
	bbs	led_on, tmp, LED

led_off:  // led is off, turn it on
	movbit	tmp, LED
	sbbo	tmp, gpio1, GPIO_SET, 4
	halt

led_on:   // led is on, turn it off
	movbit	tmp, LED
	sbbo	tmp, gpio1, GPIO_CLEAR, 4
	halt
