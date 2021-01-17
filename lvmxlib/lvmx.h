#ifndef LVMX_H
#define LVMX_H

#define WORLDROOT_SLOT 0
#define DEVICEROOT_SLOT 1
#define UIXROOT_SLOT 2

#define debuglog(message) __raw(void, "PRINT", 0, message)
#define createSlotFromTemplate(templateName) __raw(int, "CSFT", 0, templateName)
#define setSlotParent(targetSlotID, newParentSlotID) __raw(void, "SSPA", 0, targetSlotID, newParentSlotID)

#define getDVInt(destSlotID, key) __raw(int, "LOADD", 0, destSlotID, key)
#define getDVFloat(destSlotID, key) __raw(float, "LOADD", 1, destSlotID, key)
#define getDVString(destSlotID, key, dest) __raw(void, "LOADD", 2, destSlotID, key, dest)

#define setDVInt(destSlotID, key, value) __raw(void, "STORED", 0, destSlotID, key, value)
#define setDVFloat(destSlotID, key, value) __raw(void, "STORED", 1, destSlotID, key, value)
#define setDVString(destSlotID, key, value) __raw(void, "STORED", 2, destSlotID, key, value)

#endif
