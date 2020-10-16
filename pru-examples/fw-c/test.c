#include <stdint.h>

// The location attribute is used to set the exact address since the
// python code (elf-test.py) needs to know where this variable is at.
//
uint32_t volatile foo __attribute__((location(0x1234))) = 41;

// Variables in the shared memory region (offset 0x10000 - 0x12fff in pruss)
// need to be marked as "far".
//
far uint32_t volatile bar __attribute__((location(0x10000))) = 1000;

int main() {
	foo++;
	bar++;
	__halt();
}
