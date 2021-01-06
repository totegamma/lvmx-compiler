import glob as g
import MODEL as m
from mnemonic import mnemonic as opc

# -= :: TOP MODELS :: =-

class OPT:
    def __init__(self, popc = 0, lr = 'r', bp = None, cp = None):
        self.popc = popc
        self.lr = lr
        self.bp = bp
        self.cp = cp

class AST (object):

    nullarg = 0

    def __init__(self, tok):
        self.tok = tok

    def gencode(self, env, opt):
        pass

    def assertOnlyRValue(self, env, opt):
        if (opt.lr != 'r'):
            g.r.addReport(m.Report('error', self.tok, f'expression \'{self.__class__.__name__}\' is not assignable'))
            return m.Insts()

    def assertOnlyPop1(self, env, opt):
        if (opt.popc != 1):
            g.r.addReport(m.Report('warning', self.tok, 'expression result unused'))
            return m.Insts()

    def eval(self):
        return None

    def decideType(self, a, b):
        if (a.isVoid() or b.isVoid()):
            return MODEL.Types.Void
        #elif (a == 'any' and b == 'any'):
        #    return 'any'
        #elif (a == 'any'):
        #    return b
        #elif (b == 'any'):
        #    return a

        elif (a.isIndirect() and b.isInt()):
            return a

        elif (a.isInt() and b.isInt()):
            return m.Type('int')
        elif (a.isFloat() and b.isFloat()):
            return m.Type('float')
        raise DeclTypeException(f"invalid operands to binary expression('{a}' and '{b}')")

class DeclTypeException(Exception):
    pass

# -= :: Inherited MODEL :: =-

class BIOP (AST):

    opI = None
    opF = None

    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        left = self.left.gencode(env, OPT(1))
        right = self.right.gencode(env, OPT(1))

        try:
            typ = self.decideType(left.typ, right.typ)
        except DeclTypeException as e:
            g.r.addReport(m.Report('error', self.tok, e))
            return m.Insts()


        code = right.bytecodes
        code.extend(left.bytecodes)

        if typ.isInt():
            code.append(m.Inst(self.opI, self.nullarg))
        elif typ.isFloat():
            code.append(m.Inst(self.opF, self.nullarg))
        else:
            g.r.addReport(m.Report('fatal', self.tok, 'Type inference failed'))
            return m.Insts()

        return m.Insts(typ, code)


# -- Lv0 modules --

class Program (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body
        pass

    def gencode(self, env, opt):
        for elem in self.body:
            dumps = elem.gencode(env, OPT(0))
        env.addStatic(m.Symbol("__MAGIC_RETADDR__", m.Type(), 0))
        env.addStatic(m.Symbol("__MAGIC_RETFP__", m.Type(), 0))
        return env

class GlobalVar (AST):
    def __init__(self, tok, symbolname, typ, body = None):
        self.tok = tok
        self.typ = typ
        self.symbolname = symbolname
        self.body = body

    def gencode(self, env, opt):
        if isinstance(self.body, list):
            self.typ.resolve(env, length=len(self.body))
        else:
            self.typ.resolve(env)

        # スカラーか配列かstructかenumが入ってくる

        if self.typ.isScalar():
            if self.body is None:
                init = 0
            else:
                init = self.body.eval()
        elif self.typ.isArray():
            if self.body is None:
                init = [0] * self.typ.length
            else:
                init = list(map(lambda a : a.eval(), self.body))
        else:
            init = 0
            #g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while processing GlobalVar'))

        env.addStatic(m.Symbol(self.symbolname, self.typ, init))
        return env

class Struct (AST):
    def __init__(self, tok, symbolname, members):
        self.tok = tok
        self.symbolname = symbolname
        self.members = members

    def gencode(self, env, opt):
        typ = m.Type('struct')
        for elem in self.members:
            typ.addMember(elem)

        env.addStruct(self.symbolname, typ)
        return m.Insts(m.Type(), [])

class Enum (AST):
    def __init__(self, tok, symbolname, members):
        self.tok = tok
        self.symbolname = symbolname
        self.members = members

    def gencode(self, env, opt):
        enumitr = 0
        for elem in self.members:
            if elem[1] is None:
                env.addEnumMember(elem[0], enumitr)
                enumitr += 1
            else:
                env.addEnumMember(elem[0], elem[1])
                enumitr = elem[1]
        env.addEnum(self.symbolname)
        return m.Insts(m.Type(), [])

class Func (AST):
    def __init__(self, tok, symbolname, typ, args, body):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ
        self.args = args
        self.body = body

    def gencode(self, env, opt):
        self.typ.resolve(env)

        env.resetFrame(self.symbolname)

        for elem in self.args:
            env.addArg(elem)

        codes = self.body.gencode(env, OPT(0)).bytecodes

        insts = []
        insts.append(m.Inst(opc.ENTRY, self.symbolname))
        insts.append(m.Inst(opc.FRAME, env.getFrameSize()))
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

    def gencode(self, env, opt):
        env.pushScope()

        insts = []
        for elem in self.body:
            insts.extend(elem.gencode(env, OPT(0)).bytecodes)

        env.popScope()
        return m.Insts(m.Type(), insts)

class LocalVar (AST):
    def __init__(self, tok, symbolname, typ, init = None):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ
        self.init = init 

    def gencode(self, env, opt):

        if isinstance(self.init, list):
            self.typ.resolve(env, length=len(self.init))
        else:
            self.typ.resolve(env)

        # スカラーか配列かstructかenumが入ってくる

        var = env.addLocal(m.Symbol(self.symbolname, self.typ))

        if self.init is None:
            return m.Insts()
        elif isinstance(self.init, list):
            codes = []
            for i, elem in enumerate(self.init):
                codes.extend(elem.gencode(env, OPT(1)).bytecodes)
                codes.append(var.genAddrCode())
                codes.append(m.Inst(opc.PUSH, i))
                codes.append(m.Inst(opc.ADDI, self.nullarg))
                codes.append(m.Inst(opc.STOREP, self.nullarg))
            return m.Insts(m.Type(), codes)
        else:
            codes = self.init.gencode(env, OPT(1)).bytecodes
            codes.append(m.Inst(opc.STOREL, var.id))

        return m.Insts(m.Type(), codes)

class Indirect (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, opt):

        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        body = self.body.gencode(env, OPT(1))
        codes = body.bytecodes
        if opt.lr == 'r':
            codes.append(m.Inst(opc.LOADP, self.nullarg))
            return m.Insts(body.typ, codes) # TODO typeのrefcountを増減する必要があるかも
        else:
            codes.append(m.Inst(opc.STOREP, self.nullarg))
            return m.Insts(body.typ, codes) # TODO typeのrefcountを増減する必要があるかも

class Address (AST):
    def __init__(self, tok, symbol):
        self.tok = tok
        self.symbol = symbol

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        var = env.variableLookup(self.symbol)
        codes = [var.genAddrCode()]
        return m.Insts(var.typ, codes)

class FieldAccess (AST):
    def __init__(self, tok, left, fieldname):
        self.tok = tok
        self.left = left
        self.fieldname = fieldname

    def gencode(self, env, opt):
        left = self.left.gencode(env, OPT(1))
        codes = left.bytecodes

        field = left.typ.getField(env, self.fieldname)
        codes.append(m.Inst(opc.PUSH, field.offset))
        codes.append(m.Inst(opc.ADDI, self.nullarg))

        return m.Insts(field.typ, codes)


class Return (AST): #TODO 自分の型とのチェック
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, opt):
        codes = self.body.gencode(env, OPT(1)).bytecodes
        codes.append(m.Inst(opc.RET, self.nullarg))
        return m.Insts(m.Type(), codes)

class Funccall (AST):
    def __init__(self, tok, name, args):
        self.tok = tok
        self.name = name
        self.args = args

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        mytype = env.functionLookup(self.name).typ
        codes = []
        for elem in reversed(self.args):
            codes.extend(elem.gencode(env, OPT(1)).bytecodes) # TODO 型チェック
        codes.append(m.Inst(opc.CALL, self.name))
        codes.append(m.Inst(opc.POPR, len(self.args)))
        if (opt.popc == 0):
            codes.append(m.Inst(opc.POP, self.nullarg))
        return m.Insts(mytype, codes)

class If (AST):
    def __init__(self, tok, cond, then):
        self.tok = tok
        self.cond = cond
        self.then = then

    def gencode(self, env, opt):
        cond = self.cond.gencode(env, OPT(1)).bytecodes
        then = self.then.gencode(env, OPT(0)).bytecodes

        l0 = env.issueLabel()
        codes = cond
        codes.append(m.Inst(opc.JIF0, l0))
        codes.extend(then)
        codes.append(m.Inst(opc.LABEL, l0))
        return m.Insts(m.Type(), codes)

class Ifelse (AST):
    def __init__(self, tok, cond, then, elst):
        self.tok = tok
        self.cond = cond
        self.then = then
        self.elst = elst

    def gencode(self, env, opt):
        cond = self.cond.gencode(env, OPT(1)).bytecodes
        then = self.then.gencode(env, OPT(0)).bytecodes
        elst = self.elst.gencode(env, OPT(0)).bytecodes

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        codes = cond
        codes.append(m.Inst(opc.JIF0, l0))
        codes.extend(then)
        codes.append(m.Inst(opc.JUMP, l1))
        codes.append(m.Inst(opc.LABEL, l0))
        codes.extend(elst)
        codes.append(m.Inst(opc.LABEL, l1))
        return m.Insts(m.Type(), codes)

class DoWhile (AST):
    def __init__(self, tok, body, cond):
        self.tok = tok
        self.body = body
        self.cond = cond

    def gencode(self, env, opt):
        body = self.body.gencode(env, OPT(0)).bytecodes
        cond = self.cond.gencode(env, OPT(1)).bytecodes

        l0 = env.issueLabel()

        codes = [m.Inst(opc.LABEL, l0)]
        codes.extend(body)
        codes.extend(cond)
        codes.append(m.Inst(opc.INV, self.nullarg))
        codes.append(m.Inst(opc.JIF0, l0))

        return m.Insts(m.Type(), codes)


class While (AST):
    def __init__(self, tok, cond, body):
        self.tok = tok
        self.cond = cond
        self.body = body

    def gencode(self, env, opt):
        cond = self.cond.gencode(env, OPT(1)).bytecodes
        body = self.body.gencode(env, OPT(0)).bytecodes

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        codes = [m.Inst(opc.LABEL, l0)]
        codes.extend(cond)
        codes.append(m.Inst(opc.JIF0, l1))
        codes.extend(body)
        codes.append(m.Inst(opc.JUMP, l0))
        codes.append(m.Inst(opc.LABEL, l1))
        return m.Insts(m.Type(), codes)



class For (AST):
    def __init__(self, tok, init, cond, loop, body):
        self.tok = tok
        self.init = init
        self.cond = cond
        self.loop = loop
        self.body = body

    def gencode(self, env, opt):
        init = self.init.gencode(env, OPT(0)).bytecodes
        cond = self.cond.gencode(env, OPT(1)).bytecodes
        loop = self.loop.gencode(env, OPT(0)).bytecodes
        body = self.body.gencode(env, OPT(0)).bytecodes

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
        return m.Insts(m.Type(), codes)


class Switch (AST):
    def __init__(self, tok, cond, cases):
        self.tok = tok
        self.cond = cond
        self.cases = cases

    def gencode(self, env, opt):

        tableCodes = self.cond.gencode(env, OPT(1)).bytecodes
        bodyCodes = []
        end = env.issueLabel()
        default = None

        for elem in self.cases:
            label = env.issueLabel()
            if elem[0] == 'default':
                default = label
                bodyCodes.append(m.Inst(opc.LABEL, label))
                for e in elem[1]:
                    bodyCodes.extend(e.gencode(env, OPT(1, bp = end)).bytecodes)
                #bodyCodes.extend([e.gencode(env, OPT(1, bp = end)).bytecodes for e in elem[1]])
            else:
                tableCodes.append(m.Inst(opc.DUP, 1))
                tableCodes.extend(elem[0].gencode(env, OPT(1)).bytecodes)
                tableCodes.append(m.Inst(opc.NEQI, self.nullarg)) #TODO Int以外にも対応させる
                tableCodes.append(m.Inst(opc.JIF0, label))

                bodyCodes.append(m.Inst(opc.LABEL, label))
#                bodyCodes.extend([e.gencode(env, OPT(1, bp = end)).bytecodes for e in elem[1]])
                for e in elem[1]:
                    bodyCodes.extend(e.gencode(env, OPT(1, bp = end)).bytecodes)

        if default is not None:
            tableCodes.append(m.Inst(opc.JUMP, default))
        else:
            tableCodes.append(m.Inst(opc.JUMP, end))

        bodyCodes.append(m.Inst(opc.LABEL, end))
        bodyCodes.append(m.Inst(opc.POP, self.nullarg))

        codes = tableCodes
        codes.extend(bodyCodes)

        return m.Insts(m.Type(), codes)

class Break (AST):
    def __init__(self, tok):
        self.tok = tok

    def gencode(self, env, opt):
        if opt.bp is None:
            g.r.addReport(m.Report('error', self.tok, 'break in unbreakable point'))
            return m.Insts()
        else:
            return m.Insts(m.Type(), [m.Inst(opc.JUMP, opt.bp)])

class Continue (AST):
    def __init__(self, tok):
        self.tok = tok

    def gencode(self, env, opt):
        if opt.cp is None:
            g.r.addReport(m.Report('error', self.tok, 'to continue, you need extra gem! (you can\'t continue here.)'))
            return m.Insts()
        else:
            return m.Insts(m.Type(), [m.Inst(opc.JUMP, opt.cp)])

class Label (AST):
    def __init__(self, tok, name, expr):
        self.tok = tok
        self.name = name
        self.expr = expr

    def gencode(self, env, opt):
        label = env.currentFuncName + self.name
        expr = self.expr.gencode(env, OPT(0))

        codes = [m.Inst(opc.LABEL, label)]
        codes.extend(expr.bytecodes)

        return m.Insts(expr.typ, codes)

class Goto (AST):
    def __init__(self, tok, name):
        self.tok = tok
        self.name = name

    def gencode(self, env, opt):
        label = env.currentFuncName + self.name
        return m.Insts(m.Type(), [m.Inst(opc.JUMP, label)])


# -- Lv.2 modules --

class Cast (AST):
    def __init__(self, tok, targetType, body):
        self.tok = tok
        self.targetType = targetType
        self.body = body

    def gencode(self, env, opt):

        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        body = self.body.gencode(env, OPT(1))
        codes = body.bytecodes

        if body.typ.isInt():
            if self.targetType == 'float':
                codes.append(m.Inst(opc.ITOF, self.nullarg))
                return m.Insts(m.Type('float'), codes)
            else:
                g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while evaluating \'Cast\''))
                return m.Insts()

        elif body.typ.isFloat():
            if self.targetType == 'int':
                codes.append(m.Inst(opc.FTOI, self.nullarg))
                return m.Insts(m.Type('int'), codes)
            else:
                g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while evaluating \'Cast\''))
                return m.Insts()

        else:
            g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while evaluating \'Cast\''))
            return m.Insts()

class Raw (AST):
    def __init__(self, tok, typ, opc, arg, bodys):
        self.tok = tok
        self.typ = typ
        self.opc = opc
        self.arg = arg
        self.bodys = bodys

    def gencode(self, env, opt):
        self.typ.resolve(env)
        insts = []
        for elem in reversed(self.bodys):
            insts.extend(elem.gencode(env, OPT(1)).bytecodes)
        #insts.append(m.Inst(opc[self.opc], self.arg.eval()))
        insts.append(m.Inst(opc[self.opc], self.arg))

        return m.Insts(self.typ, insts)

class Assign (AST):
    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, opt):

        right = self.right.gencode(env, OPT(1))
        left = self.left.gencode(env, OPT(1, 'l'))

        typ = m.Type()

        codes = right.bytecodes
        if opt.popc == 1:
            codes.append(m.Inst(opc.DUP, 1))
            typ = right.typ
        codes.extend(left.bytecodes)

        return m.Insts(typ, codes)

class Inv (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        right = self.right.gencode(env, OPT(1, 'r'))

        codes = right.bytecodes
        codes.append(m.Inst(opc.INV, self.nullarg))

        return m.Insts(right.typ, codes)

class Pre_inc (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        right = self.right.gencode(env, OPT(1, 'r'))
        codes = right.bytecodes
        codes.append(m.Inst(opc.INC, self.nullarg))

        typ = m.Type()

        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
            typ = right.typ

        codes.extend(self.right.gencode(env, OPT(0, 'l')).bytecodes)

        return m.Insts(typ, codes)

class Pre_dec (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        right = self.right.gencode(env, OPT(1, 'r'))
        codes = right.bytecodes
        codes.append(m.Inst(opc.DEC, self.nullarg))

        typ = m.Type()

        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
            typ = right.typ

        codes.extend(self.right.gencode(env, OPT(0, 'l')).bytecodes)

        return m.Insts(typ, codes)

class Post_inc (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        right = self.right.gencode(env, OPT(1, 'r'))
        codes = right.bytecodes

        typ = m.Type()
        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
            typ = right.typ

        codes.append(m.Inst(opc.INC, self.nullarg))
        codes.extend(self.right.gencode(env, OPT(0, 'l')).bytecodes)

        return m.Insts(typ, codes)


class Post_dec (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        right = self.right.gencode(env, OPT(1, 'r'))
        codes = right.bytecodes

        typ = m.Type()
        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
            typ = right.typ

        codes.append(m.Inst(opc.DEC, self.nullarg))
        codes.extend(self.right.gencode(env, OPT(0, 'l')).bytecodes)

        return m.Insts(typ, codes)

class Add (BIOP):
    opI = opc.ADDI
    opF = opc.ADDF

class Sub (BIOP):
    opI = opc.SUBI
    opF = opc.SUBF

class Mul (BIOP):
    opI = opc.MULI
    opF = opc.MULF

class Div (BIOP):
    opI = opc.DIVI
    opF = opc.DIVF

class Mod (BIOP):
    opI = opc.MODI
    opF = opc.MODF

class And (BIOP):
    opI = opc.AND
    opF = opc.AND

class Or (BIOP):
    opI = opc.OR
    opF = opc.OR

class Xor (BIOP):
    opI = opc.XOR
    opF = opc.XOR

class LShift (BIOP):
    opI = opc.LSHI
    opF = opc.LSHI

class RShift (BIOP):
    opI = opc.RSHI
    opF = opc.RSHI

class Lt (BIOP):
    opI = opc.LTI
    opF = opc.LTF

class Lte (BIOP):
    opI = opc.LTEI
    opF = opc.LTEF

class Gt (BIOP):
    opI = opc.GTI
    opF = opc.GTF

class Gte (BIOP):
    opI = opc.GTEI
    opF = opc.GTEF

class Eq (BIOP):
    opI = opc.EQI
    opF = opc.EQF

class Neq (BIOP):
    opI = opc.NEQI
    opF = opc.NEQF

class Symbol (AST):
    def __init__(self, tok, symbolname):
        self.tok = tok
        self.symbolname = symbolname

    def gencode(self, env, opt):

        try:
            var = env.variableLookup(self.symbolname)
        except m.SymbolNotFoundException as e:

            # 変数が見つからなかったら、Enumとして解決を試みる
            try:
                value = env.enumLookup(self.symbolname)
            except m.SymbolNotFoundException as e:
                g.r.addReport(m.Report('error', self.tok, f'{e} not found'))
                return m.Inst()

            if (result := self.assertOnlyRValue(env, opt)) is not None:
                return result
            if (result := self.assertOnlyPop1(env, opt)) is not None:
                return result

            return m.Insts(m.Type('int'), [m.Inst(opc.PUSH, value)])

        if opt.lr == 'r':
            if (result := self.assertOnlyPop1(env, opt)) is not None:
                return result
            codes = [var.genLoadCode()]
            return m.Insts(var.typ, codes)
        else:
            codes = [var.genStoreCode()]
            return m.Insts(m.Type(), codes)

class NumberI (AST):
    def __init__(self, tok, value):
        self.tok = tok
        if isinstance(value, str):
            value = int(value)
        self.value = value

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        return m.Insts(m.Type('int'), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class NumberF (AST):
    def __init__(self, tok, value):
        self.tok = tok
        if isinstance(value, str):
            value = float(value.replace('f', ''))
        self.value = value

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        return m.Insts(m.Type('float'), [m.Inst(opc.PUSH, self.value)])

    def eval(self):
        return self.value

class String (AST):
    def __init__(self, tok, value):
        self.tok = tok
        self.value = value

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        strid = env.issueString(self.value)
        return m.Insts(m.Type('int'), [m.Inst(opc.PUSH, strid)])

    def eval(self):
        return self.value


