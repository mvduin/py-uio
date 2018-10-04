.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 19

#define MAGIC_FOR_RAM0  0xbabe0000
#define MAGIC_FOR_RAM1  0xbabe0001
#define MAGIC_FOR_RAM2  0xbabe0002

START:	
    LBCO r0, C4, 4, 4					// Load the config 
    CLR  r0, r0, 4						// No, really, clear it!
    SBCO r0, C4, 4, 4					// Actually i have no idea what this does

    MOV  r0, 0x0120
    MOV  r1, 0x00022028
    SBBO r0, r1, 0, 4
    MOV  r1, 0x00024028
    SBBO r0, r1, 0, 4

    MOV r0, MAGIC_FOR_RAM0               // r0 = other knwon, strange sequence
    SBCO r0, c24, 0, 4                  // Place sequence in local PRU 0 ram    

    MOV r0, MAGIC_FOR_RAM1               // r0 = other knwon, strange sequence
    SBCO r0, c25, 0, 4                  // Place sequence in local PRU 0 ram    

    MOV r0, MAGIC_FOR_RAM2            // r0 = known, strange sequence
    SBCO r0, c28, 0, 4                   // Place the sequence in shared ram 

    MOV R31.b0, PRU0_ARM_INTERRUPT+16   // Send notification to Host for program completion
HALT
