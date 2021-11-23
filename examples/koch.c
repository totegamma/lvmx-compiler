#include <lvmx.h>

void koch(int n, float length) {
	if (n <= 0) {
		writereg(8, length); // forward
		return;
	}
	koch(n-1, length/3.0f);
	writereg(10, 60.0f); // rotate Y
	koch(n-1, length/3.0f);
	writereg(10, -120.0f); // rotate Y
	koch(n-1, length/3.0f);
	writereg(10, 60.0f); // rotate Y
	koch(n-1, length/3.0f);

}

void main() {

	writereg(17, 1.0f);
	writereg(18, 1.0f);
	writereg(19, 0.0f);
	writereg(20, 1.00f);

	int n = 4;
	float length = 3.0f;
	writereg(16, 1); // pen down
	koch(n, length);
	writereg(16, 0); // pen up
}
