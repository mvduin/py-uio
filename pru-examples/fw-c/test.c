// Variables in the shared memory region (offset 0x10000 - 0x12fff in pruss) need to be
// marked as "far".  The location attribute is used to set the exact address since the
// python code (elf-test.py) needs to know where this variable is at.
//
far int volatile foo __attribute__((location(0x10000))) = 41;

int main() {
	foo++;
	__halt();
}
