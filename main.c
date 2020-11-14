var i;

func calcsum(arg) {
	var buf = 0;
	for (i = 0; i < arg; i++) {
		buf = buf + i + 1;
	}
	return buf;
}

func main() {
	var in = input("input");

	var result = calcsum(in);

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
	var j = 0;
	while (i > 0) {
		j = j + 10;
		i--;
	}

	output("whiletest", j);

	return;
}

