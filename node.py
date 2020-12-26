import glob
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
        if (a.isVoid() or b.isVoid()):
            glob.compileerrors += "eval void error\n"
            return MODEL.Types.Void
        #elif (a == 'any' and b == 'any'):
        #    return 'any'
        #elif (a == 'any'):
        #    return b
        #elif (b == 'any'):
        #    return a
        elif (a.isUint() and b.isUint()):
            return m.Types(m.BT.Uint)
        elif (a.isInt() and b.isInt()):
            return m.Types(m.BT.Int)
        elif (a.isFloat() and b.isFloat()):
            return m.Types(m.BT.Float)
        #elif ('uint' in [a, b] and 'float' in [a, b]):
        #    return 'float'
        #elif ('int' in [a, b] and 'float' in [a, b]):
        #    return 'float'
        glob.compileerrors += "{a=}\n"
        glob.compileerrors += "{b=}\n"


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

        typ = self.decideType(left.typ, right.typ)

        code = right.bytecodes
        code.extend(left.bytecodes)

        if typ.isUint():
            code.append(m.Inst(self.opU, self.nullarg))
        elif typ.isInt():
            code.append(m.Inst(self.opI, self.nullarg))
        elif typ.isFloat():
            code.append(m.Inst(self.opF, self.nullarg))
        else:
            glob.compileerrors += f"{typ=}"
            glob.compileerrors += f"ERROR BIOP ONLY SUPPORTS UINT OR INT OR FLOAT"

        return m.Insts(typ, code)

class UNIOP (AST):

    opU = None
    opI = None
    opF = None

    def __init__(self, right):
        self.right = right

    def gencode(self, env):

        var = env.variableLookup(self.right)

        symbolname = var.name
        typ = var.typ

        if typ.isUint():
            code = [m.Inst(opc.PUSH, 1)]
            code.append(env.variableLookup(symbolname).genLoadCode())
            code.append(m.Inst(self.opU, self.nullarg))
        elif typ.isInt():
            code = [m.Inst(opc.PUSH, 1)]
            code.append(env.variableLookup(symbolname).genLoadCode())
            code.append(m.Inst(self.opI, self.nullarg))
        elif typ.isFloat():
            code = [m.Inst(opc.PUSH, 1.0)]
            code.append(env.variableLookup(symbolname).genLoadCode())
            code.append(m.Inst(self.opF, self.nullarg))
        else:
            glob.compileerrors += f"ERROR UNIOP ONLY SUPPORTS UINT OR INT"

        code.append(env.variableLookup(symbolname).genStoreCode())

        return m.Insts(typ, code)



# -- Lv0 modules --

class Program (AST):
    def __init__(self, body):
        self.body = body
        pass

    def gencode(self, env):
        for elem in self.body:
            dumps = elem.gencode(env)
        env.addGlobal(m.Symbol("__MAGIC_RETADDR__", m.Types(m.BT.Void), 0))
        env.addGlobal(m.Symbol("__MAGIC_RETFP__", m.Types(m.BT.Void), 0))
        return env

class GlobalVar (AST):
    def __init__(self, symbolname, typ, body):
        self.typ = typ
        self.symbolname = symbolname
        self.body = body

    def gencode(self, env):
        env.addGlobal(m.Symbol(self.symbolname, self.typ, self.body.eval()))
        return env

class Func (AST):
    def __init__(self, symbolname, typ, args, body):
        self.symbolname = symbolname
        self.typ = typ
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
        if (insts[-1].opc is not opc.RET):
            insts.append(m.Inst(opc.PUSH, 0))
            insts.append(m.Inst(opc.RET, self.nullarg))

        env.addFunction(m.Function(self.symbolname, self.typ, self.args, insts))

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

        env.popLocal()
        return m.Insts(m.Types(m.BT.Void), insts)

class LocalVar (AST):
    def __init__(self, symbolname, typ, body):
        self.symbolname = symbolname
        self.typ = typ
        self.body = body

    def gencode(self, env):
        newid = env.addLocal(m.Symbol(self.symbolname, self.typ))
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.STOREL, newid))
        return m.Insts(m.Types(m.BT.Void), codes)

class Indirect (AST):
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        body = self.body.gencode(env)
        codes = body.bytecodes
        codes.append(m.Inst(opc.LOADP, self.nullarg))
        return m.Insts(body.typ, codes)

class Address (AST):
    def __init__(self, symbol):
        self.symbol = symbol

    def gencode(self, env):
        var = env.variableLookup(self.symbol)
        codes = [var.genAddrCode()]
        return m.Insts(var.typ, codes)

class Return (AST): #TODO 自分の型とのチェック
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.RET, self.nullarg))
        return m.Insts(m.Types(m.BT.Void), codes)

class Funccall (AST):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def gencode(self, env):
        mytype = env.functionLookup(self.name).typ
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
        return m.Insts(m.Types(m.BT.Void), codes)

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
        return m.Insts(m.Types(m.BT.Void), codes)

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
        return m.Insts(m.Types(m.BT.Void), codes)



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
        return m.Insts(m.Types(m.BT.Void), codes)

# -- Lv.2 modules --

class Cast (AST):
    def __init__(self, targetType, body):
        self.targetType = targetType
        self.body = body

    def gencode(self, env):

        body = self.body.gencode(env)
        codes = body.bytecodes

        if body.typ.isUint():
            if self.targetType == 'int':
                codes.append(m.Inst(opc.UTOI, self.nullarg))
                return m.Insts(m.Types(m.BT.Int), codes)
            elif self.targetType == 'float':
                codes.append(m.Inst(opc.UTOF, self.nullarg))
                return m.Insts(m.Types(m.BT.Float), codes)
            else:
                glob.compileerrors += f"Cast error"

        elif body.typ.isInt():
            if self.targetType == 'float':
                codes.append(m.Inst(opc.ITOF, self.nullarg))
                return m.Insts(m.Types(m.BT.Float), codes)
            elif self.targetType == 'uint':
                codes.append(m.Inst(opc.ITOU, self.nullarg))
                return m.Insts(m.Types(m.BT.Uint), codes)
            else:
                glob.compileerrors += f"Cast error"

        elif body.typ.isFloat():
            if self.targetType == 'uint':
                codes.append(m.Inst(opc.FTOU, self.nullarg))
                return m.Insts(m.Types(m.BT.Uint), codes)
            elif self.targetType == 'int':
                codes.append(m.Inst(opc.FTOI, self.nullarg))
                return m.Insts(m.Types(m.BT.Int), codes)
            else:
                glob.compileerrors += f"Cast error"

        else:
            glob.compileerrors += f"Cast error"

        print("PROGRAM ERROR in Cast")



class Input (AST):
    def __init__(self, key):
        self.key = key

    def gencode(self, env):
        self.key.gencode(env)
        stringslot = env.stringLookup(self.key.eval())
        return m.Insts(m.Types(m.BT.Any), [m.Inst(opc.INPUT, stringslot)])

class Output (AST):
    def __init__(self, key, body):
        self.key = key
        self.body = body

    def gencode(self, env):
        self.key.gencode(env)
        stringslot = env.stringLookup(self.key.eval(env))
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.OUTPUT, stringslot))
        return m.Insts(m.Types(m.BT.Void), codes)

class Readreg (AST):
    def __init__(self, key):
        self.key = key

    def gencode(self, env):
        addr = self.key.eval()
        return m.Insts(m.Types(m.BT.Any), [m.Inst(opc.LOADR, addr)])

class Writereg (AST):
    def __init__(self, key, body):
        self.key = key
        self.body = body

    def gencode(self, env):
        addr = self.key.eval()
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.STORER, addr))
        return m.Insts(m.Types(m.BT.Void), codes)

class Assign (AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def gencode(self, env):
        if isinstance(self.left, Symbol):
            right = self.right.gencode(env)
            codes = right.bytecodes
            var = env.variableLookup(self.left.symbolname)
            codes.append(var.genStoreCode())

            return m.Insts(m.Types(m.BT.Void), codes)
        elif isinstance(self.left, Indirect):
            right = self.right.gencode(env)
            codes = right.bytecodes
            body = self.left
            refcount = 0
            while (isinstance(body, Indirect)):
                body = body.body
                refcount += 1
            codes.extend(body.gencode(env).bytecodes)
            for i in range(refcount -1):
                codes.append(m.Inst(opc.LOADP, self.nullarg))
            codes.append(m.Inst(opc.STOREP, self.nullarg))

            return m.Insts(m.Types(m.BT.Void), codes)
        else:
            glob.compileerrors += f"コンパイルエラー: 代入できるのはシンボルか参照のみです(代入しようとしたオブジェクト: {self.left})" + '\n'



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
        return m.Insts(m.Types(m.BT.Float), codes)


class Cos (AST):
    def __init__(self, body):
        self.body = body

    def gencode(self, env):
        codes = self.body.gencode(env).bytecodes
        codes.append(m.Inst(opc.COS, self.nullarg))
        return m.Insts(m.Types(m.BT.Float), codes)

class Symbol (AST):
    def __init__(self, symbolname):
        self.symbolname = symbolname

    def gencode(self, env):
        var = env.variableLookup(self.symbolname)
        codes = [var.genLoadCode()]
        return m.Insts(var.typ, codes)


class NumberU (AST):
    def __init__(self, value):
        if isinstance(value, str):
            value = int(value.replace('u', ''))
        self.value = value

    def gencode(self, env):
        return m.Insts(m.Types(m.BT.Uint), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberI (AST):
    def __init__(self, value):
        if isinstance(value, str):
            value = int(value)
        self.value = value

    def gencode(self, env):
        return m.Insts(m.Types(m.BT.Int), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberF (AST):
    def __init__(self, value):
        if isinstance(value, str):
            value = float(value.replace('f', ''))
        self.value = value

    def gencode(self, env):
        return m.Insts(m.Types(m.BT.Float), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class String (AST):
    def __init__(self, value):
        self.value = value

    def gencode(self, env):
        strid = env.issueString(self.value)
        return m.Insts(m.Types(m.BT.Uint), [m.Inst(opc.PUSH, strid)])

    def eval(self):
        return self.value


