import sys
import time
from mnemonic import mnemonic
from yacc import makeAST


globalvars = {}
stringregion = {}
funcs = []

arguments = {}
localvars = {}

labelitr = 0;

def compile(ast):
    global labelitr
    f = ast[0]

    if (f == 'program'):
        for elem in ast[1]:
            compile(elem)
    elif (f == 'globalvar'):
        globalvars[ast[1]] = len(globalvars)
    elif (f == 'func'):
        frame = []
        code = []
        arguments.clear()
        localvars.clear()
        for elem in ast[2]:
            arguments[elem] = len(arguments)
        for elem in ast[3]: # code
            code.extend(compile(elem))
        frame.append(['ENTRY', ast[1]])
        frame.append(['FRAME', len(localvars)])
        frame.extend(code)
        frame.append(['RET', 0])
        funcs.append([ast[1], frame])

    elif (f == 'localvar'):
        localvars[ast[1]] = len(localvars)
        code = compile(ast[2])
        code.append(['STOREL', localvars[ast[1]]])
        return code

    elif (f == 'return'):
        if (ast[1] != None):
            code = compile(ast[1])
            code.append(['RET', 0])
            return code
        else:
            return [['RET', 0]]

    elif (f == 'funccall'):
        code = []
        for elem in ast[2]:
            code.extend(compile(elem))
        code.append(['CALL', ast[1]])
        code.append(['POPR', len(ast[2])])
        return code

    elif (f == 'if'):
        cond = compile(ast[1])
        blck = []
        for elem in ast[2]:
            blck.extend(compile(elem))

        l0 = labelitr
        labelitr += 1

        code = cond
        code.append(['JIF0', l0])
        code.extend(blck)
        code.append(['LABEL', l0])
        return code


    elif (f == 'ifelse'):
        cond = compile(ast[1])
        blck = []
        for elem in ast[2]:
            blck.extend(compile(elem))

        blelse = []
        for elem in ast[3]:
            blelse.extend(compile(elem))

        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1

        code = cond
        code.append(['JIF0', l0])
        code.extend(blck)
        code.append(['JUMP', l1])
        code.append(['LABEL', l0])
        code.extend(blelse)
        code.append(['LABEL', l1])
        return code

    elif (f == 'while'):
        cond = compile(ast[1])
        blck = []
        for elem in ast[2]:
            blck.extend(compile(elem))

        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1

        code = [['LABEL', l0]]
        code.extend(cond)
        code.append(['JIF0', l1])
        code.extend(blck)
        code.append(['JUMP', l0])
        code.append(['LABEL', l1])
        return code

    elif (f == 'for'):
        init = compile(ast[1])
        cond = compile(ast[2])
        cont = compile(ast[3])
        blck = []
        for elem in ast[4]:
            blck.extend(compile(elem))
        code = init
        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1
        code.append(['LABEL', l0])
        code.extend(cond)
        code.append(['JIF0', l1])
        code.extend(blck)
        code.extend(cont)
        code.append(['JUMP', l0])
        code.append(['LABEL', l1])
        return code

    elif (f == 'input'):
        stringslot = compile(ast[1]) # TODO error check
        return [['INPUT', stringslot[0][1]]]

    elif (f == 'output'):
        stringslot = compile(ast[1]) # TODO error check
        code = (compile(ast[2]))
        code.append(['OUTPUT', stringslot[0][1]])
        return code

    elif (f == 'readreg'):
        addr = compile(ast[1])
        return [['LOADR', addr[0][1]]]

    elif (f == 'writereg'):
        addr = compile(ast[1])
        code = (compile(ast[2]))
        code.append(['STORER', addr[0][1]])
        return code

    elif (f == 'assign'):
        code = compile(ast[2])
        if (ast[1] in localvars):
            code.append(['STOREL', localvars[ast[1]]])
            return code
        elif (ast[1] in arguments):
            code.append(['STOREA', arguments[ast[1]]])
            return code
        elif (ast[1] in globalvars):
            code.append(['STOREG', globalvars[ast[1]]])
            return code
        else:
            print("variable not found")

    elif (f == 'inc'):
        code = compile(ast[1])
        code.extend([['PUSH', 1], ['ADD', 0]])
        if (ast[1][1] in localvars):
            code.append(['STOREL', localvars[ast[1][1]]])
            return code
        elif (ast[1][1] in arguments):
            code.append(['STOREA', arguments[ast[1][1]]])
            return code
        elif (ast[1][1] in globalvars):
            code.append(['STOREG', globalvars[ast[1][1]]])
            return code
        else:
            print("variable not found")
        return code

    elif (f == 'dec'):
        code = compile(ast[1])
        code.extend([['PUSH', 1], ['SUB', 0]])
        if (ast[1][1] in localvars):
            code.append(['STOREL', localvars[ast[1][1]]])
            return code
        elif (ast[1][1] in arguments):
            code.append(['STOREA', arguments[ast[1][1]]])
            return code
        elif (ast[1][1] in globalvars):
            code.append(['STOREG', globalvars[ast[1][1]]])
            return code
        else:
            print("variable not found")
        return code

    elif (f == 'inv'):
        code = compile(ast[1])
        code.extend([['PUSH', -1], ['MUL', 0]])
        return code

    elif (f == 'add'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['ADD', 0])
        return code

    elif (f == 'sub'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['SUB', 0])
        return code

    elif (f == 'mul'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['MUL', 0])
        return code

    elif (f == 'div'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['DIV', 0])
        return code

    elif (f == 'lt'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['LT', 0])
        return code

    elif (f == 'lte'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['LTE', 0])
        return code

    elif (f == 'gt'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['GT', 0])
        return code

    elif (f == 'gte'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['GTE', 0])
        return code

    elif (f == 'eq'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['EQ', 0])
        return code

    elif (f == 'neq'):
        code = compile(ast[2])
        code.extend(compile(ast[1]))
        code.append(['NEQ', 0])
        return code

    elif (f == 'ternary'):
        pass

    elif (f == 'symbol'):
        if (ast[1] in localvars):
            return [['LOADL', localvars[ast[1]]]]
        elif (ast[1] in arguments):
            return [['LOADA', arguments[ast[1]]]]
        elif (ast[1] in globalvars):
            return [['LOADG', globalvars[ast[1]]]]
        else:
            print("variable not found")

    elif (f == 'number'):
        return [['PUSH', ast[1]]]

    elif (f == 'string'):
        if (ast[1] not in stringregion):
            stringregion[ast[1]] = len(stringregion)
        return [['PUSH', stringregion[ast[1]]]]

    return [['ERROR', f]]


def dumpbytecode(code):
    start = time.time()

    ast = makeAST(code)

    compile(ast)

    funcLocator = {}
    labelLocator = {}

    middlecode = []
    bytecode = []

# search for main
    for elem in funcs:
        if (elem[0] == 'main'):
            for byte in elem[1]:
                middlecode.append(byte)

# add others
    for elem in funcs:
        if (elem[0] != 'main'):
            for byte in elem[1]:
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
            elem[1] = funcLocator[elem[1]]
        elif (elem[0] == 'JUMP' or elem[0] == 'JIF0'):
            elem[1] = labelLocator[elem[1]]
        elif (elem[0] == 'LOADG' or elem[0] == 'STOREG'):
            elem[1] = len(bytecode) + elem[1];

    stream = ""

# append global variable space
    for i in globalvars:
        bytecode.append(['DUMMY', 0])

# writeout
    stream += f".string {len(stringregion)}" + '\n'
    for elem in stringregion:
        stream += elem
        stream += '\n'

    stream += f".bytecode {len(bytecode)}" + '\n'
    for elem in bytecode:
        stream += f"{mnemonic[elem[0]]:04x}{int(elem[1]):04x}" + '\n'

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

