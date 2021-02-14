#ifndef LVMX_H
#define LVMX_H

typedef int size_t;
#define NULL 0

#define WORLDROOT_SLOT 0
#define DEVICEROOT_SLOT 1
#define UIXROOT_SLOT 2
#define APPFOLDER_SLOT 3
#define CURRENTAPP_SLOT 4

#define debuglog(message) __raw(void, "PRINT", 0, message)
#define exit(status) __raw(void, "EXIT", 0, status)
#define createSlotFromTemplate(templateName) __raw(int, "CSFT", 0, templateName)
#define setSlotParent(targetSlotID, newParentSlotID) __raw(void, "SSPA", 0, targetSlotID, newParentSlotID)
#define getSlotParent(targetSlotID) __raw(int, "SLUS", 0, targetSlotID)
#define dupSlot(targetSlotID) __raw(int, "SLUS", 1, targetSlotID)
#define childrenCount(targetSlotID) __raw(int, "SLUS", 2, targetSlotID)
#define getSlotChild(targetSlotID, pos) __raw(int, "GSLC", 0, targetSlotID, pos)
#define destroySlot(targetSlotID) __raw(void, "DESS", 0, targetSlotID)

#define getSlotName(targetSlotID, dest) __raw(void, "GSN", 0, targetSlotID, dest)

#define readreg(addr) __raw(int, "LOADR", addr)
#define writereg(addr, value) __raw(void, "STORER", addr, value)

#define getDVInt(destSlotID, key) __raw(int, "LOADD", 0, destSlotID, key)
#define getDVFloat(destSlotID, key) __raw(float, "LOADD", 1, destSlotID, key)
#define getDVString(destSlotID, key, dest) __raw(void, "LOADD", 2, destSlotID, key, dest)

#define setDVInt(destSlotID, key, value) __raw(void, "STORED", 0, destSlotID, key, value)
#define setDVFloat(destSlotID, key, value) __raw(void, "STORED", 1, destSlotID, key, value)
#define setDVString(destSlotID, key, value) __raw(void, "STORED", 2, destSlotID, key, value)

#define strlen(str) __raw(int, "SLEN", 0, str)
#define stoi(str) __raw(int, "STOI", 0, str)
#define stof(str) __raw(float, "STOF", 0, str)

#define memcmp(strA, strB, n) __raw(int, "MCMP", 0, strA, strB, n)
#define memcpy(strA, strB, n) __raw(void, "MCPY", 0, strA, strB, n)
#define strcmp(strA, strB) __raw(int, "SCMP", 0, strA, strB)
#define strcpy(strA, strB) __raw(void, "SCPY", 0, strA, strB)
#define itos(number, dest) __raw(void, "ITOS", 0, number, dest)
#define ftos(number, dest) __raw(void, "FTOS", 0, number, dest)

#define format(dest, form, ...) __raw(void, "FRMT", 0, dest, form, __VA_ARGS__)

#define sendDI(dest, name) __raw(void, "ADIT", 0, dest, name)

#define sin(number) __raw(float, "SIN", 0, number)
#define cos(number) __raw(float, "COS", 0, number)

#endif
