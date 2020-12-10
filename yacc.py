import ply.yacc as yacc
import MODEL as m
import node
from lex import lexer
from tokens import tokens

start = 'program'

precedence = (
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV'),
)

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
    external_definition : TYPE SYMBOL SEMICOLON
    | TYPE SYMBOL arguments block
    | TYPE SYMBOL ASSIGN expr SEMICOLON
    '''
    if (len(p) == 4):
        if p[1] == 'uint':
            p[0] = node.GlobalVar(p[2], m.Types.Uint, node.NumberU(0))
        elif p[1] == 'int':
            p[0] = node.GlobalVar(p[2], m.Types.Int, node.NumberI(0))
        elif p[1] == 'float':
            p[0] = node.GlobalVar(p[2], m.Types.Float, node.NumberF(0))
        else:
            print("yacc-external_definition: Unknown Type!!")

    elif (len(p) == 5):
        p[0] = node.Func(p[2], p[1], p[3], p[4])

    else:
        if p[1] == 'uint':
            p[0] = node.GlobalVar(p[2], m.Types.Uint, p[4])
        elif p[1] == 'int':
            p[0] = node.GlobalVar(p[2], m.Types.Int, p[4])
        elif p[1] == 'float':
            p[0] = node.GlobalVar(p[2], m.Types.Float, p[4])
        else:
            print("yacc-external_definition: Unknown Type!!")


def p_arguments(p):
    '''
    arguments : LPAREN RPAREN
    | LPAREN definition_list RPAREN
    '''
    if (len(p) == 3):
        p[0] = []
    if (len(p) == 4):
        p[0] = p[2]

def p_definition_list(p):
    '''
    definition_list : TYPE SYMBOL
    | definition_list COMMA TYPE SYMBOL
    '''
    if (len(p) == 3):
        p[0] = [[p[1], p[2]]]
    if (len(p) == 5):
        tmp = p[1]
        tmp.append([p[3], p[4]])
        p[0] = tmp

def p_block(p):
    '''
    block : LBRACE statements RBRACE
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
    statement : expr SEMICOLON
    | block
    | local_vars
    | RETURN expr SEMICOLON
    | RETURN SEMICOLON
    | IF LPAREN expr RPAREN statement
    | IF LPAREN expr RPAREN statement ELSE statement
    | WHILE LPAREN expr RPAREN statement
    | FOR LPAREN expr SEMICOLON expr SEMICOLON expr RPAREN statement
    '''
    if (p[1] == 'return'):
        if (len(p) == 3):
            p[0] = node.Return(None)

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
    local_vars : TYPE SYMBOL SEMICOLON
    local_vars : TYPE SYMBOL ASSIGN expr SEMICOLON
    '''
    if (len(p) == 4):
        if p[1] == 'uint':
            p[0] = node.LocalVar(p[2], m.Types.Uint, node.NumberU(0))
        elif p[1] == 'int':
            p[0] = node.LocalVar(p[2], m.Types.Int, node.NumberI(0))
        elif p[1] == 'float':
            p[0] = node.LocalVar(p[2], m.Types.Float, node.NumberF(0))
        else:
            print("yacc-local-vars: Unknown Type!!")
    else:
        if p[1] == 'uint':
            p[0] = node.LocalVar(p[2], m.Types.Uint, p[4])
        elif p[1] == 'int':
            p[0] = node.LocalVar(p[2], m.Types.Int, p[4])
        elif p[1] == 'float':
            p[0] = node.LocalVar(p[2], m.Types.Float, p[4])
        else:
            print("yacc-local-vars: Unknown Type!!")

def p_expr(p):
    '''
    expr : primary_expr
    | LPAREN expr RPAREN
    | SYMBOL ASSIGN expr
    | UNIOP expr
    | expr BIOP expr
    | expr ADD expr
    | expr SUB expr
    | expr MUL expr
    | expr DIV expr
    | expr TERNARY expr COLON expr
    | SIN LPAREN expr RPAREN
    | COS LPAREN expr RPAREN
    | TAN LPAREN expr RPAREN
    | ASIN LPAREN expr RPAREN
    | ACOS LPAREN expr RPAREN
    | ATAN LPAREN expr RPAREN
    | ATAN2 LPAREN expr COMMA expr RPAREN
    | ROOT LPAREN expr COMMA expr RPAREN
    | POW LPAREN expr COMMA expr RPAREN
    | LOG LPAREN expr COMMA expr RPAREN
    | OUTPUT LPAREN string COMMA expr RPAREN
    | WRITEREG LPAREN number COMMA expr RPAREN
    '''
    if (len(p) == 2):
        p[0] = p[1]
    elif (p[1] == '('):
        p[0] = p[2]
    elif (p[1] == 'output'):
        p[0] = node.Output(p[3], p[5])
    elif (p[1] == 'writereg'):
        p[0] = node.Writereg(p[3], p[5])
    elif (p[2] == '='):
        p[0] = node.Assign(p[1], p[3])
    elif (p[2] == '!'):
        p[0] = node.Inv(p[2])
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
    | string
    | SYMBOL LPAREN arg_list RPAREN
    | SYMBOL LPAREN RPAREN
    | INPUT LPAREN string RPAREN
    | READREG LPAREN number RPAREN
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

def p_string(p):
    '''
    string : STRING
    '''
    p[0] = node.String(p[1])

def p_arg_list(p):
    '''
    arg_list : expr
    | arg_list COMMA expr
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_error(p):
    print("Syntax error at '%s'" % p)


def makenode(code):

    parser = yacc.yacc(debug=False, write_tables=False)
    node = yacc.parse(code, lexer=lexer)

    #print(node)

    return node;

if __name__ == '__main__':
    with open('test.c', 'r') as f:
        data = f.read()

    parser = yacc.yacc(debug=True, write_tables=False)
    node = yacc.parse(data, lexer=lexer)

    print(node)


