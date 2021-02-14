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

def value2hex(val):
    if isinstance(val, int):
        if val > 2147483647: # uint
            arg = format(val, "d")
        else:
            arg = format(struct.unpack('>I', struct.pack('>i', val))[0], "d")

    elif isinstance(val, float):
        arg = format(struct.unpack('>I', struct.pack('>f', val))[0], "d")

    else:
        print(f"serialize arg unkown type error: {val.arg=}")
        return "0"

    return f'{arg}'

def compile(code):

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
            if elem.insts is None:
                g.r.addReport(m.Report('error', None, f"function '{elem.symbolname}' is not implemented"))
                return
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
    for elem in env.statics:
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

    return body


if __name__ == '__main__':
    argparser = ArgumentParser()

    argparser.add_argument('filename',type=str,
                           help='target source file')

    argparser.add_argument('-j', '--json',
                           action='store_true',
                           help='output as json')

    args = argparser.parse_args()

    cpp = Preprocessor()
    cpp.add_path(os.getcwd() + "/lvmxlib")
    tmpf = io.StringIO("")

    with open(args.filename, mode="r") as f:
        cpp.parse(f)

    cpp.write(tmpf)

    g.init(args.filename, tmpf.getvalue())

    try:
        dumps = compile(g.source)
    except Exception as e:
        g.r.report()
        raise

    if dumps is None:
        g.r.report()
        exit(-1)

    delim = "\n"

    if args.json:
        for elem in dumps['code']:
            elem.opc = elem.opc.name
        bytecode = json.dumps(dumps, default=lambda x: x.__dict__)
    else:
        bytecode = f".data {len(dumps['data'])}" + delim
        for elem in dumps['data']:
            bytecode += value2hex(elem) + delim
        bytecode += f".code {len(dumps['code'])}" + delim
        for elem in dumps['code']:
            bytecode += elem.serialize() + delim

    if g.r.hasError():
        g.r.report()
    else:
        if g.r.hasNotice():
            g.r.report()
        print(bytecode)

