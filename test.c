
int writeCircle(float segment, float size) {

	float inc = 6.28/segment;

	writereg(1, cos(0) * size);
	writereg(3, sin(0) * size);
	writereg(7, 1);

	writereg(16, 1);

	float i;
	for (i = 1f; i <= segment; i = i + 1f) {
		writereg(1, cos(inc * i) * size);
		writereg(3, sin(inc * i) * size);
		writereg(7, 1);
	}

	writereg(16, 0);

	return;
}


int main() {

	float base = 1f;
	float height = 1f;

	float coneseg = 5f;
	float circleseg = 16f;

	float heightinc = height/coneseg;
	float circledec = base/coneseg;

	//0, 1, 1.6, 1
	writereg(17, 0f);
	writereg(18, 1f);
	writereg(19, 1.6f);
	writereg(20, 1f);

	float j;
	for (j = 0f; j <= coneseg; j = j + 1f) {
		writereg(2, heightinc * j);
		writeCircle(circleseg, base - circledec * j);
	}

	return;
}

