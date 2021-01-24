#ifndef DEBUGUTILS_H
#define DEBUGUTILS_H 

#include <lvmx.h>

#ifdef USE_STRCMP
int strcmp(int* p1, int* p2) {

	do {
		if (*p1 == '\0') return *p1 - *p2;
	} while (*p1++ == *p2++);

	return *p1 - *p2;
}
#endif

#ifdef USE_MEMCMP
int memcmp(int* p1, int* p2, int len) {
	int i;
	for (i = 0; i < len; ++i) {
		if (*p1++ != *p2++) return 1;
	}
	return 0;
}
#endif

#ifdef USE_PRINT1
int print1(int a) {
	int buf[3];
	buf[0] = a;
	buf[1] = '\n';
	buf[2] = 0;
	debuglog(buf);
}
#endif

#ifdef USE_WWMALLOC
// world worst memory allocation
/* static */ int ww_malloc_ptr = 100000; //memory allocation initial address
int* ww_malloc(int size) {
	ww_malloc_ptr -= size;
	return ww_malloc_ptr;
}
#endif

#ifdef USE_ITOA
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

void itoa(int input, int* dest) {
	int i = 0;
	while (input >= 1) {
		dest[i++] = (input % 10) + '0';
		input /= 10;
	}
	dest[i] = 0;

	reverse_string(dest, i);
}

#endif


#endif
