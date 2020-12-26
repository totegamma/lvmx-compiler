import json
import node
import glob
import MODEL as m
import ply.yacc as yacc
from lex import lexer
from tokens import tokens

start = 'program'

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
)

def parseType(typestring):
    if typestring == 'uint':
        return m.Types(m.BT.Uint)
    elif typestring == 'int':
        return m.Types(m.BT.Int)
    elif typestring == 'float':
        return m.Types(m.BT.Float)
    else:
        glob.yaccerrors += f"Parse Type Failed ({typestring=})" + "\n"

def p_program(p):
    '''
    program : external_definitions
    '''
    p[0] = node.Program(p[1])

def p_external_definitions(p):
    '''
    external_definitions : external_definition
    | external_definitions external_definition
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_external_definition(p):
    '''
    external_definition : TYPE SYMBOL ';'
    | TYPE SYMBOL arguments block
    | TYPE SYMBOL '=' expr ';'
    '''
    if (len(p) == 4):
        if p[1] == 'uint':
            p[0] = node.GlobalVar(p[2], m.Types(m.BT.Uint), node.NumberU(0))
        elif p[1] == 'int':
            p[0] = node.GlobalVar(p[2], m.Types(m.BT.Int), node.NumberI(0))
        elif p[1] == 'float':
            p[0] = node.GlobalVar(p[2], m.Types(m.BT.Float), node.NumberF(0))
        else:
            glob.yaccerrors += f"yacc-external_definition: Unknown Type!!" + "\n"

    elif (len(p) == 5):
        p[0] = node.Func(p[2], p[1], p[3], p[4])

    else:
        if p[1] == 'uint':
            p[0] = node.GlobalVar(p[2], m.Types(m.BT.Uint), p[4])
        elif p[1] == 'int':
            p[0] = node.GlobalVar(p[2], m.Types(m.BT.Int), p[4])
        elif p[1] == 'float':
            p[0] = node.GlobalVar(p[2], m.Types(m.BT.Float), p[4])
        else:
            glob.yaccerrors += f"yacc-external_definition: Unknown Type!!" + "\n"


def p_arguments(p):
    '''
    arguments : '(' ')'
    | '(' definition_list ')'
    '''
    if (len(p) == 3):
        p[0] = []
    if (len(p) == 4):
        p[0] = p[2]

def p_definition_list(p):
    '''
    definition_list : TYPE SYMBOL
    | definition_list ',' TYPE SYMBOL
    '''
    if (len(p) == 3):
        p[0] = [m.Symbol(p[2], parseType(p[1]))]
    if (len(p) == 5):
        tmp = p[1]
        tmp.append(m.Symbol(p[4], parseType(p[3])))
        p[0] = tmp

def p_block(p):
    '''
    block : '{' statements '}'
    '''
    p[0] = node.Block(p[2])

def p_statements(p):
    '''
    statements : statement
    | statements statement
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''
    statement : expr ';'
    | block
    | local_vars
    | RETURN expr ';'
    | RETURN ';'
    | IF '(' expr ')' statement
    | IF '(' expr ')' statement ELSE statement
    | WHILE '(' expr ')' statement
    | FOR '(' expr ';' expr ';' expr ')' statement
    '''
    if (p[1] == 'return'):
        if (len(p) == 3):
            p[0] = node.Return(node.NumberU(0))

        else:
            p[0] = node.Return(p[2])

    elif (p[1] == 'if'):
        if (len(p) == 6):
            p[0] = node.If(p[3], p[5])

        else:
            p[0] = node.Ifelse(p[3], p[5], p[7])

    elif (p[1] == 'while'):
        p[0] = node.While(p[3], p[5])

    elif (p[1] == 'for'):
        p[0] = node.For(p[3], p[5], p[7], p[9])

    else:
        p[0] = p[1];

def p_local_vars(p):
    '''
    local_vars : TYPE SYMBOL ';'
               | TYPE SYMBOL '=' expr ';'
               | TYPE pointer SYMBOL ';'
               | TYPE pointer SYMBOL '=' expr ';'
    '''
    if (len(p) == 4):
        if p[1] == 'uint':
            p[0] = node.LocalVar(p[2], m.Types(m.BT.Uint, 0), node.NumberU(0))
        elif p[1] == 'int':
            p[0] = node.LocalVar(p[2], m.Types(m.BT.Int, 0), node.NumberI(0))
        elif p[1] == 'float':
            p[0] = node.LocalVar(p[2], m.Types(m.BT.Float, 0), node.NumberF(0))
        else:
            glob.yaccerrors += f"yacc-local-vars: Unknown Type!!" + "\n"
    elif (len(p) == 6):
        if p[1] == 'uint':
            p[0] = node.LocalVar(p[2], m.Types(m.BT.Uint, 0), p[4])
        elif p[1] == 'int':
            p[0] = node.LocalVar(p[2], m.Types(m.BT.Int, 0), p[4])
        elif p[1] == 'float':
            p[0] = node.LocalVar(p[2], m.Types(m.BT.Float, 0), p[4])
        else:
            glob.yaccerrors += f"yacc-local-vars: Unknown Type!!" + "\n"
    elif (len(p) == 5):
        if p[1] == 'uint':
            p[0] = node.LocalVar(p[3], m.Types(m.BT.Uint, 0), node.NumberU(0))
        elif p[1] == 'int':
            p[0] = node.LocalVar(p[3], m.Types(m.BT.Int, 0), node.NumberI(0))
        elif p[1] == 'float':
            p[0] = node.LocalVar(p[3], m.Types(m.BT.Float, 0), node.NumberF(0))
        else:
            glob.yaccerrors += f"yacc-local-vars: Unknown Type!!" + "\n"
    elif (len(p) == 7):
        if p[1] == 'uint':
            p[0] = node.LocalVar(p[3], m.Types(m.BT.Uint, 0), p[5])
        elif p[1] == 'int':
            p[0] = node.LocalVar(p[3], m.Types(m.BT.Int, 0), p[5])
        elif p[1] == 'float':
            p[0] = node.LocalVar(p[3], m.Types(m.BT.Float, 0), p[5])
        else:
            glob.yaccerrors += f"yacc-local-vars: Unknown Type!!" + "\n"

def p_pointer(p):
    '''
    pointer : '*'
            | '*' pointer
    '''
    if (len(p) == 2):
        p[0] = 1
    else:
        p[0] = p[2] + 1


def p_expr(p):
    '''
    expr : primary_expr
         | '(' expr ')' 
         | UNIOP SYMBOL
         | '&' SYMBOL
         | '*' expr
         | expr BIOP expr
         | expr '=' expr
         | expr '+' expr
         | expr '-' expr
         | expr '*' expr
         | expr '/' expr
         | expr '[' expr ']'
         | expr '?' expr ':' expr
         | SIN '(' expr ')'
         | COS '(' expr ')'
         | TAN '(' expr ')'
         | ASIN '(' expr ')'
         | ACOS '(' expr ')'
         | ATAN '(' expr ')'
         | ATAN2 '(' expr ',' expr ')'
         | ROOT '(' expr ',' expr ')'
         | POW '(' expr ',' expr ')'
         | LOG '(' expr ',' expr ')'
         | OUTPUT '(' string ',' expr ')'
         | WRITEREG '(' expr ',' expr ')'
    '''
    if (len(p) == 2):
        p[0] = p[1]
    elif (p[1] == '('):
        p[0] = p[2]
    elif (p[1] == '&'):
        p[0] = node.Address(p[2])
    elif (p[1] == '*'):
        p[0] = node.Indirect(p[2])
    elif (p[1] == 'output'):
        p[0] = node.Output(p[3], p[5])
    elif (p[1] == 'writereg'):
        p[0] = node.Writereg(p[3], p[5])
    elif (p[2] == '['):
        p[0] = node.Indirect(node.Add(p[1], p[3]))
    elif (p[2] == '!'):
        p[0] = node.Inv(p[2])
    elif (p[2] == '='):
        p[0] = node.Assign(p[1], p[3])
    elif (p[2] == '+'):
        p[0] = node.Add(p[1], p[3])
    elif (p[2] == '-'):
        p[0] = node.Sub(p[1], p[3])
    elif (p[2] == '*'):
        p[0] = node.Mul(p[1], p[3])
    elif (p[2] == '/'):
        p[0] = node.Div(p[1], p[3])
    elif (p[2] == '<'):
        p[0] = node.Lt(p[1], p[3])
    elif (p[2] == '<='):
        p[0] = node.Lte(p[1], p[3])
    elif (p[2] == '>'):
        p[0] = node.Gt(p[1], p[3])
    elif (p[2] == '>='):
        p[0] = node.Gte(p[1], p[3])
    elif (p[2] == '=='):
        p[0] = node.Eq(p[1], p[3])
    elif (p[2] == '!='):
        p[0] = node.Neq(p[1], p[3])
    elif (p[1] == '++'):
        p[0] = node.Inc(p[2])
    elif (p[1] == '--'):
        p[0] = node.Dec(p[2])
    elif (p[2] == '?'):
        p[0] = node.Ternary(p[1], p[3], p[5])
    elif (p[1] == 'sin'):
        p[0] = node.Sin(p[3])
    elif (p[1] == 'cos'):
        p[0] = node.Cos(p[3])
    elif (p[1] == 'tan'):
        p[0] = node.Tan(p[3])
    elif (p[1] == 'asin'):
        p[0] = node.Asin(p[3])
    elif (p[1] == 'acos'):
        p[0] = node.Acos(p[3])
    elif (p[1] == 'atan'):
        p[0] = node.Atan(p[3])
    elif (p[1] == 'atan2'):
        p[0] = node.Atan2(p[3], p[5])
    elif (p[1] == 'root'):
        p[0] = node.Root(p[3], p[5])
    elif (p[1] == 'pow'):
        p[0] = node.Pow(p[3], p[5])
    elif (p[1] == 'log'):
        p[0] = node.Log(p[3], p[5])
    else:
        p[0] = p[1]

def p_primary_expr(p):
    '''
    primary_expr : symbol
    | number
    | char
    | string
    | SYMBOL '(' arg_list ')'
    | SYMBOL '(' ')'
    | INPUT '(' string ')'
    | READREG '(' expr ')'
    '''
    if (len(p) == 2):
        p[0] = p[1]
    elif (p[1] == "input"):
        p[0] = node.Input(p[3])
    elif (p[1] == "readreg"):
        p[0] = node.Readreg(p[3])
    else:
        if (len(p) == 4):
            p[0] = node.Funccall(p[1], [])
        else:
            p[0] = node.Funccall(p[1], p[3])

def p_symbol(p):
    '''
    symbol : SYMBOL
    '''
    p[0] = node.Symbol(p[1])


def p_numberi(p):
    '''
    number : NUMBERI
    '''
    p[0] = node.NumberI(p[1])

def p_numberf(p):
    '''
    number : NUMBERF
    '''
    p[0] = node.NumberF(p[1])

def p_numberu(p):
    '''
    number : NUMBERU
    '''
    p[0] = node.NumberU(p[1])

def p_char(p):
    '''
    char : CHAR
    '''
    p[1] = p[1].replace(r'\n', '\n') #TODO 無茶な置換をなんとかしたい
    if (len(p[1]) == 1):
        p[0] = node.NumberU(int.from_bytes(p[1].encode('utf-32be'), byteorder='big'))
    else:
        glob.yaccerrors += f"charは一文字でなければなりません (入力文字: '{p[1]}')" + "\n"


def p_string(p):
    '''
    string : STRING
    '''
    p[0] = node.String(p[1])

def p_arg_list(p):
    '''
    arg_list : expr
    | arg_list ',' expr
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_error(p):
    glob.yaccerrors += f"line: {p.lineno}. Syntax error at or near '{p.value}'"


def makeAST(code):

    parser = yacc.yacc(debug=False, write_tables=False)
    node = yacc.parse(code, lexer=lexer)

    return node;

if __name__ == '__main__':
    with open('test.c', 'r') as f:
        data = f.read()

    glob.init()

    parser = yacc.yacc(debug=True, write_tables=False)
    node = yacc.parse(data, lexer=lexer)

    print(glob.lexerrors)
    print(glob.yaccerrors)

    print(json.dumps(node, default=lambda x: {x.__class__.__name__: x.__dict__}))


