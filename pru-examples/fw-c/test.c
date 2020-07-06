// "far" will make the linker script place it in shared memory
far int volatile foo = 41;
// alternative declaration that allows more efficient access:
//	far int volatile foo __attribute__((cregister("SHARED", near))) = 41;

int main() {
	foo++;
	__halt();
}
