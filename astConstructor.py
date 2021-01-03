
import glob as g
import MODEL as m
from pycparser import CParser, c_parser, c_ast, parse_file


def projectAST(ast):

    if isinstance(ast, c_ast.ArrayDecl):
        pass
    elif isinstance(ast, c_ast.ArrayRef):
        pass
    elif isinstance(ast, c_ast.Assignment):
        pass
    elif isinstance(ast, c_ast.BinaryOp):
        pass
    elif isinstance(ast, c_ast.Break):
        pass
    elif isinstance(ast, c_ast.Case):
        pass
    elif isinstance(ast, c_ast.Cast):
        pass
    elif isinstance(ast, c_ast.Compound):
        return list(map(projectAST, ast.block_items))
    elif isinstance(ast, c_ast.CompoundLiteral):
        pass
    elif isinstance(ast, c_ast.Constant):
        pass
    elif isinstance(ast, c_ast.Continue):
        pass
    elif isinstance(ast, c_ast.Decl):
        return f"{ast.name} type: {projectAST(ast.type)} ({ast.coord.file}:{ast.coord.line}:{ast.coord.column})"
    elif isinstance(ast, c_ast.DeclList):
        pass
    elif isinstance(ast, c_ast.Default):
        pass
    elif isinstance(ast, c_ast.DoWhile):
        pass
    elif isinstance(ast, c_ast.EllipsisParam):
        pass
    elif isinstance(ast, c_ast.EmptyStatement):
        pass
    elif isinstance(ast, c_ast.Enum):
        pass
    elif isinstance(ast, c_ast.Enumerator):
        pass
    elif isinstance(ast, c_ast.EnumeratorList):
        pass
    elif isinstance(ast, c_ast.ExprList):
        pass
    elif isinstance(ast, c_ast.FileAST):
        return list(map(projectAST, ast.ext))
    elif isinstance(ast, c_ast.For):
        pass
    elif isinstance(ast, c_ast.FuncCall):
        pass
    elif isinstance(ast, c_ast.FuncDecl):
        pass
    elif isinstance(ast, c_ast.FuncDef):
        return projectAST(ast.body)
    elif isinstance(ast, c_ast.Goto):
        pass
    elif isinstance(ast, c_ast.ID):
        pass
    elif isinstance(ast, c_ast.IdentifierType):
        return f"{ast.names}"
    elif isinstance(ast, c_ast.If):
        pass
    elif isinstance(ast, c_ast.InitList):
        pass
    elif isinstance(ast, c_ast.Label):
        pass
    elif isinstance(ast, c_ast.NamedInitializer):
        pass
    elif isinstance(ast, c_ast.ParamList):
        pass
    elif isinstance(ast, c_ast.PtrDecl):
        pass
    elif isinstance(ast, c_ast.Return):
        pass
    elif isinstance(ast, c_ast.Struct):
        pass
    elif isinstance(ast, c_ast.StructRef):
        pass
    elif isinstance(ast, c_ast.Switch):
        pass
    elif isinstance(ast, c_ast.TernaryOp):
        pass
    elif isinstance(ast, c_ast.TypeDecl):
        return f"{ast.declname}, {ast.quals}, {projectAST(ast.type)}"
    elif isinstance(ast, c_ast.Typedef):
        pass
    elif isinstance(ast, c_ast.Typename):
        pass
    elif isinstance(ast, c_ast.UnaryOp):
        pass
    elif isinstance(ast, c_ast.Union):
        pass
    elif isinstance(ast, c_ast.While):
        pass
    elif isinstance(ast, c_ast.Pragma):
        pass
    elif isinstance(ast, c_ast.Raw):
        return(f"{ast}")
    else:
        g.r.addReport(m.Report('fatal', m.TokenInfo(ast.coord.line, ast.coord.column, ast.coord.file), f"{type(ast)} is not listed!"))
        return

    g.r.addReport(m.Report('fatal', m.TokenInfo(ast.coord.line, ast.coord.column, ast.coord.file), f"{type(ast)} is not yet implemented!"))

def makeAST(code):
    try:
        parser = CParser(lex_optimize=False, yacc_optimize=False)
        ast = parser.parse(code, filename='<none>')
    except Exception as e:
        print(e)
        exit()

    return projectAST(ast)



