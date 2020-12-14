import glob
import ply.lex as lex
from tokens import tokens


reserved = {
        'int': 'TYPE',
        'float': 'TYPE',
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'input': 'INPUT',
        'output': 'OUTPUT',
        'readreg': 'READREG',
        'writereg': 'WRITEREG',
        'sin': 'SIN',
        'cos': 'COS',
        'tan': 'TAN',
        'asin': 'ASIN',
        'acos': 'ACOS',
        'atan': 'ATAN',
        'atan2': 'ATAN2',
        'root': 'ROOT',
        'pow': 'POW',
        'log': 'LOG',
        'return': 'RETURN'
}

states = (
        ('string', 'exclusive'),
)

t_COLON = r':'
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','

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

def t_UNIOP(t):
    r'\+\+|--|\!'
    return t

def t_BIOP(t):
    r'<=|>=|==|\!=|<|>'
    return t

def t_ADD(t):
    r'\+'
    return t

def t_SUB(t):
    r'-'
    return t

def t_MUL(t):
    r'\*'
    return t

def t_DIV(t):
    r'/'
    return t

def t_ASSIGN(t):
    r'='
    return t


def t_SYMBOL(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
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

t_ignore = '\t| '
t_string_ignore = ''

def t_newline(t):
    r'\r?\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    glob.lexerrors += f"illegal character '{t.value[0]}'" + '\n'
    t.lexer.skip(1)

def t_string_error(t):
    glob.lexerrors += f"illegal character '{t.value[0]}'" + '\n'
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    with open('test.c', 'r') as f:
        data = f.read()

    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

