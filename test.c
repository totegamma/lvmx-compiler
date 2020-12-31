#include <lvmx.h>
int i;

int strncmp(int* a, int* b, int n) {
	for (i = 0; i < n; ++i) {
		if (*a == *b) return 1;
		a = a + 1;
		b = b + 1;
	}

	return 0;
}

int print1num(int a) {
	int buf[2];
	buf[0] = a + '0';
	buf[1] = 0;
	debuglog(buf);
}

int main() {

	int a[] = "hoge";
	int b[] = "hoge";
	int judge = strncmp(a, b, 5);
	print1num(judge);

	int c[] = "hoge";
	int d[] = "hooe";
	judge = strncmp(c, d, 5);
	print1num(judge);

	/*
	debuglog("test start\n");
	
	if (0) {
		debuglog("ng\n");
	}

	if (1) {
		debuglog("ok\n");
	}

	if (0) {
		debuglog("ng\n");
	} else {
		debuglog("ok\n");
	}

	if (1) {
		debuglog("ok\n");
	} else {
		debuglog("ng\n");
	}

	int localarr[5];
	for (i = 0; i < 3; ++i) {
		localarr[i] = i + 'a';
	}
	localarr[3] = '\n';
	localarr[4] = 0;
	debuglog(localarr);

	debuglog("test end\n");
	*/
	return 0;
}
