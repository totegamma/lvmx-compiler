int i = 3;

int square(int size) {
	writereg(1, 0);
	writereg(16, 1);
	writereg(1, size);
	writereg(3, size);
	writereg(1, 0);
	writereg(3, 0);
	writereg(16, 0);
	return;
}

int main() {

	int in = input("input");

	square(in);

	return;
}

