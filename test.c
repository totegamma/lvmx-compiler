
int main() {

	int i;
	int* p = 1000;
	for (i = 0; i < 10; ++i) {
		p[i] = i;
	}

	return p[5];
}
