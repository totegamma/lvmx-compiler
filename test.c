#include <lvmx.h>

#define USE_PRINT1
#define USE_MEMCMP
#include <debugutil.h>

int i;

struct testStruct {
	int fieldA;
	int fieldB;
};

int testGlobalA;
int testGlobalB = 3;
int testGlobalC[2];
int testGlobalD[2] = "a";
int testGlobalE[2] = {'a', 0};
int testGlobalF[] = "test";

struct testStruct globalStruct;

int main() {

	int judge;

	int testLocalA;
	int testLocalB = 3;
	int testLocalC[2];
	int testLocalD[2] = "a";
	int testLocalE[2] = {'a', 0};
	int testLocalF[] = "test";

	int testLocalZ[] = "hoge";

	judge = memcmp(testGlobalD, testLocalD, 2);
	print1(judge + '0');
	judge = memcmp(testGlobalE, testLocalE, 2);
	print1(judge + '0');
	judge = memcmp(testGlobalF, testLocalF, 5);
	print1(judge + '0');

	struct testStruct localStruct;

	globalStruct.fieldA = 'a';
	globalStruct.fieldB = 0;

	localStruct.fieldA = 'a';
	localStruct.fieldB = 0;


	judge = memcmp(globalStruct, localStruct, 2);
	print1(judge + '0');

	judge = memcmp(globalStruct, testLocalE, 2);
	print1(judge + '0');

	judge = memcmp(localStruct, testGlobalE, 2);
	print1(judge + '0');

	judge = memcmp(testLocalZ, testGlobalF, 5);
	print1(judge + '0');

	return 0;
}
