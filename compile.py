import sys
import json
import time
import glob
import struct
import MODEL as m
from argparse import ArgumentParser
from mnemonic import mnemonic as opc
from mnemonic import mnemonic
from yacc import makeAST

def value2hex(val):
    if isinstance(val, int):
        if val > 2147483647: # uint
            arg = format(val, "08x")
        else:
            arg = format(struct.unpack('>I', struct.pack('>i', val))[0], "08x")

    elif isinstance(val, float):
        arg = format(struct.unpack('>I', struct.pack('>f', val))[0], "08x")

    else:
        print(f"serialize arg unkown type error: {val.arg=}")
        return "0000000000000000"

    return f'00000000{arg}'


def dumpbytecode(code):

    start = time.time()

    ast = makeAST(code)
    if (glob.lexerrors != '' or glob.yaccerrors != ''):
        return glob.lexerrors + glob.yaccerrors

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

# writeout
    stream = ""
    stream += f".string {len(env.strings)}" + '\n'
    for elem in env.strings:
        stream += elem
        stream += '\n'

    # append global variable space
    stream += f".global {len(env.globals)}" + '\n'
    for elem in env.globals:
        stream += value2hex(elem.initvalue) + '\n'

    stream += f".bytecode {len(bytecode)}" + '\n'
    for elem in bytecode:
        stream += elem.serialize() + '\n'
        #stream += elem.debugserial() + '\n'

    return stream

    elapsed = time.time() - start
    print(f"done! ({elapsed*1000:.3f}ms)")


def dumpjson(code):

    body = {}

    start = time.time()

    ast = makeAST(code)
    if (glob.lexerrors != '' or glob.yaccerrors != ''):
        return glob.lexerrors + glob.yaccerrors

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

    data = []
    for elem in env.globals:
        if isinstance(elem, m.Symbol):
            data.append(elem.initvalue)
        elif isinstance(elem, str):
            for c in elem:
                data.append(int.from_bytes(c.encode('utf-32be'), byteorder='big'))
            data.append(0)
        else:
            console.log("program error")

    body['code'] = bytecode
    body['data'] = data

    return json.dumps(body, default=lambda x: x.__dict__)


if __name__ == '__main__':
    argparser = ArgumentParser()

    argparser.add_argument('filename',type=str,
                           nargs='?',
                           default="test.c",
                           help='target source file')

    argparser.add_argument('-j', '--json',
                           action='store_true',
                           help='output as json')

    args = argparser.parse_args()

    data = ""
    with open(args.filename, mode="r") as f:
        data = f.read()

    glob.init()

    try:
        if args.json:
            bytecode = dumpjson(data)
        else:
            bytecode = dumpbytecode(data)
    except Exception as e:
        if (glob.lexerrors != '' or glob.yaccerrors != '' or glob.compileerrors != ''):
            print(glob.lexerrors)
            print(glob.yaccerrors)
            print(glob.compileerrors)
        raise

    if (glob.lexerrors != '' or glob.yaccerrors != '' or glob.compileerrors != ''):
        print(glob.lexerrors)
        print(glob.yaccerrors)
        print(glob.compileerrors)
        exit(-1)

    print(bytecode)

