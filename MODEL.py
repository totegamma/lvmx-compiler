import struct
from enum import IntEnum, auto
from mnemonic import mnemonic as opc

class Types (IntEnum):
    Void = auto()
    Any = auto()
    Uint  = auto()
    Int = auto()
    Float = auto()

class VarRegion (IntEnum):
    GLOBAL = auto()
    ARGUMENT = auto()
    LOCAL = auto()


class Function:
    def __init__(self, symbolname, typename, args, insts):
        self.symbolname = symbolname
        self.typename = typename
        self.args = args
        self.insts = insts

class GlobalVar:
    def __init__(self, symbolname, typename, insts):
        self.symbolname = symbolname
        self.typename = typename
        self.insts = insts

class Inst:
    def __init__(self, opc, arg):
        self.opc = opc
        self.arg = arg

    def serialize(self):
        if isinstance(self.arg, int):
            if self.arg > 2147483647: # uint
                arg = format(self.arg, "08x")
            else:
                arg = format(struct.unpack('>I', struct.pack('>i', self.arg))[0], "08x")

        elif isinstance(self.arg, float):
            arg = format(struct.unpack('>I', struct.pack('>f', self.arg))[0], "08x")

        else:
            print(f"serialize arg unkown type error: {self.arg=}")
            return "0000000000000000"

        return f'{self.opc.value:08x}{arg}'

    def debugserial(self):
        return f'{self.opc.name} {self.arg}'

class Insts:
    def __init__(self, typename, bytecodes):
        self.typename = typename
        self.bytecodes = bytecodes

class Symbol:
    def __init__(self, name, typename, initvalue = 0):
        self.name = name
        self.typename = typename
        self.initvalue = initvalue

    def setID(self, newid):
        self.id = newid

    def setRegion(self, region):
        self.region = region

    def genStoreCode(self):
        if (self.region == VarRegion.GLOBAL):
            return Inst(opc.STOREG, self.id)
        elif (self.region == VarRegion.ARGUMENT):
            return Inst(opc.STOREA, self.id)
        elif (self.region == VarRegion.LOCAL):
            return Inst(opc.STOREL, self.id)
        else:
            print("PROGRAM ERROR GENSTORECODE")

    def genLoadCode(self):
        if (self.region == VarRegion.GLOBAL):
            return Inst(opc.LOADG, self.id)
        elif (self.region == VarRegion.ARGUMENT):
            return Inst(opc.LOADA, self.id)
        elif (self.region == VarRegion.LOCAL):
            return Inst(opc.LOADL, self.id)
        else:
            print("PROGRAM ERROR GENLOADCODE")

class Env:
    def __init__(self):
        self.functions = []
        self.strings = {}
        self.globals = []
        self.args = []
        self.locals = []
        self.localcount = 0
        self.labelitr = 0

    def functionLookup(self, name):
        for elem in self.functions:
            if (elem.symbolname == name):
                return elem
        print("ERROR: FUNCTION NOT FOUND")

    def variableLookup(self, name):
        for scope in reversed(self.locals):
            for elem in scope:
                if (elem.name == name):
                    return elem

        for elem in self.args:
            if (elem.name == name):
                return elem

        for elem in self.globals:
            if (elem.name == name):
                return elem
        print(f"{name=}")
        print("ERROR: VAR NOT FOUND")

    def stringLookup(self, string):
        return self.strings[string]

    def issueString(self, string):
        if (string not in self.strings):
            self.strings[string] = len(self.strings)
        return self.strings[string]

    def addFunction(self, function):
        self.functions.append(function)

    def addGlobal(self, symbol):
        symbol.setRegion(VarRegion.GLOBAL)
        symbol.setID(len(self.globals))
        self.globals.append(symbol)

    def addArg(self, symbol):
        symbol.setRegion(VarRegion.ARGUMENT)
        symbol.setID(len(self.args))
        self.args.append(symbol)

    def addLocal(self, symbol):
        symbol.setRegion(VarRegion.LOCAL)
        newid = self.localcount
        symbol.setID(newid)
        self.localcount += 1
        self.locals[-1].append(symbol)
        return newid

    def pushLocal(self):
        self.locals.append([])

    def popLocal(self):
        self.locals.pop()

    def resetFrame(self):
        self.localcount = 0
        self.args.clear()
        self.locals.clear()

    def getGlobalCount(self):
        return len(self.globals)

    def getArgCount(self):
        return len(self.args)

    def getLocalCount(self):
        return self.localcount

    def issueLabel(self):
        newlabel = self.labelitr
        self.labelitr += 1
        return newlabel

