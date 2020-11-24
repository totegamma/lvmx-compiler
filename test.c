
int draw8men(float size, float offsetx, float offsety, float offsetz) {

	writereg(1, offsetx);
	writereg(2, offsety);
	writereg(3, offsetz);
	writereg(7, 1);

	writereg(2, offsety + size);
	writereg(7, 1);

	writereg(16, 1);

	writereg(1, offsetx + size);
	writereg(2, offsety);
	writereg(7, 1);

	writereg(1, offsetx);
	writereg(2, offsety - size);
	writereg(7, 1);

	writereg(1, offsetx - size);
	writereg(2, offsety);
	writereg(7, 1);

	writereg(1, offsetx);
	writereg(2, offsety + size);
	writereg(7, 1);

	writereg(2, offsety);
	writereg(3, offsetz + size);
	writereg(7, 1);

	writereg(2, offsety - size);
	writereg(3, offsetz);
	writereg(7, 1);

	writereg(2, offsety);
	writereg(3, offsetz - size);
	writereg(7, 1);

	writereg(2, offsety + size);
	writereg(3, offsetz);
	writereg(7, 1);

	writereg(16, 0);

	writereg(1, offsetx);
	writereg(2, offsety);
	writereg(3, offsetz-size);
	writereg(7, 1);

	writereg(16, 1);

	writereg(1, offsetx+size);
	writereg(2, offsety);
	writereg(3, offsetz);
	writereg(7, 1);

	writereg(1, offsetx);
	writereg(2, offsety);
	writereg(3, offsetz+size);
	writereg(7, 1);

	writereg(1, offsetx-size);
	writereg(2, offsety);
	writereg(3, offsetz);
	writereg(7, 1);

	writereg(1, offsetx);
	writereg(2, offsety);
	writereg(3, offsetz-size);
	writereg(7, 1);

	writereg(16, 0);

	writereg(1, offsetx);
	writereg(2, offsety);
	writereg(3, offsetz);
	writereg(7, 1);

}

int drawCircle(float segment, float size) {

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

int drawCircleWith8men(float segment, float size, float offset) {

	float inc = 6.28/segment;

	writereg(1, cos(0) * size);
	writereg(3, sin(0) * size);
	writereg(7, 1);

	writereg(16, 1);

	float i;
	float ev;
	ev = offset;
	for (i = 1f; i <= segment; i = i + 1f) {
		writereg(1, cos(inc * i) * size);
		writereg(3, sin(inc * i) * size);
		writereg(7, 1);

		if (ev >= 4.0f) {
			//red
			writereg(16, 0);
			writereg(17, 1.81f);
			writereg(18, 0.21f);
			writereg(19, 0f);
			writereg(20, 1f);
			draw8men(0.05f, readreg(1), readreg(2), readreg(3));
			writereg(17, 0.08f);
			writereg(18, 1.6f);
			writereg(19, 0.04f);
			writereg(20, 1f);
			writereg(16, 1);
			ev = 0;
		} else {
			ev = ev + 1f;
		}

	}

	writereg(16, 0);

	return;
}


int main() {

	//brown
	writereg(17, 0.74f);
	writereg(18, 0.29f);
	writereg(19, 0f);
	writereg(20, 1f);

	float j;
	for (j = 0f; j <= 5.0; j = j + 1f) {
		writereg(2, 0.1 * j);
		drawCircle(8.0f, 0.4);
	}

	//green
	writereg(17, 0.08f);
	writereg(18, 1.6f);
	writereg(19, 0.04f);
	writereg(20, 1f);

	float base = 1f;
	float height = 2f;

	float coneseg = 6f;
	float circleseg = 16f;

	float heightinc = height/coneseg;
	float circledec = base/coneseg;

	for (j = 0f; j < coneseg; j = j + 1f) {
		writereg(2, 0.5 + heightinc * j);
		drawCircleWith8men(circleseg, base - circledec * j, j);
	}

	//yellow
	writereg(17, 3.88f);
	writereg(18, 4.02f);
	writereg(19, 0.3f);
	writereg(20, 1f);

	draw8men(0.3f, 0.0f, 2.6f, 0.0f);

	return;
}

