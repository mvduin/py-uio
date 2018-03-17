--ram_model
--stack_size 0x100
--heap_size 0x100

/* diagnostic output */
-abs

/* link-time optimization */
/* --make_static */



MEMORY
{
	PAGE 0:   /* instruction address space */
	IRAM	(  IX) : org = 0x00000000,  len = 0x1ffc
	
	PAGE 1:   /* data address space */
	LOCAL	(RWI ) : org = 0x00000000,  len = 0x1ffc
	PEER	(RWI ) : org = 0x00002000,  len = 0x2000
	SHARED	(RWI ) : org = 0x00010000,  len = 0x3000
}

SECTIONS
{
	.text       : {} > IRAM, PAGE 0

	.init_array : {} > LOCAL, PAGE 1   /* constructors */
	.cinit      : {} > LOCAL, PAGE 1   /* init tables used by --rom_model */

	.rodata     : {} > LOCAL, PAGE 1
	.data       : {} > LOCAL, PAGE 1
	.bss        : {} > LOCAL, PAGE 1

	.rofardata  : {} > SHARED, PAGE 1
	.fardata    : {} > SHARED, PAGE 1
	.farbss     : {} > SHARED, PAGE 1

	.sysmem     : {} > LOCAL, PAGE 1   /* heap */
	.stack      : {} > LOCAL, PAGE 1
}

