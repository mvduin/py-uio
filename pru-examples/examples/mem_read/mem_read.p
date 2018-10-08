.origin 0
.entrypoint START

#define MAGIC_FOR_RAM0  0xbabe0000
#define MAGIC_FOR_RAM1  0xbabe0001
#define MAGIC_FOR_RAM2  0xbabe0002

START:	
    LBCO r0, C4, 4, 4					 
    CLR  r0, r0, 4					
    SBCO r0, C4, 4, 4					

    MOV  r0, 0x0120
    MOV  r1, 0x00022028
    SBBO r0, r1, 0, 4
    MOV  r1, 0x00024028
    SBBO r0, r1, 0, 4

    MOV r0, MAGIC_FOR_RAM0               
    SBCO r0, c24, 0, 4                      

    MOV r0, MAGIC_FOR_RAM1               
    SBCO r0, c25, 0, 4                      

    MOV r0, MAGIC_FOR_RAM2            
    SBCO r0, c28, 0, 4                    

HALT
