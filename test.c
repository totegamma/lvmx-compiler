#include <lvmx.h>

struct test_t {
	int first;
	int second;
};

int main() {

	struct test_t test;
	test.first = 'a';
	test.second = 0;

	int a[2];
	a[0] = test.first;
	a[1] = test.second;

	debuglog(a);

	return 0;
}
