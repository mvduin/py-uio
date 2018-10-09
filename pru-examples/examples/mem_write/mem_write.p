.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 19
#define CONST_PRUDRAM C24


START:	
    LBCO r0, C4, 4, 4					
    CLR  r0, r0, 4					
    SBCO r0, C4, 4, 4					
; load
    LBCO r0.b0, CONST_PRUDRAM, 1, 1 ; read byte 1			
    LBCO r0.b1, CONST_PRUDRAM, 2, 1 ; read byte 2
; add
    ADD r0.b2, r0.b0, r0.b1
; write result
    SBCO r0.b2, CONST_PRUDRAM, 3, 1 ; write to byte 3
; send interrupt
    MOV R31.b0, PRU0_ARM_INTERRUPT+16   
HALT
