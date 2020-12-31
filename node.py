import glob
import MODEL as m
from mnemonic import mnemonic as opc

# -= :: TOP MODELS :: =-
class AST:

    nullarg = 0

    def __init__(self, tok):
        self.t = tok

    def gencode(self, env, pops = 0):
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

        elif (a.isIndirect() and b.isUint()):
            return a
        elif (a.isIndirect() and b.isInt()):
            return a

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
        glob.compileerrors += f"型不一致エラー({a.__str__()}と{b.__str__()})" + '\n'

# -= :: Inherited MODEL :: =-

class BIOP (AST):

    opU = None
    opI = None
    opF = None

    def __init__(self, tok, left, right):
        self.t = tok
        self.left = left
        self.right = right

    def gencode(self, env, pops = 0):

        if (pops == 1):
            left = self.left.gencode(env, 1)
            right = self.right.gencode(env, 1)

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
                glob.compileerrors += f"ERROR BIOP ONLY SUPPORTS UINT OR INT OR FLOAT"

            return m.Insts(typ, code)
        else:
            return m.Insts(m.Types(m.BT.Void), [])
            glob.warn += f"[BIOP] 利用していない評価結果"


class UNIOP (AST):

    opU = None
    opI = None
    opF = None

    def __init__(self, tok, right):
        self.t = tok
        self.right = right

    def gencode(self, env, pops):

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

        if pops == 0:
            code.append(env.variableLookup(symbolname).genStoreCode())
            return m.Insts(typ, code)

        elif pops == 1:
            code.append(m.Inst(opc.DUP, 1))
            code.append(env.variableLookup(symbolname).genStoreCode())
            return m.Insts(typ, code)

        else:
            glob.compileerrors += f"Program Error"



# -- Lv0 modules --

class Program (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body
        pass

    def gencode(self, env, pops = 0):
        for elem in self.body:
            dumps = elem.gencode(env, 0)
        env.addGlobal(m.Symbol("__MAGIC_RETADDR__", m.Types(m.BT.Void), 1, 0))
        env.addGlobal(m.Symbol("__MAGIC_RETFP__", m.Types(m.BT.Void), 1, 0))
        return env

class GlobalVar (AST):
    def __init__(self, tok, symbolname, typ, body):
        self.tok = tok
        self.typ = typ
        self.symbolname = symbolname
        self.body = body

    def gencode(self, env, pops = 0):
        #TODO 処遇に困る
        env.addGlobal(m.Symbol(self.symbolname, self.typ, 1, self.body.eval()))
        return env

class Struct (AST):
    def __init__(self, tok, symbolname, members):
        self.tok = tok
        self.symbolname = symbolname
        self.members = members

    def gencode(self, env, pops = 0):
        env.addType(self.symbolname, m.Types(None, 0, len(self.members), self.members))
        return m.Insts(m.Types(m.BT.Void), [])

class Func (AST):
    def __init__(self, tok, symbolname, typ, args, body):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ
        self.args = args
        self.body = body

    def gencode(self, env, pops):

        env.resetFrame()

        for elem in self.args:
            env.addArg(elem)

        codes = self.body.gencode(env, 0).bytecodes

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
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, pops):
        env.pushLocal()

        insts = []
        for elem in self.body:
            insts.extend(elem.gencode(env, 0).bytecodes)

        env.popLocal()
        return m.Insts(m.Types(m.BT.Void), insts)

class LocalVar (AST):
    def __init__(self, tok, symbolname, typ, init = None):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ
        self.init = init 

    def gencode(self, env, pops):

        self.typ.resolve(env)

        if (self.typ.size is None):
            if (self.init is None):
                size = 1
            else:
                size = len(self.init)
        elif (isinstance(self.typ.size, AST)):
            size = self.typ.size.eval()
        elif (type(self.typ.size) == int or float): # XXX
            size = self.typ.size
        else:
            print("fatal")

        if (size > 1):
            self.typ.isarray = 1

        var = env.addLocal(m.Symbol(self.symbolname, self.typ, size))

        if (self.init is None):
            return m.Insts(m.Types(m.BT.Void), [])

        if (isinstance(self.init, list)):

            if (size != len(self.init)):
                print("initalizer length mismatch!")
                return m.Insts(m.Types(m.BT.Void), [])

            codes = []
            for i, elem in enumerate(self.init):
                codes.extend(elem.gencode(env, 1).bytecodes)
                codes.append(var.genAddrCode())
                codes.append(m.Inst(opc.PUSH, i))
                codes.append(m.Inst(opc.ADDI, self.nullarg))
                codes.append(m.Inst(opc.STOREP, self.nullarg))
            return m.Insts(m.Types(m.BT.Void), codes)
        else:
            print(self.init)
            codes = self.init.gencode(env, 1).bytecodes
            codes.append(m.Inst(opc.STOREL, var.id))
            return m.Insts(m.Types(m.BT.Void), codes)

class Indirect (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, pops):
        body = self.body.gencode(env, 1)
        codes = body.bytecodes
        codes.append(m.Inst(opc.LOADP, self.nullarg))
        return m.Insts(body.typ, codes)

class Address (AST):
    def __init__(self, tok, symbol):
        self.tok = tok
        self.symbol = symbol

    def gencode(self, env, pops):
        var = env.variableLookup(self.symbol)
        codes = [var.genAddrCode()]
        return m.Insts(var.typ, codes)

class Return (AST): #TODO 自分の型とのチェック
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, pops):
        codes = self.body.gencode(env, 1).bytecodes
        codes.append(m.Inst(opc.RET, self.nullarg))
        return m.Insts(m.Types(m.BT.Void), codes)

class Funccall (AST):
    def __init__(self, tok, name, args):
        self.tok = tok
        self.name = name
        self.args = args

    def gencode(self, env, pops):
        mytype = env.functionLookup(self.name).typ
        codes = []
        for elem in reversed(self.args):
            codes.extend(elem.gencode(env, 1).bytecodes) # TODO 型チェック
        codes.append(m.Inst(opc.CALL, self.name))
        codes.append(m.Inst(opc.POPR, len(self.args) + 1 if (pops == 0) else 0))
        return m.Insts(mytype, codes)

class If (AST):
    def __init__(self, tok, cond, then):
        self.tok = tok
        self.cond = cond
        self.then = then

    def gencode(self, env, pops):
        cond = self.cond.gencode(env, 1).bytecodes
        then = self.then.gencode(env, 0).bytecodes

        l0 = env.issueLabel()
        codes = cond
        codes.append(m.Inst(opc.JIF0, l0))
        codes.extend(then)
        codes.append(m.Inst(opc.LABEL, l0))
        return m.Insts(m.Types(m.BT.Void), codes)

class Ifelse (AST):
    def __init__(self, tok, cond, then, elst):
        self.tok = tok
        self.cond = cond
        self.then = then
        self.elst = elst

    def gencode(self, env, pops):
        cond = self.cond.gencode(env, 1).bytecodes
        then = self.then.gencode(env, 0).bytecodes
        elst = self.elst.gencode(env, 0).bytecodes

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
    def __init__(self, tok, cond, body):
        self.tok = tok
        self.cond = cond
        self.body = body

    def gencode(self, env, pops):
        cond = self.cond.gencode(env, 1).bytecodes
        body = self.body.gencode(env, 0).bytecodes

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
    def __init__(self, tok, init, cond, loop, body):
        self.tok = tok
        self.init = init
        self.cond = cond
        self.loop = loop
        self.body = body

    def gencode(self, env, pops):
        init = self.init.gencode(env, 0).bytecodes
        cond = self.cond.gencode(env, 1).bytecodes
        loop = self.loop.gencode(env, 0).bytecodes
        body = self.body.gencode(env, 0).bytecodes

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
    def __init__(self, tok, targetType, body):
        self.tok = tok
        self.targetType = targetType
        self.body = body

    def gencode(self, env, pops):

        body = self.body.gencode(env, 1)
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

class Raw (AST):
    def __init__(self, tok, typ, opc, arg, bodys):
        self.tok = tok
        self.typ = typ
        self.opc = opc
        self.arg = arg
        self.bodys = bodys

    def gencode(self, env, pops):
        insts = []
        for elem in reversed(self.bodys):
            insts.extend(elem.gencode(env, 1).bytecodes)
        insts.append(m.Inst(opc[self.opc], self.arg.eval()))

        return m.Insts(self.typ, insts)

class Readreg (AST):
    def __init__(self, tok, key):
        self.tok = tok
        self.key = key

    def gencode(self, env, pops):
        if pops == 1:
            addr = self.key.eval()
            return m.Insts(m.Types(m.BT.Any), [m.Inst(opc.LOADR, addr)])
        else:
            print("unused value in readreg")

class Writereg (AST):
    def __init__(self, tok, key, body):
        self.tok = tok
        self.key = key
        self.body = body

    def gencode(self, env, pops):
        addr = self.key.eval()
        codes = self.body.gencode(env, 1).bytecodes
        codes.append(m.Inst(opc.STORER, addr))
        return m.Insts(m.Types(m.BT.Void), codes)

class Assign (AST):
    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, pops):
        if isinstance(self.left, Symbol):
            right = self.right.gencode(env, 1)
            codes = right.bytecodes
            var = env.variableLookup(self.left.symbolname)
            codes.append(var.genStoreCode())

            if pops == 0:
                return m.Insts(m.Types(m.BT.Void), codes)

            elif pops == 1:
                codes.append(m.Inst(opc.DUP, 1));
                return m.Insts(var.typ, codes)

            else:
                print("program error in Assign")

        elif isinstance(self.left, Indirect):
            right = self.right.gencode(env, 1)
            codes = right.bytecodes
            body = self.left
            refcount = 0

            while (isinstance(body, Indirect)):
                body = body.body
                refcount += 1

#           if isinstance(body, Symbol) and not body.isIndirect():
#               var = env.variableLookup(body.symbolname)
#               codes.append(var.genAddrCode())
#           else:
#               codes.extend(body.gencode(env, 1).bytecodes)

            codes.extend(body.gencode(env, 1).bytecodes)

            for i in range(refcount -1):
                codes.append(m.Inst(opc.LOADP, self.nullarg))
            codes.append(m.Inst(opc.STOREP, self.nullarg))

            if pops == 0:
                return m.Insts(m.Types(m.BT.Void), codes)

            elif pops == 1:
                codes.append(m.Inst(opc.DUP, 1));
                return m.Insts(var.typ, codes)
            else:
                print("program error in Assign")

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

class Symbol (AST):
    def __init__(self, tok, symbolname):
        self.tok = tok
        self.symbolname = symbolname

    def gencode(self, env, pops):
        var = env.variableLookup(self.symbolname)
        codes = [var.genLoadCode()]
        return m.Insts(var.typ, codes)

class NumberU (AST):
    def __init__(self, tok, value):
        self.tok = tok
        if isinstance(value, str):
            value = int(value.replace('u', ''))
        self.value = value

    def gencode(self, env, pops):
        return m.Insts(m.Types(m.BT.Uint), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberI (AST):
    def __init__(self, tok, value):
        self.tok = tok
        if isinstance(value, str):
            value = int(value)
        self.value = value

    def gencode(self, env, pops):
        return m.Insts(m.Types(m.BT.Int), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberF (AST):
    def __init__(self, tok, value):
        self.tok = tok
        if isinstance(value, str):
            value = float(value.replace('f', ''))
        self.value = value

    def gencode(self, env, pops):
        return m.Insts(m.Types(m.BT.Float), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class String (AST):
    def __init__(self, tok, value):
        self.tok = tok
        self.value = value

    def gencode(self, env, pops):
        strid = env.issueString(self.value)
        return m.Insts(m.Types(m.BT.Uint), [m.Inst(opc.PUSH, strid)])

    def eval(self):
        return self.value


