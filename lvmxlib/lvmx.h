#ifndef LVMX_H
#define LVMX_H

#define WORLDROOT_SLOT 0
#define UIXROOT_SLOT 1

#define debuglog(message) __raw(void, "PRINT", 0, message)
#define createSlotFromTemplate(templateName) __raw(int, "CSFT", 0, templateName)
#define setSlotParent(targetSlotID, newParentSlotID) __raw(void, "SSPA", 0, targetSlotID, newParentSlotID)
#define setDVs(destSlotID, key, value) __raw(void, "WRIDS", 0, destSlotID, key, value)

#endif
