.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 19
#define CONST_PRUDRAM C24


START:	
    LBCO r0, C4, 4, 4					
    CLR  r0, r0, 4					
    SBCO r0, C4, 4, 4					
; send interrupt
    MOV R31.b0, PRU0_ARM_INTERRUPT+16
HALT
