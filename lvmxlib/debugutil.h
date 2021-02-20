#ifndef DEBUGUTILS_H
#define DEBUGUTILS_H

#include <lvmx.h>

int print1(int a) {
	int buf[3];
	buf[0] = a;
	buf[1] = '\n';
	buf[2] = 0;
	debuglog(buf);
}

// world worst memory allocation
/* static */ int ww_malloc_ptr = 100000; //memory allocation initial address
int* ww_malloc(int size) {
	ww_malloc_ptr -= size;
	return ww_malloc_ptr;
}

void reverse_string(int* start, int len) {

	int* end = start + len - 1;

	while (start < end) {
		int tmp = *start;
		*start = *end;
		*end = tmp;
		start++;
		end--;
	}
}

#endif
