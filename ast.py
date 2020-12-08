from enum import IntEnum, auto

# -= :: TOP MODELS :: =-

class TYPES (IntEnum):
    Void = auto()
    Any = auto()
    Uint  = auto()
    Int = auto()
    Float = auto()

class VALREGION (IntEnum):
    GLOBAL = auto()
    ARGUMENT = auto()
    LOCAL = auto()

class BYTECODE:
    def __init__(self, typename, bytecode):
        self.typename = typename
        self.bytecode = vytecode

class SYMBOL:
    def __init__(self, name, typename):
        self.name = name
        self.typename = typename

    def setID(self, newid):
        self.id = newid

    def setRegion(self, region):
        self.region = region



class ENV:
    def __init__(self):
        self.globals = []
        self.args = []
        self.locals = []
        self.localcount = 0

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

    def addGlobal(self, symbol):
        symbol.setRegion(VALREGION.GLOBAL)
        symbol.setID(len(self.globals))
        self.globals.append(symbol)

    def addArg(self, symbol):
        symbol.setRegion(VALREGION.ARG)
        symbol.setID(len(self.args))
        self.args.append(symbol)

    def addLocal(self, symbol):
        symbol.setRegion(VALREGION.LOCAL)
        symbol.setID(self.localcount)
        self.localcount += 1
        self.locals[-1].append(symbol)

    def pushLocal():
        self.locals.append([])

    def popLocal():
        self.locals.pop()

    def resetFrame():
        self.args.clear()
        self.locals.clear()

    def getGlobalCount():
        return len(self.globals)

    def getArgCount():
        return len(self.args)

    def getLocalCount():
        return self.localcount

class AST:

    nullarg = '00000000'

    def __init__(self):
        pass

    def compile(self, env):
        pass


    def decideType(a, b):
        if (TYPES.Void in [a, b]):
            print('eval void error')
            return TYPES.Void
        #elif (a == 'any' and b == 'any'):
        #    return 'any'
        #elif (a == 'any'):
        #    return b
        #elif (b == 'any'):
        #    return a
        elif (a ==  TYPES.Uint and b == TYPES.Uint):
            return TYPES.Uint
        elif (a == TYPES.Int and b == TYPES.Int):
            return TYPES.Int
        elif (a == TYPES.Float and b == TYPES.Float):
            return TYPES.FLoat
        #elif ('uint' in [a, b] and 'float' in [a, b]):
        #    return 'float'
        #elif ('int' in [a, b] and 'float' in [a, b]):
        #    return 'float'


# -= :: Inherited MODEL :: =-

class BIOP (AST):

    op = ['U', 'I', 'F']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def compile(self, env):
        left = compile(self.left)
        right = compile(self.right)

        mytype = decideType(left.typename, right.typename)

        code = right.code
        code.extend(left.code)

        code.append([op[mytype], nullarg])

        return BYTECODE(mytype, code)



# -- Lv.1 modules --

class Program:
    def __init__(self, body):
        self.body = body
        pass

    def compile(self, env):
        return self.body.compile()

class GlobalVar:
    pass

class Func:
    def __init__(self, body):
        self.body = body
        pass

    def compile(self, env):
        return self.body.compile()

class Block:
    def __init__(self, body):
        self.body = body
        pass

    def compile(self, env):
        return self.body.compile(env)

class Localvar:
    pass

class Return:
    pass

class Funccall:
    pass

class If:
    pass

class Ifelse:
    pass

class While:
    pass

class For:
    pass


# -- Lv.2 modules --

class Add (BIOP):
    op = ['ADDU', 'ADDI', 'ADDF']


'''
class Input:
    pass
class Output:
    pass
class Readreg:
    pass
class Writereg:
    pass
class Assign:
    pass
class Inc:
    pass
class Dec:
    pass
class Inv:
    pass
class Sub:
    pass
class Mul:
    pass
class Div:
    pass
class Lt:
    pass
class Lte:
    pass
class Gt:
    pass
class Gte:
    pass
class Eq:
    pass
class Neq:
    pass
class Sin:
    pass
class Cos:
    pass
class Symbol:
    pass
class NumberI:
    pass
class NumberF:
    pass
class NumberU:
    pass
class String:
    pass

'''
