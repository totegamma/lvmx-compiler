#include <lvmx.h>
int i;

struct testStruct {
	int fieldA;
	int fieldB;
};

int testGlobalA;
int testGlobalB = 3;
int testGlobalC[2];
int testGlobalD[2] = "a";
int testGlobalE[2] = {'a', 0};
int testGlobalF[] = "test";

int strncmp(int* a, int* b, int n) {
	for (i = 0; i < n; ++i) {
		if (*a == *b) return 1;
		++a;
		++b;
	}

	return 0;
}

int print1num(int a) {
	int buf[3];
	buf[0] = a + '0';
	buf[1] = '\n';
	buf[2] = 0;
	debuglog(buf);
}

struct testStruct globalStruct;

int main() {

	int judge;

	int testLocalA;
	int testLocalB = 3;
	int testLocalC[2];
	int testLocalD[2] = "a";
	int testLocalE[2] = {'a', 0};
	int testLocalF[] = "test";

	int testLocalZ[] = "hoge";

	judge = strncmp(testGlobalD, testLocalD, 2);
	print1num(judge);
	judge = strncmp(testGlobalE, testLocalE, 2);
	print1num(judge);
	judge = strncmp(testGlobalF, testLocalF, 5);
	print1num(judge);

	struct testStruct localStruct;

	globalStruct.fieldA = 'a';
	globalStruct.fieldB = 0;
	localStruct.fieldA = 'a';
	localStruct.fieldB = 0;

	judge = strncmp(globalStruct, localStruct, 2);
	print1num(judge);

	judge = strncmp(globalStruct, testLocalE, 2);
	print1num(judge);

	judge = strncmp(localStruct, testGlobalE, 2);
	print1num(judge);

	judge = strncmp(testLocalZ, testGlobalF, 5);
	print1num(judge);

	int a = 5;
	int b = 5;
	print1num(++a);
	print1num(b++);

	print1num(a);
	print1num(b);

	return 0;
}
