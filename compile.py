import sys
import time
import struct
import MODEL as m
from mnemonic import mnemonic as opc
from mnemonic import mnemonic
from yacc import makeAST


def dumpbytecode(code):
    start = time.time()

    ast = makeAST(code)

    env = m.Env()
    ast.gencode(env)

    funcLocator = {}
    labelLocator = {}

    middlecode = []
    bytecode = []

# search for main
    for elem in env.functions:
        if (elem.symbolname == 'main'):
            middlecode.extend(elem.insts)

# add others
    for elem in env.functions:
        if (elem.symbolname != 'main'):
            middlecode.extend(elem.insts)

# locate func & labels
    for elem in middlecode:
        if (elem.opc == opc.ENTRY):
            funcLocator[elem.arg] = len(bytecode)
        elif (elem.opc == opc.LABEL):
            labelLocator[elem.arg] = len(bytecode)
        else:
            bytecode.append(elem)

# update funcall & jump & JIF0
    for elem in bytecode:
        if (elem.opc == opc.CALL):
            elem.arg = funcLocator[elem.arg]
        elif (elem.opc == opc.JUMP or elem.opc == opc.JIF0):
            elem.arg = labelLocator[elem.arg]
        elif (elem.opc == opc.LOADG or elem.opc == opc.STOREG):
            elem.arg = len(bytecode) + elem.arg

# append global variable space
    for elem in env.globals:
        bytecode.append(m.Inst(opc.DUMMY, elem.initvalue))

# writeout
    stream = ""
    stream += f".string {len(env.strings)}" + '\n'
    for elem in env.strings:
        stream += elem
        stream += '\n'

    stream += f".bytecode {len(bytecode)}" + '\n'
    for elem in bytecode:
        stream += elem.serialize() + '\n'
        #stream += elem.debugserial() + '\n'

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

