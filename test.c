#include <lvmx.h>

int main() {

	int testA[2];
	testA[0] = 'A';
	testA[1] = 0;
	int testB[2];
	testB[0] = 'B';
	testB[1] = 0;
	int testC[2];
	testC[0] = testB[0] + 1;
	testC[1] = testA[1];

	debuglog(testA);
	debuglog(testB);
	debuglog(testC);

	return 0;
}
