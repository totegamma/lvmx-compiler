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
    ('right', 'CAST')
)


def p_basetype(p):
    '''
    basetype : BASETYPE
    '''
    if p[1] == 'uint':
        p[0] = m.BT.Uint
    elif p[1] == 'int':
        p[0] = m.BT.Int
    elif p[1] == 'float':
        p[0] = m.BT.Float
    elif p[1] == 'void':
        p[0] = m.BT.Void
    elif p[1] == 'any':
        p[0] = m.BT.Any
    else:
        glob.yaccerrors += f"Parse Type Failed ({typestring=})" + "\n"

def p_type(p):
    '''
    type : basetype
         | basetype pointer
         | STRUCT SYMBOL
         | STRUCT SYMBOL pointer
    '''
    if (p[1] == 'struct'):
        if (len(p) == 3):
            p[0] = m.Types(p[2], 0)
        else:
            p[0] = m.Types(p[2], p[3])
    else:
        if (len(p) == 2):
            p[0] = m.Types(p[1], 0)
        else:
            p[0] = m.Types(p[1], p[2])

def p_program(p):
    '''
    program : external_definitions
    '''
    p[0] = node.Program(genTokenInfo(p, 1), p[1])

def p_external_definitions(p):
    '''
    external_definitions : external_definition
    | external_definitions external_definition
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_struct_def(p):
    '''
    struct_def : STRUCT SYMBOL '{' struct_member_list '}' ';'
    '''
    p[0] = node.Struct(genTokenInfo(p, 1), p[2], p[4])

def p_struct_member_list(p):
    '''
    struct_member_list : type SYMBOL ';'
                       | struct_member_list type SYMBOL ';'
    '''
    if (len(p) == 4):
        p[0] = [m.Symbol(p[2], p[1])]
    if (len(p) == 5):
        tmp = p[1]
        tmp.append(m.Symbol(p[3], p[2]))
        p[0] = tmp


def p_global_array(p):
    '''
    global_array : type SYMBOL '[' expr ']' ';'
                 | type SYMBOL '[' expr ']' '=' initializer ';'
                 | type SYMBOL '[' ']' '=' initializer ';'
    '''
    if (len(p) == 7):
        p[0] = node.GlobalVar(genTokenInfo(p, 1), p[2], p[1].convertToArray(p[4]), None)
    elif (len(p) == 9):
        p[0] = node.GlobalVar(genTokenInfo(p, 1), p[2], p[1].convertToArray(p[4]), p[7])
    else:
        p[0] = node.GlobalVar(genTokenInfo(p, 1), p[2], p[1].convertToArray(None), p[6])


def p_external_definition(p):
    '''
    external_definition : function_def
                        | struct_def
                        | global_array
                        | type SYMBOL ';'
                        | type SYMBOL '=' expr ';'
    '''
    if (len(p) == 4):
        p[0] = node.GlobalVar(genTokenInfo(p, 1), p[2], p[1])

    elif (len(p) == 6):
        p[0] = node.GlobalVar(genTokenInfo(p, 1), p[2], p[1], p[4])

    else:
        p[0] = p[1]



def p_function_def(p):
    '''
    function_def : type SYMBOL arguments block
    '''
    p[0] = node.Func(genTokenInfo(p, 1), p[2], p[1], p[3], p[4])


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
    definition_list : type SYMBOL
                    | definition_list ',' type SYMBOL
    '''
    if (len(p) == 3):
        p[0] = [m.Symbol(p[2], p[1])]
    if (len(p) == 5):
        tmp = p[1]
        tmp.append(m.Symbol(p[4], p[3]))
        p[0] = tmp

def p_block(p):
    '''
    block : '{' statements '}'
    '''
    p[0] = node.Block(genTokenInfo(p, 1), p[2])

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
            p[0] = node.Return(genTokenInfo(p, 1), node.NumberI(0))

        else:
            p[0] = node.Return(genTokenInfo(p, 1), p[2])

    elif (p[1] == 'if'):
        if (len(p) == 6):
            p[0] = node.If(genTokenInfo(p, 1), p[3], p[5])

        else:
            p[0] = node.Ifelse(genTokenInfo(p, 1), p[3], p[5], p[7])

    elif (p[1] == 'while'):
        p[0] = node.While(genTokenInfo(p, 1), p[3], p[5])

    elif (p[1] == 'for'):
        p[0] = node.For(genTokenInfo(p, 1), p[3], p[5], p[7], p[9])

    else:
        p[0] = p[1];

def p_initializer(p):
    '''
    initializer : STRING
                | '{' initializer_list '}'
    '''
    if (len(p) == 2):
        li = list(map(lambda a : node.NumberI(genTokenInfo(p, 1), int.from_bytes(a.encode('utf-32be'), byteorder='big')), p[1]))
        li.append(node.NumberI(genTokenInfo(p, 1), 0))
        p[0] = li
    else:
        p[0] = p[2]

def p_initializer_list(p):
    '''
    initializer_list : expr
                     | initializer_list ',' expr
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        buf = p[1]
        buf.append(p[3])
        p[0] = buf

def p_local_array(p):
    '''
    local_array : type SYMBOL '[' expr ']' ';'
                | type SYMBOL '[' expr ']' '=' initializer ';'
                | type SYMBOL '[' ']' '=' initializer ';'
    '''
    if (len(p) == 7):
        p[0] = node.LocalVar(genTokenInfo(p, 1), p[2], p[1].convertToArray(p[4]), None)
    elif (len(p) == 9):
        p[0] = node.LocalVar(genTokenInfo(p, 1), p[2], p[1].convertToArray(p[4]), p[7])
    else:
        p[0] = node.LocalVar(genTokenInfo(p, 1), p[2], p[1].convertToArray(None), p[6])

def p_local_vars(p):
    '''
    local_vars : local_array
               | type SYMBOL ';'
               | type SYMBOL '=' expr ';'
    '''
    if (len(p) == 4):
        p[0] = node.LocalVar(genTokenInfo(p, 1), p[2], p[1])

    elif (len(p) == 6):
        p[0] = node.LocalVar(genTokenInfo(p, 1), p[2], p[1], p[4])

    else:
        p[0] = p[1]

def p_pointer(p):
    '''
    pointer : '*'
            | '*' pointer
    '''
    if (len(p) == 2):
        p[0] = 1
    else:
        p[0] = p[2] + 1


def p_expr_csl(p):
    '''
    expr_csl : expr
             | expr_csl ',' expr
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        tmp = p[1]
        tmp.append(p[3])
        p[0] = tmp

def p_op(p):
    '''
    raw : RAW '(' type ',' STRING ',' expr ')'
        | RAW '(' type ',' STRING ',' expr ',' expr_csl ')'
    '''
    if (len(p) == 9):
        p[0] = node.Raw(genTokenInfo(p, 1), p[3], p[5], p[7], [])
    else:
        p[0] = node.Raw(genTokenInfo(p, 1), p[3], p[5], p[7], p[9])

def p_expr(p):
    '''
    expr : primary_expr
         | cast
         | raw
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
         | expr '.' SYMBOL
         | expr '?' expr ':' expr
    '''
    if (len(p) == 2):
        p[0] = p[1]
    elif (p[1] == '('):
        p[0] = p[2]
    elif (p[1] == '&'):
        p[0] = node.Address(genTokenInfo(p, 1), p[2])
    elif (p[1] == '*'):
        p[0] = node.Indirect(genTokenInfo(p, 1), p[2])
    elif (p[2] == '['):
        p[0] = node.Indirect(genTokenInfo(p, 2), node.Add(genTokenInfo(p, 2), p[1], p[3]))
    elif (p[2] == '.'):
        p[0] = node.Indirect(genTokenInfo(p, 2), node.FieldAccess(genTokenInfo(p, 2), p[1], p[3]))
    elif (p[2] == '!'):
        p[0] = node.Inv(genTokenInfo(p, 2), p[2])
    elif (p[2] == '='):
        p[0] = node.Assign(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '+'):
        p[0] = node.Add(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '-'):
        p[0] = node.Sub(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '*'):
        p[0] = node.Mul(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '/'):
        p[0] = node.Div(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '<'):
        p[0] = node.Lt(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '<='):
        p[0] = node.Lte(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '>'):
        p[0] = node.Gt(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '>='):
        p[0] = node.Gte(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '=='):
        p[0] = node.Eq(genTokenInfo(p, 2), p[1], p[3])
    elif (p[2] == '!='):
        p[0] = node.Neq(genTokenInfo(p, 2), p[1], p[3])
    elif (p[1] == '++'):
        p[0] = node.Inc(genTokenInfo(p, 2), p[2])
    elif (p[1] == '--'):
        p[0] = node.Dec(genTokenInfo(p, 2), p[2])
    elif (p[2] == '?'):
        p[0] = node.Ternary(genTokenInfo(p, 2), p[1], p[3], p[5])
    elif (p[1] == '__op'):
        p[0] = node.Eval(genTokenInfo(p, 1), p[3], p[5])
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
    '''
    if (len(p) == 2):
        p[0] = p[1]
    else:
        if (len(p) == 4):
            p[0] = node.Funccall(genTokenInfo(p, 1), p[1], [])
        else:
            p[0] = node.Funccall(genTokenInfo(p, 1), p[1], p[3])

def p_cast(p):
    '''
    cast : '(' type ')' expr %prec CAST
    '''
    p[0] = node.Cast(genTokenInfo(p, 1), p[2], p[4])

def p_symbol(p):
    '''
    symbol : SYMBOL
    '''
    p[0] = node.Symbol(genTokenInfo(p, 1), p[1])


def p_numberi(p):
    '''
    number : NUMBERI
    '''
    p[0] = node.NumberI(genTokenInfo(p, 1), p[1])

def p_numberf(p):
    '''
    number : NUMBERF
    '''
    p[0] = node.NumberF(genTokenInfo(p, 1), p[1])

def p_numberu(p):
    '''
    number : NUMBERU
    '''
    p[0] = node.NumberU(genTokenInfo(p, 1), p[1])

def p_char(p):
    '''
    char : CHAR
    '''
    p[1] = p[1].replace(r'\n', '\n') #TODO 無茶な置換をなんとかしたい
    if (len(p[1]) == 1):
        p[0] = node.NumberI(genTokenInfo(p, 1), int.from_bytes(p[1].encode('utf-32be'), byteorder='big'))
    else:
        glob.yaccerrors += f"charは一文字でなければなりません (入力文字: '{p[1]}')" + "\n"


def p_string(p):
    '''
    string : STRING
    '''
    p[0] = node.String(genTokenInfo(p, 1), p[1].replace(r'\n', '\n'))

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


def genTokenInfo(p, index):
    global target
    line_start = target.rfind('\n', 0, p.lexpos(index)) + 1
    colno = (p.lexpos(index) - line_start) + 1

    return m.TokenInfo(p.lineno(index), colno)


def makeAST(code):
    global target
    target = code

    parser = yacc.yacc(debug=False, write_tables=False)
    node = yacc.parse(code, lexer=lexer)

    return node;

if __name__ == '__main__':

    global target

    with open('test.c', 'r') as f:
        data = f.read()

    glob.init()

    target = data

    parser = yacc.yacc(debug=True, write_tables=False)
    node = yacc.parse(data, lexer=lexer)

    print(glob.lexerrors)
    print(glob.yaccerrors)

    print(json.dumps(node, default=lambda x: {x.__class__.__name__: x.__dict__}))


