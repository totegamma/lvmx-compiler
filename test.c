int hoge = 10;
int piyo = 20;

int main() {
	int* i = 1000;
	*i = 10;

	int* a = i + 1;
	int** b = &a;
	**b = 20;

	int c = *i;
	
	return;
}
