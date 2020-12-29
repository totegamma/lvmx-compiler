
int main() {

	uint* message = "日本語もOK!";

	__raw(void, "PRINT", 0, message);

	return 0;
}
