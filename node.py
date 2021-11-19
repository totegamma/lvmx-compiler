from copy import copy
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

def newopt(opt, popc = 0, lr = 'r', bp = None, cp = None):
    newpopc = popc
    newlr = lr
    newbp = bp or opt.bp
    newcp = cp or opt.cp
    return OPT(newpopc, newlr, newbp, newcp)

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

# -= :: Inherited MODEL :: =-

class BIOP (AST):

    opI = None
    opF = None
    isCompOP = False

    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        left = self.left.gencode(env, newopt(opt, 1))
        right = self.right.gencode(env, newopt(opt, 1))

        code = right.bytecodes
        code.extend(left.bytecodes)

        if self.isCompOP: # 比較演算子ならポインタ同士の演算が可能
            if left.typ.isPointer() or right.typ.isPointer():
                code.append(m.Inst(self.opI, self.nullarg))
                return m.Insts(m.Type('int'), code)
        else: # そうでないならスカラーしか演算できない
            if not (left.typ.isScalar() and right.typ.isScalar()):
                g.r.addReport(m.Report('error', self.tok, f"invalid operands to binary expression('{left.typ}' and '{right.typ}')"))
                return m.Insts()

        if (not left.typ.isBasetype()):
            left.typ = env.getType(left.typ.basetype)

        if (not right.typ.isBasetype()):
            right.typ = env.getType(right.typ.basetype)

        if (left.typ.basetype == 'int' or left.typ.basetype == 'enum') and (right.typ.basetype == 'int' or right.typ.basetype == 'enum'):
            code.append(m.Inst(self.opI, self.nullarg))
            typ = m.Type('int')

        elif left.typ.basetype == 'float' and right.typ.basetype == 'float':
            code.append(m.Inst(self.opF, self.nullarg))
            typ = m.Type('float')

        else:
            g.r.addReport(m.Report('error', self.tok, f"invalid operands to binary expression('{left.typ}' and '{right.typ}')"))
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
            dumps = elem.gencode(env, newopt(opt, 0))
        env.addStatic(m.Symbol("__MAGIC_RETADDR__", m.Type(), 0))
        env.addStatic(m.Symbol("__MAGIC_RETFP__", m.Type(), 0))
        return env

class GlobalVar (AST):
    def __init__(self, tok, symbolname, typ, init = None):
        self.tok = tok
        self.typ = typ
        self.symbolname = symbolname
        self.init = init

    def gencode(self, env, opt):

        size = env.calcTypeSize(self.typ, self.init)

        init = [0] * size

        if isinstance(self.init, AST):
            init[0] = self.init.eval()

        elif isinstance(self.init, list):
            for i, elem in enumerate(self.init):
                init[i] = self.init[i].eval()

        env.addStatic(m.Symbol(self.symbolname, self.typ, init))
        return env

class Struct (AST):
    def __init__(self, tok, symbolname, typ):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ

    def gencode(self, env, opt):

        env.addStruct(self.symbolname, self.typ)

        return m.Insts(m.Type(), [])

class Enum (AST):
    def __init__(self, tok, symbolname, typ):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ 

    def gencode(self, env, opt):

        env.addEnum(self.symbolname, self.typ)

        return m.Insts(m.Type(), [])

class Func (AST):
    def __init__(self, tok, symbolname, typ, args, body):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ
        self.args = args
        self.body = body

    def gencode(self, env, opt):

        if self.body is None: # 定義
            try:
                env.addFunction(m.Function(self.symbolname, self.typ, self.args, None))
            except m.SymbolRedefineException:
                g.r.addReport(m.Report('error', self.tok, f"Redefinition of '{self.symbolname}'"))
            return env
        else: # 実装
            env.resetFrame(self.symbolname)

            for elem in self.args:
                env.addArg(elem)

            codes = self.body.gencode(env, newopt(opt, 0)).bytecodes

            insts = []
            insts.append(m.Inst(opc.ENTRY, self.symbolname))
            insts.append(m.Inst(opc.FRAME, env.getFrameSize()))
            insts.extend(codes)
            if (insts[-1].opc is not opc.RET):
                insts.append(m.Inst(opc.PUSH, 0))
                insts.append(m.Inst(opc.RET, self.nullarg))

            try:
                env.addFunction(m.Function(self.symbolname, self.typ, self.args, insts))
            except m.SymbolRedefineException:
                g.r.addReport(m.Report('error', self.tok, f"Redefinition of '{self.symbolname}'"))
            except m.ConflictingTypesException:
                g.r.addReport(m.Report('error', self.tok, f"Conflicting types for '{self.symbolname}'"))

            return env

    def setBody(self, body):
        self.body = body
        return self


class Typedef (AST):
    def __init__(self, tok, name, typ):
        self.tok = tok
        self.name = name
        self.typ = typ

    def gencode(self, env, opt):

        if self.typ.isStruct():
            env.addStruct(self.name, self.typ)

        if self.typ.isEnum():
            env.addEnum(self.name, self.typ)

        env.addType(self.name, self.typ)

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
            insts.extend(elem.gencode(env, newopt(opt, 0)).bytecodes)

        env.popScope()
        return m.Insts(m.Type(), insts)

class LocalVar (AST):
    def __init__(self, tok, symbolname, typ, init = None):
        self.tok = tok
        self.symbolname = symbolname
        self.typ = typ
        self.init = init 

    def gencode(self, env, opt):

        env.calcTypeSize(self.typ, self.init)
        var = env.addLocal(m.Symbol(self.symbolname, self.typ))

        if self.init is None:
            return m.Insts()
        elif isinstance(self.init, list):
            codes = []
            for i, elem in enumerate(self.init):
                codes.extend(elem.gencode(env, newopt(opt, 1)).bytecodes)
                codes.append(var.genAddrCode())
                codes.append(m.Inst(opc.PUSH, i))
                codes.append(m.Inst(opc.ADDI, self.nullarg))
                codes.append(m.Inst(opc.STOREP, self.nullarg))
            return m.Insts(m.Type(), codes)
        else:
            codes = self.init.gencode(env, newopt(opt, 1)).bytecodes
            codes.append(m.Inst(opc.STOREL, var.id))

        return m.Insts(m.Type(), codes)

class Indirect (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, opt):

        body = self.body.gencode(env, newopt(opt, 1))
        codes = body.bytecodes
        if opt.lr == 'r':
            if (result := self.assertOnlyPop1(env, opt)) is not None:
                return result
            codes.append(m.Inst(opc.LOADP, self.nullarg))
            return m.Insts(copy(body.typ).addRefcount(-1), codes)
        else:
            codes.append(m.Inst(opc.STOREP, self.nullarg))
            return m.Insts(copy(body.typ).addRefcount(-1), codes)

class Address (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        if isinstance(self.body, Symbol):
            var = env.variableLookup(self.body.symbolname)
            codes = [var.genAddrCode()]
            return m.Insts(copy(var.typ).addRefcount(1), codes)

        elif isinstance(self.body, Indirect):
            return self.body.body.gencode(env, newopt(opt, 1))

        else:
            g.r.addReport(m.Report('error', self.tok, f"cannot get address"))




class FieldAccess (AST):
    def __init__(self, tok, left, fieldname):
        self.tok = tok
        self.left = left
        self.fieldname = fieldname

    def gencode(self, env, opt):
        left = self.left.gencode(env, newopt(opt, 1))
        codes = left.bytecodes

        field = env.getField(left.typ, self.fieldname) # TODO handle exception
#            g.r.addReport(m.Report('error', self.tok, f"cannot get field '{self.fieldname}' of type '{left.typ}'"))
#            return m.Insts()
        codes.append(m.Inst(opc.PUSH, field[0]))
        codes.append(m.Inst(opc.ADDI, self.nullarg))

        return m.Insts(field[1], codes)


class Return (AST): #TODO 自分の型とのチェック
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, opt):
        codes = self.body.gencode(env, newopt(opt, 1)).bytecodes
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

        try:
            define = env.functionLookup(self.name)
        except m.SymbolNotFoundException:
            g.r.addReport(m.Report('error', self.tok, f"function '{self.name}' not defined"))
            return m.Insts()

        if self.args is None:
            self.args = []

        selfArgLength = len(self.args)
        definedArgLength = len(define.args)

        if selfArgLength != definedArgLength:
            g.r.addReport(m.Report('error', self.tok, f'too {"many" if selfArgLength > definedArgLength else "few"} arguments to function call, expected {definedArgLength}, have {selfArgLength}'))
            return m.Insts()

        mytype = define.typ
        codes = []
        argtypes = []
        for elem in reversed(self.args):
            arg = elem.gencode(env, newopt(opt, 1))
            codes.extend(arg.bytecodes)
            argtypes.append(arg.typ)

        argtypes = list(reversed(argtypes))

        for i in range(selfArgLength):
            if argtypes[i] != define.args[i].typ:
                g.r.addReport(m.Report('error', self.tok, f'{"%d%s" % (i+1,"tsnrhtdd"[(i+1//10%10!=1)*((i+1)%10<4)*(i+1)%10::4])} parameter type mismatches'))
                return m.Insts()


        codes.append(m.Inst(opc.CALL, self.name))
        codes.append(m.Inst(opc.POPR, len(self.args)))
        if (opt.popc == 0):
            codes.append(m.Inst(opc.POP, self.nullarg))

        env.markCalledFunc(self.name)

        return m.Insts(mytype, codes)

class If (AST):
    def __init__(self, tok, cond, then):
        self.tok = tok
        self.cond = cond
        self.then = then

    def gencode(self, env, opt):
        cond = self.cond.gencode(env, newopt(opt, 1)).bytecodes
        then = self.then.gencode(env, newopt(opt, 0)).bytecodes

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
        cond = self.cond.gencode(env, newopt(opt, 1)).bytecodes
        then = self.then.gencode(env, newopt(opt, 0)).bytecodes
        elst = self.elst.gencode(env, newopt(opt, 0)).bytecodes

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

        l0 = env.issueLabel()

        body = self.body.gencode(env, newopt(opt, cp=l0, bp=None)).bytecodes
        cond = self.cond.gencode(env, newopt(opt, 1)).bytecodes

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

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        cond = self.cond.gencode(env, newopt(opt, 1)).bytecodes
        body = self.body.gencode(env, newopt(opt, 0, cp=l0, bp=l1)).bytecodes

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

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        if self.init is None: # TODO 1ライン化するか関数化して全部に適用
            init = []
        else:
            init = self.init.gencode(env, newopt(opt, 0)).bytecodes
        cond = self.cond.gencode(env, newopt(opt, 1)).bytecodes
        loop = self.loop.gencode(env, newopt(opt, 0)).bytecodes
        body = self.body.gencode(env, newopt(opt, 0, cp=l0, bp=l1)).bytecodes

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

        tableCodes = self.cond.gencode(env, newopt(opt, 1)).bytecodes
        bodyCodes = []
        end = env.issueLabel()
        default = None

        for elem in self.cases:
            label = env.issueLabel()
            if elem[0] == 'default':
                default = label
                bodyCodes.append(m.Inst(opc.LABEL, label))
                for e in elem[1]:
                    bodyCodes.extend(e.gencode(env, newopt(opt, 1, bp = end)).bytecodes)
            else:
                tableCodes.append(m.Inst(opc.DUP, 1))
                tableCodes.extend(elem[0].gencode(env, newopt(opt, 1)).bytecodes)
                tableCodes.append(m.Inst(opc.NEQI, self.nullarg)) #TODO Int以外にも対応させる
                tableCodes.append(m.Inst(opc.JIF0, label))

                bodyCodes.append(m.Inst(opc.LABEL, label))
                for e in elem[1]:
                    bodyCodes.extend(e.gencode(env, newopt(opt, 1, bp = end)).bytecodes)

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
        expr = self.expr.gencode(env, newopt(opt, 0))

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

class Ternary (AST):
    def __init__(self, tok, cond, then, elst):
        self.tok = tok
        self.cond = cond
        self.then = then
        self.elst = elst

    def gencode(self, env, opt):
        cond = self.cond.gencode(env, newopt(opt, 1))
        then = self.then.gencode(env, newopt(opt, 1))
        elst = self.elst.gencode(env, newopt(opt, 1))

        # TODO check if then.typ != elst.typ

        l0 = env.issueLabel()
        l1 = env.issueLabel()

        codes = cond.bytecodes
        codes.append(m.Inst(opc.JIF0, l0))
        codes.extend(then.bytecodes)
        codes.append(m.Inst(opc.JUMP, l1))
        codes.append(m.Inst(opc.LABEL, l0))
        codes.extend(elst.bytecodes)
        codes.append(m.Inst(opc.LABEL, l1))

        return m.Insts(then.typ, codes)



class Cast (AST):
    def __init__(self, tok, targetType, body):
        self.tok = tok
        self.targetType = targetType
        self.body = body

    def gencode(self, env, opt):

        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        bodyc = self.body.gencode(env, newopt(opt, 1))
        codes = bodyc.bytecodes

        if bodyc.typ.basetype == 'int':
            if self.targetType.basetype == 'float':
                codes.append(m.Inst(opc.ITOF, self.nullarg))
                return m.Insts(m.Type('float'), codes)
            else:
                g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while evaluating \'Cast\' #0'))
                return m.Insts()

        elif bodyc.typ.basetype == 'float':
            if self.targetType.basetype == 'int':
                codes.append(m.Inst(opc.FTOI, self.nullarg))
                return m.Insts(m.Type('int'), codes)
            else:
                g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while evaluating \'Cast\' #1'))
                return m.Insts()

        else:
            g.r.addReport(m.Report('fatal', self.tok, 'Program error occurred while evaluating \'Cast\' #2'))
            return m.Insts()

class Sizeof (AST):
    def __init__(self, tok, body):
        self.tok = tok
        self.body = body

    def gencode(self, env, opt):
        if isinstance(self.body, m.Type):
            return m.Insts(m.Type('int'), [m.Inst(opc.PUSH, env.calcTypeSize(self.body))])
        elif isinstance(self.body, Symbol):
            try:
                var = env.variableLookup(self.body.symbolname)
            except m.SymbolNotFoundException as e:
                g.r.addReport(m.Report('fatal', self.tok, f"cannot eval size of type '{type(self.body)}'"))
                return m.Insts()

            return m.Insts(m.Type('int'), [m.Inst(opc.PUSH, env.calcTypeSize(var.typ))])
        else:
            g.r.addReport(m.Report('fatal', self.tok, f"cannot eval size of type '{type(self.body)}'"))
        return m.Insts()

class Raw (AST):
    def __init__(self, tok, typ, opc, arg, bodys):
        self.tok = tok
        self.typ = typ
        self.opc = opc
        self.arg = arg
        self.bodys = bodys

    def gencode(self, env, opt):
#        self.typ.resolve(env)
        insts = []
        for elem in reversed(self.bodys):
            insts.extend(elem.gencode(env, newopt(opt, 1)).bytecodes)
        #insts.append(m.Inst(opc[self.opc], self.arg.eval()))
        insts.append(m.Inst(opc[self.opc], self.arg))

        return m.Insts(self.typ, insts)

class Assign (AST):
    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, opt):

        right = self.right.gencode(env, newopt(opt, 1))
        left = self.left.gencode(env, newopt(opt, 1, 'l'))

        typ = m.Type()

        codes = right.bytecodes
        if opt.popc == 1:
            codes.append(m.Inst(opc.DUP, 1))
            typ = right.typ
        codes.extend(left.bytecodes)

        return m.Insts(typ, codes)

class Minus (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        right = self.right.gencode(env, newopt(opt, 1, 'r'))
        codes = right.bytecodes
        typ = copy(right.typ)

        if right.typ.basetype == 'int':
            codes.append(m.Inst(opc.PUSH, -1))
            codes.append(m.Inst(opc.MULI, self.nullarg))
            typ = m.Type('int')
            return m.Insts(typ, codes)

        elif right.typ.basetype == 'float':
            codes.append(m.Inst(opc.PUSH, -1.0))
            codes.append(m.Inst(opc.MULF, self.nullarg))
            typ = m.Type('float')
            return m.Insts(typ, codes)

        else:
            g.r.addReport(m.Report('fatal', self.tok, f'fatal error in node.Minus'))
            return m.Insts()


class Inv (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        right = self.right.gencode(env, newopt(opt, 1, 'r'))

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

        right = self.right.gencode(env, newopt(opt, 1, 'r'))
        codes = right.bytecodes
        typ = copy(right.typ)

        if typ.isPointer():
            codes.append(m.Inst(opc.INC, env.calcPointeredSize(typ)))
        else:
            codes.append(m.Inst(opc.INC, 1))

        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
        else:
            typ = m.Type()

        codes.extend(self.right.gencode(env, newopt(opt, 0, 'l')).bytecodes)

        return m.Insts(typ, codes)

class Pre_dec (AST):

    def __init__(self, tok, right):
        self.tok = tok
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        right = self.right.gencode(env, newopt(opt, 1, 'r'))
        codes = right.bytecodes
        typ = copy(right.typ)

        if typ.isPointer():
            codes.append(m.Inst(opc.DEC, env.calcPointeredSize(typ)))
        else:
            codes.append(m.Inst(opc.DEC, 1))

        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
        else:
            typ = m.Type()

        codes.extend(self.right.gencode(env, newopt(opt, 0, 'l')).bytecodes)

        return m.Insts(typ, codes)

class Post_inc (AST):

    def __init__(self, tok, left):
        self.tok = tok
        self.left = left

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        left = self.left.gencode(env, newopt(opt, 1, 'r'))
        codes = left.bytecodes
        typ = copy(left.typ)

        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
        else:
            typ = m.Type()

        if typ.isPointer():
            codes.append(m.Inst(opc.INC, env.calcPointeredSize(typ)))
        else:
            codes.append(m.Inst(opc.INC, 1))

        codes.extend(self.left.gencode(env, newopt(opt, 0, 'l')).bytecodes)

        return m.Insts(typ, codes)


class Post_dec (AST):

    def __init__(self, tok, left):
        self.tok = tok
        self.left = left

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result

        left = self.left.gencode(env, newopt(opt, 1, 'r'))
        codes = left.bytecodes
        typ = copy(left.typ)

        if (opt.popc == 1):
            codes.append(m.Inst(opc.DUP, self.nullarg))
        else:
            typ = m.Type()

        if typ.isPointer():
            codes.append(m.Inst(opc.DEC, env.calcPointeredSize(typ)))
        else:
            codes.append(m.Inst(opc.DEC, 1))

        codes.extend(self.left.gencode(env, newopt(opt, 0, 'l')).bytecodes)

        return m.Insts(typ, codes)

class Add (AST):

    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        left = self.left.gencode(env, newopt(opt, 1))
        right = self.right.gencode(env, newopt(opt, 1))

        code = right.bytecodes

#        if (not left.typ.isBasetype()):
#            left.typ = env.getType(left.typ.basetype)
#            print(left.typ)
#
#        if (not right.typ.isBasetype()):
#            right.typ = env.getType(right.typ.basetype)
#            print(right.typ)

        if (left.typ.length > 1 or left.typ.refcount > 0) or (right.typ.length > 1 and right.typ.refcount > 0):
            typ = copy(left.typ)
            if typ.length > 1:
                typ.setLength(1).addRefcount(1)

            try:
                size = env.calcPointeredSize(typ)
            except m.NonPointerException:
                g.r.addReport(m.Report('fatal', self.tok, f"non pointer exception"))
                return m.Insts()

            if size > 1:
                code.append(m.Inst(opc.PUSH, size))
                code.append(m.Inst(opc.MULI, self.nullarg))

            code.extend(left.bytecodes)
            code.append(m.Inst(opc.ADDI, self.nullarg))

        elif (left.typ.basetype  == 'int') and (right.typ.basetype == 'int'):
            code.extend(left.bytecodes)
            code.append(m.Inst(opc.ADDI, self.nullarg))
            typ = m.Type('int')

        elif (left.typ.basetype == 'float') and (right.typ.basetype == 'float'):
            code.extend(left.bytecodes)
            code.append(m.Inst(opc.ADDF, self.nullarg))
            typ = m.Type('float')

        else:
            g.r.addReport(m.Report('fatal', self.tok, f'fatal error in node.Add'))
            return m.Insts()

        return m.Insts(typ, code)


class Sub (AST):

    def __init__(self, tok, left, right):
        self.tok = tok
        self.left = left
        self.right = right

    def gencode(self, env, opt):

        if (result := self.assertOnlyRValue(env, opt)) is not None:
            return result
        if (result := self.assertOnlyPop1(env, opt)) is not None:
            return result

        left = self.left.gencode(env, newopt(opt, 1))
        right = self.right.gencode(env, newopt(opt, 1))

        code = right.bytecodes

        if (left.typ.length > 1 or left.typ.refcount > 0) or (right.typ.length > 1 and right.typ.refcount > 0):
            typ = copy(left.typ)
            if typ.length > 1:
                typ.setLength(1).addRefcount(1)

            try:
                size = env.calcPointeredSize(typ)
            except m.NonPointerException:
                g.r.addReport(m.Report('fatal', self.tok, f"non pointer exception"))
                return m.Insts()

            if size > 1:
                code.append(m.Inst(opc.PUSH, size))
                code.append(m.Inst(opc.MULI, self.nullarg))

            code.extend(left.bytecodes)
            code.append(m.Inst(opc.SUBI, self.nullarg))

        elif (left.typ.basetype  == 'int') and (right.typ.basetype == 'int'):
            code.extend(left.bytecodes)
            code.append(m.Inst(opc.SUBI, self.nullarg))
            typ = m.Type('int')

        elif (left.typ.basetype == 'float') and (right.typ.basetype == 'float'):
            code.extend(left.bytecodes)
            code.append(m.Inst(opc.SUBF, self.nullarg))
            typ = m.Type('float')

        else:
            g.r.addReport(m.Report('fatal', self.tok, f'fatal error in node.Sub'))

        return m.Insts(typ, code)

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
    isCompOP = True

class Lte (BIOP):
    opI = opc.LTEI
    opF = opc.LTEF
    isCompOP = True

class Gt (BIOP):
    opI = opc.GTI
    opF = opc.GTF
    isCompOP = True

class Gte (BIOP):
    opI = opc.GTEI
    opF = opc.GTEF
    isCompOP = True

class Eq (BIOP):
    opI = opc.EQI
    opF = opc.EQF
    isCompOP = True

class Neq (BIOP):
    opI = opc.NEQI
    opF = opc.NEQF
    isCompOP = True

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
                return m.Insts()

            if (result := self.assertOnlyRValue(env, opt)) is not None:
                return result
            if (result := self.assertOnlyPop1(env, opt)) is not None:
                return result

            return m.Insts(m.Type('int'), [m.Inst(opc.PUSH, value)])

        if opt.lr == 'r':
            if (result := self.assertOnlyPop1(env, opt)) is not None:
                return result
            if var.typ.isArray():
                codes = [var.genAddrCode()]
                return m.Insts(copy(var.typ).setLength(1).addRefcount(1), codes) # 配列からポインタにキャスト
            else:
                codes = [var.genLoadCode()]
                return m.Insts(copy(var.typ), codes)
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


