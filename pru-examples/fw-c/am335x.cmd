/* vim: ft=ld
 */
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
	IRAM	(  IX) : org = 0x00000000,  len = 0x2000  /* 8K iram */

	PAGE 1:   /* data address space */
	LOCAL	(RWI ) : org = 0x00000000,  len = 0x2000,  cregister = 24  /* 8K data ram for this core */
	SHARED	(RWI ) : org = 0x00010000,  len = 0x3000,  cregister = 28  /* 12K shared data ram */

	PAGE 2:   /* uninitializable space */
	PEER	(RW  ) : org = 0x00002000,  len = 0x2000,  cregister = 25  /* 8K data ram for other core */

	PRU_CFG	(RW  ) : org = 0x00026000,  len = 0x1000,  cregister =  4
	PRU_ECAP(RW  ) : org = 0x00030000,  len = 0x1000,  cregister =  3
	PRU_IEP	(RW  ) : org = 0x0002e000,  len = 0x1000,  cregister = 26
	PRU_INTC(RW  ) : org = 0x00020000,  len = 0x1000,  cregister =  0
	PRU_UART(RW  ) : org = 0x00028000,  len = 0x1000,  cregister =  7
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

