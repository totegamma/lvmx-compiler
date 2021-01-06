import struct
import glob as g
import node
from enum import IntEnum, auto
from mnemonic import mnemonic as opc


BASETYPE = ['void', 'int', 'float', 'struct', 'enum']

class SymbolNotFoundException (Exception):
    pass

class FuncDecl:
    def __init__(self, name):
        self.name = name
        self.args = []
        self.typ = None

    def setArgs(self, args):
        self.args = args
        return self

    def setType(self, typ):
        self.typ = typ
        return self

class Type:
    def __init__(self, basetype = 'void'):
        self.basetype = basetype
        self.refcount = 0
        self.length = 1 if basetype in ['int', 'float'] else 0
        self.size = 1 if basetype in ['int', 'float'] else 0
        self.quals = []
        self.members = []
        self.name = None
        self.hint = None

    def __str__(self):
        buff = self.basetype.name
        buff += ' '
        buff += '*' * self.refcount
        if (self.isArray()):
            buff += '['
            buff += str(self.size)
            buff += ']'

        return buff

    def addRefcount(self, plus):
        self.refcount += plus
        return self

    def addQuals(self, quals):
        for elem in quals:
            if elem not in self.quals:
                self.quals.append(elem)
        return self

    def setHint(self, hint):
        self.hint = hint
        return self

    def setLength(self, length):
        self.length = length
        self.size = length #TODO
        return self

    def setName(self, name):
        self.name = name
        return self

    def addMember(self, member):
        self.members.append(member)
        self.size += member.typ.size

    def isResolved(self):
        return (self.basetype in BASETYPE) and isinstance(self.refcount, int) and isinstance(self.length, int)

    def resolve(self, env, length=None):

        if length is not None:
            self.length = length
            self.size = length #XXX

        if self.isResolved():
            return

        if self.hint == 'struct':
            typ = env.getStruct(self.basetype)
            self.basetype = typ.basetype
            self.size = typ.size
            self.members = typ.members
            return

        elif self.hint == 'enum':
            self.baestype = 'int'
            self.size = 1
            self.length = 1
            return

        if not (self.basetype in BASETYPE):
            typ = env.getTypeInfo(self.basetype)
            self.basetype = typ.basetype
            self.size = typ.size
            self.members = typ.members

        elif not isinstance(self.refcount, int):
            self.refcount = self.refcount.eval()

        elif not isinstance(self.length, int):
            self.length = self.length.eval()
            self.size = self.length #XXX
            #env.getTypeInfo(self.basetype)

    def isArray(self):
        return self.length != 1

    def isBaseType(self):
        return isinstance(self.basetype, BT)

    def isIndirect(self):
        return self.refcount != 0

    def isVoid(self):
        return self.basetype == 'void'

    def isAny(self):
        return self.basetype == 'any'

    def isInt(self):
        return self.basetype == 'int'

    def isFloat(self):
        return self.basetype == 'float'

    def isScalar(self):
        return (self.basetype == 'int' or self.basetype == 'float') and self.length == 1

    def isArray(self):
        return self.length > 1

    def isStruct(self):
        return self.basetype == 'struct' or self.hint == 'struct'

# isStruct
# isEnum
# isArray


    def getField(self, env, name):
        offset = 0
        for elem in self.members:
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
    def __init__(self, typ = Type(), bytecodes = []):
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
        if (self.typ.isArray() or self.typ.isStruct()):
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

class scopedEnv:
    def __init__(self):
        self.variables = []
        self.structs = {}
        self.enums = []
        self.enumMembers = {}
        self.types = {}

class Env:
    def __init__(self):
        self.functions = []
        self.labelitr = 0

        self.statics = []
        self.strings = {} # string重複時にIDを読み出すためだけに使う
        self.staticItr = 0
        self.scopeStack = [scopedEnv()]

        self.args = []
        self.argItr = 0
        self.localItr = 0

        self.currentFuncName = '__DEFAULT'


    def functionLookup(self, name):
        for elem in self.functions:
            if (elem.symbolname == name):
                return elem
        raise SymbolNotFoundException(f"function '{name=}'")

    def variableLookup(self, name):
        for scope in reversed(self.scopeStack):
            for elem in scope.variables:
                if (elem.name == name):
                    return elem

        for elem in self.args:
            if (elem.name == name):
                return elem

        for elem in self.statics:
            if (elem.name == name):
                return elem
        raise SymbolNotFoundException(f"variable '{name=}'")

    def enumLookup(self, name):
        for scope in reversed(self.scopeStack):
            if name in scope.enumMembers:
                return scope.enumMembers[name]
        raise SymbolNotFoundException(f"variable '{name=}'")


    def issueString(self, string):
        if (string not in self.strings):
            self.strings[string] = self.staticItr
            self.statics.append(string)
            self.staticItr += len(string) + 1

        return self.strings[string]

    def addFunction(self, function):
        self.functions.append(function)

    def addStatic(self, symbol):
        symbol.setRegion(VarRegion.GLOBAL)
        symbol.setID(self.staticItr)
        self.staticItr += symbol.typ.size
        self.statics.append(symbol)

    def addArg(self, symbol):
        symbol.setRegion(VarRegion.ARGUMENT)
        symbol.setID(self.argItr)
        self.argItr += symbol.typ.size
        self.args.append(symbol)

    def addLocal(self, symbol):
        symbol.setRegion(VarRegion.LOCAL)
        symbol.setID(self.localItr)
        self.localItr += symbol.typ.size
        self.scopeStack[-1].variables.append(symbol)
        return symbol

    def pushScope(self):
        self.scopeStack.append(scopedEnv())

    def popScope(self):
        self.scopeStack.pop()

    def resetFrame(self, funcname):
        self.localItr = 0
        self.argItr = 0
        self.args.clear()
        currentFuncName = funcname

    def issueLabel(self):
        newlabel = self.labelitr
        self.labelitr += 1
        return newlabel

    def addType(self, name, typ): # TODO Type Name X is already exists!
        self.scopeStack[-1].types[name] = typ

    def addStruct(self, name, typ):
        self.scopeStack[-1].structs[name] = typ

    def addEnum(self, name):
        self.scopeStack[-1].enums.append(name)

    def addEnumMember(self, name, value):
        self.scopeStack[-1].enumMembers[name] = value

    def getTypeInfo(self, name):
        for scope in reversed(self.scopeStack):
            if name in scope.types:
                return scope.types[name]

    def getStruct(self, name):
        for scope in reversed(self.scopeStack):
            if name in scope.structs:
                return scope.structs[name]

    def getFrameSize(self):
        return self.localItr

class TokenInfo:
    def __init__(self, lineno, colno, filename = "input.c"):
        self.lineno = lineno
        self.colno = colno
        self.filename = filename

    def __str__(self):
        return f"{self.filename}:{self.lineno}:{self.colno}"

class ErrorModule:
    def __init__(self):
        self.reports = []
        self.fail = 0
        self.notice = 0

    def addReport(self, report):
        if (report.level == 'fatal' or report.level == 'error'):
            self.fail += 1
        self.notice += 1
        self.reports.append(report)

    def hasError(self):
        return self.fail != 0

    def hasNotice(self):
        return self.notice != 0

    def report(self):
        fatal = 0
        error = 0
        warning = 0

        for elem in self.reports:
            level = elem.level

            if (level == 'fatal'):
                level = '\033[35mfatal\033[0m'
                fatal += 1

            if (level == 'error'):
                level = '\033[31merror\033[0m'
                error += 1

            if (level == 'warning'):
                level = '\033[33mwarning\033[0m'
                warning += 1

            print(f"\033[1m{elem.tok}: {level}\033[1m: {elem.message}\033[0m")

            rawline = g.source.split("\n")[elem.tok.lineno - 1]
            line = rawline.lstrip()

            deleted = len(rawline) - len(line)

            print('\t' + line)
            print('\t' + ' ' * (elem.tok.colno - deleted - 1) + '\033[32m^\033[0m')

        if (fatal == 0 and error == 0 and warning == 0):
            return

        msg = ""
        if (warning != 0):
            msg += f"{warning} warning" + ("s" if warning != 1 else "")
        if (error != 0):
            msg += (" and" if len(msg) != 0 else "") + f" {error} error" + ("s" if error != 1 else "")
        if (fatal != 0):
            msg += (" and" if len(msg) != 0 else "") + f" {fatal} fatal error" + ("s" if fatal != 1 else "")
        msg += " generated."
        print(msg)


class Report:
    def __init__(self, level, tok, message):
        self.level = level
        self.tok = tok
        self.message = message
