// Fast speed test. Each loop iteration takes 3 instruction cycles = 15ns
.origin 0
.entrypoint START
 
START:
    LBCO r0, C4, 4, 4      
    CLR  r0, r0, 4         
    SBCO r0, C4, 4, 4      
 
BLINK:
    MOV r30, 1<<14
    MOV r30, 0
    QBA BLINK
