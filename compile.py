import sys
import time
import struct
import MODEL as m
from mnemonic import mnemonic
from yacc import makeAST

nullarg = '00000000'

globalvars = {}
stringregion = {}
funcs = {}

arguments = {}
localvars = {}

labelitr = 0;

def float2hex(f):
    n = float(f.replace('f', ''))
    return format(struct.unpack('>I', struct.pack('>f', n))[0], "08x")

def int2hex(f):
    n = int(f.replace('u', ''))
    return format(struct.unpack('>I', struct.pack('>i', n))[0], "08x")

def uint2hex(f):
    return format(f, "08x")

def preparecompile():
    globalvars.clear();
    stringregion.clear();
    funcs.clear();
    arguments.clear();
    localvars.clear();
    labelitr.clear();

def decideType(a, b):
    if ('void' in [a, b]):
        print('eval void error')
        return 'error'
    #elif (a == 'any' and b == 'any'):
    #    return 'any'
    #elif (a == 'any'):
    #    return b
    #elif (b == 'any'):
    #    return a
    elif (a == 'uint' and b == 'uint'):
        return 'uint'
    elif (a == 'int' and b == 'int'):
        return 'int'
    elif (a == 'float' and b == 'float'):
        return 'float'
    #elif ('uint' in [a, b] and 'float' in [a, b]):
    #    return 'float'
    #elif ('int' in [a, b] and 'float' in [a, b]):
    #    return 'float'

    print(f'eval type error! {a} and {b}')

    return 'error'


def dumpbytecode(code):
    start = time.time()

    ast = makeAST(code)

    env = m.Env()
    return ast.gencode(env)

    compile(ast)

    funcLocator = {}
    labelLocator = {}

    middlecode = []
    bytecode = []


# search for main
    for key, value in funcs.items():
        if (key == 'main'):
            for byte in value['code']:
                middlecode.append(byte)

# add others
    for key, value in funcs.items():
        if (key != 'main'):
            for byte in value['code']:
                middlecode.append(byte)

# locate func & labels
    for elem in middlecode:
        if (elem[0] == 'ENTRY'):
            funcLocator[elem[1]] = len(bytecode)
        elif (elem[0] == 'LABEL'):
            labelLocator[elem[1]] = len(bytecode)
        else:
            bytecode.append(elem)

# update funcall & jump & JIF0
    for elem in bytecode:
        if (elem[0] == 'CALL'):
            elem[1] = f"{funcLocator[elem[1]]:08x}"
        elif (elem[0] == 'JUMP' or elem[0] == 'JIF0'):
            elem[1] = f"{labelLocator[elem[1]]:08x}"
        elif (elem[0] == 'LOADG' or elem[0] == 'STOREG'):
            elem[1] = f"{len(bytecode) + elem[1]:08x}"

    stream = ""

# append global variable space
    for i in globalvars:
        bytecode.append(['DUMMY', nullarg])

# writeout
    stream += f".string {len(stringregion)}" + '\n'
    for elem in stringregion:
        stream += elem
        stream += '\n'

    stream += f".bytecode {len(bytecode)}" + '\n'
    for elem in bytecode:
        stream += f"{mnemonic[elem[0]]:08x}{elem[1]}" + '\n'

    return stream

    elapsed = time.time() - start
    print(f"done! ({elapsed*1000:.3f}ms)")


if __name__ == '__main__':
    filename = ""
    if (len(sys.argv) == 2):
        filename = sys.argv[1]
    else:
        filename = "test.c"

    data = ""
    with open(filename, mode="r") as f:
        data = f.read()

    bytecode = dumpbytecode(data)

    print(bytecode)

