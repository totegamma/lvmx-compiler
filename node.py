import MODEL as m
from mnemonic import mnemonic as opc

# -= :: TOP MODELS :: =-
class AST:

    nullarg = 0

    def __init__(self):
        pass

    def gencode(self, env):
        pass

    def eval(self):
        return None


    def decideType(self, a, b):
        if (m.Types.Void in [a, b]):
            print('eval void error')
            return MODEL.Types.Void
        #elif (a == 'any' and b == 'any'):
        #    return 'any'
        #elif (a == 'any'):
        #    return b
        #elif (b == 'any'):
        #    return a
        elif (a ==  m.Types.Uint and b == m.Types.Uint):
            return m.Types.Uint
        elif (a == m.Types.Int and b == m.Types.Int):
            return m.Types.Int
        elif (a == m.Types.Float and b == m.Types.Float):
            return m.Types.Float
        #elif ('uint' in [a, b] and 'float' in [a, b]):
        #    return 'float'
        #elif ('int' in [a, b] and 'float' in [a, b]):
        #    return 'float'
        print(f"{a=}")
        print(f"{b=}")


# -= :: Inherited MODEL :: =-

class BIOP (AST):

    opU = None
    opI = None
    opF = None

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def gencode(self, env):

        left = self.left.gencode(env)
        right = self.right.gencode(env)

        typename = self.decideType(left.typename, right.typename)

        code = right.bytecodes
        code.extend(left.bytecodes)

        if (typename == m.Types.Uint):
            code.append(m.Inst(self.opU, self.nullarg))
        elif (typename == m.Types.Int):
            code.append(m.Inst(self.opI, self.nullarg))
        elif (typename == m.Types.Float):
            code.append(m.Inst(self.opF, self.nullarg))
        else:
            print(f"{typename=}")
            print("ERROR BIOP ONLY SUPPORTS UINT OR INT OR FLOAT")

        return m.Insts(typename, code)

class UNIOP (AST):

    opU = None
    opI = None
    opF = None

    def __init__(self, right):
        self.right = right

    def gencode(self, env):

        var = env.variableLookup(self.right)

        symbolname = var.name
        typename = var.typename

        if (typename == m.Types.Uint):
            code= [m.Inst(opc.PUSH, 1)]
            code.append(m.Inst(self.opU, self.nullarg))
        elif (typename == m.Types.Int):
            code= [m.Inst(opc.PUSH, 1)]
            code.append(m.Inst(self.opI, self.nullarg))
        elif (typename == m.Types.Float):
            code= [m.Inst(opc.PUSH, 1.0)]
            code.append(m.Inst(self.opF, self.nullarg))
        else:
            print("ERROR UNIOP ONLY SUPPORTS UINT OR INT")
        code.append(env.variableLookup(symbolname).genStoreCode())

        return m.Insts(typename, code)



# -- Lv0 modules --

class Program (AST):
    def __init__(self, body):
        self.body = body
        pass

    def gencode(self, env):
        for elem in self.body:
            dumps = elem.gencode(env)
        return env

class GlobalVar (AST):
    def __init__(self, symbolname, typename, body):
        self.typename = typename
        self.symbolname = symbolname
        self.body = body

    def gencode(self, env):
        env.addGlobal(m.Symbol(self.symbolname, self.typename, self.body.eval()))
        return env

class Func (AST):
    def __init__(self, symbolname, typename, args, body):
        self.symbolname = symbolname
        self.typename = typename
        self.args = args
        self.body = body

    def gencode(self, env):

        env.resetFrame()

        for elem in self.args:
            env.addArg(elem)

        codes = self.body.gencode(env).bytecodes

        insts = []
        insts.append(m.Inst(opc.ENTRY, self.symbolname))
        insts.append(m.Inst(opc.FRAME, env.getLocalCount()))
        insts.extend(codes)
        insts.append(m.Inst(opc.RET, self.nullarg)) # TODO codesの末尾にRETがないときだけ挿入するように

        env.addFunction(m.Function(self.symbolname, self.typename, self.args, insts))

        return env

# -- Lv1 modules --

class Block (AST):
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        env.pushLocal()

        insts = []
        for elem in self.body:
            insts.extend(elem.gencode(env).bytecodes)

        #env.popLocal()
        return m.Insts(m.Types.Void, insts)

class LocalVar (AST):
    def __init__(self, symbolname, typename, body):
        self.symbolname = symbolname
        self.typename = typename
        self.body = body

    def gencode(self, env):
        newid = env.addLocal(m.Symbol(self.symbolname, self.typename))
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.STOREL, newid))
        return m.Insts(m.Types.Void, codes)

class Return (AST): #TODO 自分の型とのチェック
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.RET, self.nullarg))
        return m.Insts(m.Types.Void, codes)

class Funccall (AST):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def gencode(self, env):
        mytype = env.functionLookup(self.name).typename
        codes = []
        for elem in reversed(self.args):
            codes.extend(elem.gencode(env).bytecodes) # TODO 型チェック
        codes.append(m.Inst(opc.CALL, self.name))
        codes.append(m.Inst(opc.POPR, len(self.args)))
        return m.Insts(mytype, codes)

class If (AST):
    def __init__(self, cond, then):
        self.cond = cond
        self.then = then

    def gencode(self, env):
        cond = self.cond.gencode(env).bytecodes
        then = self.then.gencode(env).bytecodes

        l0 = env.issueLabel()
        codes = cond
        codes.append(m.Inst(opc.JIF0, l0))
        codes.extend(then)
        codes.append(m.Inst(opc.LABEL, l0))
        return m.Insts(m.Types.Void, codes)

class Ifelse (AST):
    def __init__(self, cond, then, elst):
        self.cond = cond
        self.then = then
        self.elst = elst

    def gencode(self, env):
        cond = self.cond.gencode(env).bytecodes
        then = self.then.gencode(env).bytecodes
        elst = self.elst.gencode(env).bytecodes

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        codes = cond
        codes.append(m.Inst(opc.JIF0, l0))
        codes.extend(then)
        codes.append(m.Inst(opc.JUMP, l1))
        codes.append(m.Inst(opc.LABEL, l0))
        codes.extend(elst)
        codes.append(m.Inst(opc.LABEL, l1))
        return m.Insts(m.Types.Void, codes)

class While (AST):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def gencode(self, env):
        cond = self.cond.gencode(env).bytecodes
        body = self.body.gencode(env).bytecodes

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        codes = m.Inst(opc.LABEL, l0)
        codes.extend(cond)
        codes.append(m.Inst(opc.JIF0, l1))
        codes.extend(body)
        codes.append(m.Inst(opc.JUMP, l0))
        codes.append(m.Inst(opc.LABEL, l1))
        return m.Insts(m.Types.Void, codes)



class For (AST):
    def __init__(self, init, cond, loop, body):
        self.init = init
        self.cond = cond
        self.loop = loop
        self.body = body

    def gencode(self, env):
        init = self.init.gencode(env).bytecodes
        cond = self.cond.gencode(env).bytecodes
        loop = self.loop.gencode(env).bytecodes
        body = self.body.gencode(env).bytecodes

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        codes = init
        codes.append(m.Inst(opc.LABEL, l0))
        codes.extend(cond)
        codes.append(m.Inst(opc.JIF0, l1))
        codes.extend(body)
        codes.extend(loop)
        codes.append(m.Inst(opc.JUMP, l0))
        codes.append(m.Inst(opc.LABEL, l1))
        return m.Insts(m.Types.Void, codes)


# -- Lv.2 modules --

class Input (AST):
    def __init__(self, key):
        self.key = key

    def gencode(self, env):
        self.key.gencode(env)
        stringslot = env.stringLookup(self.key.eval())
        return m.Insts(m.Types.Any, [m.Inst(opc.INPUT, stringslot)])

class Output (AST):
    def __init__(self, key, body):
        self.key = key
        self.body = body

    def gencode(self, env):
        self.key.gencode(env)
        stringslot = env.stringLookup(self.key.eval(env))
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.OUTPUT, stringslot))
        return m.Insts(m.Types.Void, codes)

class Readreg (AST):
    def __init__(self, key):
        self.key = key

    def gencode(self, env):
        addr = self.key.eval()
        return m.Insts(m.Types.Any, [m.Inst(opc.LOADR, addr)])

class Writereg (AST):
    def __init__(self, key, body):
        self.key = key
        self.body = body

    def gencode(self, env):
        addr = self.key.eval()
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.STORER, addr))
        return m.Insts(m.Types.Void, codes)

class Assign (AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def gencode(self, env):
        var = env.variableLookup(self.left)

        right = self.right.gencode(env)
        codes = right.bytecodes
        codes.append(var.genStoreCode())

        return m.Insts(right.typename, codes)


class Inc (UNIOP):
    opU = opc.ADDU
    opI = opc.ADDI
    opF = opc.ADDF

class Dec (UNIOP):
    opU = opc.SUBU
    opI = opc.SUBI
    opF = opc.SUBF

class Inv: # TODO
    pass

class Add (BIOP):
    opU = opc.ADDU
    opI = opc.ADDI
    opF = opc.ADDF

class Sub (BIOP):
    opU = opc.SUBU
    opI = opc.SUBI
    opF = opc.SUBF

class Mul (BIOP):
    opU = opc.MULU
    opI = opc.MULI
    opF = opc.MULF

class Div (BIOP):
    opU = opc.DIVU
    opI = opc.DIVI
    opF = opc.DIVF

class Lt (BIOP):
    opU = opc.LTU
    opI = opc.LTI
    opF = opc.LTF

class Lte (BIOP):
    opU = opc.LTEU
    opI = opc.LTEI
    opF = opc.LTEF

class Gt (BIOP):
    opU = opc.GTU
    opI = opc.GTI
    opF = opc.GTF

class Gte (BIOP):
    opU = opc.GTEU
    opI = opc.GTEI
    opF = opc.GTEF

class Eq (BIOP):
    opU = opc.EQU
    opI = opc.EQI
    opF = opc.EQF

class Neq (BIOP):
    opU = opc.NEQU
    opI = opc.NEQI
    opF = opc.NEQF

class Sin (AST):
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.SIN, self.nullarg))
        return m.Insts(m.Types.Float, codes)


class Cos (AST):
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.COS, self.nullarg))
        return m.Insts(m.Types.Float, codes)

class Symbol (AST):
    def __init__(self, symbolname):
        self.symbolname = symbolname

    def gencode(self, env):
        var = env.variableLookup(self.symbolname)
        codes = [var.genLoadCode()]
        return m.Insts(var.typename, codes)

class NumberU (AST):
    def __init__(self, value):
        if isinstance(value, str):
            value = int(value.replace('u', ''))
        self.value = value

    def gencode(self, env):
        return m.Insts(m.Types.Uint, [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberI (AST):
    def __init__(self, value):
        if isinstance(value, str):
            value = int(value)
        self.value = value

    def gencode(self, env):
        return m.Insts(m.Types.Int, [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberF (AST):
    def __init__(self, value):
        if isinstance(value, str):
            value = float(value.replace('f', ''))
        self.value = value

    def gencode(self, env):
        return m.Insts(m.Types.Float, [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class String (AST):
    def __init__(self, value):
        self.value = value

    def gencode(self, env):
        strid = env.issueString(self.value)
        return m.Insts(m.Types.Uint, [m.Inst(opc.PUSH, strid)])

    def eval(self):
        return self.value


