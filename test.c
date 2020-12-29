#include <lvmx.h>

int main() {

	int id = createSlotFromTemplate("uix_text");
	if (id < 0) {
		debuglog("failed to create slot\n");
	}

	setSlotParent(id, UIXROOT_SLOT);
	setDVs(id, "text", "ユー・アイ・エックス！");

	return 0;
}
