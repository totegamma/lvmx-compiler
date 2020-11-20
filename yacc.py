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
    p[0] = {
            'op': 'program',
            'body': p[1]
            }

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
        p[0] = {
                'op': 'globalvar',
                'type': p[1],
                'symbol': p[2],
                'body': {
                    'op': 'number',
                    'type': p[1],
                    'body': 0
                    }
                }
    elif (len(p) == 5):
        p[0] = {
                'op': 'func',
                'type': p[1],
                'symbol': p[2],
                'arg': p[3],
                'body': p[4]
                }
    else:
        p[0] = {
                'op': 'globalvar',
                'type': p[1],
                'symbol': p[2],
                'body': p[4]
                }

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
        p[0] = [p[1], p[2]]
    if (len(p) == 5):
        p[0] = [p[1], [p[3], p[4]]]

def p_block(p):
    '''
    block : LBRACE statements RBRACE
    '''
    p[0] = {
            'op': 'block',
            'body': p[2]
            }

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
            p[0] = {
                    'op': 'return',
                    'body': None
                    }
        else:
            p[0] = {
                    'op': 'return',
                    'body': p[2]
                    }
    elif (p[1] == 'if'):
        if (len(p) == 6):
            p[0] = {
                    'op': 'if',
                    'cond': p[3],
                    'then': p[5]
                    }
        else:
            p[0] = {
                    'op': 'ifelse', 
                    'cond': p[3],
                    'then': p[5],
                    'else': p[7]
                    }

    elif (p[1] == 'while'):
        p[0] = {
                'op': 'while',
                'cond': p[3],
                'body': p[5]
                }
    elif (p[1] == 'for'):
        p[0] = {
                'op': 'for',
                'init': p[3],
                'cond': p[5],
                'loop': p[7],
                'body': p[9]
                }
    else:
        p[0] = p[1];

def p_local_vars(p):
    '''
    local_vars : TYPE SYMBOL SEMICOLON
    local_vars : TYPE SYMBOL ASSIGN expr SEMICOLON
    '''
    if (len(p) == 4):
        p[0] = {
                'op': 'localvar',
                'type': p[1],
                'symbol': p[2],
                'body': {
                    'op': 'number',
                    'type': p[1],
                    'body': 0
                    }
                }
    else:
        p[0] = {
                'op': 'localvar',
                'type': p[1],
                'symbol': p[2],
                'body': p[4]
                }

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
        p[0] = {
                'op': 'output',
                'key': p[3],
                'value': p[5]
                }
    elif (p[1] == 'writereg'):
        p[0] = {
                'op': 'writereg',
                'key': p[3],
                'value': p[5]
                }
    elif (p[2] == '='):
        p[0] = {
                'op': 'assign',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '!'):
        p[0] = {
                'op': 'inv',
                'right': p[2]
                }
    elif (p[2] == '+'):
        p[0] = {
                'op': 'add',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '-'):
        p[0] = {
                'op': 'sub',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '*'):
        p[0] = {
                'op': 'mul',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '/'):
        p[0] = {
                'op': 'div',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '<'):
        p[0] = {
                'op': 'lt',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '<='):
        p[0] = {
                'op': 'lte',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '>'):
        p[0] = {
                'op': 'gt',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '>='):
        p[0] = {
                'op': 'gte',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '=='):
        p[0] = {
                'op': 'eq',
                'left': p[1],
                'right': p[3]
                }
    elif (p[2] == '!='):
        p[0] = {
                'op': 'neq',
                'left': p[1],
                'right': p[3]
                }
    elif (p[1] == '++'):
        p[0] = {
                'op': 'inc',
                'right': p[2]
                }
    elif (p[1] == '--'):
        p[0] = {
                'op': 'dec',
                'right': p[2]
                }
    elif (p[2] == '?'):
        p[0] = {
                'op': 'ternary',
                'cond': p[1],
                'true': p[3],
                'false': p[5]
                }
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
        p[0] = {
                'op': 'input',
                'key': p[3]
                }
    elif (p[1] == "readreg"):
        p[0] = {
                'op': 'readreg',
                'key': p[3]
                }
    else:
        if (len(p) == 4):
            p[0] = {
                    'op': 'funccall',
                    'name': p[1],
                    'arg': []
                    }
        else:
            p[0] = {
                    'op': 'funccall',
                    'name': p[1],
                    'arg': p[3]
                    }

def p_symbol(p):
    '''
    symbol : SYMBOL
    '''
    p[0] = {
            'op': 'symbol',
            'body': p[1]
            }

def p_numberi(p):
    '''
    number : NUMBERI
    '''
    p[0] = {
            'op': 'numberi',
            'body': p[1]
            }

def p_numberf(p):
    '''
    number : NUMBERF
    '''
    p[0] = {
            'op': 'numberf',
            'body': p[1]
            }

def p_string(p):
    '''
    string : STRING
    '''
    p[0] = {
            'op': 'string',
            'body': p[1]
            }


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

    #print(ast)

    return ast;

if __name__ == '__main__':
    with open('test.c', 'r') as f:
        data = f.read()

    parser = yacc.yacc(debug=True, write_tables=False)
    ast = yacc.parse(data, lexer=lexer)

    print(ast)


