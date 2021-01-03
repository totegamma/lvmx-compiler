import io
import os
import sys
import json
import time
import struct
import glob as g
import MODEL as m
from node import OPT
from pcpp import Preprocessor
from argparse import ArgumentParser
from mnemonic import mnemonic as opc
from astConstructor import makeAST

def dumpjson(code):

    body = {}

    start = time.time()

    ast = makeAST(code)
    if g.r.hasError():
        return

    env = m.Env()
    ast.gencode(env, OPT())
    if g.r.hasError():
        return

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

# overwrite mnemonic
    for elem in bytecode:
        elem.opc = elem.opc.name

    data = []
    for elem in env.globals:
        if isinstance(elem, m.Symbol):
            if isinstance(elem.initvalue, list):
                for value in elem.initvalue:
                    data.append(value)
            else:
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

    rawinput = ""
    with open(args.filename, mode="r") as f:
        rawinput = f.read()

    cpp = Preprocessor()
    cpp.add_path(os.getcwd() + "/lvmxlib")
    cpp.parse(rawinput)
    tmpf = io.StringIO("")
    cpp.write(tmpf)

    g.init(tmpf.getvalue())

    try:
        if args.json:
            bytecode = dumpjson(g.source)
        else:
            bytecode = dumpbytecode(g.source)
    except Exception as e:
        g.r.report()
        raise

    if g.r.hasError():
        g.r.report()
    else:
        if g.r.hasNotice():
            g.r.report()
        print(bytecode)

