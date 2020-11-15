import ply.yacc as yacc
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
    p[0] = ['program', p[1]]

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
    external_definition : VAR SYMBOL SEMICOLON
    | FUNC SYMBOL parameter_list block
    | VAR SYMBOL ASSIGN expr SEMICOLON
    '''
    if (len(p) == 4):
        #p[0] = "define var"
        p[0] = ["globalvar", p[2], ['number', 0]]
    elif (len(p) == 5):
        p[0] = ["func", p[2], p[3], p[4]]
    else:
        p[0] = ["globalvar", p[2], p[4]]

def p_parameter_list(p):
    '''
    parameter_list : LPAREN RPAREN
    | LPAREN symbol_list RPAREN
    '''
    if (len(p) == 3):
        p[0] = []
    if (len(p) == 4):
        p[0] = p[2]

def p_symbol_list(p):
    '''
    symbol_list : SYMBOL
    | symbol_list COMMA SYMBOL
    '''
    if (len(p) == 2):
        p[0] = [p[1]]
    if (len(p) == 4):
        p[0] = p[1] + [p[3]]

def p_block(p):
    '''
    block : LBRACE statements RBRACE
    '''
    p[0] = ['block', p[2]]

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
            p[0] = ['return', None]
        else:
            p[0] = ['return', p[2]]
    elif (p[1] == 'if'):
        if (len(p) == 6):
            p[0] = ['if', p[3], p[5]]
        else:
            p[0] = ['ifelse', p[3], p[5], p[7]]
    elif (p[1] == 'while'):
        p[0] = ['while', p[3], p[5]]
    elif (p[1] == 'for'):
        p[0] = ['for', p[3], p[5], p[7], p[9]]
    else:
        p[0] = p[1];

def p_local_vars(p):
    '''
    local_vars : VAR SYMBOL SEMICOLON
    local_vars : VAR SYMBOL ASSIGN expr SEMICOLON
    '''
    if (len(p) == 4):
        p[0] = ["localvar", p[2], ['number', 0]]
    else:
        p[0] = ["localvar", p[2], p[4]]

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
    | OUTPUT LPAREN string COMMA expr RPAREN
    | WRITEREG LPAREN number COMMA expr RPAREN
    '''
    if (len(p) == 2):
        p[0] = p[1]
    elif (p[1] == '('):
        p[0] = p[2]
    elif (p[1] == 'output'):
        p[0] = ['output', p[3], p[5]]
    elif (p[1] == 'writereg'):
        p[0] = ['writereg', p[3], p[5]]
    elif (p[2] == '='):
        p[0] = ['assign', p[1], p[3]]
    elif (p[2] == '!'):
        p[0] = ['inv', p[2]]
    elif (p[2] == '+'):
        p[0] = ['add', p[1], p[3]]
    elif (p[2] == '-'):
        p[0] = ['sub', p[1], p[3]]
    elif (p[2] == '*'):
        p[0] = ['mul', p[1], p[3]]
    elif (p[2] == '/'):
        p[0] = ['div', p[1], p[3]]
    elif (p[2] == '<'):
        p[0] = ['lt', p[1], p[3]]
    elif (p[2] == '<='):
        p[0] = ['lte', p[1], p[3]]
    elif (p[2] == '>'):
        p[0] = ['gt', p[1], p[3]]
    elif (p[2] == '>='):
        p[0] = ['gte', p[1], p[3]]
    elif (p[2] == '=='):
        p[0] = ['eq', p[1], p[3]]
    elif (p[2] == '!='):
        p[0] = ['neq', p[1], p[3]]
    elif (p[1] == '++'):
        p[0] = ['inc', p[2]]
    elif (p[1] == '--'):
        p[0] = ['dec', p[2]]
    elif (p[2] == '?'):
        p[0] = ['ternary', p[1], p[3], p[5]]
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
        p[0] = ['input', p[3]]
    elif (p[1] == "readreg"):
        p[0] = ['readreg', [3]]
    else:
        if (len(p) == 4):
            p[0] = ['funccall', p[1], []]
        else:
            p[0] = ['funccall', p[1], p[3]]

def p_symbol(p):
    '''
    symbol : SYMBOL
    '''
    p[0] = ['symbol', p[1]]

def p_number(p):
    '''
    number : NUMBER
    '''
    p[0] = ['number', p[1]]

def p_string(p):
    '''
    string : STRING
    '''
    p[0] = ['string', p[1]]


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


def makeAST(code):

    parser = yacc.yacc(debug=False, write_tables=False)
    ast = yacc.parse(code, lexer=lexer)

    print(ast)
    print("-----")

    return ast;


