import struct
import glob
import node
from enum import IntEnum, auto
from mnemonic import mnemonic as opc

class BT (IntEnum):
    Void = auto()
    Any = auto()
    Uint  = auto()
    Int = auto()
    Float = auto()

class Types:
    def __init__(self, basetype, refcount = 0, size = 1, fields = []):
        self.basetype = basetype
        self.refcount = refcount
        self.size = size
        self.fields = fields

    def __str__(self):
        return '*' * self.refcount + self.basetype.name

    def convertToArray(self, size):
        self.size = size
        return self

    def isBaseType(self):
        return isinstance(self.basetype, BT)

    def isIndirect(self):
        return self.refcount != 0

    def isArray(self):
        return self.size != 1

    def isVoid(self):
        return self.basetype == BT.Void

    def isAny(self):
        return self.basetype == BT.Any

    def isUint(self):
        return self.basetype == BT.Uint

    def isInt(self):
        return self.basetype == BT.Int

    def isFloat(self):
        return self.basetype == BT.Float

    def addRefcount(self, delta):
        self.refcount += delta

    def resolve(self, env):
        if isinstance(self.basetype, BT):
            if isinstance(self.size, node.AST):
                self.size = self.size.eval()
        else:
            typ = env.resolveType(self.basetype)
            self.basetype = typ.basetype
            self.size = typ.size
            self.fields = typ.fields


    def getField(self, env, name):
        offset = 0
        for elem in self.fields:
            elem.typ.resolve(env)
            if (elem.name == name):
                return StructField(elem.typ, offset)
            offset += elem.typ.size

        return None

class StructField:
    def __init__ (self, typ, offset):
        self.typ = typ
        self.offset = offset

class VarRegion (IntEnum):
    GLOBAL = auto()
    ARGUMENT = auto()
    LOCAL = auto()

class Function:
    def __init__(self, symbolname, typ, args, insts):
        self.symbolname = symbolname
        self.typ = typ
        self.args = args
        self.insts = insts

class GlobalVar:
    def __init__(self, symbolname, typ, insts):
        self.symbolname = symbolname
        self.typ = typ
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
    def __init__(self, typ, bytecodes):
        self.typ = typ
        self.bytecodes = bytecodes

class Symbol:
    def __init__(self, name, typ, initvalue = 0):
        self.name = name
        self.typ = typ
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
        if (self.typ.isArray()):
            return self.genAddrCode()

        if (self.region == VarRegion.GLOBAL):
            return Inst(opc.LOADG, self.id)
        elif (self.region == VarRegion.ARGUMENT):
            return Inst(opc.LOADA, self.id)
        elif (self.region == VarRegion.LOCAL):
            return Inst(opc.LOADL, self.id)
        else:
            print("PROGRAM ERROR GENLOADCODE")

    def genAddrCode(self):
        if (self.region == VarRegion.GLOBAL):
            return Inst(opc.PUSH, self.id)
        elif (self.region == VarRegion.ARGUMENT):
            return Inst(opc.PUAP, self.id)
        elif (self.region == VarRegion.LOCAL):
            return Inst(opc.PULP, self.id)
        else:
            print("PROGRAM ERROR GENLOADCODE")

class Env:
    def __init__(self):
        self.functions = []
        self.strings = {}
        self.globals = []
        self.globalcount = 0
        self.args = []
        self.locals = []
        self.localcount = 0
        self.labelitr = 0
        self.types = {}

    def functionLookup(self, name):
        for elem in self.functions:
            if (elem.symbolname == name):
                return elem
        glob.compileerrors += f"コンパイルエラー: 関数{name=}が見つかりません"

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
        glob.compileerrors += f"コンパイルエラー: 変数{name=}が見つかりません"

    def stringLookup(self, string):
        return self.strings[string]

    def issueString(self, string):
        if (string not in self.strings):
            self.strings[string] = self.globalcount
            self.globals.append(string)
            self.globalcount += len(string) + 1

        return self.strings[string]

    def addFunction(self, function):
        self.functions.append(function)

    def addGlobal(self, symbol):
        symbol.setRegion(VarRegion.GLOBAL)
        symbol.setID(self.globalcount)
        self.globalcount += symbol.typ.size
        self.globals.append(symbol)

    def addArg(self, symbol):
        symbol.setRegion(VarRegion.ARGUMENT)
        symbol.setID(len(self.args))
        self.args.append(symbol)

    def addLocal(self, symbol):
        symbol.setRegion(VarRegion.LOCAL)
        newid = self.localcount
        symbol.setID(newid)
        self.localcount += symbol.typ.size
        self.locals[-1].append(symbol)
        return symbol

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

    def addType(self, name, typ): # TODO Type Name X is already exists!
        self.types[name] = typ

    def resolveType(self, name):
        return self.types[name]

class TokenInfo:
    def __init__(self, lineno, colno, filename = "unnamed.c"):
        self.lineno = lineno
        self.colno = colno
        self.filename = filename

    def __str__(self):
        return f"{self.filename}:{self.lineno}:{self.colno}"

