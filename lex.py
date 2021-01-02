import glob as g
import MODEL as m
import ply.lex as lex
from tokens import tokens


reserved = {
        'void': 'BASETYPE',
        'any': 'BASETYPE',
        'int': 'BASETYPE',
        'float': 'BASETYPE',
        'struct': 'STRUCT',
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'do': 'DO',
        'while': 'WHILE',
        'for': 'FOR',
        'return': 'RETURN',
        '__raw': 'RAW'
}

states = (
        ('char', 'exclusive'),
        ('string', 'exclusive'),
)

literals = '+-*/%&$^=,.!?:;()<>{}[]'

def t_NUMBERF(t):
    r'-?[0-9]+(([.][0-9]+)(f)?|f)'
    return t

def t_NUMBERU(t):
    r'[0-9]+((e|E)(\+|-)?[0-9]+)?u'
    return t

def t_NUMBERI(t):
    r'-?[0-9]+((e|E)(\+|-)?[0-9]+)?'
    return t

def t_COMMENT(t):
    '/\*[\s\S]*?\*/|//.*'
    t.lexer.lineno += t.value.count('\n')

def t_DIRECTIVE(t):
    '\#.*\n'

def t_INC_OP(t):
    r'\+\+'
    return t

def t_NEQ_OP(t):
    r'--'
    return t

def t_LE_OP(t):
    r'<='
    return t

def t_GE_OP(t):
    r'>='
    return t

def t_EQ_OP(t):
    r'=='
    return t

def t_NE_OP(t):
    r'!='
    return t

def t_LEFT_OP(t):
    r'<<'
    return t

def t_RIGHT_OP(t):
    r'>>'
    return t

def t_MUL_ASSIGN(t):
    r'\*='
    return t

def t_DIV_ASSIGN(t):
    r'/='
    return t

def t_MOD_ASSIGN(t):
    r'%='
    return t

def t_ADD_ASSIGN(t):
    r'\+='
    return t

def t_SUB_ASSIGN(t):
    r'-='
    return t

def t_LEFT_ASSIGN(t):
    r'<<'
    return t

def t_RIGHT_ASSIGN(t):
    r'>>'
    return t

def t_AND_ASSIGN(t):
    r'&='
    return t

def t_XOR_ASSIGN(t):
    r'^='
    return t

def t_OR_ASSIGN(t):
    r'$='
    return t

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'SYMBOL')
    return t

def t_begin_string(t):
    r'"'
    t.lexer.push_state('string')

def t_string_STRING(t):
    r'[^"]+'
    return t

def t_string_end(t):
    r'"'
    t.lexer.pop_state()

def t_begin_char(t):
    r"'"
    t.lexer.push_state('char')

def t_char_CHAR(t):
    r"[^']+"
    return t

def t_char_end(t):
    r"'"
    t.lexer.pop_state()

t_ignore = '\t| '
t_char_ignore = ''
t_string_ignore = ''

def t_newline(t):
    r'\r?\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    g.r.addReport(m.Report('warning', genTokenInfo(t), f'illegal character \'{t.value[0]}\' skipped'))
    t.lexer.skip(1)

def t_char_error(t):
    g.r.addReport(m.Report('warning', genTokenInfo(t), f'illegal character \'{t.value[0]}\' skipped'))
    t.lexer.skip(1)

def t_string_error(t):
    g.r.addReport(m.Report('warning', genTokenInfo(t), f'illegal character \'{t.value[0]}\' skipped'))
    t.lexer.skip(1)

def genTokenInfo(t):

    line_start = g.source.rfind('\n', 0, t.lexpos) + 1
    colno = (t.lexpos - line_start) + 1

    return m.TokenInfo(t.lexer.lineno, colno)

lexer = lex.lex()

if __name__ == '__main__':
    with open('test.c', 'r') as f:
        data = f.read()

    g.init(data)
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

