far int foo = 41;

int main() {
	foo++;
	asm("\thalt");
}
