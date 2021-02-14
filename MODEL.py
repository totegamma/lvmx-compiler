import node
import struct
import glob as g
import linecache
from copy import copy
from functools import reduce
from enum import IntEnum, auto
from mnemonic import mnemonic as opc


BASETYPE = ['void', 'int', 'float', 'struct', 'enum']

class SymbolNotFoundException (Exception):
    pass

class SymbolRedefineException (Exception):
    pass

class TypeRedefineException (Exception):
    pass

class SymbolLengthNotSpecifiedException (Exception):
    pass

class NonPointerException (Exception):
    pass

class ConflictingTypesException(Exception):
    pass


class Type:
    def __init__(self, basetype = 'void'):
        self.basetype = basetype
        self.refcount = 0
        self.length = 1
        self.quals = []
        self.members = []
        self.name = None
        self.hint = None

    def __str__(self):
        buff = self.basetype
        if self.refcount > 0 or self.length > 1:
            buff += ' '
        buff += '*' * self.refcount
        if (self.length > 1):
            buff += f'[{self.length}]'
        return buff

    def __eq__(self, other):
        if not isinstance(other, Type):
            return NotImplemented
        return self.basetype == other.basetype \
           and self.refcount == other.refcount \
           and self.length == other.length \
           and self.quals == other.quals \
           and self.members == other.members \
           and self.hint == other.hint

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
        return self

    def setName(self, name):
        self.name = name
        return self

    def addMember(self, member):
        self.members.append(member)
        return self

    def isBasetype(self):
        return self.basetype in BASETYPE

    def isScalar(self):
        return self.basetype in ('int', 'float', 'enum') and self.refcount == 0 and self.length == 1

    def isPointer(self):
        return self.refcount > 0 and self.length == 1

    def isArray(self):
        return self.length > 1

    def isStruct(self):
        return self.basetype == 'struct'

    def isEnum(self):
        return self.basetype == 'enum'


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
            arg = format(struct.unpack('>I', struct.pack('>i', self.arg))[0], "d")

        elif isinstance(self.arg, float):
            arg = format(struct.unpack('>I', struct.pack('>f', self.arg))[0], "d")

        else:
            print(f"serialize arg unkown type error: {self.arg=}")
            return "0"

        if arg == '0':
            return f'{self.opc.value}'
        else:
            return f'{self.opc.value}.{arg}'

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

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.name == other.name and self.typ == other.typ

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
        self.enums = {}
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

        self.calledFunc = []

    def markCalledFunc(self, funcname):
        if not funcname in self.calledFunc:
            self.calledFunc.append(funcname)

    def functionLookup(self, name):
        for elem in self.functions:
            if (elem.symbolname == name):
                return elem
        raise SymbolNotFoundException(f"function '{name}'")

    def variableLookup(self, name):
        for scope in reversed(self.scopeStack):
            for elem in scope.variables:
                if (elem.name == name):
                    return elem

        for elem in self.args:
            if (elem.name == name):
                return elem

        for elem in self.statics:
            if (type(elem) is Symbol and elem.name == name):
                return elem

        raise SymbolNotFoundException(f"variable '{name}'")

    def enumLookup(self, name):
        for scope in reversed(self.scopeStack):
            if name in scope.enumMembers:
                return scope.enumMembers[name]
        raise SymbolNotFoundException(f"variable '{name}'")


    def issueString(self, string):
        if (string not in self.strings):
            self.strings[string] = self.staticItr
            self.statics.append(string)
            self.staticItr += len(string) + 1

        return self.strings[string]

    def addFunction(self, function):
        for elem in self.functions:
            if elem.symbolname == function.symbolname:
                if elem.insts is None and function.insts is not None:
                    if elem.typ == function.typ and elem.args == function.args:
                        elem.insts = function.insts
                    else:
                        raise ConflictingTypesException()
                else:
                    raise SymbolRedefineException()
                return
        self.functions.append(function)

    def addStatic(self, symbol):
        symbol.setRegion(VarRegion.GLOBAL)
        symbol.setID(self.staticItr)
        self.staticItr += self.calcTypeSize(symbol.typ)
        self.statics.append(symbol)

    def addArg(self, symbol):
        symbol.setRegion(VarRegion.ARGUMENT)
        symbol.setID(self.argItr)
        self.argItr += self.calcTypeSize(symbol.typ)
        self.args.append(symbol)

    def addLocal(self, symbol):
        symbol.setRegion(VarRegion.LOCAL)
        symbol.setID(self.localItr)
        self.localItr += self.calcTypeSize(symbol.typ)
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

    def addType(self, name, typ):
        target = self.scopeStack[-1].types
        if name in target:
            raise TypeRedefineException(f"Redefined Type '{name}'")
        target[name] = typ

    def addStruct(self, name, typ):
        target = self.scopeStack[-1].structs
        if name in target:
            raise TypeRedefineException(f"Redefined Struct '{name}'")
        target[name] = typ

    def addEnum(self, name, typ):
        target = self.scopeStack[-1].enums
        if name in target:
            raise TypeRedefineException(f"Redefined Struct '{name}'")

        for elem in typ.members:
            self.scopeStack[-1].enumMembers[elem[0]] = elem[1]

        target[name] = typ

    def getType(self, name, hint = ""):

        if hint == 'struct':
            return self.getStruct(name)

        for scope in reversed(self.scopeStack):
            if name in scope.types:
                return scope.types[name]
        print(f"type '{name}' not found")

    def getStruct(self, name):
        for scope in reversed(self.scopeStack):
            if name in scope.structs:
                return scope.structs[name]

    def getFrameSize(self):
        return self.localItr

    def getField(self, typ, field):
        if len(typ.members) == 0:
            typ = self.getType(typ.basetype, typ.hint)

        offset = 0
        for elem in typ.members:
            if elem[0] == field:
                return (offset, elem[1])
            offset += self.calcTypeSize(elem[1])

        print('field not found exception')


    def calcTypeSize(self, typ, hint=None):

        # 前準備
        if typ.length is None:
            if isinstance(hint, list):
                length = len(hint)
                typ.length = length
            else:
                print(hint)
                raise SymbolLengthNotSpecifiedException
        else:
            length = typ.length

        if isinstance(typ.length, node.AST):
            length = typ.length.eval()
            typ.length = length

        if typ.refcount > 0:
            return length

        if typ.basetype in ('void', 'int', 'float', 'enum'):
            return length

        if len(typ.members) == 0:
            return self.calcTypeSize(self.getType(typ.basetype, typ.hint)) * length
        else:
            return reduce(lambda sigma, e: sigma + self.calcTypeSize(e[1]), typ.members, 0) * length

    def calcPointeredSize(self, typ):

        tmp = copy(typ)

        if tmp.length > 1:
            tmp.setLength(1).addRefcount(1)

        if not tmp.isPointer():
            raise NonPointerException()
            return None

        tmp.addRefcount(-1)

        return self.calcTypeSize(tmp)


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


            if elem.tok is None:
                print(f"\033[1m<position info not available>: {level}\033[1m: {elem.message}\033[0m")
            else:

                print(f"\033[1m{elem.tok}: {level}\033[1m: {elem.message}\033[0m")
                rawline = linecache.getline(elem.tok.filename, elem.tok.lineno)
                line = rawline.lstrip()
                deleted = len(rawline) - len(line)
                line = line.rstrip()

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

        return msg


class Report:
    def __init__(self, level, tok, message):
        self.level = level
        self.tok = tok
        self.message = message
