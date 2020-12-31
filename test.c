#include <lvmx.h>
int i;

int strcmp(int* a, int* b) {
	int itr = 0;
	while (a[i] != 0) {

		++itr;
	}

}

int main() {
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
	return 0;
}
