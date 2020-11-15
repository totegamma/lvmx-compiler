var i;

func calcsum(arg) {
	var buf = 0;
	for (i = 0; i <= arg; i++) {
		buf = buf + i + 1;
	}
	return buf;
}

func main() {
	var in = input("input");

	var result = calcsum(in);

	output("output", result);

	return;
}

