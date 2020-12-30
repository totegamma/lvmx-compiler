#include <lvmx.h>

int main() {

	int testA[2] = "A";
	int testB[2] = {'B', 0};

	debuglog(testA);
	debuglog(testB);

	return 0;
}
