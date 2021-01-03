import json
import node
import glob as g
import MODEL as m
from pycparser import CParser, c_parser, c_ast, parse_file


def projectAST(ast, scope = 0):

    if (ast is None):
        return None

    elif isinstance(ast, c_ast.ArrayDecl):
        return projectAST(ast.type, scope).setLength(projectAST(ast.dim, scope)) #MEMO dim_quals unused

    elif isinstance(ast, c_ast.ArrayRef): #TODO [name*, subscript*]
        pass
    elif isinstance(ast, c_ast.Assignment): #TODO [op, lvalue*, rvalue*]
        pass
    elif isinstance(ast, c_ast.BinaryOp): #TODO [op, left* right*]
        pass
    elif isinstance(ast, c_ast.Break): #TODO []
        pass
    elif isinstance(ast, c_ast.Case): #TODO [expr*, stmts**]
        pass
    elif isinstance(ast, c_ast.Cast): #TODO [to_type*, expr*]
        pass
    elif isinstance(ast, c_ast.Compound): #TODO [block_items**]
        pass
    elif isinstance(ast, c_ast.CompoundLiteral): #TODO [type*, init*]
        pass
    elif isinstance(ast, c_ast.Constant):
        if (ast.type == 'int'):
            return node.NumberI(a2t(ast), ast.value)
        elif (ast.type == 'float'):
            return node.NumberF(a2t(ast), ast.value)
        g.r.addReport(m.Report('fatal', a2t(ast), f"unsupported constant type {ast.value}"))

    elif isinstance(ast, c_ast.Continue): #TODO []
        pass
    elif isinstance(ast, c_ast.Decl): #TODO [name, quals, storage, funcspec, type*, init*, bitsize*]
        if (ast.name is None):
            if (scope == 0):
                return node.GlobalVar(a2t(ast), ast.name, projectAST(ast.type, scope), projectAST(ast.init))
            else:
                return node.LocalVar(a2t(ast), ast.name, projectAST(ast.type, scope), ast.init)
        else:
            return projectAST(ast.type, scope)

    elif isinstance(ast, c_ast.DeclList): #TODO [decls**]
        pass
    elif isinstance(ast, c_ast.Default): #TODO [stmts**]
        pass
    elif isinstance(ast, c_ast.DoWhile): #TODO [cond*, stmt*]
        pass
    elif isinstance(ast, c_ast.EllipsisParam): #TODO []
        pass
    elif isinstance(ast, c_ast.EmptyStatement): #TODO []
        pass
    elif isinstance(ast, c_ast.Enum): #TODO [name, values*]
        pass
    elif isinstance(ast, c_ast.Enumerator): #TODO [name, value*]
        pass
    elif isinstance(ast, c_ast.EnumeratorList): #TODO [enumerators**]
        pass
    elif isinstance(ast, c_ast.ExprList): #TODO [exprs**]
        pass
    elif isinstance(ast, c_ast.FileAST):
        return node.Program(a2t(ast), [projectAST(e, scope) for e in ast.ext])

    elif isinstance(ast, c_ast.For): #TODO [init*, cond*, next*, stmt*]
        pass
    elif isinstance(ast, c_ast.FuncCall): #TODO [name*, args*]
        pass
    elif isinstance(ast, c_ast.FuncDecl): #TODO [args*, type*]
        return {"args": projectAST(ast.args, scope), "type": projectAST(ast.type, scope)}

    elif isinstance(ast, c_ast.FuncDef): #TODO [args*, type*]
        decl = projectAST(ast.decl, scope)
        return node.Func(a2t(ast), decl['type'].name, decl['type'], decl['args'], projectAST(ast.body, scope))

    elif isinstance(ast, c_ast.Goto): #TODO [name]
        pass
    elif isinstance(ast, c_ast.ID): #TODO [name]
        pass
    elif isinstance(ast, c_ast.IdentifierType):
        if len(ast.names) == 1:
            return  m.Type(ast.names[0])
        g.r.addReport(m.Report('fatal', a2t(ast), f"program error while processing IdentifierType"))

    elif isinstance(ast, c_ast.If): #TODO [cond*, iftrue*, iffalse*]
        pass
    elif isinstance(ast, c_ast.InitList): #TODO [exprs**]
        pass
    elif isinstance(ast, c_ast.Label): #TODO [name, stmt*]
        pass
    elif isinstance(ast, c_ast.NamedInitializer): #TODO [name**, expr*]
        pass
    elif isinstance(ast, c_ast.ParamList): #TODO [params**]
        pass
    elif isinstance(ast, c_ast.PtrDecl):
        return projectAST(ast.type, scope).addQuals(ast.quals).addRefcount(1)

    elif isinstance(ast, c_ast.Raw): #TODO [type*, opc, arg, exprs**]
        pass
    elif isinstance(ast, c_ast.Return): #TODO [expr*]
        pass
    elif isinstance(ast, c_ast.Struct):
        return node.Struct(a2t(ast), ast.name, [projectAST(e, scope) for e in ast.decls])

    elif isinstance(ast, c_ast.StructRef): #TODO [name*, type, filed*]
        pass
    elif isinstance(ast, c_ast.Switch): #TODO [cond*, stmt*]
        pass
    elif isinstance(ast, c_ast.TernaryOp): #TODO [cond*, ifture*, iffalse*]
        pass
    elif isinstance(ast, c_ast.TypeDecl):
        return projectAST(ast.type, scope).addQuals(ast.quals).setName(ast.declname)

    elif isinstance(ast, c_ast.Typedef): #TODO [name, equals, storage, type*]
        pass
    elif isinstance(ast, c_ast.Typename): #TODO [name, quals, type*]
        pass
    elif isinstance(ast, c_ast.UnaryOp): #TODO [op, expr*]
        pass
    elif isinstance(ast, c_ast.Union): #TODO [name, decls**]
        pass
    elif isinstance(ast, c_ast.While): #TODO [cond*, stmt*]
        pass
    elif isinstance(ast, c_ast.Pragma): #TODO [string]
        pass
    else:
        g.r.addReport(m.Report('fatal', a2t(ast), f"{type(ast)} is not listed!"))
        return

    g.r.addReport(m.Report('fatal', a2t(ast), f"{type(ast)} is not yet implemented!"))

def a2t(ast):
    if (ast is not None and ast.coord is not None):
        return m.TokenInfo(ast.coord.line, ast.coord.column, ast.coord.file)
    else:
        return m.TokenInfo(0, 0, '<ERROR>')


def makeAST(code):
    try:
        parser = CParser(lex_optimize=False, yacc_optimize=False)
        ast = parser.parse(code, filename='<none>')
    except Exception as e:
        print(e)
        exit()

    ast.show()

    node = projectAST(ast)

    print(json.dumps(node, default=lambda x: {x.__class__.__name__: x.__dict__}, indent=2))

    return node



