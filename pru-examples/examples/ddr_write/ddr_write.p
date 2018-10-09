.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 	19
#define MAGIC_NUMBER		0xbabe7175		// Magic number  
#define CTPPR_1         	0x2202C 

START:
    LBCO r0, C4, 4, 4					// Load Bytes Constant Offset (?)
    CLR  r0, r0, 4						// Clear bit 4 in reg 0
    SBCO r0, C4, 4, 4					// Store Bytes Constant Offset

 	MOV  r0, 0							// Load the dataram address into r0
	LBBO r2, r0, 0, 4					// Load the ddr_addr from the first adress in the PRU0 DRAM

	MOV r1, MAGIC_NUMBER				// Place the magic number ito the register
	SBBO r1, r2, 0, 4					// Write the magic number into DDR, addr is now in r2

 	MOV  r0, 0x00000004					// Load the dataram address into r0
	LBBO r2, r0, 0, 4					// Load the ddr_addr from the first adress in the PRU0 DRAM

	MOV r1, MAGIC_NUMBER				// Place the magic number ito the register
	SBBO r1, r2, 0, 4					// Write the magic number into DDR, addr is now in r2

	MOV R31.b0, PRU0_ARM_INTERRUPT+16   // Send notification to Host that the instructions are done
HALT
