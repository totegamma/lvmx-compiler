
#ifndef UIX_H
#define UIX_H

#include <lvmx.h>

/* template
int (int parent) {
	int slot = createSlotFromTemplate("");
	setSlotParent(slot, parent);
	return slot;
}
*/

#define UIX_LAYOUT_HORIZONTAL_LEFT 0
#define UIX_LAYOUT_HORIZONTAL_CENTER 1
#define UIX_LAYOUT_HORIZONTAL_RIGHT 2

#define UIX_LAYOUT_VERTICAL_LEFT 0
#define UIX_LAYOUT_VERTICAL_CENTER 1
#define UIX_LAYOUT_VERTICAL_RIGHT 2

#define UIX_LAYOUT_FORCE_EXPAND 0
#define UIX_LAYOUT_NO_EXPAND 1

#define UIX_TEXT_ALIGN_LEFT 0
#define UIX_TEXT_ALIGN_CENTER 1
#define UIX_TEXT_ALIGN_RIGHT 2


int uixAnchorRect(int parent, float minX, float minY, float maxX, float maxY) {
	int slot = createSlotFromTemplate("UIXempty");
	setDVFloat(slot, "Amx", minX);
	setDVFloat(slot, "Amy", minY);
	setDVFloat(slot, "AMx", maxX);
	setDVFloat(slot, "AMy", maxY);
	setSlotParent(slot, parent);
	return slot;
}

int uixOffsetRect(int parent, float minX, float minY, float maxX, float maxY) {
	int slot = createSlotFromTemplate("UIXempty");
	setDVFloat(slot, "Omx", minX);
	setDVFloat(slot, "Omy", minY);
	setDVFloat(slot, "OMx", maxX);
	setDVFloat(slot, "OMy", maxY);
	setSlotParent(slot, parent);
	return slot;
}

int uixImage(int parent, float R, float G, float B) {
	int slot = createSlotFromTemplate("UIXimage");
	setDVFloat(slot, "R", R);
	setDVFloat(slot, "G", G);
	setDVFloat(slot, "B", B);
	setSlotParent(slot, parent);
	return slot;
}

int uixRawImage(int parent, int* url) {
	int slot = createSlotFromTemplate("UIXrawImage");
	setDVString(slot, "URL", url);
	setSlotParent(slot, parent);
	return slot;

}

int uixText(int parent, int* string, float size, float R, float G, float B, int alignH, int alignV) {
	int slot = createSlotFromTemplate("UIXtext");
	setDVString(slot, "content", string);
	setDVFloat(slot, "size", size);
	setDVFloat(slot, "R", R);
	setDVFloat(slot, "G", G);
	setDVFloat(slot, "B", B);
	setDVInt(slot, "alignH", alignH);
	setDVInt(slot, "alignV", alignV);
	setSlotParent(slot, parent);
	return slot;
}

int uixButton(int parent) {
	int slot = createSlotFromTemplate("UIXbutton");
	setSlotParent(slot, parent);
	return slot;
}

int uixTextField(int parent) {
	int slot = createSlotFromTemplate("UIXtextField");
	setSlotParent(slot, parent);
	return slot;
}

int uixHorizontalLayout(int parent, int expand) {
	int slot = createSlotFromTemplate("UIXlayoutH");
	setDVInt(slot, "expandW", expand);
	setSlotParent(slot, parent);
	return slot;
}

int uixVerticalLayout(int parent, int expand) {
	int slot = createSlotFromTemplate("UIXlayoutV");
	setDVInt(slot, "expandH", expand);
	setSlotParent(slot, parent);
	return slot;
}

int uixHorizontalLayoutElem(int parent, float size) {
	int slot = createSlotFromTemplate("UIXlayoutElem");
	setDVFloat(slot, "minW", size);
	setSlotParent(slot, parent);
	return slot;
}

int uixVerticalLayoutElem(int parent, float size) {
	int slot = createSlotFromTemplate("");
	setDVFloat(slot, "minH", size);
	setSlotParent(slot, parent);
	return slot;
}

int uixHorizontalScroll(int parent, float R, float G, float B) {
	int mask = createSlotFromTemplate("UIXmask");
	setDVFloat(slot, "R", R);
	setDVFloat(slot, "G", G);
	setDVFloat(slot, "B", B);
	setSlotParent(mask, parent);
	int scroll = createSlotFromTemplate("UIXscrollH");
	setSlotParent(scroll, mask);
	return scroll;
}

int uixVirticalScroll(int parent, float R, float G, float B) {
	int mask = createSlotFromTemplate("UIXmask");
	setDVFloat(slot, "R", R);
	setDVFloat(slot, "G", G);
	setDVFloat(slot, "B", B);
	setSlotParent(mask, parent);
	int scroll = createSlotFromTemplate("UIXscrollV");
	setSlotParent(scroll, mask);
	return scroll;
}

#endif

