#include <lvmx.h>

int main() {

	uint id = __raw(uint, "CSFT", 0, "uix_text");
	__raw(void, "SSPA", 0, id, 0);
	__raw(void, "WRIDS", 0, id, "text", "Hello, World!");

	return 0;
}
