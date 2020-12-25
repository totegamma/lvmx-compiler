
int main() {
	int* i = 1000;
	*i = 10;

	int* a = 1001;
	int** b = &a;
	**b = 20;
	
	return;
}
