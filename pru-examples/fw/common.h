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
