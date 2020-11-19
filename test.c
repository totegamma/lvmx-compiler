int i;

int calcsum(int arg, int bias) {
	int buf = 0;
	for (i = 0; i < arg; ++i) {
		buf = buf + i + 1;
	}
	return buf;
}

// this is comment

int main() {
	int in = input("input");

	int result = calcsum(in);

	output("output", result);

	if (result == 55) {
		output("iftest", 100);
	} else {
		output("iftest", 200);
	}

	if (result == 55) {
		output("test2", 100);
	}

	i = 10;
	float j = 0;
	while (i > 0) {
		j = j + 10;
		--i;
	}

	output("whiletest", j);
	return;
}

