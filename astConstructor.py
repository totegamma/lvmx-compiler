
import glob as g
import MODEL as m
from pycparser import CParser, c_parser, c_ast, parse_file


def projectAST(ast):

    if isinstance(ast, c_ast.ArrayDecl): #TODO
        pass
    elif isinstance(ast, c_ast.ArrayRef): #TODO
        pass
    elif isinstance(ast, c_ast.Assignment): #TODO
        pass
    elif isinstance(ast, c_ast.BinaryOp): #TODO
        pass
    elif isinstance(ast, c_ast.Break): #TODO
        pass
    elif isinstance(ast, c_ast.Case): #TODO
        pass
    elif isinstance(ast, c_ast.Cast): #TODO
        pass
    elif isinstance(ast, c_ast.Compound): #TODO
        return list(map(projectAST, ast.block_items))
    elif isinstance(ast, c_ast.CompoundLiteral): #TODO
        pass
    elif isinstance(ast, c_ast.Constant): #TODO
        pass
    elif isinstance(ast, c_ast.Continue): #TODO
        pass
    elif isinstance(ast, c_ast.Decl): #TODO
        return f"{ast.name} type: {projectAST(ast.type)} ({ast.coord.file}:{ast.coord.line}:{ast.coord.column})"
    elif isinstance(ast, c_ast.DeclList): #TODO
        pass
    elif isinstance(ast, c_ast.Default): #TODO
        pass
    elif isinstance(ast, c_ast.DoWhile): #TODO
        pass
    elif isinstance(ast, c_ast.EllipsisParam): #TODO
        pass
    elif isinstance(ast, c_ast.EmptyStatement): #TODO
        pass
    elif isinstance(ast, c_ast.Enum): #TODO
        pass
    elif isinstance(ast, c_ast.Enumerator): #TODO
        pass
    elif isinstance(ast, c_ast.EnumeratorList): #TODO
        pass
    elif isinstance(ast, c_ast.ExprList): #TODO
        pass
    elif isinstance(ast, c_ast.FileAST): #TODO
        return list(map(projectAST, ast.ext))
    elif isinstance(ast, c_ast.For): #TODO
        pass
    elif isinstance(ast, c_ast.FuncCall): #TODO
        pass
    elif isinstance(ast, c_ast.FuncDecl): #TODO
        pass
    elif isinstance(ast, c_ast.FuncDef): #TODO
        return projectAST(ast.body)
    elif isinstance(ast, c_ast.Goto): #TODO
        pass
    elif isinstance(ast, c_ast.ID): #TODO
        pass
    elif isinstance(ast, c_ast.IdentifierType): #TODO
        return f"{ast.names}"
    elif isinstance(ast, c_ast.If): #TODO
        pass
    elif isinstance(ast, c_ast.InitList): #TODO
        pass
    elif isinstance(ast, c_ast.Label): #TODO
        pass
    elif isinstance(ast, c_ast.NamedInitializer): #TODO
        pass
    elif isinstance(ast, c_ast.ParamList): #TODO
        pass
    elif isinstance(ast, c_ast.PtrDecl): #TODO
        pass
    elif isinstance(ast, c_ast.Return): #TODO
        pass
    elif isinstance(ast, c_ast.Struct): #TODO
        pass
    elif isinstance(ast, c_ast.StructRef): #TODO
        pass
    elif isinstance(ast, c_ast.Switch): #TODO
        pass
    elif isinstance(ast, c_ast.TernaryOp): #TODO
        pass
    elif isinstance(ast, c_ast.TypeDecl): #TODO
        return f"{ast.declname}, {ast.quals}, {projectAST(ast.type)}"
    elif isinstance(ast, c_ast.Typedef): #TODO
        pass
    elif isinstance(ast, c_ast.Typename): #TODO
        pass
    elif isinstance(ast, c_ast.UnaryOp): #TODO
        pass
    elif isinstance(ast, c_ast.Union): #TODO
        pass
    elif isinstance(ast, c_ast.While): #TODO
        pass
    elif isinstance(ast, c_ast.Pragma): #TODO
        pass
    elif isinstance(ast, c_ast.Raw): #TODO
        return(f"{ast}")
    else:
        g.r.addReport(m.Report('fatal', a2t(ast), f"{type(ast)} is not listed!"))
        return

    g.r.addReport(m.Report('fatal', a2t(ast), f"{type(ast)} is not yet implemented!"))

def a2t(ast):
    return m.TokenInfo(ast.coord.line, ast.coord.column, ast.coord.file)

def makeAST(code):
    try:
        parser = CParser(lex_optimize=False, yacc_optimize=False)
        ast = parser.parse(code, filename='<none>')
    except Exception as e:
        print(e)
        exit()

    return projectAST(ast)



