// vim: ft=asm

// Change link register to something other than the pasm default (r30).
// (EABI uses r3.w2, we may as well roll with that.)
.setcallreg r3.w2

// Programs normally always start at address 0
.origin 0

// Saner compare-and-branch mnemonics.  (The "quick" doesn't mean anything, and
// more disturbingly lt/gt behave the opposite of what you would expect.)
#define blt qbgt
#define bgt qblt
#define ble qbge
#define bge qble
#define beq qbeq
#define bne qbne
#define bbs qbbs
#define bbc qbbc

// Generalize the "wait until" macros
#define weq bne 0,
#define wne beq 0,
#define wlt bge 0,
#define wgt ble 0,
#define wle bgt 0,
#define wge blt 0,

// General utility
.macro nop
	mov	r0.b0, r0.b0
.endm

// For the "set" instruction, using r31 as source operand is treated as zero.
// Since this is not very intuitive, use a macro for moving a single-bit value.
.macro movbit
.mparam dst, bit
	set	dst, r31, bit
.endm

// Trigger event (in range 16..31) in interrupt controller
.macro sendevent
.mparam ev
	mov	r31.w0, ( (ev) & 15 ) | 32
.endm

// Delay 2*n cycles (== n * 10ns), where n must be nonzero.
.macro delay
.mparam n
delay_loop:
	sub	n, n, 1
	bne	delay_loop, n, 0
.endm

#define DELAY_US 100
#define DELAY_MS 100000
